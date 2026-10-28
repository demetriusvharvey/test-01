import copy
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from scripts.line_lab.constants import BOOKS
from scripts.line_lab.history import append_observations, finalize_closing_proxies
from scripts.line_lab.ledger import grade_ledger
from scripts.line_lab.ledger_v2 import attach_retail_closing_proxies, paper_breakdowns, snapshot_hash, validate_transition
from scripts.line_lab.market import choose_candidates
from scripts.line_lab.reproducibility import reproduce_pure_elo_v1,verify_paper_pick,attach_prediction_checks


class LedgerV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = datetime(2026, 10, 28, 1, 30, tzinfo=timezone.utc)
        self.event = {'id': 'nba:2026-10-27:POR:LAL', 'league': 'NBA', 'home': 'LAL', 'away': 'POR',
                      'home_name': 'Lakers', 'away_name': 'Portland',
                      'starts_at': (self.now + timedelta(hours=2)).isoformat(), 'books': {}}
        for i, (_, name) in enumerate(BOOKS[:4]):
            self.event['books'][name] = {'home': -105 if i == 2 else -110, 'away': -110, 'as_of': self.now.isoformat()}
        self.model = {'ratings': {'LAL': 1800, 'POR': 1300}, 'last': {'LAL': date(2026, 10, 25), 'POR': date(2026, 10, 23)},
                      'margins': {}, 'home_advantage': 55, 'rest_weight': 0, 'form_weight': 0}
        self.pick = choose_candidates({self.event['id']: self.event}, {'NBA': self.model}, self.now, [])[0]

    def tearDown(self):
        self.tmp.cleanup()

    def test_records_quote_not_a_real_bet_and_hashes_reproducible_features(self):
        pick = self.pick
        self.assertEqual(pick['ledger_version'], 2)
        self.assertEqual(pick['recommended_book'], 'BetMGM')
        self.assertEqual(pick['observed_price'], -105)
        self.assertIsNone(pick['price_taken'])
        self.assertIsNone(pick['book_taken'])
        self.assertIsNone(pick['stake_units'])
        self.assertIsNone(pick['units_pnl'])
        self.assertEqual(pick['paper_stake_units'], 1)
        self.assertEqual(pick['feature_snapshot_hash'], snapshot_hash(pick['feature_snapshot']))
        self.assertEqual(pick['anchor_source'], 'retail_median_not_sharp')
        self.assertIsNone(pick['clv_vs_sharp'])
        self.assertFalse(pick['staking_allowed'])
        self.assertEqual(verify_paper_pick(pick),'verified')
        self.assertAlmostEqual(reproduce_pure_elo_v1(pick['feature_snapshot'],'home'),pick['model_only_probability'])

    def test_tampered_frozen_features_hide_a_new_active_pick(self):
        pick=copy.deepcopy(self.pick);pick['feature_snapshot']['home_rating']+=10
        self.assertEqual(verify_paper_pick(pick),'hash_mismatch')
        board={'picks':[{'id':pick['id']}],'errors':[]};attach_prediction_checks(board,[pick])
        self.assertEqual(board['picks'],[]);self.assertTrue(board['errors'])

    def test_grade_and_append_only_transition(self):
        original = copy.deepcopy(self.pick)
        final = {'id': self.event['id'], 'home': 'LAL', 'away': 'POR', 'home_score': 120, 'away_score': 100}
        self.assertEqual(grade_ledger([self.pick], [final], self.now), 0)  # no early grade
        self.assertEqual(grade_ledger([self.pick], [final], self.now + timedelta(hours=4)), 1)
        self.assertAlmostEqual(self.pick['paper_units_pnl'], 100 / 105, places=5)
        self.assertIsNone(self.pick['units_pnl'])
        self.assertTrue(validate_transition([original], [self.pick]))
        changed = copy.deepcopy(self.pick); changed['probability'] = .999
        with self.assertRaises(ValueError): validate_transition([original], [changed])
        changed = copy.deepcopy(self.pick); changed['paper_units_pnl'] = 50
        with self.assertRaises(ValueError): validate_transition([self.pick], [changed])
        with self.assertRaises(ValueError): validate_transition([original], [])

    def test_wrong_team_cannot_be_graded(self):
        bad = {'id': self.event['id'], 'home': 'NYK', 'away': 'POR', 'home_score': 90, 'away_score': 95}
        self.assertEqual(grade_ledger([self.pick], [bad], self.now + timedelta(hours=4)), 0)
        self.assertEqual(self.pick['outcome'], 'pending')

    def test_closing_proxy_is_same_book_pregame_and_never_sharp(self):
        quote = {'id': self.event['id'], 'provider': 'agentbets', 'provider_event_id': 'x', 'league': 'NBA',
                 'home': 'LAL', 'away': 'POR', 'book': 'BetMGM', 'home_odds': -115, 'away_odds': -105,
                 'as_of': (self.now + timedelta(hours=1)).isoformat(),
                 'fetched_at': (self.now + timedelta(hours=1)).isoformat(), 'starts_at': self.event['starts_at']}
        self.assertEqual(append_observations(self.root, [quote], quote['fetched_at']), 1)
        after = (self.now + timedelta(hours=3)).isoformat()
        self.assertEqual(finalize_closing_proxies(self.root, after, {quote['id']: quote['starts_at']}), 1)
        before = copy.deepcopy(self.pick)
        self.assertEqual(attach_retail_closing_proxies(self.root, [self.pick]), 1)
        self.assertEqual(self.pick['closing_odds'], -115)
        self.assertEqual(self.pick['closing_label'], 'last_observed_pregame_not_certified_close')
        self.assertGreater(self.pick['retail_proxy_clv'], 0)
        self.assertIsNone(self.pick['clv_vs_sharp'])
        self.assertTrue(validate_transition([before], [self.pick]))
        self.assertEqual(attach_retail_closing_proxies(self.root, [self.pick]), 0)

    def test_breakdowns_exclude_legacy_and_real_money(self):
        final = {'id': self.event['id'], 'home': 'LAL', 'away': 'POR', 'home_score': 90, 'away_score': 100}
        grade_ledger([self.pick], [final], self.now + timedelta(hours=4))
        rows = [self.pick, {'league': 'NBA', 'outcome': 'win', 'initial_best_odds': 100}]
        report = paper_breakdowns(rows)
        self.assertEqual(report['league']['NBA']['settled'], 1)
        self.assertEqual(report['league']['NBA']['paper_roi'], -1)
        self.assertIsNone(report['league']['NBA']['sharp_clv'])
        self.assertIsNone(report['league']['NBA']['paper_roi_interval'])


if __name__ == '__main__':
    unittest.main()
