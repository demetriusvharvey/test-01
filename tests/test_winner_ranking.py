import unittest
from datetime import datetime, timedelta, timezone

from scripts.line_lab.constants import BOOKS
from scripts.line_lab.market import choose_candidates


class WinnerRankingTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 28, 17, 0, tzinfo=timezone.utc)
        self.model = {'ratings': {'A': 1800, 'B': 1300, 'C': 1600, 'D': 1400,
                                  'E': 1500, 'F': 1500},
                      'last': {}, 'margins': {}, 'home_advantage': 0,
                      'rest_weight': 0, 'form_weight': 0}

    def event(self, identifier, home, away, home_odds, away_odds):
        return {'id': identifier, 'league': 'NBA', 'home': home, 'away': away,
                'home_name': home, 'away_name': away,
                'starts_at': (self.now + timedelta(hours=5)).isoformat(),
                'books': {name: {'home': home_odds, 'away': away_odds,
                                 'as_of': self.now.isoformat()} for _, name in BOOKS[:3]}}

    def test_highest_win_probability_precedes_higher_estimated_return(self):
        stronger = self.event('game-a', 'A', 'B', -400, 1000)
        better_payout = self.event('game-b', 'C', 'D', -110, 500)
        tied = self.event('game-c', 'E', 'F', -110, 300)
        markets = {x['id']: x for x in (better_payout, tied, stronger)}
        picks = choose_candidates(markets, {'NBA': self.model}, self.now, [])
        self.assertEqual([p['id'] for p in picks], ['game-a', 'game-b'])
        self.assertGreater(picks[0]['probability'], picks[1]['probability'])
        self.assertLess(picks[0]['estimated_ev'], picks[1]['estimated_ev'])
        self.assertEqual([p['team_code'] for p in picks], ['A', 'C'])
        self.assertTrue(all(p['selection_rule'] == 'model-win-ranking-v1' for p in picks))

    def test_unqualified_prices_and_unfavored_sides_do_not_force_a_pick(self):
        overpriced = self.event('expensive', 'A', 'B', -10000, 1500)
        self.assertEqual(choose_candidates({'expensive': overpriced}, {'NBA': self.model}, self.now, []), [])

    def test_existing_predictions_remain_frozen_and_the_daily_cap_applies(self):
        events = [self.event(f'game-{n}', 'A', 'B', -200, 180) for n in range(4)]
        old = [{'id': 'earlier', 'pick_day': '2026-10-28'}]
        picks = choose_candidates({e['id']: e for e in events}, {'NBA': self.model}, self.now, old)
        self.assertEqual([p['id'] for p in picks], ['game-0', 'game-1'])
        self.assertEqual(old, [{'id': 'earlier', 'pick_day': '2026-10-28'}])


if __name__ == '__main__':
    unittest.main()
