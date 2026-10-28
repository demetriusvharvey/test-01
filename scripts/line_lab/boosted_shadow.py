"""Market-independent, monotonic boosted-stump research challenger."""
import hashlib
import json
import math
from .history import aware
from .model_stack import FEATURES,FORBIDDEN,_sigmoid,eligible_rows

GRID=((25,.05,10.0),(50,.05,10.0),(50,.10,10.0))


def _thresholds(rows,width,max_bins=15):
    result=[]
    for j in range(width):
        vals=sorted({r['vector'][j] for r in rows})
        if len(vals)<2:result.append([]);continue
        positions={min(len(vals)-2,int(i*(len(vals)-1)/(max_bins+1))) for i in range(1,max_bins+1)}
        result.append([(vals[i]+vals[i+1])/2 for i in sorted(positions) if vals[i]<vals[i+1]])
    return result


def _fit(rows,stages,learning_rate,l2,min_leaf):
    n=len(rows);wins=sum(r['home_win'] for r in rows)
    base=math.log((wins+1)/(n-wins+1));scores=[base]*n;trees=[]
    thresholds=_thresholds(rows,len(rows[0]['vector']))
    # Sum of individually monotone stumps preserves monotonicity for those inputs.
    monotone={0,1}
    for _ in range(stages):
        probabilities=[_sigmoid(s) for s in scores]
        gradients=[r['home_win']-p for r,p in zip(rows,probabilities)]
        hessians=[p*(1-p) for p in probabilities]
        total_g,total_h=sum(gradients),sum(hessians);best=None
        for j,cuts in enumerate(thresholds):
            for cut in cuts:
                left=[i for i,r in enumerate(rows) if r['vector'][j]<=cut]
                if len(left)<min_leaf or n-len(left)<min_leaf:continue
                gl=sum(gradients[i] for i in left);hl=sum(hessians[i] for i in left)
                gr,hr=total_g-gl,total_h-hl
                lv=max(-3.0,min(3.0,gl/(hl+l2)));rv=max(-3.0,min(3.0,gr/(hr+l2)))
                if j in monotone and lv>rv:continue
                gain=gl*gl/(hl+l2)+gr*gr/(hr+l2)-total_g*total_g/(total_h+l2)
                if gain>0 and (best is None or gain>best[0]):best=(gain,j,cut,lv,rv)
        if best is None:break
        _,feature,cut,left_value,right_value=best
        tree={'feature':feature,'threshold':cut,'left':learning_rate*left_value,'right':learning_rate*right_value}
        trees.append(tree)
        for i,row in enumerate(rows):scores[i]+=tree['left'] if row['vector'][feature]<=cut else tree['right']
    return {'base_logit':base,'trees':trees,'learning_rate':learning_rate,'l2':l2,'min_leaf':min_leaf}


def _predict_vector(model,vector):
    score=model['base_logit']+sum(t['left'] if vector[t['feature']]<=t['threshold'] else t['right'] for t in model['trees'])
    return _sigmoid(score)


def fit_boosted_shadow(rows,league,cutoff,features=FEATURES,min_training=500,min_validation=100,min_seasons=3,min_leaf=30):
    """Tune the registered grid on a later prior season, then refit for future."""
    if tuple(features)!=FEATURES:raise ValueError('boosted feature set is fixed by preregistration')
    data=eligible_rows(rows,league,cutoff,features)
    seasons=sorted({str(r.get('season','')) for r in data if r.get('season')})
    if len(seasons)<min_seasons:return None
    validation=[r for r in data if str(r.get('season'))==seasons[-1]]
    if len(validation)<min_validation:return None
    validation_start=min(aware(r['forecast_at']) for r in validation)
    training=[r for r in data if str(r.get('season'))!=seasons[-1] and aware(r['final_observed_at'])<validation_start]
    if len(training)<min_training:return None
    results=[]
    for stages,rate,l2 in GRID:
        model=_fit(training,stages,rate,l2,min_leaf)
        predictions=[_predict_vector(model,r['vector']) for r in validation]
        loss=sum(-(r['home_win']*math.log(p)+(1-r['home_win'])*math.log(1-p)) for r,p in zip(validation,predictions))/len(validation)
        brier=sum((p-r['home_win'])**2 for r,p in zip(validation,predictions))/len(validation)
        results.append({'stages':stages,'learning_rate':rate,'l2':l2,'validation_log_loss':loss,'validation_brier':brier})
    chosen=min(results,key=lambda r:r['validation_log_loss'])
    final=_fit(data,chosen['stages'],chosen['learning_rate'],chosen['l2'],min_leaf)
    digest=hashlib.sha256(json.dumps([(r['game_id'],r['forecast_at'],r['final_observed_at'],r['vector'],r['home_win']) for r in data],separators=(',',':')).encode()).hexdigest()
    return {**final,'model_version':'pure-stumpboost-v1','league':league,'features':list(features),
            'trained_before':aware(cutoff).isoformat(),'training_hash':digest,'training_games':len(data),
            'inner_training_games':len(training),'validation_games':len(validation),'validation_season':seasons[-1],
            'validation_scores':results,'status':'shadow_unvalidated','promoted':False}


def predict_boosted_shadow(model,features,prediction_at,feature_observed_at):
    try:
        if not model or model.get('promoted') is not False or model.get('model_version')!='pure-stumpboost-v1':return None
        if aware(model['trained_before'])>=aware(prediction_at) or aware(feature_observed_at)>aware(prediction_at):return None
        names=model['features']
        if any(any(word in name.lower() for word in FORBIDDEN) for name in names):return None
        vector=[float(features[name]) for name in names]
        if any(not math.isfinite(x) for x in vector):return None
        return _predict_vector(model,vector)
    except (KeyError,TypeError,ValueError,IndexError):return None


def explain_boosted(model,features,prediction_at,feature_observed_at):
    p=predict_boosted_shadow(model,features,prediction_at,feature_observed_at)
    if p is None:return None
    names=model['features'];contributions={name:0.0 for name in names}
    for tree in model['trees']:
        name=names[tree['feature']]
        contributions[name]+=tree['left'] if float(features[name])<=tree['threshold'] else tree['right']
    return {'probability':p,'base_logit':model['base_logit'],'feature_logit_contributions':contributions,
            'method':'sum of fitted stump outputs; not SHAP or a causal effect','status':'shadow_unvalidated'}
