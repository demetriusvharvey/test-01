"""Runner components for the picks pipeline."""
import copy, hashlib, json, os
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
from .ledger_v2 import attach_retail_closing_proxies, paper_breakdowns, validate_transition
from .model_stack import record_challenger_forecasts
from .trust import record_candidates
from .validation import progress_from_ledger
from .monitoring import build_monitoring
from .line_movement import attach_histories
from .schedule_context import attach_rest_context
from .referees import attach_current_officials
from .availability import attach_nfl_reports, nfl_report_context
from .availability_features import availability_features
from .research_dashboard import research_dashboard
from .reproducibility import attach_prediction_checks
from .watchlist import render_watchlist
from .nba_injury_feed import fetch_nba_injuries, attach_nba_summaries


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
            featured=os.environ.get('ODDS_API_FEATURED_MARKETS','').strip().lower()=='true'
            api_rows,api_warnings=collect_odds_api(data_root,api_key,datetime.now(timezone.utc).isoformat(),featured=featured)
            raw.extend(api_rows)
            for warning in api_warnings: print('ODDS SOURCE:',warning)
        except Exception as e:
            errors.append('Second odds source unavailable ('+type(e).__name__+')')
    else:
        errors.append('Odds history storage is not configured')
    data_dir=ROOT/'data'; data_dir.mkdir(exist_ok=True)
    ledger_path=data_dir/'predictions.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    frozen_ledger=copy.deepcopy(ledger)
    refs_path=data_dir/'referee_history.json'
    refs=json.loads(refs_path.read_text()) if refs_path.exists() else []
    ref_report=None;ref_observed_at=None
    try:
        ref_report=parse_referees(get(NBA_REFS),today)
        observed_at=datetime.now(timezone.utc)
        ref_observed_at=observed_at.isoformat()
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
    # Capture status before the forecast timestamp, not after a pick is frozen.
    nba_injury_key=os.environ.get('PROPLINE_API_KEY','').strip()
    nba_injury_enabled=os.environ.get('PROPLINE_INJURY_ENABLED','').strip().lower()=='true'
    injury_payload=None;injury_observed_at=None
    if nba_injury_enabled and nba_injury_key and any(e.get('league')=='NBA' for e in markets.values()):
        try:injury_payload,injury_observed_at=fetch_nba_injuries(nba_injury_key,True)
        except Exception as e:errors.append('NBA injury context unavailable ('+type(e).__name__+')')
    now=datetime.now(timezone.utc)
    if now.astimezone(ET).date()!=today and not day_rolled:
        day_rolled=True;errors.append('ET date changed during update; new picks suppressed')
    # Reapply freshness and start-time checks after the optional network call.
    markets=build_market(selected,now)
    for event in markets.values():
        if event['league']=='NFL' and event['id'] in nfl_locations: event['neutral']=nfl_locations[event['id']]
        if event['id'] in espn_starts:
            event['starts_at']=min(event['starts_at'],espn_starts[event['id']])
    # If a league's training history is missing, do not produce predictions for it.
    blocked={('NBA' if x.startswith('NBA historical') else 'NFL') for x in errors if x.startswith(('NBA historical','NFL historical'))}
    permitted={k:v for k,v in markets.items() if archive_ok and not day_rolled and v['league'] not in blocked and (v['league']!='NFL' or 'neutral' in v)}
    status_by_game={};nba_context={}
    if injury_payload is not None:
        try:
            temp={'picks':[{'id':key} for key in permitted]}
            attach_nba_summaries(temp,markets,injury_payload,injury_observed_at)
            nba_context={row['id']:row['nba_availability_context'] for row in temp['picks'] if row.get('nba_availability_context')}
        except Exception as exc:errors.append('NBA injury context invalid ('+type(exc).__name__+')')
    for key,event in permitted.items():
        try:
            context=nba_context.get(key) if event['league']=='NBA' else nfl_report_context(data_root,event,nfl_csv,nfl_observed_at,now.isoformat(),max_players=1000) if data_root and nfl_csv and nfl_observed_at else None
            features=availability_features(event,context,now.isoformat())
            if features:status_by_game[key]=features
        except Exception as exc:errors.append(event['league']+' injury research unavailable ('+type(exc).__name__+')')
    try:
        if data_root and archive_ok:
            result_count=record_outcomes(data_root,finals,now.isoformat())
            qb_shadow={}
            if nfl_csv and nfl_observed_at:
                try:qb_shadow=build_nfl_shadow_context(data_root,nfl_csv,nfl_observed_at,now.isoformat())
                except Exception as exc:print('NFL shadow context unavailable:',type(exc).__name__)
            shadow={key:{'quarterback':qb_shadow.get(key),'availability':status_by_game.get(key)}
                    for key in permitted if key in qb_shadow or key in status_by_game}
            forecast_count=record_forecasts(data_root,permitted,models,now.isoformat(),shadow)
            print('Paper study:',forecast_count,'forecasts;',result_count,'confirmed outcomes')
            challenger_count=record_challenger_forecasts(data_root,permitted,models,now.isoformat(),status_by_game)
            print('Shadow challenger:',challenger_count,'forecasts; no automatic promotion')
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
    chosen=choose_candidates(permitted,models,now,ledger)
    if data_root and archive_ok:
        try:
            candidate_count=record_candidates(data_root,permitted,models,now.isoformat(),ledger,chosen)
            print('Candidate audit:',candidate_count,'selected and skipped paper sides')
        except Exception as e:
            errors.append('Candidate audit unavailable ('+type(e).__name__+')')
            chosen=[]
    ledger.extend(chosen)
    try:
        if data_root: attach_retail_closing_proxies(data_root,ledger)
        validate_transition(frozen_ledger,ledger)
    except Exception as e:
        # Never publish a rewritten historical pick if integrity fails.
        errors.append('Ledger integrity check failed ('+type(e).__name__+')')
        ledger=copy.deepcopy(frozen_ledger)
    ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
    training_counts={league:sum(1 for g in games if g['league']==league and g['date']<today) for league in ('NBA','NFL')}
    board=render_board(markets,ledger,now,errors,models,training_counts,added_finals)
    attach_prediction_checks(board,ledger)
    try:
        watch_path=data_dir/'watchlist.json'
        watched=json.loads(watch_path.read_text()) if watch_path.exists() else []
        board['watchlist']=render_watchlist(markets,watched,now.isoformat()) if isinstance(watched,list) else []
    except (OSError,ValueError,TypeError):
        board['watchlist']=[];board['errors'].append('Watchlist unavailable')
    if injury_payload is not None:
        try:attach_nba_summaries(board,markets,injury_payload,injury_observed_at)
        except Exception as e:board['errors'].append('NBA injury context unavailable ('+type(e).__name__+')')
    attach_rest_context(board,markets,models,now.isoformat())
    attach_current_officials(board,markets,ref_report,ref_observed_at,now.isoformat())
    try:
        if data_root:attach_nfl_reports(data_root,board,markets,nfl_csv,nfl_observed_at,now.isoformat())
    except Exception as e:
        board['errors'].append('Injury context unavailable ('+type(e).__name__+')')
    try:
        if data_root:attach_histories(data_root,board,markets,ledger,now.isoformat())
    except Exception as e:
        board['errors'].append('Observed line history unavailable ('+type(e).__name__+')')
    watch_board={'picks':board['watchlist'],'errors':board['errors']}
    attach_rest_context(watch_board,markets,models,now.isoformat())
    attach_current_officials(watch_board,markets,ref_report,ref_observed_at,now.isoformat())
    try:
        if data_root:
            attach_nfl_reports(data_root,watch_board,markets,nfl_csv,nfl_observed_at,now.isoformat())
            attach_histories(data_root,watch_board,markets,board['watchlist'],now.isoformat())
    except Exception as e:
        board['errors'].append('Watchlist context unavailable ('+type(e).__name__+')')
    try: board['study']=build_scoreboard(data_root,ledger,now.isoformat()) if data_root else {}
    except Exception as e:
        board['study']={};board['errors'].append('Paper study report unavailable ('+type(e).__name__+')')
    board['paper_breakdowns']=paper_breakdowns(ledger)
    board['validation_progress']=progress_from_ledger(ledger)
    try:board['research_dashboard']=research_dashboard(data_root,now.isoformat()) if data_root else {}
    except Exception as e:
        board['research_dashboard']={};board['errors'].append('Research dashboard unavailable ('+type(e).__name__+')')
    try:
        board['monitoring']=build_monitoring(data_root,now.isoformat(),markets,board['errors']) if data_root else {}
    except Exception as e:
        board['monitoring']={};board['errors'].append('Monitoring unavailable ('+type(e).__name__+')')
    board['source_status']={'the_odds_api':'configured' if api_key else 'missing_api_key',
                            'odds_history':'available' if archive_ok else 'unavailable',
                            'nba_injury_context':'configured' if nba_injury_key and nba_injury_enabled else 'not_configured',
                            'cross_check_independent':False}
    (ROOT/'dist'/'board.json').write_text(json.dumps(board,indent=2)+'\n')
    print('Board:',len(board['picks']),'active picks;',board['accuracy']['wins'],'wins;',board['accuracy']['losses'],'losses;',len(errors),'source warnings')
    print(json.dumps({'event':'pipeline_complete','generated_at':now.isoformat(),'active_board_picks':len(board['picks']),
                      'quote_count':len(verified),'source_warnings':len(board['errors']),'archive_ok':archive_ok},sort_keys=True))
    for e in errors: print('SOURCE:',e)
    if not raw: print('No odds sources reachable; board intentionally has no active picks.')
