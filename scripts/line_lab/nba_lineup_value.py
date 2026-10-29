"""Conditional lineup associations from learned stint coefficients, never win odds."""
import hashlib
import json
import math
from datetime import date
from itertools import product
from .constants import ET
from .history import aware
from .nba_lineup import map_injury_statuses,project_rotation


def rotation_value(model,rotation):
    names=model['features'];values=model['weights']
    if len(names)!=len(values) or len(names)!=len(set(names)):raise ValueError('rating dimensions')
    effects=dict(zip(names,values));samples=model['player_training_minutes']
    estimate=0.
    for player in rotation['players']:
        p=player['player_id'];value=effects.get(p)
        if type(value) not in (int,float) or not math.isfinite(value) or samples.get(p,0)<120:
            return None
        minutes=player['minutes']
        if type(minutes) not in (int,float) or not math.isfinite(minutes) or not 0<minutes<=48:raise ValueError('invalid projected minutes')
        estimate+=minutes/48*value
    if not math.isclose(sum(p['minutes'] for p in rotation['players']),240,abs_tol=1e-6):raise ValueError('incomplete rotation')
    return estimate


def lineup_associations(model,event,players,rosters,payload,observed_at,now):
    try:
        current=aware(now)
        if (model.get('model_version') not in ('nba-stint-ridge-v1','nba-full-stint-ridge-v1') or model.get('promoted') is not False
                or aware(model['exported_at'])>current
                or date.fromisoformat(model['trained_before_date'])>current.astimezone(ET).date()):
            raise ValueError('rating artifact unavailable')
        if not payload or not observed_at:return {'status':'injury_feed_unavailable','scenarios':[]}
        mapped={}
        for side in ('home','away'):
            roster=rosters.get(event[side])
            if not roster:return {'status':'roster_unavailable','scenarios':[]}
            report=map_injury_statuses(payload,roster,observed_at)
            if not report or not report['identity_mapping_valid']:return {'status':'unmatched_injury_identity','scenarios':[]}
            mapped[side]=(roster,report)
        uncertain=[(side,p) for side,(_,report) in mapped.items() for p,status in sorted(report['players'].items())
                   if status in ('questionable','doubtful','game_time_decision','day_to_day')]
        if len(uncertain)>6:return {'status':'scenario_limit_exceeded','scenarios':[]}
        baseline={};cache={}
        for side,(roster,report) in mapped.items():
            # Explicit counterfactual only, never a forecast that injured players play.
            counterfactual={**report,'players':{p:'available' for p in report['players']}}
            rotation=project_rotation(players,roster,counterfactual,now,event['starts_at'],conditional=True)
            baseline[side]=rotation_value(model,rotation) if rotation else None
        scenarios=[]
        for states in product((False,True),repeat=len(uncertain)):
            strengths={}
            for side,(roster,report) in mapped.items():
                excluded=tuple(p for (s,p),out in zip(uncertain,states) if s==side and out)
                key=(side,excluded)
                if key not in cache:
                    rotation=project_rotation(players,roster,report,now,event['starts_at'],excluded,conditional=True)
                    if not rotation:return {'status':'rotation_or_freshness_unavailable','scenarios':[]}
                    cache[key]=rotation_value(model,rotation)
                if cache[key] is None:return {'status':'unknown_player_effect','scenarios':[]}
                strengths[side]=cache[key]
            value=strengths['home']-strengths['away']
            base=baseline['home']-baseline['away'] if all(v is not None for v in baseline.values()) else None
            scenarios.append({'scenario':'availability_'+(''.join('0' if out else '1' for out in states) or 'no_uncertain_players'),
                              'home_lineup_association':strengths['home'],'away_lineup_association':strengths['away'],
                              'home_minus_away_association':value,'change_from_all_available_counterfactual':value-base if base is not None else None})
        return {'status':'lineup_associations_available','scenarios':scenarios,'scenario_count':len(scenarios),
                'model_version':model['model_version'],'model_hash':hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest(),
                'model_input_hash':model['input_hash'],'model_exported_at':model['exported_at'],
                'model_trained_before_date':model['trained_before_date'],'injury_observed_at':observed_at,
                'counterfactual_available':all(v is not None for v in baseline.values()),
                'units':model.get('units','net points per 48 minutes; learned lineup association'),
                'used_in_public_picks':False,
                'limitations':'observational association, inferred minutes, incomplete defense; counterfactual delta is not a causal injury effect or win probability'}
    except (KeyError,ValueError,TypeError,OverflowError):return {'status':'lineup_model_unavailable','scenarios':[]}


def partial_rotation_value(model,rotation):
    """Return a measured supported subset and coverage, never total lineup value."""
    names=model['features'];values=model['weights']
    if len(names)!=len(values) or len(set(names))!=len(names):raise ValueError('rating dimensions')
    effects=dict(zip(names,values));samples=model['player_training_minutes'];component=0.;known=0.
    for player in rotation['players']:
        minutes=player['minutes'];p=player['player_id'];value=effects.get(p)
        if type(minutes) not in (int,float) or not math.isfinite(minutes) or not 0<minutes<=48:raise ValueError('invalid minutes')
        if type(value) in (int,float) and math.isfinite(value) and samples.get(p,0)>=120:
            component+=minutes/48*value;known+=minutes
    total=sum(p['minutes'] for p in rotation['players'])
    if not math.isclose(total,240,abs_tol=1e-6):raise ValueError('incomplete rotation')
    return {'known_component':component,'supported_fraction':min(1.,max(0.,known/240)),'unknown_minutes':max(0.,240-known),
            'total_lineup_value':None if known<240-1e-6 else component}
