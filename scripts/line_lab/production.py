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


def decision(forecast,event,now,validation=None,min_edge=.03,min_ev=.02,max_odds_minutes=20):
    """Fail closed using independent model evidence, current news and prices.

    No-vig is a comparison benchmark; break-even at the actual wager price
    determines EV. A scenario envelope is NOT a statistical confidence bound.
    """
    result={'eligible':False,'reasons':[],'pricing':None};reasons=result['reasons']
    try:
        current,start=aware(now),aware(event['starts_at']);predicted=aware(forecast['predicted_at'])
        if not predicted<=current<start or current-predicted>timedelta(minutes=20):reasons.append('forecast_not_fresh_pregame')
        v=validation or {}
        if (v.get('betting_approved') is not True or v.get('artifact_hash')!=forecast.get('artifact_hash')
            or v.get('league')!=event['league'] or v.get('out_of_sample_games',0)<300
            or v.get('calibration_passed') is not True or v.get('positive_edge_validated') is not True
            or not v.get('evidence_hash') or aware(v['evaluated_at'])>predicted):reasons.append('validation_insufficient')
        p=forecast['home_probability'];side='home' if p>=.5 else 'away';p=p if side=='home' else 1-p
        if type(p) not in (int,float) or not math.isfinite(p) or not 0<p<1:raise ValueError('probability')
        result.update({'side':side,'probability':p})
        news=forecast.get('availability') or {}
        if (news.get('verified') is not True or news.get('incomplete') is not False
            or not current-timedelta(minutes=20)<=aware(news['observed_at'])<=predicted):reasons.append('injury_information_unverified')
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
            try:
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
                               'observed_at':book['fetched_at'],'uncertainty_adjusted_edge':conservative_edge,
                               'uncertainty_adjusted_ev':conservative_ev}
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
        for table in ('forecasts','outcomes'):
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
            if row.get('home_score') is None or row.get('away_score') is None:continue
            # Caller supplies only parser-qualified confirmed finals. The
            # earliest frozen forecast start must already be in the past.
            existing=[json.loads(v[0]) for v in db.execute("SELECT payload FROM forecasts WHERE json_extract(payload,'$.id')=?",(row['id'],))]
            matching=[f for f in existing if f['id']==row['id'] and aware(f['starts_at'])<=aware(now)]
            if not matching:continue
            db.execute('INSERT OR IGNORE INTO outcomes VALUES (?,?)',(row['id'],json.dumps({**row,'observed_at':now},sort_keys=True)))
        records=[json.loads(v[0]) for v in db.execute('SELECT payload FROM forecasts')]
        outcomes={v[0]:json.loads(v[1]) for v in db.execute('SELECT key,payload FROM outcomes')}
    first={}
    for r in sorted(records,key=lambda r:r['predicted_at']):
        identity=r.get('model_identity_hash',r['artifact_hash'])
        first.setdefault((r['id'],identity),r)
        candidate=r.get('research_model')
        if candidate:
            key=candidate.get('model_identity_hash',candidate['artifact_hash'])
            first.setdefault((r['id'],key),{**r,**candidate})
    groups={}
    for r in first.values():
        result=outcomes.get(r['id']);y=None
        if result and result['home_score']!=result['away_score']:y=int(result['home_score']>result['away_score'])
        # Score home probabilities against home outcomes (not selected winners).
        groups.setdefault(r['model_version']+':'+r.get('model_identity_hash',r['artifact_hash'])[:12],[]).append(
            {'probability':r['home_probability'],'baseline_probability':r.get('baseline_elo_probability'),
             'outcome':'pending' if y is None else 'win' if y else 'loss'})
    return {'policy':'first pregame forecast per game/artifact; refreshed snapshots never overwrite it',
            'mode':'forward_paper_forecasts','models':{k:{**metrics(v),'matched_elo':metrics([{**r,'probability':r['baseline_probability']} for r in v if r['baseline_probability'] is not None])} for k,v in groups.items()},
            'paper_roi':None,'closing_line_value':None,'maximum_drawdown':None,
            'wager_metrics_reason':'no qualified frozen priced recommendations yet','snapshots':len(records)}


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
        try:
            artifact=artifacts.get(event['league']);estimate=infer(artifact,row,now) if artifact else None
        except (KeyError,ValueError,TypeError,OverflowError):estimate=None
        candidate=estimate
        # No challenger has earned independent forward promotion. Publish its
        # output as research alongside the incumbent, never silently replace it.
        if estimate is None or artifact.get('validation',{}).get('prediction_approved') is not True:
            incumbent=project_home(models[event['league']],event['home'],event['away'],aware(event['starts_at']),event.get('neutral',False))
            if incumbent is None:public['forecast_status']='model_unavailable';continue
            snapshot=feature_snapshot(event,models[event['league']])
            identity=snapshot_hash({'league':event['league'],'version':'pure-elo-v1','parameters':{key:models[event['league']].get(key) for key in ('k','home_advantage','rest_weight','form_weight')}})
            estimate={'incumbent_snapshot':snapshot,'incumbent_snapshot_hash':snapshot_hash(snapshot),
                      'model_identity_hash':identity,'home_probability':incumbent,'away_probability':1-incumbent,'components':{'elo':incumbent},
                      'model_version':event['league'].lower()+'-elo-research-v2','artifact_hash':identity,
                      'calibration_status':'uncalibrated','validation':{},'availability_used':False}
        if candidate is not None:estimate['research_model']=candidate
        context=public.get('nba_availability_context') or public.get('nfl_provider_availability_context') or {}
        estimate.update({'id':event['id'],'league':event['league'],'starts_at':event['starts_at'],'predicted_at':now,
                         'feature_snapshot':row,'availability':{'verified':False,'incomplete':context.get('incomplete',True),
                                                               'observed_at':context.get('observed_at'),'source':context.get('source'),
            'status_fingerprint':context.get('status_fingerprint')},
                         'mode':'research','baseline_elo_probability':row['elo']})
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
                'recommendation_eligible':True,'pricing':estimate['decision']['pricing']})
    board['research_forecasts']=forecasts;board['picks']=picks
    board['model_evaluation']={league:{'artifact_hash':a['artifact_hash'],'calibration_status':a['calibration_status'],
        'evaluation_season':a['evaluation_season'],'validation':a['validation']} for league,a in artifacts.items()}
    board['selection_policy']={'version':'validated-value-v2','minimum_edge':.03,'minimum_ev':.02,
        'recommendations':len(picks),'research_forecasts':len(forecasts),'automatic_top_three':False,
        'status':'no_qualified_bets' if not picks else 'qualified','odds_max_age_minutes':20,
        'injury_max_age_minutes':20,'refresh_latency':'scheduled snapshots; not real-time'}
    board['model']='League-specific chronological research forecasts; validated value gate'
    if root:
        board['forecast_evaluation']=archive_forecasts(root,forecasts,finals,now)
    return board
