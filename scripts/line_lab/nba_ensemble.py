"""Chronologically fitted convex probability ensemble; no promotion side effects."""
import hashlib
import json
import math
from datetime import date,timedelta
from .history import aware
from .simulator import score_metrics

COMPONENTS=('elo','team','rotation','multi_stat')


def mix(weights,probabilities):
    if set(weights)!=set(COMPONENTS) or any(type(w) not in (int,float) or not math.isfinite(w) or w<0 for w in weights.values()):raise ValueError('invalid ensemble weights')
    if not math.isclose(sum(weights.values()),1.,abs_tol=1e-12):raise ValueError('ensemble weights do not sum to one')
    value=0.
    for name,weight in weights.items():
        if not weight:continue
        p=probabilities[name]
        if type(p) not in (int,float) or not math.isfinite(p) or not 0<p<1:raise ValueError('invalid component probability')
        value+=weight*p
    return value


def fit_weights(rows,min_games=500,min_days=30):
    if len(rows)<min_games or len({r['date'] for r in rows})<min_days:return None
    loss=lambda p,y:-(y*math.log(p)+(1-y)*math.log1p(-p))
    candidates=[]
    for a in range(11):
        for b in range(11-a):
            for c in range(11-a-b):
                values=(a,b,c,10-a-b-c);weights=dict(zip(COMPONENTS,(v/10 for v in values)))
                score=sum(loss(mix(weights,r['probabilities']),r['home_win']) for r in rows)/len(rows)
                candidates.append((score,sum(v>0 for v in values),tuple(-v for v in values),weights))
    best=min(candidates,key=lambda x:x[:3])
    return {'weights':best[3],'training_log_loss':best[0],'training_games':len(rows),
            'training_days':len({r['date'] for r in rows}),'training_seasons':sorted({r['season'] for r in rows}),
            'input_hash':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
            'model_version':'nba-convex-ensemble-v1','grid_step':.1,'promoted':False}


def walk_forward(records,min_games=500,min_days=30):
    unique={r['game_id']:r for r in records}
    if len(unique)!=len(records):raise ValueError('duplicate component prediction')
    for r in records:
        date.fromisoformat(r['date'])
        if r['home_win'] not in (0,1) or set(r['probabilities'])!=set(COMPONENTS):raise ValueError('invalid component row')
        for name in COMPONENTS:mix(dict.fromkeys(COMPONENTS,0)|{name:1},r['probabilities'])
    results=[]
    for season in sorted({r['season'] for r in records}):
        test=sorted((r for r in records if r['season']==season),key=lambda r:(r['date'],r['game_id']))
        boundary=min(r['date'] for r in test)
        training=sorted((r for r in records if r['season']<season and r['date']<boundary),key=lambda r:(r['date'],r['game_id']))
        model=fit_weights(training,min_games,min_days)
        if model is None:continue
        metric=lambda name:score_metrics([{'probability':r['probabilities'][name],'outcome':r['home_win']} for r in test])
        selected=min(COMPONENTS,key=lambda name:score_metrics([{'probability':r['probabilities'][name],'outcome':r['home_win']} for r in training])['log_loss'])
        predictions=[{**r,'probability':mix(model['weights'],r['probabilities'])} for r in test]
        results.append({'season':season,'model':model,'selected_component_from_training':selected,
                        'components':{name:metric(name) for name in COMPONENTS},
                        'ensemble':score_metrics([{'probability':r['probability'],'outcome':r['home_win']} for r in predictions]),
                        'predictions':predictions})
    return results


def conditional_ensemble(model,base,elo,rotation,multi_stat,event,now):
    try:
        if model.get('model_version')!='nba-convex-ensemble-v1' or model.get('promoted') is not False or aware(model['exported_at'])>aware(now):raise ValueError('ensemble artifact unavailable')
        contexts={'rotation':rotation or {},'multi_stat':multi_stat or {}};required=[]
        for name,context in contexts.items():
            if not model['weights'][name]:continue
            if context.get('status')!='conditional_research_only' or not context.get('exhaustive_listed_uncertainty'):raise ValueError('component unavailable')
            stamp=aware(context['injury_observed_at'])
            if not stamp<=aware(now)<=stamp+timedelta(minutes=95):raise ValueError('stale or future component')
            if context.get('model_version')!=('nba-rotation-logistic-v1' if name=='rotation' else 'nba-player-box-logistic-v1'):raise ValueError('wrong component version')
            scenarios=context['scenarios']
            if not 1<=len(scenarios)<=64 or len(scenarios)!=2**context['uncertain_players']:raise ValueError('incomplete scenarios')
            if any(not math.isclose(s['home_probability']+s['away_probability'],1,abs_tol=1e-12) for s in scenarios):raise ValueError('invalid two-sided scenario')
            required.append(context)
        reference=required[0] if required else None
        if required:
            keys=[s['scenario'] for s in reference['scenarios']]
            if any([s['scenario'] for s in c['scenarios']]!=keys or c['injury_observed_at']!=reference['injury_observed_at'] for c in required):raise ValueError('unaligned scenarios')
        else:keys=['team_only']
        scenarios=[]
        for i,key in enumerate(keys):
            probabilities={'team':base,'elo':elo}
            for name,context in contexts.items():
                if model['weights'][name]:probabilities[name]=context['scenarios'][i]['home_probability']
            p=mix(model['weights'],probabilities)
            scenarios.append({'scenario':key,'home_probability':p,'away_probability':1-p,'features':probabilities})
        low=min(s['home_probability'] for s in scenarios);high=max(s['home_probability'] for s in scenarios)
        return {'status':'conditional_research_only' if required else 'team_only_ensemble',
                'scenarios':scenarios,'scenario_count':len(scenarios),'weights':model['weights'],
                'model_version':model['model_version'],'model_hash':hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest(),
                'component_model_hashes':{k:v.get('model_hash') for k,v in contexts.items() if model['weights'][k]},
                'exhaustive_listed_uncertainty':bool(required),'uncertain_players':reference['uncertain_players'] if reference else 0,
                'injury_observed_at':reference['injury_observed_at'] if reference else None,
                'injury_components_used':bool(required),'home_scenario_range':[low,high],
                'consistent_winner':event['home'] if low>.5 else event['away'] if high<.5 else None,
                'limitations':'correlated components; no scenario weights, joint calibration, causal injury effects or promotion established'}
    except (KeyError,TypeError,ValueError,IndexError,OverflowError):return {'status':'ensemble_component_unavailable','scenarios':[]}
