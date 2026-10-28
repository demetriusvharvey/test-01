"""Append-only candidate audit and explicitly hypothetical paper-risk tools."""
import hashlib
import json
import math
import random
import sqlite3
from contextlib import closing
from datetime import timedelta
from pathlib import Path

from .constants import ET
from .history import aware
from .market import decimal_odds, implied
from .model import project_home

SCHEMA = '''
CREATE TABLE IF NOT EXISTS candidates (
 candidate_key TEXT PRIMARY KEY, game_id TEXT NOT NULL, league TEXT NOT NULL,
 side TEXT NOT NULL, captured_at TEXT NOT NULL, starts_at TEXT NOT NULL,
 model_probability REAL, book TEXT, price INTEGER, estimated_ev REAL,
 decision TEXT NOT NULL, trust_probability REAL, timing TEXT NOT NULL,
 detail_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS candidates_no_update BEFORE UPDATE ON candidates BEGIN SELECT RAISE(ABORT,'candidate history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS candidates_no_delete BEFORE DELETE ON candidates BEGIN SELECT RAISE(ABORT,'candidate history is append-only'); END;
'''


def record_candidates(root, markets, models, now, old_ledger, chosen):
    """Record both sides including skips; this audit never changes decisions."""
    captured = aware(now)
    path = Path(root) / 'observations' / 'candidates' / (captured.date().isoformat() + '.sqlite')
    path.parent.mkdir(parents=True, exist_ok=True)
    old = {p['id'] for p in old_ledger}
    picked = {(p['id'], p['team_code']) for p in chosen}
    added = 0
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript(SCHEMA)
        for event in markets.values():
            start = aware(event['starts_at'])
            if start <= captured:
                continue
            model = models.get(event['league'])
            home_p = project_home(model, event['home'], event['away'], start, event.get('neutral', False)) if model else None
            for side in ('home', 'away'):
                p = (home_p if side == 'home' else 1-home_p) if home_p is not None else None
                books = event.get('books', {})
                eligible_books = [(name, quote[side]) for name, quote in books.items()
                                  if isinstance(quote.get(side), int) and abs(quote[side]) >= 100]
                name, price = max(eligible_books, key=lambda x: x[1]) if eligible_books else (None, None)
                ev = p * decimal_odds(price) - 1 if p is not None and price is not None else None
                if (event['id'], event[side]) in picked:
                    decision = 'selected_paper'
                elif event['id'] in old:
                    decision = 'already_recorded'
                elif start.astimezone(ET).date() != captured.astimezone(ET).date():
                    decision = 'different_day'
                elif start <= captured + timedelta(minutes=20):
                    decision = 'too_near_start'
                elif len(books) < 3 or p is None or price is None:
                    decision = 'insufficient_inputs'
                elif p <= .5:
                    decision = 'other_side_favored_by_model'
                elif p - implied(price) < .01:
                    decision = 'below_paper_threshold'
                else:
                    decision = 'not_selected_by_win_ranking_or_cap'
                details = {'books': books, 'model_version': 'pure-elo-v1', 'team': event[side],
                           'research_only': True, 'real_wager_recorded': False,
                           'trust_reason': 'no qualified sharp-close training data',
                           'timing_reason': 'closing-line timing model not validated'}
                blob = json.dumps(details, sort_keys=True, separators=(',', ':'))
                identity = hashlib.sha256((event['id']+'|'+side+'|'+captured.isoformat()+'|'+blob).encode()).hexdigest()
                added += db.execute('INSERT OR IGNORE INTO candidates VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (identity,event['id'],event['league'],side,captured.isoformat(),start.isoformat(),
                     p,name,price,ev,decision,None,'unknown',blob)).rowcount
    return added


def quarter_kelly_paper(probability, odds, calibration_passed=False, per_bet_cap=.01):
    """Hypothetical fraction only after independent calibration; never a real order."""
    if not calibration_passed:
        return None
    if not 0 < probability < 1 or not isinstance(odds, int) or abs(odds) < 100:
        raise ValueError('invalid probability or odds')
    if not 0 <= per_bet_cap <= 1:
        raise ValueError('invalid cap')
    b = decimal_odds(odds)-1
    return min(per_bet_cap, max(0.0, .25 * (b*probability-(1-probability))/b))


def paper_exposure(proposed, existing, daily_cap, group_cap, drawdown, stop_drawdown):
    """Bound paper units, treating bets in the same group as correlated."""
    values = (proposed, daily_cap, group_cap, drawdown, stop_drawdown)
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('invalid paper exposure')
    if drawdown >= stop_drawdown:
        return 0.0
    total = sum(x['units'] for x in existing)
    group_total = sum(x['units'] for x in existing if x.get('same_group'))
    return max(0.0, min(proposed, daily_cap-total, group_cap-group_total))


def simulate_paper_paths(probability, odds, fraction, games, paths=1000, seed=0):
    """Sensitivity scenario with independent identical bets, not a forecast."""
    if not 0 < probability < 1 or not isinstance(odds, int) or abs(odds) < 100:
        raise ValueError('invalid scenario')
    if not 0 <= fraction <= 1 or not 1 <= games <= 10000 or not 1 <= paths <= 10000:
        raise ValueError('invalid simulation size or fraction')
    rng = random.Random(seed); endings = []; below_tenth = 0
    for _ in range(paths):
        wealth = 1.0
        for _ in range(games):
            wealth *= 1 + fraction*(decimal_odds(odds)-1) if rng.random() < probability else 1-fraction
        endings.append(wealth)
        below_tenth += wealth < .1
    endings.sort()
    return {'median_multiple': endings[len(endings)//2], 'fraction_below_tenth': below_tenth/paths,
            'assumption': 'identical independent bets at supplied probability; hypothetical only'}
