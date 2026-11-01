"""Production forecast/decision boundary. A forecast is never itself a bet.

Legacy selections keep their original denominator. New refreshes are append
only, and first pregame forecasts are scored separately from legacy picks.
"""
import json,math,sqlite3
from pathlib import Path
from datetime import date,timedelta
from .history import aware
from .constants import ET
from .market import moneyline_calculation
from .ledger_v2 import snapshot_hash,feature_snapshot
from .league_forecast import examples,infer
from .model import project_home


def metrics(rows):
    settled=[r for r in rows if r.get('outcome') in ('win','loss')]
    n=len(settled);wins=sum((r.get('probability',1)>=.5)==(r['outcome']=='win') for r in settled)
    valid=[r for r in settled if type(r.get('probability')) in (int,float) and math.isfinite(r['probability']) and 0<r['probability']<1]
    pairs=[(r['probability'],int(r['outcome']=='win')) for r in valid]
    bins=[]
    for low,high in ((0,.5),(.5,.6),(.6,.7),(.7,.8),(.8,.9),(.9,1.000001)):
        band=[(p,y) for p,y in pairs if low<=p<high]
        bins.append({'range':[low,min(high,1)],'sample_size':len(band),
                     'mean_probability':sum(p for p,y in band)/len(band) if band else None,
                     'observed_rate':sum(y for p,y in band)/len(band) if band else None,
                     'winner_accuracy':sum((p>=.5)==bool(y) for p,y in band)/len(band) if band else None})
    return {'wins':wins,'losses':n-wins,'sample_size':n,'accuracy':wins/n if n else None,
            'brier':sum((p-y)**2 for p,y in pairs)/len(pairs) if pairs else None,
            'log_loss':sum(-(y*math.log(p)+(1-y)*math.log1p(-p)) for p,y in pairs)/len(pairs) if pairs else None,
            'probability_sample':len(pairs),'calibration':bins}


def legacy_metrics(rows):
    # Include failed integrity records in outcome counts; flag them instead of
    # silently deleting their wins/losses from the displayed denominator.
    return {'overall':metrics(rows),'leagues':{l:metrics([r for r in rows if r['league']==l]) for l in ('NBA','NFL')},
            'first_date':min((r['pick_day'] for r in rows),default=None),
            'last_date':max((r['pick_day'] for r in rows),default=None),
            'policy':'original top-three Elo selections; no retroactive exclusions'}


def _fresh_at(value,earliest,latest):
    try:return earliest<=aware(value)<=latest
    except (TypeError,ValueError):return False


def decision(forecast,event,now,validation=None,min_edge=.03,min_ev=.02,max_odds_minutes=20):
    """Fail closed using independent model evidence, current news and prices.

    No-vig is a comparison benchmark; break-even at the actual wager price
    determines EV. A scenario envelope is NOT a statistical confidence bound.
    """
    result={'eligible':False,'reasons':[],'pricing':None,'expires_at':None};reasons=result['reasons']
    try:
        current,start=aware(now),aware(event['starts_at']);predicted=aware(forecast['predicted_at'])
        if not predicted<=current<start or current-predicted>timedelta(minutes=20):reasons.append('forecast_not_fresh_pregame')
        if forecast.get('id',event['id'])!=event['id']:reasons.append('forecast_game_mismatch')
        v=validation or {}
        if (v.get('betting_approved') is not True or v.get('artifact_hash')!=forecast.get('artifact_hash')
            or v.get('league')!=event['league'] or v.get('out_of_sample_games',0)<300
            or v.get('calibration_passed') is not True or v.get('positive_edge_validated') is not True
            or not v.get('evidence_hash') or not _fresh_at(v.get('evaluated_at'),aware('1970-01-01T00:00:00Z'),predicted)):reasons.append('validation_insufficient')
        p=forecast['home_probability']
        if type(p) not in (int,float) or not math.isfinite(p) or not 0<p<1:raise ValueError('probability')
        side='home' if p>=.5 else 'away';p=p if side=='home' else 1-p
        result.update({'side':side,'probability':p})
        news=forecast.get('availability') or {}
        if (news.get('verified') is not True or news.get('incomplete') is not False or news.get('game_id',event['id'])!=event['id']
            or not _fresh_at(news.get('observed_at'),current-timedelta(minutes=20),predicted)):reasons.append('injury_information_unverified')
        if event['league']=='NBA' and news.get('lineup_status')!='confirmed':reasons.append('starting_lineups_unconfirmed')
        if event['league']=='NFL' and news.get('starting_quarterbacks_confirmed') is not True:reasons.append('starting_quarterbacks_unconfirmed')
        if not forecast.get('availability_used'):reasons.append('availability_model_unvalidated')
        # A bound must come from a validated error procedure for this artifact,
        # not from simulation counts, component disagreement or scenario range.
        bound=forecast.get('probability_lower_bound')
        lower=(bound if side=='home' else 1-forecast.get('probability_upper_bound',1)) if bound is not None else None
        if (lower is None or type(lower) not in (int,float) or not math.isfinite(lower) or not 0<lower<=p
            or v.get('uncertainty_validated') is not True):
            reasons.append('validated_uncertainty_unavailable');lower=None
        quotes=[]
        for name,book in event.get('books',{}).items():
            # Other books remain research context; this user wagers at FanDuel.
            if name!='FanDuel':continue
            try:
                if any(book.get(k)!=value for k,value in {
                        'game_id':event['id'],'league':event['league'],'book':name,'market':'h2h',
                        'home_team':event['home'],'away_team':event['away']}.items()):
                    reasons.append('odds_identity_mismatch');continue
                source,fetched=aware(book['as_of']),aware(book['fetched_at'])
                if not current-timedelta(minutes=max_odds_minutes)<=source<=fetched<=predicted:continue
                if source>=start or not book.get('provider'):continue
                calc=moneyline_calculation(book[side],1,p,book['away' if side=='home' else 'home'])
                quotes.append((calc['estimated_ev'],name,book,calc))
            except (KeyError,ValueError,TypeError,OverflowError):continue
        if not quotes:reasons.append('odds_missing_stale_or_unverified')
        else:
            _,name,book,calc=max(quotes,key=lambda q:(q[0],q[1]))
            conservative_ev=lower*calc['decimal_odds']-1 if lower is not None else None
            conservative_edge=lower-calc['break_even'] if lower is not None else None
            result['pricing']={**calc,'book':name,'american_odds':book[side],'source_at':book['as_of'],
                               'observed_at':book['fetched_at'],'provider':book['provider'],'game_id':event['id'],
                               'market':'h2h','source_url':book.get('source_url'),'uncertainty_adjusted_edge':conservative_edge,
                               'uncertainty_adjusted_ev':conservative_ev}
            if news.get('observed_at'):
                result['expires_at']=min(start,predicted+timedelta(minutes=20),
                    aware(news['observed_at'])+timedelta(minutes=20),
                    aware(book['as_of'])+timedelta(minutes=max_odds_minutes)).isoformat()
            if lower is None or conservative_edge<min_edge or conservative_ev<min_ev:reasons.append('positive_edge_not_established')
        result['eligible']=not reasons
    except (KeyError,TypeError,ValueError,OverflowError):
        reasons.append('invalid_or_missing_input')
    return result


def archive_forecasts(root,forecasts,finals,now):
    """Append refreshed observations and immutable confirmed results separately."""
    folder=Path(root)/'observations/production_forecasts';folder.mkdir(parents=True,exist_ok=True)
    file=folder/'ledger.sqlite'
    with sqlite3.connect(file) as db:
        for table in ('forecasts','outcomes','outcome_confirmations'):
            db.execute(f'CREATE TABLE IF NOT EXISTS {table} (key TEXT PRIMARY KEY,payload TEXT NOT NULL)')
            for operation in ('UPDATE','DELETE'):
                db.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_no_{operation} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'immutable'); END")
        db.execute("CREATE INDEX IF NOT EXISTS forecasts_game_id ON forecasts(json_extract(payload,'$.id'))")
        for row in forecasts:
            if not aware(row['predicted_at'])<=aware(now)<aware(row['starts_at']):raise ValueError('not pregame')
            if not 0<row['home_probability']<1:raise ValueError('invalid probability')
            previous=db.execute("SELECT payload FROM forecasts WHERE json_extract(payload,'$.id')=? ORDER BY rowid DESC LIMIT 1",(row['id'],)).fetchone()
            prior=json.loads(previous[0]) if previous else None
            fingerprint=row.get('availability',{}).get('status_fingerprint')
            old=prior.get('availability',{}).get('status_fingerprint') if prior else None
            row['injury_changed_since_previous_forecast']=bool(fingerprint and old and fingerprint!=old)
            text=json.dumps(row,sort_keys=True,allow_nan=False)
            db.execute('INSERT OR IGNORE INTO forecasts VALUES (?,?)',(snapshot_hash(row),text))
        for row in finals:
            try:
                # Finals arrive only from the runner's explicit-final parser.
                # Validate identity and timing here too: no arbitrary score-only
                # payload can settle a forecast at this storage boundary.
                prefix,day,away,home=row['id'].split(':')
                if row['home']!=home or row['away']!=away or home==away:continue
                if row.get('league',prefix.upper())!=prefix.upper():continue
                if any(type(row[key]) is not int or row[key]<0 for key in ('home_score','away_score')):continue
                start=aware(row['starts_at']) if isinstance(row['starts_at'],str) else row['starts_at']
                if start.tzinfo is None or start>aware(now) or not row.get('source'):continue
                existing=[json.loads(v[0]) for v in db.execute("SELECT payload FROM forecasts WHERE json_extract(payload,'$.id')=?",(row['id'],))]
                matching=[f for f in existing if aware(f['predicted_at'])<aware(f['starts_at'])<=aware(now)]
                if not matching:continue
                payload={key:row[key] for key in ('id','home','away','home_score','away_score','source')}
                payload.update(starts_at=start.isoformat(),observed_at=now)
                text=json.dumps(payload,sort_keys=True,allow_nan=False)
                db.execute('INSERT OR IGNORE INTO outcomes VALUES (?,?)',(row['id'],text))
                # Preserve later confirmations, including contradictions, rather
                # than silently accepting whichever result arrived first.
                identity={k:v for k,v in payload.items() if k!='observed_at'}
                db.execute('INSERT OR IGNORE INTO outcome_confirmations VALUES (?,?)',(snapshot_hash(identity),text))
            except (KeyError,ValueError,TypeError,AttributeError):continue
        records=[json.loads(v[0]) for v in db.execute('SELECT payload FROM forecasts')]
        outcomes={v[0]:json.loads(v[1]) for v in db.execute('SELECT key,payload FROM outcomes')}
        confirmations=[json.loads(v[0]) for v in db.execute('SELECT payload FROM outcome_confirmations')]
    from .forecast_evaluation import evaluate
    return evaluate(records, list(outcomes.values())+confirmations, now)



def apply_pipeline(board,models,games,now,root=None,nba_predictions=None,blocked=(),finals=()):
    """Publish research forecasts on every scheduled game; picks only after gates."""
    current=aware(now);scheduled=[];artifacts={};stats={'NBA':{},'NFL':{}}
    model_dir=Path(__file__).resolve().parents[2]/'data/models'
    for league in ('NBA','NFL'):
        file=model_dir/(league.lower()+'.json')
        if file.exists():
            try:artifacts[league]=json.loads(file.read_text())
            except (OSError,ValueError):pass
    compact=model_dir/'team_metrics.json'
    if compact.exists():
        try:
            for league,values in json.loads(compact.read_text()).items():
                for day,team,vector in values:stats[league][(date.fromisoformat(day),team)]=vector
        except (KeyError,ValueError,TypeError):stats={'NBA':{},'NFL':{}}
    if root:
        from .forecast_data import assets
        from .nba_efficiency import parse_team_stats
        for text,stamp,sha in assets(root,'nba_team_game_boxscores',now):stats['NBA'].update(parse_team_stats(text))
    valid_games=[g for g in games if g['date']<current.astimezone(ET).date()]
    for game in board.get('games',[]):
        for key in ('predicted_winner','forecast','forecast_status','prediction_uncertain'):
            game.pop(key,None)
        try:
            if not current<aware(game['starts_at']):continue
            if game['league']=='NFL' and 'neutral' not in game:
                game['forecast_status']='venue_status_unverified';continue
            _,_,away,home=game['id'].split(':')
            start=aware(game['starts_at']).astimezone(ET).date();year=start.year if start.month>=8 else start.year-1
            scheduled.append({**game,'home':home,'away':away,'date':start,'upcoming':True,
                              'season':str(year)+'-'+str(year+1)[-2:] if game['league']=='NBA' else str(year)})
        except (KeyError,TypeError,ValueError):continue
    features={}
    for league in ('NBA','NFL'):
        if league in blocked:continue
        for row in examples(valid_games+scheduled,league,stats[league]):
            if 'home_win' not in row:features[row['game_id']]=row
    nba={r['game_id']:r for r in nba_predictions or []};forecasts=[];picks=[]
    from .simulator import as_of_histories
    histories=as_of_histories(valid_games,current.astimezone(ET).date())
    for event in scheduled:
        public=next(g for g in board['games'] if g['id']==event['id']);row=features.get(event['id'])
        public.pop('predicted_winner',None)
        if not row:
            public['forecast_status']='history_or_features_unavailable';continue
        artifact=artifacts.get(event['league']);fallback_reason='artifact_missing' if not artifact else None
        try:
            estimate=infer(artifact,row,now) if artifact else None
        except (KeyError,ValueError,TypeError,OverflowError) as exc:
            estimate=None;fallback_reason='artifact_inference_rejected:'+type(exc).__name__+':'+str(exc)
        candidate=estimate
        incumbent_model=models.get(event['league'])
        incumbent=project_home(incumbent_model,event['home'],event['away'],aware(event['starts_at']),event.get('neutral',False)) if incumbent_model is not None else None
        # No challenger has earned independent forward promotion. Publish its
        # output as research alongside the incumbent, never silently replace it.
        if estimate is None or estimate.get('degraded_reason') or artifact.get('validation',{}).get('prediction_approved') is not True:
            if candidate is not None:
                fallback_reason=candidate.get('degraded_reason') or 'challenger_not_approved'
            if incumbent is None:public['forecast_status']='model_unavailable';continue
            snapshot=feature_snapshot(event,models[event['league']])
            identity=snapshot_hash({'league':event['league'],'version':'pure-elo-v1','parameters':{key:models[event['league']].get(key) for key in ('k','home_advantage','rest_weight','form_weight')}})
            estimate={'incumbent_snapshot':snapshot,'incumbent_snapshot_hash':snapshot_hash(snapshot),
                      'model_identity_hash':identity,'home_probability':incumbent,'away_probability':1-incumbent,'components':{'elo':incumbent},
                      'model_version':event['league'].lower()+'-elo-research-v2','artifact_hash':identity,
                      'calibration_status':'uncalibrated','validation':{},'availability_used':False,
                      'fallback_reason':fallback_reason}
        if candidate is not None and candidate is not estimate:estimate['research_model']=candidate
        context=public.get('nba_availability_context') or public.get('nfl_provider_availability_context') or {}
        estimate.update({'id':event['id'],'league':event['league'],'starts_at':event['starts_at'],'predicted_at':now,
                         'feature_snapshot':row,'market_snapshot':event.get('books',{}),'availability':{**context,'verified':False,
                         'incomplete':context.get('incomplete',True),'observed_at':context.get('observed_at'),
                         'lineup_status':context.get('lineup_status','unknown'),
                         'starting_quarterbacks_confirmed':False,'game_id':event['id']},
                         'mode':'research','lineup_evidence':public.get('nba_lineup_evidence'),'quarterback_context':public.get('nfl_qb_availability'),
                         'baseline_elo_probability':incumbent,
                         'baseline_elo_kind':'production_incumbent',
                         'baseline_fixed_elo_probability':row['elo']})
        advanced=nba.get(event['id'],{})
        scenarios=next((advanced[field] for field in ('ensemble_scenarios','availability_scenarios','player_box_scenarios')
                        if advanced.get(field,{}).get('status')=='conditional_research_only'),None)
        if (scenarios and aware(advanced['predicted_at'])<=current
                and aware(scenarios['injury_observed_at'])<=aware(advanced['predicted_at'])<aware(event['starts_at'])):
            estimate['availability_scenarios']=scenarios
            # Preserve the trained team probability separately; a conditional
            # sensitivity envelope is never averaged into an invented forecast.
            estimate['availability_status']='conditional_scenarios_available'
        else:estimate['availability_status']='player_adjustment_unavailable'
        if 'simulation' not in public:
            seed=int(snapshot_hash(event['id'])[:8],16)
            simulation=histories[event['league']].simulate(event['home'],event['away'],event.get('neutral',False),10000,seed)
            if simulation:public['simulation']={**simulation,'used_in_prediction':False}
        estimate['decision']=decision(estimate,event,now,estimate.pop('validation',{}))
        forecasts.append(estimate);public['forecast']=estimate;public['forecast_status']='research_only' if not estimate['decision']['eligible'] else 'qualified'
        p=estimate['home_probability'];public['predicted_winner']=public['home'] if p>=.5 else public['away'];public['prediction_uncertain']=.45<p<.55
        if estimate['decision']['eligible']:
            side=estimate['decision']['side'];picks.append({'id':event['id'],'league':event['league'],'team':public[side],
                'opponent':public['away' if side=='home' else 'home'],'starts_at':event['starts_at'],'predicted_at':now,
                'pick_day':current.astimezone(ET).date().isoformat(),'model':estimate['model_version'],'current':True,
                'outcome':'pending','probability':estimate['decision']['probability'],'books':[
                    {'name':name,'odds':b[side],'as_of':b['as_of']} for name,b in event.get('books',{}).items()],
                'recommendation_eligible':True,'pricing':estimate['decision']['pricing'],
                'expires_at':estimate['decision']['expires_at']})
    board['research_forecasts']=forecasts;board['picks']=picks
    from collections import Counter
    board['inference_diagnostics']={'active_models':dict(Counter(f['model_version'] for f in forecasts)),
        'fallback_reasons':dict(Counter(f['fallback_reason'] for f in forecasts if f.get('fallback_reason'))),
        'withheld_reasons':dict(Counter(g['forecast_status'] for g in board.get('games',[]) if g.get('forecast_status') not in (None,'qualified','research_only'))),
        'challenger_forecasts':sum('research_model' in f for f in forecasts),
        'eligibility_reasons':dict(Counter(reason for f in forecasts for reason in f['decision']['reasons'])),
        'availability_coverage':{league:{'forecasts':sum(f['league']==league for f in forecasts),
            'with_source':sum(f['league']==league and bool(f['availability'].get('source')) for f in forecasts),
            'complete':sum(f['league']==league and f['availability'].get('incomplete') is False for f in forecasts)}
            for league in ('NBA','NFL')},
        'lineup_collection':dict(Counter((f.get('lineup_evidence') or {}).get('reason','evidence_unavailable')
            for f in forecasts if f['league']=='NBA')),
        'quarterback_report_matching':dict(Counter(team.get('availability_reason','unknown')
            for f in forecasts if f['league']=='NFL'
            for team in (f.get('quarterback_context') or {}).get('teams',{}).values())),
        'baseline_policy':'actual production incumbent frozen at prediction time; fixed Elo is separate'}
    board['model_evaluation']={league:{'artifact_hash':a['artifact_hash'],'calibration_status':a['calibration_status'],
        'evaluation_season':a['evaluation_season'],'validation':a['validation']} for league,a in artifacts.items()}
    board['selection_policy']={'version':'validated-value-v2','minimum_edge':.03,'minimum_ev':.02,
        'recommendations':len(picks),'research_forecasts':len(forecasts),'automatic_top_three':False,
        'status':'no_qualified_bets' if not picks else 'qualified','odds_max_age_minutes':20,
        'injury_max_age_minutes':20,'recommendation_book':'FanDuel','refresh_latency':'scheduled snapshots; not real-time'}
    from .readiness import summarize
    board['recommendation_readiness']=summarize(board.get('games',[]),now)
    board['model']='League-specific chronological research forecasts; validated value gate'
    if root:
        board['forecast_evaluation']=archive_forecasts(root,forecasts,finals,now)
    return board
