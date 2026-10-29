"""NFL position-group injury challenger, trained only on frozen pregame reports.

This is a shadow comparison to Elo, not a player-value or lineup model.
"""
import hashlib
import json
import math
from datetime import timedelta

from .availability_features import NFL_GROUPS, NFL_STATUSES
from .availability_model import _fit, _predict, _score, GRID
from .history import aware

FEATURES=tuple(f'{group.lower()}_{status}_difference'
               for group in NFL_GROUPS for status in NFL_STATUSES)
VERSION='nfl-position-status-logistic-v1'


def eligible_rows(rows,cutoff):
    current=aware(cutoff);valid={};conflicts=set()
    for row in rows:
        try:
            observed,forecast,start,final=(aware(row[k]) for k in
                ('feature_observed_at','forecast_at','starts_at','final_observed_at'))
            if (row.get('league')!='NFL' or row.get('rights_verified') is not True
                    or not observed<=forecast<start<=final<current
                    or forecast-observed>timedelta(hours=30)
                    or row['home_win'] not in (0,1) or not row.get('game_id') or not row.get('season')):continue
            base=float(row['baseline_probability'])
            vector=[float(row['features'][name])/5 for name in FEATURES]
            if not 0<base<1 or any(not math.isfinite(x) or abs(x)>16 for x in vector):continue
            key=row['game_id']
            candidate={**row,'baseline_probability':base,'vector':vector}
            if key in conflicts:continue
            prior=valid.get(key)
            if prior is not None:
                # Contradictory outcomes or same-time features invalidate the
                # entire game rather than make training order-dependent.
                mismatch=(prior['home_win']!=candidate['home_win']
                          or prior['season']!=candidate['season']
                          or aware(prior['starts_at'])!=start)
                if aware(prior['forecast_at'])==forecast:
                    mismatch=mismatch or (prior['baseline_probability']!=base
                                         or prior['vector']!=vector)
                if mismatch:
                    valid.pop(key,None);conflicts.add(key);continue
            if prior is None or forecast<aware(prior['forecast_at']):valid[key]=candidate
        except (KeyError,TypeError,ValueError,OverflowError):continue
    return sorted(valid.values(),key=lambda r:(aware(r['forecast_at']),r['game_id']))


def fit_position_shadow(rows,league,cutoff,min_training=500,min_validation=100,min_seasons=3):
    if league!='NFL':return None
    data=eligible_rows(rows,cutoff);seasons=sorted({str(r['season']) for r in data})
    if len(seasons)<min_seasons:return None
    validation=[r for r in data if str(r['season'])==seasons[-1]]
    if len(validation)<min_validation:return None
    first_validation=min(aware(r['forecast_at']) for r in validation)
    training=[r for r in data if str(r['season'])!=seasons[-1] and aware(r['final_observed_at'])<first_validation]
    if len(training)<min_training:return None
    scores=[{'l2':penalty,**_score(validation,_fit(training,penalty))} for penalty in GRID]
    chosen=min(scores,key=lambda result:result['log_loss'])
    # The refit only contains finals observed before the run. The validation
    # score is not an untouched or prospective measure of this final artifact.
    final=_fit(data,chosen['l2'])
    digest=hashlib.sha256(json.dumps(
        [(r['game_id'],r['forecast_at'],r['final_observed_at'],r['baseline_probability'],r['vector'],r['home_win'])
         for r in data],separators=(',',':')).encode()).hexdigest()
    return {**final,'model_version':VERSION,'league':'NFL','features':list(FEATURES),
            'trained_before':aware(cutoff).isoformat(),'training_hash':digest,'training_games':len(data),
            'inner_training_games':len(training),'validation_games':len(validation),
            'validation_season':seasons[-1],'validation_scores':scores,'baseline_validation':_score(validation),
            'status':'shadow_unvalidated','promoted':False}


def predict_position_shadow(model,base_probability,features,prediction_at,feature_observed_at):
    try:
        if (not model or model.get('model_version')!=VERSION or model.get('promoted') is not False
                or model.get('features')!=list(FEATURES) or len(model['weights'])!=len(FEATURES)
                or aware(model['trained_before'])>=aware(prediction_at)
                or not timedelta(0)<=aware(prediction_at)-aware(feature_observed_at)<=timedelta(hours=30)):return None
        base=float(base_probability);vector=[float(features[name])/5 for name in FEATURES]
        if not 0<base<1 or any(not math.isfinite(x) or abs(x)>16 for x in vector):return None
        return _predict(model,base,vector)
    except (KeyError,TypeError,ValueError,OverflowError):return None
