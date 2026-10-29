"""Conditional roster/injury scenarios using trained rotation features."""
from .history import aware
from .nba_lineup import project_rotation,map_injury_statuses
import hashlib
import json
from itertools import product
from .constants import ET


def conditional_forecasts(model,base_vector,event,players,rosters,payload,observed_at,now,predict):
    """Return explicit scenarios, not a fabricated P(plays) mixture or interval."""
    if not payload or not observed_at:return {'status':'injury_feed_unavailable','scenarios':[]}
    if model.get('model_version') not in ('nba-rotation-logistic-v1','nba-player-box-logistic-v1') or aware(model['exported_at'])>aware(now):
        return {'status':'rotation_model_unavailable','scenarios':[]}
    mapped={}
    for side in ('home','away'):
        roster=rosters.get(event[side])
        if not roster:return {'status':'roster_unavailable','scenarios':[]}
        report=map_injury_statuses(payload,roster,observed_at)
        if not report:return {'status':'invalid_injury_report','scenarios':[]}
        mapped[side]=(roster,report)
    if any(not report['identity_mapping_valid'] for roster,report in mapped.values()):
        return {'status':'unmatched_injury_identity','scenarios':[],
                'join_diagnostics':{side:{k:report[k] for k in ('diagnostics','unmatched','invalid','matched_players','roster_players')}
                                    for side,(roster,report) in mapped.items()}}
    cutoff=aware(now).astimezone(ET).date();scenarios=[]
    multi_stat=model['model_version']=='nba-player-box-logistic-v1'
    # Enumerate each listed uncertain player independently, including opposing
    # availability states. Never assign unsupported participation probabilities.
    uncertain=[(side,p) for side,(_,report) in mapped.items()
               for p,status in sorted(report['players'].items())
               if status in ('questionable','doubtful','game_time_decision','day_to_day')]
    if len(uncertain)>6:
        return {'status':'scenario_limit_exceeded','scenarios':[],
                'uncertain_players':len(uncertain),'required_scenarios':2**len(uncertain),
                'limitation':'exhaustive availability scenarios exceed the 64-scenario compute bound'}
    cache={}
    for states in product((False,True),repeat=len(uncertain)):
        excluded={side:tuple(p for (s,p),out in zip(uncertain,states) if s==side and out)
                  for side in ('home','away')}
        label='availability_'+(''.join('0' if out else '1' for out in states) or 'no_uncertain_players')
        summaries={}
        for side in ('home','away'):
            roster,report=mapped[side]
            absent=excluded[side]
            cache_key=(side,absent)
            if cache_key in cache:
                summaries[side]=cache[cache_key];continue
            rotation=project_rotation(players,roster,report,now,event['starts_at'],absent,conditional=True)
            if rotation is None:return {'status':'insufficient_rotation_history','scenarios':[]}
            if multi_stat:
                from .nba_player_features import current_summary
                summary=current_summary(players,rotation,now)
                if summary is None:return {'status':'player_metrics_unavailable','scenarios':[]}
                summaries[side]=summary;cache[cache_key]=summary;continue
            scoring=0.;experienced=0.;minutes=[]
            for p in rotation['players']:
                rows=sorted((r for r in players if r['player_id']==p['player_id'] and r['team']==roster['team'] and r['date']<cutoff),key=lambda r:r['date'])[-10:]
                total=sum(r['minutes'] for r in rows)
                if not total:return {'status':'player_performance_unavailable','scenarios':[]}
                scoring+=p['minutes']*sum(r['points'] for r in rows)/total
                if len(rows)>=5:experienced+=p['minutes']/240
                minutes.append(p['minutes'])
            summaries[side]=(scoring,sum(sorted(minutes,reverse=True)[:5])/240,experienced)
            cache[cache_key]=summaries[side]
        h,a=summaries['home'],summaries['away']
        if multi_stat:
            from .nba_player_features import difference
            vector=base_vector+difference(h,a)
        else:vector=base_vector+[(h[0]-a[0])/20,h[1]-a[1],h[2]-a[2]]
        probability=predict(model,vector)
        scenarios.append({'scenario':label,'home_probability':probability,'away_probability':1-probability,
                          'features':dict(zip(model['features'],vector)),
                          'uncertain_available':{side:sum(s==side and not out for (s,p),out in zip(uncertain,states))
                                                 for side in ('home','away')}})
    low=min(s['home_probability'] for s in scenarios);high=max(s['home_probability'] for s in scenarios)
    return {'status':'conditional_research_only','scenario_count':len(scenarios),
            'uncertain_players':len(uncertain),'exhaustive_listed_uncertainty':True,
            'home_scenario_range':[low,high],
            'consistent_winner':event['home'] if low>.5 else event['away'] if high<.5 else None,
            'range_meaning':'conditional sensitivity range, not a confidence interval or calibrated mixture','scenarios':scenarios,
            'model_version':model['model_version'],'injury_observed_at':observed_at,
            'model_hash':hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest(),
            'assumption':'unlisted players available within each scenario; not confirmed',
            'limitations':'no scenario weights, causal injury effects, complete defensive values or validated replacement impacts; box-score events are proxies'}
