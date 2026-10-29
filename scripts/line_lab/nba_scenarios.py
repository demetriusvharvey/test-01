"""Conditional roster/injury scenarios using trained rotation features."""
from .history import aware
from .nba_lineup import project_rotation,map_injury_statuses
import hashlib
import json


def conditional_forecasts(model,base_vector,event,players,rosters,payload,observed_at,now,predict):
    """Return explicit scenarios, not a fabricated P(plays) mixture or interval."""
    if not payload or not observed_at:return {'status':'injury_feed_unavailable','scenarios':[]}
    if model.get('model_version')!='nba-rotation-logistic-v1' or aware(model['exported_at'])>aware(now):
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
    cutoff=aware(now).date();scenarios=[]
    for label,exclude_uncertain in (('listed_uncertain_players_available',False),('listed_uncertain_players_unavailable',True)):
        summaries={}
        for side in ('home','away'):
            roster,report=mapped[side]
            absent=[p for p,s in report['players'].items() if s in ('questionable','doubtful','game_time_decision','day_to_day')] if exclude_uncertain else []
            rotation=project_rotation(players,roster,report,now,event['starts_at'],absent,conditional=True)
            if rotation is None:return {'status':'insufficient_rotation_history','scenarios':[]}
            scoring=0.;experienced=0.;minutes=[]
            for p in rotation['players']:
                rows=sorted((r for r in players if r['player_id']==p['player_id'] and r['team']==roster['team'] and r['date']<cutoff),key=lambda r:r['date'])[-10:]
                total=sum(r['minutes'] for r in rows)
                if not total:return {'status':'player_performance_unavailable','scenarios':[]}
                scoring+=p['minutes']*sum(r['points'] for r in rows)/total
                if len(rows)>=5:experienced+=p['minutes']/240
                minutes.append(p['minutes'])
            summaries[side]=(scoring,sum(sorted(minutes,reverse=True)[:5])/240,experienced)
        h,a=summaries['home'],summaries['away']
        vector=base_vector+[(h[0]-a[0])/20,h[1]-a[1],h[2]-a[2]]
        probability=predict(model,vector)
        scenarios.append({'scenario':label,'home_probability':probability,'away_probability':1-probability,
                          'features':dict(zip(model['features'],vector))})
    return {'status':'conditional_research_only','scenarios':scenarios,
            'model_version':model['model_version'],'injury_observed_at':observed_at,
            'model_hash':hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest(),
            'assumption':'unlisted players available within each scenario; not confirmed',
            'limitations':'no scenario weights, causal injury effects, defensive player values or validated replacement impacts'}
