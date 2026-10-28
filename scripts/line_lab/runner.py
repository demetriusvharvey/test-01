"""Runner components for the picks pipeline."""
import hashlib, json, os
from datetime import datetime, timedelta, timezone
from statistics import median
from scripts.refresh_feed import NBA_REFS, parse_referees
from .constants import *
from .ingest import *
from .model import *
from .market import *
from .ledger import *
from .report import *
from .history import append_observations, finalize_closing_proxies, aware
from .odds_api import collect_odds_api
from .quality import validate_and_deduplicate, reconcile_quotes
from .heartbeat import record_run
from .experiment import record_forecasts, record_outcomes, build_scoreboard
from .nfl_shadow import build_nfl_shadow_context


def main():
    now=datetime.now(timezone.utc); started_at=now.isoformat(); today=now.astimezone(ET).date(); errors=[]; games=[]; nfl_locations={};nfl_csv='';nfl_observed_at=None;source_hashes={'NBA':{},'NFL':{}}
    for season in NBA_SEASONS:
        try:
            text=get(f'https://boxscorelab.com/downloads/{season}-team-game-results.csv')
            result=parse_nba_csv(text)
            if not result: raise ValueError('empty NBA season')
            games.extend(result)
            source_hashes['NBA'][season]=hashlib.sha256(text.encode('utf-8')).hexdigest()
        except Exception as e: errors.append('NBA historical data unavailable: '+season+' ('+type(e).__name__+')')
    try:
        nfl_csv=get('https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv')
        nfl_observed_at=datetime.now(timezone.utc).isoformat()
        nfl=parse_nfl_csv(nfl_csv); nfl_locations=parse_nfl_locations(nfl_csv)
        if not nfl: raise ValueError('empty NFL data')
        games.extend(nfl)
        source_hashes['NFL']['games.csv']=hashlib.sha256(nfl_csv.encode('utf-8')).hexdigest()
    except Exception as e: errors.append('NFL historical data unavailable ('+type(e).__name__+')')
    models={league:train_model(games,today,league) for league in ('NBA','NFL')}
    for league,model in models.items():model['source_hashes']=source_hashes[league]
    raw=[]; data_root=os.environ.get('PICKS_DATA_ROOT','').strip()
    for slug,name in BOOKS:
        for league in ('NBA','NFL'):
            try:
                rows,asof=parse_book_html(get(f'https://agentbets.ai/odds/{slug}/{league.lower()}'),name,league,now)
                fetched=datetime.now(timezone.utc).isoformat()
                for row in rows: row.update({'provider':'agentbets','provider_event_id':row['id'],'fetched_at':fetched})
                raw.extend(rows)
            except Exception as e: errors.append(f'{name} {league} odds unavailable ({type(e).__name__})')
    api_key=os.environ.get('ODDS_API_KEY','').strip()
    if data_root:
        try:
            api_rows,api_warnings=collect_odds_api(data_root,api_key,datetime.now(timezone.utc).isoformat())
            raw.extend(api_rows)
            for warning in api_warnings: print('ODDS SOURCE:',warning)
        except Exception as e:
            errors.append('Second odds source unavailable ('+type(e).__name__+')')
    else:
        errors.append('Odds history storage is not configured')
    data_dir=ROOT/'data'; data_dir.mkdir(exist_ok=True)
    ledger_path=data_dir/'predictions.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    legacy_path=data_dir/'legacy_pick_quotes.json'
    if legacy_path.exists(): backfill_initial_books(ledger,json.loads(legacy_path.read_text()))
    refs_path=data_dir/'referee_history.json'
    refs=json.loads(refs_path.read_text()) if refs_path.exists() else []
    try:
        ref_report=parse_referees(get(NBA_REFS),today)
        observed_at=datetime.now(timezone.utc)
        print('NBA referees:',ref_report['status'],'new/changed:',append_referee_assignments(refs,ref_report,observed_at))
    except Exception as e:
        print('NBA referee source unavailable:',type(e).__name__)
    refs_path.write_text(json.dumps(refs,indent=2)+'\n')
    finals=[{'id':g['id'],'home':g['home'],'away':g['away'],'home_score':g['home_score'],'away_score':g['away_score'],'source':'BoxScore Lab' if g['league']=='NBA' else 'nflverse'} for g in games if g['date']<=today]
    espn_starts={}; espn_finals=[]
    for league,sport in [('NBA','basketball/nba'),('NFL','football/nfl')]:
        for days_ago in range(0,4):
            day=(today-timedelta(days=days_ago)).strftime('%Y%m%d')
            try:
                payload=json.loads(get(f'https://site.api.espn.com/apis/site/v2/sports/{sport}/scoreboard?dates={day}',10))
                result=parse_espn_results(payload,league)
                finals.extend(result); espn_finals.extend(result); espn_starts.update(parse_espn_starts(payload,league))
            except Exception as e: errors.append(f'{league} scores {day} unavailable ({type(e).__name__})')
    now=datetime.now(timezone.utc)
    day_rolled=now.astimezone(ET).date()!=today
    if day_rolled: errors.append('ET date changed during update; new picks suppressed')
    grade_ledger(ledger,finals,now)
    added_finals=apply_same_day_finals(models,espn_finals,today,nfl_locations,now)
    clean,quality_warnings=validate_and_deduplicate(raw,now.isoformat())
    if quality_warnings: errors.append(f'{len(quality_warnings)} invalid or conflicting source quotes rejected')
    verified=[]
    for quote in clean:
        official=espn_starts.get(quote['id'])
        if not official or abs((aware(official)-aware(quote['starts_at'])).total_seconds())>20*60: continue
        if aware(quote['fetched_at'])>=aware(official): continue
        verified.append(quote)
    archive_ok=False
    if data_root:
        try:
            count=append_observations(data_root,verified,now.isoformat())
            closed=finalize_closing_proxies(data_root,now.isoformat(),espn_starts)
            if record_run(data_root,started_at): errors.append('A scheduled update was missed or delayed; gaps in history are possible')
            print('History:',count,'new observations;',closed,'last-observed pregame proxies')
            archive_ok=True
        except Exception as e:
            errors.append('Odds history storage unavailable ('+type(e).__name__+')')
    reconciled,disagreements=reconcile_quotes(verified)
    if disagreements: errors.append(f'{len(disagreements)} sportsbook/source disagreements quarantined')
    selected=[]
    for quote in reconciled:
        official=espn_starts.get(quote['id'])
        item=dict(quote);item['starts_at']=min(aware(quote['starts_at']),aware(official)).isoformat();selected.append(item)
    markets=build_market(selected,now)
    for event in markets.values():
        if event['league']=='NFL' and event['id'] in nfl_locations: event['neutral']=nfl_locations[event['id']]
        if event['id'] in espn_starts:
            event['starts_at']=min(event['starts_at'],espn_starts[event['id']])
    # If a league's training history is missing, do not produce predictions for it.
    blocked={('NBA' if x.startswith('NBA historical') else 'NFL') for x in errors if x.startswith(('NBA historical','NFL historical'))}
    permitted={k:v for k,v in markets.items() if archive_ok and not day_rolled and v['league'] not in blocked and (v['league']!='NFL' or 'neutral' in v)}
    try:
        if data_root and archive_ok:
            result_count=record_outcomes(data_root,finals,now.isoformat())
            shadow={}
            if nfl_csv and nfl_observed_at:
                try:shadow=build_nfl_shadow_context(data_root,nfl_csv,nfl_observed_at,now.isoformat())
                except Exception as exc:print('NFL shadow context unavailable:',type(exc).__name__)
            forecast_count=record_forecasts(data_root,permitted,models,now.isoformat(),shadow)
            print('Paper study:',forecast_count,'forecasts;',result_count,'confirmed outcomes')
    except Exception as e:
        errors.append('Paper study storage unavailable ('+type(e).__name__+')')
        permitted={}
    print('Training games:', len([x for x in games if x['league']=='NBA']), 'NBA;', len([x for x in games if x['league']=='NFL']), 'NFL. Fresh matchups:', len(markets))
    for league,model in models.items(): print('MODEL',league,'selection',model.get('validation_season'),'holdout',model.get('holdout_season'),'games',model.get('validation_count'),'brier',model.get('validation_brier'),'params',model['k'],model['home_advantage'],model['rest_weight'],model.get('form_weight',0),'same-day finals',added_finals[league])
    for event in permitted.values():
        start=datetime.fromisoformat(event['starts_at'])
        if start.astimezone(ET).date()!=today or len(event['books'])<3: continue
        estimate=project_home(models[event['league']],event['home'],event['away'],start,event.get('neutral',False))
        if estimate is None: continue
        print('TODAY', event['league'],event['away'],'at',event['home'],'pure model home',round(100*estimate,1),'best home',max(v['home'] for v in event['books'].values()),'best away',max(v['away'] for v in event['books'].values()))
    ledger.extend(choose_candidates(permitted,models,now,ledger))
    ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
    training_counts={league:sum(1 for g in games if g['league']==league and g['date']<today) for league in ('NBA','NFL')}
    board=render_board(markets,ledger,now,errors,models,training_counts,added_finals)
    try: board['study']=build_scoreboard(data_root,ledger,now.isoformat()) if data_root else {}
    except Exception as e:
        board['study']={};board['errors'].append('Paper study report unavailable ('+type(e).__name__+')')
    board['source_status']={'the_odds_api':'configured' if api_key else 'missing_api_key',
                            'odds_history':'available' if archive_ok else 'unavailable',
                            'cross_check_independent':False}
    (ROOT/'dist'/'board.json').write_text(json.dumps(board,indent=2)+'\n')
    print('Board:',len(board['picks']),'active picks;',board['accuracy']['wins'],'wins;',board['accuracy']['losses'],'losses;',len(errors),'source warnings')
    for e in errors: print('SOURCE:',e)
    if not raw: print('No odds sources reachable; board intentionally has no active picks.')
