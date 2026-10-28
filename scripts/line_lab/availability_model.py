"""Learn injury-status adjustments prospectively, in shadow mode only."""
import hashlib
import json
import math
from .history import aware
from .model_stack import _sigmoid

FEATURES=('out_difference','doubtful_difference','questionable_difference')
GRID=(.01,.1,1.0)


def eligible_rows(rows,league,cutoff):
    end=aware(cutoff);eligible=[]
    for row in rows:
        try:
            observed,forecast,start,final=(aware(row[k]) for k in ('feature_observed_at','forecast_at','starts_at','final_observed_at'))
            if row.get('league')!=league or row.get('rights_verified') is not True:continue
            if not observed<=forecast<start<=final<end or row['home_win'] not in (0,1):continue
            if not row.get('game_id') or not row.get('season'):continue
            base=float(row['baseline_probability'])
            vector=[float(row['features'][name]) for name in FEATURES]
            if not 0<base<1 or any(not math.isfinite(x) or abs(x)>80 for x in vector):continue
            eligible.append({**row,'baseline_probability':base,'vector':vector})
        except (KeyError,TypeError,ValueError,OverflowError):continue
    eligible.sort(key=lambda x:(aware(x['forecast_at']),x['game_id']))
    first={}
    for row in eligible:first.setdefault(row['game_id'],row)
    return list(first.values())


def _logit(p):return math.log(p/(1-p))


def _fit(rows,l2,epochs=400,step=.03):
    weights=[0.0]*len(FEATURES);intercept=0.0;n=len(rows)
    for _ in range(epochs):
        grad=[0.0]*len(weights);bias=0.0
        for row in rows:
            error=_sigmoid(_logit(row['baseline_probability'])+intercept+sum(w*x for w,x in zip(weights,row['vector'])))-row['home_win']
            bias+=error
            for j,x in enumerate(row['vector']):grad[j]+=error*x
        intercept-=step*bias/n
        for j in range(len(weights)):weights[j]-=step*(grad[j]/n+l2*weights[j])
    return {'intercept':intercept,'weights':weights,'l2':l2}


def _predict(fit,base,vector):
    return _sigmoid(_logit(base)+fit['intercept']+sum(w*x for w,x in zip(fit['weights'],vector)))


def _score(rows,fit=None):
    predictions=[_predict(fit,r['baseline_probability'],r['vector']) if fit else r['baseline_probability'] for r in rows]
    loss=sum(-(r['home_win']*math.log(p)+(1-r['home_win'])*math.log(1-p)) for r,p in zip(rows,predictions))/len(rows)
    brier=sum((p-r['home_win'])**2 for r,p in zip(rows,predictions))/len(rows)
    return {'log_loss':loss,'brier':brier}


def fit_availability_shadow(rows,league,cutoff,min_training=500,min_validation=100,min_seasons=3):
    data=eligible_rows(rows,league,cutoff)
    seasons=sorted({str(r['season']) for r in data})
    if len(seasons)<min_seasons:return None
    validation=[r for r in data if str(r['season'])==seasons[-1]]
    if len(validation)<min_validation:return None
    start=min(aware(r['forecast_at']) for r in validation)
    training=[r for r in data if str(r['season'])!=seasons[-1] and aware(r['final_observed_at'])<start]
    if len(training)<min_training:return None
    scores=[]
    for penalty in GRID:
        fit=_fit(training,penalty)
        scores.append({'l2':penalty,**_score(validation,fit)})
    chosen=min(scores,key=lambda item:item['log_loss'])
    final=_fit(data,chosen['l2'])
    digest=hashlib.sha256(json.dumps([(r['game_id'],r['forecast_at'],r['final_observed_at'],r['baseline_probability'],r['vector'],r['home_win']) for r in data],separators=(',',':')).encode()).hexdigest()
    return {**final,'model_version':'availability-logistic-v1','league':league,'features':list(FEATURES),
            'trained_before':aware(cutoff).isoformat(),'training_hash':digest,'training_games':len(data),
            'inner_training_games':len(training),'validation_games':len(validation),'validation_season':seasons[-1],
            'validation_scores':scores,'baseline_validation':_score(validation),'status':'shadow_unvalidated','promoted':False}


def predict_availability_shadow(model,base_probability,features,prediction_at,feature_observed_at):
    try:
        if not model or model.get('model_version')!='availability-logistic-v1' or model.get('promoted') is not False:return None
        prediction=aware(prediction_at)
        if aware(model['trained_before'])>=prediction or aware(feature_observed_at)>prediction:return None
        base=float(base_probability);vector=[float(features[name]) for name in FEATURES]
        if not 0<base<1 or any(not math.isfinite(x) or abs(x)>80 for x in vector):return None
        if model.get('features')!=list(FEATURES) or len(model.get('weights',[]))!=len(FEATURES):return None
        return _predict(model,base,vector)
    except (KeyError,TypeError,ValueError,OverflowError):return None
