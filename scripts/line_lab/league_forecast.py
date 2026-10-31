"""Past-only league features and portable, versioned probability inference.

Training is offline. Missing player/news data never becomes a numerical zero
injury adjustment; availability-sensitive forecasts remain explicit scenarios.
"""
import math
from collections import defaultdict, deque
from datetime import date
from .model import elo_probability
from .constants import ET
from .history import aware
from .ledger_v2 import snapshot_hash

BASE_FEATURES = ['elo_logit','home_court','margin','opponent_adjusted_margin',
                 'offense','defense','rest','back_to_back','games_played']
NBA_FEATURES = ['off_rating','def_rating','effective_fg','pace','turnovers','rebounds','free_throws','three_point']
NFL_FEATURES = ['off_epa','def_epa','off_success','def_success','pass_epa','rush_epa']


def examples(games, league, stats=None):
    """Freeze every day's features before consuming any results on that day.

    stats maps (game date, team) to that completed game's metrics. Publication
    timestamps for old revised archives are unavailable: retrospective only.
    """
    stats = stats or {}
    unique = {}
    for g in games:
        if g['league'] != league: continue
        if g['id'] in unique:
            if unique[g['id']] != g: raise ValueError('conflicting duplicate game')
            continue
        unique[g['id']] = g
    byday = defaultdict(list)
    for g in unique.values(): byday[g['date']].append(g)
    ratings = {}; last = {}; counts = defaultdict(int)
    history = defaultdict(lambda: deque(maxlen=20 if league == 'NBA' else 12))
    metric_history = defaultdict(lambda: deque(maxlen=20 if league == 'NBA' else 12))
    metric_last = {}
    season = None; out = []; k,hfa = (20,55) if league == 'NBA' else (24,42)
    nmetrics = len(NBA_FEATURES if league == 'NBA' else NFL_FEATURES)
    for day, slate in sorted(byday.items()):
        seasons = {str(g['season']) for g in slate}
        if len(seasons) != 1: raise ValueError('conflicting seasons on date')
        new_season = next(iter(seasons))
        if new_season != season:
            if season is not None: ratings = {t:1500+.75*(r-1500) for t,r in ratings.items()}
            season = new_season
        for g in sorted(slate,key=lambda x:x['id']):
            h,a = g['home'],g['away']; hr,ar = ratings.get(h,1500),ratings.get(a,1500)
            neutral = g.get('neutral',False); p = elo_probability(hr-ar+(0 if neutral else hfa))
            minimum = 10 if league == 'NBA' else 4
            if min(len(history[h]),len(history[a])) < minimum: continue
            avg = lambda team,i: sum(v[i] for v in history[team])/len(history[team])
            rest = lambda team: min(14,max(0,(day-last[team]).days-1)) if team in last else 3
            scale = 20 if league == 'NBA' else 14
            vector = [math.log(p/(1-p)),float(not neutral),
                      (avg(h,0)-avg(a,0))/scale,(avg(h,1)-avg(a,1))/scale,
                      (avg(h,2)-avg(a,2))/scale,(avg(h,3)-avg(a,3))/scale,
                      (rest(h)-rest(a))/7,float(rest(h)==0)-float(rest(a)==0),
                      (min(counts[h],82)-min(counts[a],82))/82]
            covered = (min(len(metric_history[h]),len(metric_history[a])) >= minimum
                       and metric_last.get(h)==last[h] and metric_last.get(a)==last[a])
            extra = None
            if covered:
                means = lambda team:[sum(v[i] for v in metric_history[team])/len(metric_history[team]) for i in range(nmetrics)]
                extra = [x-y for x,y in zip(means(h),means(a))]
            row = {'game_id':g['id'],'date':day.isoformat(),'season':season,'league':league,
                   'home':h,'away':a,'vector':vector,'extended_vector':vector+extra if extra is not None else None,
                   'elo':p,'feature_cutoff':max(last[h],last[a]).isoformat()}
            if not g.get('upcoming') and g['home_score'] != g['away_score']:
                row['home_win'] = int(g['home_score']>g['away_score'])
            elif not g.get('upcoming'): continue  # NFL ties excluded, explicitly reported by trainer
            out.append(row)
        for g in sorted(slate,key=lambda x:x['id']):
            if g.get('upcoming'): continue
            h,a = g['home'],g['away']; hr,ar = ratings.get(h,1500),ratings.get(a,1500)
            margin = g['home_score']-g['away_score']; y = 1 if margin>0 else 0 if margin<0 else .5
            p = elo_probability(hr-ar+(0 if g.get('neutral') else hfa))
            # Convert opponent rating to an approximate score scale; this is a
            # candidate feature, never a claim of measured causal adjustment.
            scale = 20 if league == 'NBA' else 14
            history[h].append((margin,margin+(ar-1500)*scale/400,g['home_score'],g['away_score']))
            history[a].append((-margin,-margin+(hr-1500)*scale/400,g['away_score'],g['home_score']))
            ratings[h]=hr+k*(y-p);ratings[a]=ar-k*(y-p)
            last[h]=last[a]=day;counts[h]+=1;counts[a]+=1
            for t in (h,a):
                values=stats.get((day,t))
                if values is not None and len(values)==nmetrics and all(math.isfinite(x) for x in values):
                    metric_history[t].append(values);metric_last[t]=day
    return out


def logistic(model, vector):
    if len(vector)!=len(model['weights']) or len(vector)!=len(model['mean']) or len(vector)!=len(model['scale']):
        raise ValueError('feature dimensions')
    values=list(vector)+model['weights']+model['mean']+model['scale']+[model['intercept']]
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in values) or any(s<=0 for s in model['scale']):
        raise ValueError('nonfinite artifact')
    z=model['intercept']+sum(w*(v-m)/s for w,v,m,s in zip(model['weights'],vector,model['mean'],model['scale']))
    return 1/(1+math.exp(-max(-35,min(35,z))))


def infer(artifact,row,now):
    if artifact['league']!=row['league'] or aware(artifact['exported_at'])>aware(now): raise ValueError('wrong/future artifact')
    if not artifact['training_cutoff'] < row['date']: raise ValueError('training leakage')
    if not row['feature_cutoff'] < row['date']: raise ValueError('feature leakage')
    if snapshot_hash({k:v for k,v in artifact.items() if k!='artifact_hash'})!=artifact['artifact_hash']:
        raise ValueError('artifact hash mismatch')
    weights=artifact['weights']
    if (not weights or any(type(w) not in (int,float) or not math.isfinite(w) or w<0 for w in weights.values())
        or not math.isclose(sum(weights.values()),1.,abs_tol=1e-10)):
        raise ValueError('invalid ensemble weights')
    if artifact.get('source_observed_at') and aware(artifact['source_observed_at'])>aware(now):raise ValueError('future source')
    components={'elo':row['elo']};missing_metrics=False
    for name,model in artifact['components'].items():
        if not artifact['weights'].get(name):continue
        vector=row['extended_vector'] if model['extended'] else row['vector']
        if vector is None:
            missing_metrics=True;continue
        components[name]=logistic(model,vector)
    p=row['elo'] if missing_metrics else sum(weight*components[name] for name,weight in artifact['weights'].items() if weight)
    c=artifact['calibration']
    if any(type(c[k]) not in (int,float) or not math.isfinite(c[k]) for k in ('intercept','weight')) or c['weight']<=0:raise ValueError('invalid calibration')
    z=c['intercept']+c['weight']*math.log(max(1e-9,p)/max(1e-9,1-p))
    p=p if missing_metrics else 1/(1+math.exp(-max(-35,min(35,z))))
    return {'home_probability':p,'away_probability':1-p,'components':components,
            'model_version':artifact['model_version'],'artifact_hash':artifact['artifact_hash'],
            'model_identity_hash':artifact.get('model_identity_hash',artifact['artifact_hash']),
            'feature_hash':snapshot_hash(row),'calibration_status':'uncalibrated_missing_metrics_fallback' if missing_metrics else artifact['calibration_status'],
            'degraded_reason':'required_efficiency_metrics_missing' if missing_metrics else None,
            'validation':artifact['validation'],'availability_used':False}
