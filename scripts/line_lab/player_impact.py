"""Regularized player-exposure research; never substitutes status counts for value."""
import hashlib
import json
import math
from .history import aware
from .availability_model import _fit,_score,_predict


def eligible_player_rows(records,league,cutoff):
    """Require genuinely pregame expected participation, not final minutes/snaps."""
    end=aware(cutoff);first={}
    for row in records:
        try:
            observed,forecast,start,final=(aware(row[k]) for k in
                ('feature_observed_at','forecast_at','starts_at','final_observed_at'))
            if (row.get('league')!=league or row.get('rights_verified') is not True
                    or row.get('exposure_type')!='pregame_expected_share'
                    or row.get('roster_verified') is not True
                    or not observed<=forecast<start<=final<end or row['home_win'] not in (0,1)):continue
            base=float(row['baseline_probability']);players=row['exposures']
            if not 0<base<1 or not isinstance(players,dict) or not players:continue
            if any(not isinstance(p,str) or not p or not isinstance(v,(int,float))
                   or isinstance(v,bool) or not math.isfinite(v) or not -1<=v<=1 for p,v in players.items()):continue
            if row['home']==row['away'] or not row.get('season') or not row.get('game_id'):continue
            # Positive share = home player; negative = away player. Team/player
            # mappings are frozen by the caller from a verified pregame roster.
            teams=row['player_teams']
            if any(teams.get(p) not in (row['home'],row['away']) or
                   (v!=0 and teams.get(p)!=(row['home'] if v>0 else row['away']))
                   for p,v in players.items()):continue
            key=row['game_id'];value={**row,'baseline_probability':base}
            if key not in first or forecast<aware(first[key]['forecast_at']):first[key]=value
        except (KeyError,TypeError,ValueError,OverflowError):continue
    return sorted(first.values(),key=lambda r:(aware(r['forecast_at']),r['game_id']))


def fit_player_impact(records,league,cutoff,min_training=500,min_validation=100,min_player_games=20):
    """Fit associations above frozen Elo; retain final season for validation.

    A model artifact remains research-only. Sparse/unseen players have unknown
    effects, not an assumed replacement value.
    """
    data=eligible_player_rows(records,league,cutoff)
    seasons=sorted({str(r['season']) for r in data})
    if len(seasons)<3:return None
    validation=[r for r in data if str(r['season'])==seasons[-1]]
    if len(validation)<min_validation:return None
    boundary=min(aware(r['forecast_at']) for r in validation)
    training=[r for r in data if str(r['season'])!=seasons[-1] and aware(r['final_observed_at'])<boundary]
    if len(training)<min_training:return None
    counts={}
    for row in training:
        for p,v in row['exposures'].items():
            if v:counts[p]=counts.get(p,0)+1
    names=sorted(p for p,n in counts.items() if n>=min_player_games)
    if not names:return None
    def vectors(rows):return [{**r,'vector':[float(r['exposures'].get(p,0)) for p in names]} for r in rows]
    train,test=vectors(training),vectors(validation)
    trials=[]
    for penalty in (.1,1.,10.):
        fit=_fit(train,penalty)
        trials.append((fit,_score(test,fit)))
    chosen,score=min(trials,key=lambda pair:pair[1]['log_loss'])
    # Keep the evaluated artifact; do not silently refit on validation outcomes.
    digest=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {**chosen,'model_version':'player-exposure-logistic-v1','league':league,
            'features':names,'trained_before':boundary.isoformat(),'evaluated_at':aware(cutoff).isoformat(),
            'training_games':len(train),'validation_games':len(test),'validation_season':seasons[-1],
            'validation':score,'baseline_validation':_score(test),'player_sample_sizes':{p:counts[p] for p in names},
            'training_hash':digest,'promoted':False,'status':'research_only',
            'limitations':'observational player associations; replacement and causal effects unverified'}


def predict_player_impact(model,base,exposures,prediction_at,observed_at):
    try:
        now=aware(prediction_at)
        if (not model or model.get('promoted') is not False
                or model.get('model_version')!='player-exposure-logistic-v1'
                or aware(model['evaluated_at'])>=now or aware(observed_at)>now
                or not isinstance(exposures,dict) or not 0<float(base)<1):return None
        if any(p not in model['features'] for p,v in exposures.items() if v):return None
        vector=[float(exposures.get(p,0)) for p in model['features']]
        if len(vector)!=len(model['weights']) or any(not math.isfinite(v) or abs(v)>1 for v in vector):return None
        return _predict(model,float(base),vector)
    except (KeyError,TypeError,ValueError,OverflowError):return None
