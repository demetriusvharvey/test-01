"""Frozen paper-pick provenance and explicitly labeled retail close proxies.

No field in this module represents a user's actual wager unless the user
supplies it. A recorded quote is not proof that a bet was available or placed.
"""
import hashlib
import json
import math
import random
import sqlite3
from collections import defaultdict
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from statistics import median

from .history import aware
from .feature_registry import FEATURE_REGISTRY_VERSION


MUTABLE_FIELDS = frozenset({
    'outcome', 'graded_at', 'final_score', 'paper_units_pnl',
    'closing_odds', 'closing_provider', 'closing_fetched_at', 'closing_as_of',
    'closing_label', 'closing_gap_seconds', 'retail_proxy_clv',
    'close_anchor_probability', 'clv_vs_sharp',
})


def _implied(american):
    if not isinstance(american, int) or isinstance(american, bool) or abs(american) < 100:
        raise ValueError('invalid American odds')
    return -american / (-american + 100) if american < 0 else 100 / (american + 100)


def _decimal(american):
    _implied(american)
    return 1 + 100 / -american if american < 0 else 1 + american / 100


def feature_snapshot(event, model):
    """Capture exactly the values currently consumed by project_home."""
    home, away = event['home'], event['away']
    return {
        'schema': FEATURE_REGISTRY_VERSION, 'model': 'pure-elo-v1',
        'home': home, 'away': away, 'starts_at': event['starts_at'],
        'home_rating': model['ratings'][home], 'away_rating': model['ratings'][away],
        'home_advantage': model['home_advantage'], 'neutral': event.get('neutral', False),
        'rest_weight': model['rest_weight'], 'form_weight': model.get('form_weight', 0),
        'home_last': str(model['last'].get(home)), 'away_last': str(model['last'].get(away)),
        'home_margins': list(model.get('margins', {}).get(home, [])),
        'away_margins': list(model.get('margins', {}).get(away, [])),
        'source_text_sha256': dict(model.get('source_hashes', {})),
    }


def snapshot_hash(snapshot):
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def initial_details(event, model, side, probability, books, predicted_at):
    """Build v2 fields without asserting that a real wager occurred."""
    available = [b for b in books if isinstance(b.get('odds'), int) and not isinstance(b.get('odds'), bool)]
    if not available:
        raise ValueError('no observed price')
    best = max(b['odds'] for b in available)
    chosen = next(b for b in available if b['odds'] == best)
    fair = []
    for quote in event['books'].values():
        try:
            h, a = _implied(quote['home']), _implied(quote['away'])
            fair.append((h if side == 'home' else a) / (h + a))
        except (KeyError, TypeError, ValueError):
            continue
    if not fair:
        raise ValueError('no two-sided market')
    reference = median(fair)
    features = feature_snapshot(event, model)
    return {
        'ledger_version': 2, 'pick_phase': 'early',
        'recommended_book': chosen['name'], 'observed_price': best,
        'observed_price_as_of': chosen.get('as_of'),
        'book_taken': None, 'price_taken': None, 'stake_units': None,
        'paper_stake_units': 1.0, 'units_pnl': None, 'paper_units_pnl': None,
        'anchor_source': 'retail_median_not_sharp', 'anchor_fair_probability': reference,
        'model_only_probability': probability, 'blend_weights': {'pure_model': 1.0, 'market': 0.0},
        'price_edge': reference - _implied(best), 'model_edge': probability - reference,
        'scenario_summary': 'unavailable', 'availability_snapshot_id': None,
        'trust_score': None, 'timing_recommendation': 'unavailable',
        'feature_snapshot': features, 'feature_snapshot_hash': snapshot_hash(features),
        'closing_odds': None, 'closing_provider': None, 'closing_fetched_at': None,
        'closing_as_of': None, 'closing_label': None, 'closing_gap_seconds': None,
        'retail_proxy_clv': None, 'close_anchor_probability': None, 'clv_vs_sharp': None,
    }


def validate_transition(before, after):
    """Existing predictions may only be graded once or given close fields once."""
    if len(after) < len(before):
        raise ValueError('ledger rows were removed')
    for old, new in zip(before, after):
        frozen_old = {k: v for k, v in old.items() if k not in MUTABLE_FIELDS}
        frozen_new = {k: v for k, v in new.items() if k not in MUTABLE_FIELDS}
        if frozen_old != frozen_new:
            raise ValueError('immutable prediction fields changed')
        for key in MUTABLE_FIELDS - {'outcome'}:
            if old.get(key) is not None and old.get(key) != new.get(key):
                raise ValueError('previous grade or close changed')
        previous, current = old.get('outcome'), new.get('outcome')
        if previous in ('win', 'loss', 'void') and current != previous:
            raise ValueError('previous outcome changed')
        if previous in (None, 'pending') and current not in (None, 'pending', 'win', 'loss', 'void'):
            raise ValueError('invalid outcome')
    return True


def attach_retail_closing_proxies(root, ledger):
    """Attach one same-book last-observed pregame proxy to v2 paper picks.

    A retail proxy is never a verified sharp close. Existing closing fields are
    not revised, even if the feed later revises its schedule or prices.
    """
    if not root:
        return 0
    changed = 0
    base = Path(root) / 'observations' / 'closes'
    for pick in ledger:
        if pick.get('ledger_version') != 2 or pick.get('closing_label'):
            continue
        try:
            start = aware(pick['starts_at'])
            book = pick['recommended_book']
            observed = pick['observed_price']
            side = 'home' if pick['team_code'] == pick['feature_snapshot']['home'] else 'away'
            if pick['team_code'] not in (pick['feature_snapshot']['home'], pick['feature_snapshot']['away']):
                continue
        except (KeyError, TypeError, ValueError):
            continue
        rows = []
        for delta in (-1, 0, 1):
            path = base / ((start + timedelta(days=delta)).date().isoformat() + '.sqlite')
            if not path.exists():
                continue
            with closing(sqlite3.connect(path)) as db:
                rows.extend(db.execute('SELECT provider,home_odds,away_odds,source_as_of,fetched_at,starts_at,observed_gap_seconds,label FROM closes WHERE game_id=? AND book=? AND market=?',
                                       (pick['id'], book, 'h2h')).fetchall())
        valid = []
        for row in rows:
            try:
                if row[7] != 'last_observed_pregame_not_certified_close':
                    continue
                if not (aware(row[3]) <= aware(row[4]) < min(start, aware(row[5]))):
                    continue
                if abs((aware(row[5]) - start).total_seconds()) > 20 * 60:
                    continue
                _decimal(row[1] if side == 'home' else row[2])
                valid.append(row)
            except (TypeError, ValueError):
                continue
        if not valid:
            continue
        row = max(valid, key=lambda item: aware(item[4]))
        close = row[1] if side == 'home' else row[2]
        pick.update({'closing_odds': close, 'closing_provider': row[0],
                     'closing_as_of': row[3], 'closing_fetched_at': row[4],
                     'closing_gap_seconds': row[6], 'closing_label': row[7],
                     'retail_proxy_clv': _decimal(observed) / _decimal(close) - 1})
        changed += 1
    return changed


def _interval(day_groups, iterations=2000):
    if len(day_groups) < 10 or sum(map(len, day_groups.values())) < 30:
        return None
    groups = list(day_groups.values()); rng = random.Random(20261028); draws = []
    for _ in range(iterations):
        values = [x for _ in groups for x in groups[rng.randrange(len(groups))]]
        draws.append(sum(values) / len(values))
    draws.sort()
    return [round(draws[int(.025 * (iterations - 1))], 4),
            round(draws[int(.975 * (iterations - 1))], 4)]


def paper_breakdowns(ledger):
    """Report only explicitly simulated v2 picks, never inferred user returns."""
    grouped = {key: defaultdict(list) for key in ('league', 'edge_type', 'edge_bucket', 'book', 'pick_phase')}
    for pick in ledger:
        value = pick.get('paper_units_pnl')
        if pick.get('ledger_version') != 2 or pick.get('outcome') not in ('win', 'loss', 'void') or not isinstance(value, (float, int)):
            continue
        edge = pick.get('model_edge')
        bucket = 'unknown' if not isinstance(edge, (float, int)) or not math.isfinite(edge) else 'negative' if edge < 0 else '0-4.9pp' if edge < .05 else '5pp+'
        labels = {'league': pick.get('league', 'unknown'), 'edge_type': 'pure_model',
                  'edge_bucket': bucket, 'book': pick.get('recommended_book', 'unknown'),
                  'pick_phase': pick.get('pick_phase', 'unknown')}
        for dimension, name in labels.items():
            grouped[dimension][name].append(pick)
    result = {}
    for dimension, groups in grouped.items():
        result[dimension] = {}
        for name, picks in groups.items():
            daily = defaultdict(list)
            for p in picks:
                daily[p.get('pick_day', 'unknown')].append(p['paper_units_pnl'])
            proxies = [p['retail_proxy_clv'] for p in picks if isinstance(p.get('retail_proxy_clv'), (int, float))]
            result[dimension][name] = {'settled': len(picks),
                'paper_roi': sum(p['paper_units_pnl'] for p in picks) / len(picks),
                'paper_roi_interval': _interval(daily), 'retail_proxy_clv_samples': len(proxies),
                'retail_proxy_clv': sum(proxies) / len(proxies) if proxies else None,
                'sharp_clv': None}
    return result
