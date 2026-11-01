"""Point-in-time scoring of immutable production forecasts.

The original public winner ledger is deliberately outside this evaluator.
Never replace an early forecast with a later, better-performing snapshot.
"""
import math
from collections import Counter, defaultdict
from .history import aware


def probability(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 < value < 1


def wilson(wins, total):
    if not total:
        return None
    z = 1.959963984540054
    p = wins / total
    denominator = 1 + z*z/total
    center = (p + z*z/(2*total)) / denominator
    radius = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denominator
    return [max(0., center-radius), min(1., center+radius)]


def evaluate(records, outcomes, now):
    from .production import metrics
    current = aware(now)
    first = {}
    conflicting = set()
    diagnostics = Counter()
    for row in records:
        try:
            predicted, start = aware(row['predicted_at']), aware(row['starts_at'])
            if predicted > current:
                diagnostics['future_forecasts'] += 1
                continue
            if predicted >= start or not probability(row['home_probability']):
                raise ValueError('invalid forecast')
            prefix, day, away, home = row['id'].split(':')
            if home == away or prefix.upper() not in ('NBA', 'NFL'):
                raise ValueError('invalid game')
            for candidate in [None] + ([row['research_model']] if row.get('research_model') else []):
                if candidate is None:
                    forecast = row
                else:
                    # Research inference inherits the original observation time,
                    # game and frozen benchmark, never a later replacement.
                    forecast = {**row, **candidate}
                if not probability(forecast['home_probability']):
                    diagnostics['invalid_candidates'] += 1
                    continue
                identity = forecast.get('model_identity_hash', forecast['artifact_hash'])
                key = (row['id'], identity)
                previous = first.get(key)
                if previous is None or predicted < aware(previous['predicted_at']):
                    first[key] = forecast
                    conflicting.discard(key)
                # Equal instants with conflicting probabilities are not silently
                # resolved by SQLite row order.
                elif predicted == aware(previous['predicted_at']) and forecast['home_probability'] != previous['home_probability']:
                    diagnostics['conflicting_same_time_forecasts'] += 1
                    conflicting.add(key)
        except (KeyError, ValueError, TypeError):
            diagnostics['invalid_forecasts'] += 1

    available = defaultdict(list)
    for outcome in outcomes:
        try:
            if aware(outcome['observed_at']) > current:
                diagnostics['future_outcomes'] += 1
                continue
            hs, aws = outcome['home_score'], outcome['away_score']
            if any(type(score) is not int or score < 0 for score in (hs, aws)):
                raise ValueError('invalid scores')
            _, _, away, home = outcome['id'].split(':')
            if outcome.get('home', home) != home or outcome.get('away', away) != away:
                raise ValueError('wrong teams')
            if outcome.get('starts_at') and aware(outcome['starts_at']) > aware(outcome['observed_at']):
                raise ValueError('outcome before start')
            available[outcome['id']].append(outcome)
        except (KeyError, ValueError, TypeError):
            diagnostics['invalid_outcomes'] += 1

    groups = defaultdict(list)
    for forecast in first.values():
        confirmations = available.get(forecast['id'], [])
        signatures = {(r['home_score'], r['away_score']) for r in confirmations}
        outcome = 'pending'
        identity = forecast.get('model_identity_hash', forecast['artifact_hash'])
        if (forecast['id'], identity) in conflicting:
            diagnostics['unscored_conflicting_forecasts'] += 1
        elif len(signatures) > 1:
            diagnostics['conflicting_result_forecasts'] += 1
        elif confirmations:
            matches = [r for r in confirmations
                       if aware(forecast['starts_at']) <= aware(r['observed_at'])
                       and aware(forecast['starts_at']) <= current
                       and (not r.get('starts_at') or aware(r['starts_at']) == aware(forecast['starts_at']))]
            if matches:
                hs, aws = next(iter(signatures))
                outcome = 'void' if hs == aws else 'win' if hs > aws else 'loss'
            else:
                diagnostics['unmatched_final_timing_forecasts'] += 1
        key = forecast['model_version'] + ':' + identity[:12]
        groups[key].append({'probability': forecast['home_probability'], 'outcome': outcome,
                            'game_id': forecast['id'], 'starts_at': forecast['starts_at'],
                            'league': forecast.get('league', forecast['id'].split(':')[0].upper()),
                            'baseline_probability': forecast.get('baseline_elo_probability'),
                            'baseline_kind': forecast.get('baseline_elo_kind', 'legacy_fixed_elo')})

    def summary(rows):
        result = metrics(rows)
        result.update({'forecasts': len(rows), 'pending': sum(r['outcome'] == 'pending' for r in rows),
                       'void': sum(r['outcome'] == 'void' for r in rows),
                       'accuracy_interval_95': wilson(result['wins'], result['sample_size']),
                       'accuracy_interval_method': 'Wilson; descriptive, game dependence not adjusted',
                       'first_start': min((r['starts_at'] for r in rows), default=None),
                       'last_start': max((r['starts_at'] for r in rows), default=None)})
        return result

    def model_summary(rows):
        matched = [r for r in rows if probability(r['baseline_probability']) and r['baseline_kind'] == 'production_incumbent']
        legacy = [r for r in rows if probability(r['baseline_probability']) and r['baseline_kind'] != 'production_incumbent']
        baseline = summary([{**r, 'probability': r['baseline_probability']} for r in matched])
        candidate = summary(matched)
        settled = [r for r in matched if r['outcome'] in ('win', 'loss')]
        return {**summary(rows), 'matched_candidate': candidate, 'matched_elo': baseline,
                'matched_elo_kind': 'production_incumbent',
                'legacy_fixed_elo': summary([{**r, 'probability': r['baseline_probability']} for r in legacy]),
                'unmatched_incumbent_forecasts': len(rows)-len(matched),
                'paired_brier_difference': candidate['brier']-baseline['brier'] if settled else None,
                'paired_log_loss_difference': candidate['log_loss']-baseline['log_loss'] if settled else None,
                'home_team_baseline': {'sample_size': len(settled),
                    'accuracy': sum(r['outcome']=='win' for r in settled)/len(settled) if settled else None,
                    'probability_metrics': None, 'reason': 'always-home winner rule has no fitted probability'},
                'leagues': {league: summary([r for r in rows if r['league'] == league])
                            for league in ('NBA', 'NFL')}}

    return {'policy': 'first pregame forecast per game/model identity; timestamps compared as instants',
            'mode': 'forward_paper_forecasts', 'evaluated_at': now,
            'models': {key: model_summary(rows) for key, rows in groups.items()},
            'diagnostics': dict(diagnostics), 'snapshots': len(records),
            'paper_roi': None, 'closing_line_value': None, 'maximum_drawdown': None,
            'wager_metrics_reason': 'no qualified frozen priced recommendations yet',
            'market_benchmark_reason': 'no verified contemporaneous market probabilities in this forecast ledger'}
