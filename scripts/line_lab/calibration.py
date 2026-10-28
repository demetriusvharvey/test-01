"""Research-only walk-forward calibration and fitted sharp-market blend.

These utilities are deliberately not wired into live picks. No calibration or
sharp anchor is claimed until qualified pregame data and validation exist.
"""
import math, random
from collections import defaultdict
from .history import aware
from .constants import ET


def _logit(p):
    p=max(1e-6,min(1-1e-6,p));return math.log(p/(1-p))

def _sigmoid(x):return 1/(1+math.exp(-max(-30,min(30,x))))

def eligible_past_rows(rows,as_of,require_sharp=False):
    """One first pregame observation per event, with the outcome already known."""
    cutoff=aware(as_of);first={}
    for row in sorted(rows,key=lambda x:x.get('captured_at','')):
        try:
            captured=aware(row['captured_at']);start=aware(row['starts_at']);settled=aware(row['settled_at'])
            p=float(row['pure_probability']);y=row['outcome']
            if not (captured<start<=settled<cutoff and 0<p<1 and y in (0,1)):continue
            if require_sharp:
                q=float(row['sharp_probability']);published=aware(row['sharp_as_of'])
                if row.get('anchor_type')!='sharp' or not (0<q<1 and published<=captured):continue
            first.setdefault(row['game_id'],row)
        except (KeyError,ValueError,TypeError,OverflowError):continue
    return list(first.values())

def _fit(rows,use_sharp,iterations=500,rate=.04,l2=.02):
    weights=[0.0,1.0]+([0.0] if use_sharp else [])
    for _ in range(iterations):
        gradients=[0.0]*len(weights)
        for row in rows:
            values=[1.0,_logit(float(row['pure_probability']))]
            if use_sharp:values.append(_logit(float(row['sharp_probability'])))
            error=_sigmoid(sum(a*b for a,b in zip(weights,values)))-row['outcome']
            for i,x in enumerate(values):gradients[i]+=error*x
        for i in range(len(weights)):
            penalty=0 if i==0 else l2*weights[i]
            weights[i]-=rate*(gradients[i]/len(rows)+penalty)
    return weights

def fit_platt_shadow(rows,as_of,min_games=500):
    qualified=eligible_past_rows(rows,as_of)
    if len(qualified)<min_games:return None
    return {'method':'platt_shadow','weights':_fit(qualified,False),'games':len(qualified),'trained_before':as_of,'promoted':False}

def fit_sharp_blend_shadow(rows,as_of,min_games=500):
    qualified=eligible_past_rows(rows,as_of,require_sharp=True)
    if len(qualified)<min_games:return None
    return {'method':'logit_blend_shadow','weights':_fit(qualified,True),'games':len(qualified),'trained_before':as_of,'promoted':False}

def predict_shadow(fit,pure,sharp=None):
    values=[1.0,_logit(pure)]
    if fit['method']=='logit_blend_shadow':
        if sharp is None:return None
        values.append(_logit(sharp))
    return _sigmoid(sum(a*b for a,b in zip(fit['weights'],values)))

def bootstrap_shadow_interval(rows,as_of,pure,sharp=None,min_games=500,min_days=20,draws=200,seed=20261028):
    """Block-bootstrap parameter uncertainty for research, not proven coverage."""
    use_sharp=sharp is not None
    qualified=eligible_past_rows(rows,as_of,require_sharp=use_sharp)
    groups=defaultdict(list)
    for row in qualified:groups[aware(row['starts_at']).astimezone(ET).date().isoformat()].append(row)
    if len(qualified)<min_games or len(groups)<min_days:return None
    if draws<2:raise ValueError('at least two bootstrap draws are required')
    blocks=list(groups.values());rng=random.Random(seed);estimates=[]
    for _ in range(draws):
        sampled=[row for _ in blocks for row in blocks[rng.randrange(len(blocks))]]
        weights=_fit(sampled,use_sharp,iterations=150)
        fit={'method':'logit_blend_shadow' if use_sharp else 'platt_shadow','weights':weights}
        estimates.append(predict_shadow(fit,pure,sharp))
    estimates.sort()
    return {'interval':[estimates[int(.025*(draws-1))],estimates[int(.975*(draws-1))]],
            'games':len(qualified),'days':len(groups),'draws':draws,'promoted':False,
            'meaning':'parameter bootstrap, predictive coverage not established'}
