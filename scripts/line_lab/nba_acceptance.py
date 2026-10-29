"""Acceptance checks for implemented NBA model capabilities, not betting validity."""
import math
from .history import aware
from .constants import ET


def check_predictions(predictions,now):
    current=aware(now);today=current.astimezone(ET).date();checks=[]
    active=[p for p in predictions if aware(p['starts_at']).astimezone(ET).date()==today]
    checks.append(('today_has_forecasts',bool(active)))
    for p in active:
        game=p['game_id'];home=p.get('home_probability');away=p.get('away_probability')
        checks.append((game+':probabilities',all(isinstance(v,(int,float)) and math.isfinite(v) and 0<v<1 for v in (home,away))
                       and math.isclose(home+away,1,abs_tol=1e-12)))
        checks.append((game+':pregame',aware(p['predicted_at'])<aware(p['starts_at']) and aware(p['model_exported_at'])<=aware(p['predicted_at'])<=current))
        checks.append((game+':provenance',bool(p.get('model_version') and p.get('model_input_hash') and p.get('features') and p.get('input_data_observed_at'))))
        checks.append((game+':missingness_and_uncertainty',bool(p.get('missing_inputs') and p.get('uncertainty'))))
        context=p.get('availability_scenarios') or {}
        scenarios=context.get('scenarios') or []
        checks.append((game+':live_roster_injury_join',context.get('status')=='conditional_research_only' and len(scenarios)==2))
        checks.append((game+':scenario_reproducibility',bool(context.get('model_hash')) and all(s.get('features') for s in scenarios)))
        checks.append((game+':scenario_probabilities',bool(scenarios) and all(
            0<s['home_probability']<1 and math.isclose(s['home_probability']+s['away_probability'],1,abs_tol=1e-12)
            for s in scenarios)))
    return {'status':'passed' if all(ok for _,ok in checks) else 'incomplete',
            'games_checked':len(active),'checks':[{'check':name,'passed':ok} for name,ok in checks],
            'scope':'model inference and conditional roster/injury integration; not model promotion or causal injury validation'}
