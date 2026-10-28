"""Prior-only, odds-independent elastic-net challenger and immutable registry."""
import hashlib
import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path
from .history import aware

FEATURES=('rating_difference','home_advantage','games_played_difference')
FORBIDDEN=('odds','price','market','spread','total','vig','implied','sharp','book')
REGISTRY='''
CREATE TABLE IF NOT EXISTS trials (
 trial_id TEXT PRIMARY KEY, league TEXT NOT NULL, completed_at TEXT NOT NULL,
 status TEXT NOT NULL, input_hash TEXT NOT NULL, artifact_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trial_no_update BEFORE UPDATE ON trials BEGIN SELECT RAISE(ABORT,'trials are append-only'); END;
CREATE TRIGGER IF NOT EXISTS trial_no_delete BEFORE DELETE ON trials BEGIN SELECT RAISE(ABORT,'trials are append-only'); END;
'''
FORECASTS='''
CREATE TABLE IF NOT EXISTS challenger_forecasts (
 forecast_key TEXT PRIMARY KEY, game_id TEXT NOT NULL, league TEXT NOT NULL,
 model_id TEXT NOT NULL, captured_at TEXT NOT NULL, starts_at TEXT NOT NULL,
 probability REAL NOT NULL, feature_json TEXT NOT NULL, status TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS challenger_no_update BEFORE UPDATE ON challenger_forecasts BEGIN SELECT RAISE(ABORT,'challenger forecasts are append-only'); END;
CREATE TRIGGER IF NOT EXISTS challenger_no_delete BEFORE DELETE ON challenger_forecasts BEGIN SELECT RAISE(ABORT,'challenger forecasts are append-only'); END;
'''


def _sigmoid(x):
    x=max(-35,min(35,x));return 1/(1+math.exp(-x))


def eligible_rows(rows,league,cutoff,features=FEATURES):
    """Only pregame, source-observed features and earlier known final outcomes."""
    if not features or any(any(word in feature.lower() for word in FORBIDDEN) for feature in features):
        raise ValueError('pure-model features must not contain market information')
    end=aware(cutoff);valid=[]
    for row in rows:
        try:
            observed,forecast,start,final=(aware(row[k]) for k in ('feature_observed_at','forecast_at','starts_at','final_observed_at'))
            if row.get('league')!=league or row.get('rights_verified') is not True:continue
            if not observed<=forecast<start<=final<end or row['home_win'] not in (0,1):continue
            data=row['features'];x=[float(data[name]) for name in features]
            if not row.get('game_id') or any(not math.isfinite(v) for v in x):continue
            valid.append({**row,'vector':x})
        except (KeyError,TypeError,ValueError):continue
    valid.sort(key=lambda r:(aware(r['forecast_at']),r['game_id']));first={}
    for row in valid:first.setdefault(row['game_id'],row)
    return list(first.values())


def _fit(rows,l1,l2,epochs=300,step=.08):
    n=len(rows);width=len(rows[0]['vector'])
    means=[sum(r['vector'][j] for r in rows)/n for j in range(width)]
    scales=[math.sqrt(sum((r['vector'][j]-means[j])**2 for r in rows)/n) or 1.0 for j in range(width)]
    matrix=[[(r['vector'][j]-means[j])/scales[j] for j in range(width)] for r in rows]
    weights=[0.0]*width;intercept=0.0
    for _ in range(epochs):
        gradients=[0.0]*width;bias=0.0
        for x,row in zip(matrix,rows):
            err=_sigmoid(intercept+sum(a*b for a,b in zip(weights,x)))-row['home_win'];bias+=err
            for j in range(width):gradients[j]+=err*x[j]
        intercept-=step*bias/n
        for j in range(width):
            value=weights[j]-step*(gradients[j]/n+l2*weights[j])
            weights[j]=math.copysign(max(0,abs(value)-step*l1),value)
    return {'means':means,'scales':scales,'weights':weights,'intercept':intercept,'l1':l1,'l2':l2}


def _predict_vector(model,vector):
    return _sigmoid(model['intercept']+sum(w*(x-m)/s for w,x,m,s in zip(model['weights'],vector,model['means'],model['scales'])))


def fit_elastic_net_shadow(rows,league,cutoff,features=FEATURES,min_training=500,min_validation=100,min_seasons=3):
    """Choose regularization on a strictly later prior season, then refit for future games."""
    eligible=eligible_rows(rows,league,cutoff,features)
    seasons=sorted({str(row.get('season','')) for row in eligible if row.get('season')})
    if len(seasons)<min_seasons:return None
    validation_season=seasons[-1];validation=[r for r in eligible if str(r.get('season'))==validation_season]
    if len(validation)<min_validation:return None
    validation_start=min(aware(r['forecast_at']) for r in validation)
    training=[r for r in eligible if str(r.get('season'))!=validation_season and aware(r['final_observed_at'])<validation_start]
    if len(training)<min_training:return None
    scores=[]
    for l1,l2 in ((0.0,.01),(.001,.01),(.01,.1)):
        fit=_fit(training,l1,l2)
        predictions=[_predict_vector(fit,r['vector']) for r in validation]
        loss=sum(-(r['home_win']*math.log(p)+(1-r['home_win'])*math.log(1-p)) for r,p in zip(validation,predictions))/len(validation)
        brier=sum((p-r['home_win'])**2 for r,p in zip(validation,predictions))/len(validation)
        scores.append({'l1':l1,'l2':l2,'validation_log_loss':loss,'validation_brier':brier})
    chosen=min(scores,key=lambda item:item['validation_log_loss'])
    final=_fit(eligible,chosen['l1'],chosen['l2'])
    reference=[r for r in validation if isinstance(r.get('baseline_probability'),(int,float)) and 0<r['baseline_probability']<1]
    baseline_loss=sum(-(r['home_win']*math.log(r['baseline_probability'])+(1-r['home_win'])*math.log(1-r['baseline_probability'])) for r in reference)/len(reference) if reference else None
    baseline_brier=sum((r['baseline_probability']-r['home_win'])**2 for r in reference)/len(reference) if reference else None
    selected_fit=_fit(training,chosen['l1'],chosen['l2'])
    paired=[(_predict_vector(selected_fit,r['vector']),r['home_win']) for r in reference]
    paired_loss=sum(-(y*math.log(p)+(1-y)*math.log(1-p)) for p,y in paired)/len(paired) if paired else None
    paired_brier=sum((p-y)**2 for p,y in paired)/len(paired) if paired else None
    digest=hashlib.sha256(json.dumps([(r['game_id'],r['forecast_at'],r['final_observed_at'],r['vector'],r['home_win']) for r in eligible],separators=(',',':')).encode()).hexdigest()
    return {**final,'model_version':'pure-elasticnet-v1','league':league,'features':list(features),
            'trained_before':aware(cutoff).isoformat(),'training_hash':digest,'training_games':len(eligible),
            'inner_training_games':len(training),'validation_games':len(validation),'validation_season':validation_season,
            'validation_scores':scores,'baseline_comparison_games':len(reference),
            'validation_baseline_log_loss':baseline_loss,'validation_baseline_brier':baseline_brier,
            'validation_paired_candidate_log_loss':paired_loss,'validation_paired_candidate_brier':paired_brier,
            'status':'shadow_unvalidated','promoted':False}


def predict_elastic_shadow(model,features,prediction_at,feature_observed_at):
    try:
        if not model or model.get('promoted') is not False or aware(model['trained_before'])>=aware(prediction_at):return None
        if aware(feature_observed_at)>aware(prediction_at):return None
        names=model['features']
        if any(any(word in name.lower() for word in FORBIDDEN) for name in names):return None
        vector=[float(features[name]) for name in names]
        if any(not math.isfinite(x) for x in vector) or len(vector)!=len(model['weights']):return None
        return _predict_vector(model,vector)
    except (KeyError,TypeError,ValueError,ZeroDivisionError):return None


def append_trial(root,league,rows,completed_at,artifact=None,error=None,family='pure-elasticnet-v1'):
    now=aware(completed_at);path=Path(root)/'observations'/'model_registry.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
    status='failed' if error else 'candidate' if artifact else 'insufficient_data'
    payload=artifact or {'model_version':family,'reason':error or 'not enough verified, settled prior seasons','promoted':False}
    key=hashlib.sha256((league+'|'+family+'|'+now.isoformat()+'|'+digest).encode()).hexdigest()
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript(REGISTRY)
        db.execute('INSERT OR IGNORE INTO trials VALUES (?,?,?,?,?,?)',(key,league,now.isoformat(),status,digest,json.dumps(payload,sort_keys=True)))
    return key


def latest_candidates(root,league,as_of):
    path=Path(root)/'observations'/'model_registry.sqlite';now=aware(as_of)
    if not path.exists():return []
    with closing(sqlite3.connect(path)) as db:
        rows=db.execute('SELECT trial_id,completed_at,artifact_json FROM trials WHERE league=? AND status=? ORDER BY completed_at DESC',(league,'candidate')).fetchall()
    result=[];seen=set()
    for key,completed,payload in rows:
        try:
            model=json.loads(payload)
            version=model.get('model_version')
            if version not in ('pure-elasticnet-v1','pure-stumpboost-v1') or version in seen:continue
            if aware(completed)<=now and aware(model['trained_before'])<now and model.get('promoted') is False:
                result.append((key,model));seen.add(version)
        except (KeyError,TypeError,ValueError):continue
    return result


def latest_candidate(root,league,as_of):
    """Backward-compatible single-candidate view."""
    candidates=latest_candidates(root,league,as_of)
    return candidates[0] if candidates else None


def predict_candidate(model,features,prediction_at,feature_observed_at):
    if model.get('model_version')=='pure-elasticnet-v1':
        return predict_elastic_shadow(model,features,prediction_at,feature_observed_at)
    if model.get('model_version')=='pure-stumpboost-v1':
        from .boosted_shadow import predict_boosted_shadow
        return predict_boosted_shadow(model,features,prediction_at,feature_observed_at)
    return None


def model_features(model,event):
    home,away=event['home'],event['away'];counts=model.get('games_played',{})
    if home not in model['ratings'] or away not in model['ratings'] or home not in counts or away not in counts:return None
    return {'rating_difference':model['ratings'][home]-model['ratings'][away],
            'home_advantage':0 if event.get('neutral',False) else model['home_advantage'],
            'games_played_difference':counts[home]-counts[away]}


def record_challenger_forecasts(root,markets,models,now):
    """Log candidate forecasts before games; do not influence pick selection."""
    observed=aware(now);path=Path(root)/'observations'/'challenger_forecasts'/(observed.date().isoformat()+'.sqlite');added=0
    candidates={league:latest_candidates(root,league,now) for league in ('NBA','NFL')}
    if not any(candidates.values()):return 0
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path)) as db,db:
        db.executescript(FORECASTS)
        for event in markets.values():
            group=candidates.get(event['league'])
            if not group or aware(event['starts_at'])<=observed:continue
            inputs=model_features(models[event['league']],event)
            if not inputs:continue
            content=json.dumps(inputs,sort_keys=True,separators=(',',':'))
            for key,model in group:
                p=predict_candidate(model,inputs,now,now)
                if p is None:continue
                identity=hashlib.sha256((event['id']+'|'+key+'|'+observed.isoformat()+'|'+content).encode()).hexdigest()
                added+=db.execute('INSERT OR IGNORE INTO challenger_forecasts VALUES (?,?,?,?,?,?,?,?,?)',
                    (identity,event['id'],event['league'],key,observed.isoformat(),aware(event['starts_at']).isoformat(),p,content,'shadow_unvalidated')).rowcount
    return added
