"""Recompute held-out results without fitting or selecting a model.

Day-block intervals preserve dependence among games on the same date. These
exploratory intervals do not turn an inspected archive into a fresh holdout.
"""
import math
import random
from collections import defaultdict
from .forecast_evaluation import probability, wilson
from .production import metrics


def audit_fold(fold, iterations=2000, seed=20261101):
    if not fold['training_end'] < fold['test_start'] or not fold['tuning_end'] < fold['test_start'] or not fold['calibration_end'] < fold['test_start']:
        raise ValueError('training/tuning/calibration overlaps test')
    rows = fold['predictions']
    seen = set()
    candidate = []
    baseline = []
    blocks = defaultdict(list)
    home_wins = 0
    for row in rows:
        if row['id'] in seen:
            raise ValueError('duplicate game in test fold')
        seen.add(row['id'])
        if not fold['test_start'] <= row['date'] <= fold['test_end'] or not row['feature_cutoff'] < row['date']:
            raise ValueError('feature/test date leakage')
        p, b, y = row['probability'], row['elo'], row['home_win']
        if not probability(p) or not probability(b) or type(y) is not int or y not in (0, 1):
            raise ValueError('invalid prediction/outcome')
        outcome = 'win' if y else 'loss'
        candidate.append({'probability':p, 'outcome':outcome})
        baseline.append({'probability':b, 'outcome':outcome})
        home_wins += y
        ll = lambda v: -(y*math.log(v)+(1-y)*math.log1p(-v))
        blocks[row['date']].append(((p-y)**2-(b-y)**2, ll(p)-ll(b)))
    model, elo = metrics(candidate), metrics(baseline)
    # Fail rather than silently replacing a previously published denominator.
    for name, recomputed in (('ensemble',model), ('elo',elo)):
        for key in ('sample_size','accuracy','brier','log_loss'):
            expected = fold[name][key]
            if expected is None or recomputed[key] is None:
                if expected != recomputed[key]:raise ValueError('reported metric mismatch')
            elif not math.isclose(expected,recomputed[key],abs_tol=1e-12):
                raise ValueError('reported metric mismatch')
    totals = [(len(v), sum(x[0] for x in v), sum(x[1] for x in v)) for v in blocks.values()]
    intervals = None
    if len(totals) >= 10:
        rng = random.Random(seed)
        draws = [[], []]
        for _ in range(iterations):
            sample = [totals[rng.randrange(len(totals))] for _ in totals]
            n = sum(v[0] for v in sample)
            for i in range(2):draws[i].append(sum(v[i+1] for v in sample)/n)
        for values in draws:values.sort()
        low, high = int(.025*iterations), min(iterations-1,int(.975*iterations))
        intervals = {'brier_difference':[draws[0][low],draws[0][high]],
                     'log_loss_difference':[draws[1][low],draws[1][high]],
                     'method':'paired day-block percentile bootstrap', 'iterations':iterations,
                     'seed':seed, 'game_days':len(totals),
                     'interpretation':'candidate minus fixed Elo; negative favors candidate; exploratory'}
    for result in (model, elo):
        result['accuracy_interval_95'] = wilson(result['wins'], result['sample_size'])
    n = len(rows)
    return {'season':fold['season'], 'test_start':fold['test_start'], 'test_end':fold['test_end'],
            'candidate':model, 'simple_fixed_elo':elo,
            'always_home_winner':{'sample_size':n,'wins':home_wins,
                'accuracy':home_wins/n if n else None,'accuracy_interval_95':wilson(home_wins,n),
                'probability_metrics':None,'reason':'winner rule, no fitted probability'},
            'paired_intervals_95':intervals, 'reported_metrics_reproduced':True,
            'market_baseline':None,'betting_roi':None,'preferred_odds_segment':None,
            'missing_price_reason':'historical observation timestamps absent; no prices or returns synthesized'}
