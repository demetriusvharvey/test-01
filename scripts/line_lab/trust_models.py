"""Time-ordered, unpromoted trust and closing-movement research models."""
import hashlib
import json
import math
from .history import aware
from .model_stack import _fit,_predict_vector

FEATURES=('model_edge','price_edge','source_disagreement','hours_to_start','line_movement',
          'model_uncertainty','news_age_hours','games_played','liquidity')


def _vector(features):
    values=[float(features[name]) for name in FEATURES]
    if any(not math.isfinite(x) for x in values):raise ValueError('non-finite feature')
    if any(values[i]<0 for i in (2,3,5,6,7)) or values[8]<=0:raise ValueError('invalid feature range')
    if any(abs(values[i])>1 for i in (0,1,4)) or values[2]>1 or values[5]>1:raise ValueError('invalid probability-scale feature')
    return values


def eligible_samples(rows,league,cutoff):
    """Choose a first candidate before testing its labels or data eligibility."""
    end=aware(cutoff);ordered=[]
    for row in rows:
        try:
            if row.get('league')==league and row.get('game_id') and row.get('side') in ('home','away'):
                ordered.append((aware(row['predicted_at']),row))
        except (KeyError,TypeError,ValueError):continue
    first={}
    for _,row in sorted(ordered,key=lambda x:(x[0],x[1]['game_id'],x[1]['side'])):
        first.setdefault((row['game_id'],row['side']),row)
    valid=[]
    for row in first.values():
        try:
            prediction,start,feature,quote,quote_seen,anchor,anchor_seen,close,close_seen,certified=(aware(row[k]) for k in (
                'predicted_at','starts_at','feature_observed_at','quote_source_at','quote_observed_at',
                'anchor_source_at','anchor_observed_at','close_source_at','close_observed_at','close_certified_at'))
            if not (feature<=prediction<start and quote<=quote_seen<=prediction and anchor<=anchor_seen<=prediction):continue
            if not prediction<=close<=close_seen<start<=certified<end:continue
            if not all(row.get(k) is True for k in ('rights_verified','independent_sharp','close_certified','liquidity_verified','news_verified')):continue
            p=float(row['anchor_probability']);q=float(row['close_probability']);decimal=float(row['decimal_odds'])
            if not 0<p<1 or not 0<q<1 or not math.isfinite(decimal) or decimal<=1:continue
            features=_vector(row['features'])
            clv=decimal*q-1
            valid.append({**row,'vector':features,'home_win':int(clv>0),'movement':q-p})
        except (KeyError,TypeError,ValueError,OverflowError):continue
    return valid


def _fit_linear(rows,l2=.01,epochs=300,step=.08):
    n=len(rows);width=len(FEATURES)
    means=[sum(r['vector'][j] for r in rows)/n for j in range(width)]
    scales=[math.sqrt(sum((r['vector'][j]-means[j])**2 for r in rows)/n) or 1.0 for j in range(width)]
    matrix=[[(r['vector'][j]-means[j])/scales[j] for j in range(width)] for r in rows]
    weights=[0.0]*width;intercept=sum(r['movement'] for r in rows)/n
    for _ in range(epochs):
        gradient=[0.0]*width;bias=0.0
        for x,row in zip(matrix,rows):
            error=intercept+sum(a*b for a,b in zip(weights,x))-row['movement'];bias+=error
            for j in range(width):gradient[j]+=error*x[j]
        intercept-=step*bias/n
        for j in range(width):weights[j]-=step*(gradient[j]/n+l2*weights[j])
    return {'means':means,'scales':scales,'weights':weights,'intercept':intercept,'l2':l2}


def _linear_prediction(model,vector):
    return model['intercept']+sum(w*(x-m)/s for w,x,m,s in zip(model['weights'],vector,model['means'],model['scales']))


def fit_trust_timing_shadow(rows,league,cutoff,min_training=500,min_validation=100,min_seasons=3):
    eligible=eligible_samples(rows,league,cutoff)
    seasons=sorted({str(r.get('season','')) for r in eligible if r.get('season')})
    if len(seasons)<min_seasons:return None
    validation=[r for r in eligible if str(r.get('season'))==seasons[-1]]
    if len(validation)<min_validation:return None
    validation_start=min(aware(r['predicted_at']) for r in validation)
    training=[r for r in eligible if str(r.get('season'))!=seasons[-1] and aware(r['close_certified_at'])<validation_start]
    if len(training)<min_training:return None
    classifier=_fit(training,0.0,.01);movement=_fit_linear(training)
    pred=[_predict_vector(classifier,r['vector']) for r in validation]
    brier=sum((p-r['home_win'])**2 for p,r in zip(pred,validation))/len(validation)
    mae=sum(abs(_linear_prediction(movement,r['vector'])-r['movement']) for r in validation)/len(validation)
    data_hash=hashlib.sha256(json.dumps([(r['game_id'],r['side'],r['predicted_at'],r['close_certified_at'],r['vector'],r['home_win'],r['movement']) for r in eligible],separators=(',',':')).encode()).hexdigest()
    return {'model_version':'trust-timing-shadow-v1','league':league,'features':list(FEATURES),
            'trained_before':end_time(cutoff),'training_games':len(eligible),'training_hash':data_hash,
            'inner_training_games':len(training),'validation_games':len(validation),'validation_season':seasons[-1],
            'inner_brier':brier,'inner_movement_mae':mae,
            'classifier':_fit(eligible,0.0,.01),'movement_model':_fit_linear(eligible),
            'status':'shadow_unvalidated','promoted':False}


def end_time(value):return aware(value).isoformat()


def predict_trust_timing_shadow(model,features,observed_at,prediction_at):
    try:
        if not model or model.get('promoted') is not False or model.get('model_version')!='trust-timing-shadow-v1':return None
        if aware(model['trained_before'])>=aware(prediction_at) or aware(observed_at)>aware(prediction_at):return None
        vector=_vector(features)
        return {'positive_clv_probability':_predict_vector(model['classifier'],vector),
                'expected_sharp_probability_change':_linear_prediction(model['movement_model'],vector),
                'status':'shadow_unvalidated','timing_recommendation':'unknown','staking_allowed':False}
    except (KeyError,TypeError,ValueError,ZeroDivisionError):return None
