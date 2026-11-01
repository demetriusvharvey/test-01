import copy
import unittest
from scripts.line_lab.readiness import summarize
from scripts.line_lab.history import aware
from scripts.line_lab.market import build_market
from tests import test_production_forecast as fixtures
from scripts.line_lab.production import decision

NOW = fixtures.NOW


class ReadinessTests(unittest.TestCase):
    def game(self, reasons, start='2026-10-31T23:00:00Z'):
        return {'starts_at': start, 'forecast': {'decision': {'eligible': not reasons, 'reasons': reasons}}}

    def test_prerequisite_failures_are_not_reported_as_no_edge(self):
        games = [self.game(['validation_insufficient', 'odds_missing_stale_or_unverified'])]
        r = summarize(games, NOW)
        self.assertEqual(r['status'], 'validation_pending')
        self.assertTrue(r['data_pending'])
        self.assertEqual(r['recommendations'], 0)
        self.assertEqual(summarize([self.game(['positive_edge_not_established'])], NOW)['status'], 'no_qualified_edge')
        self.assertEqual(summarize([self.game(['odds_missing_stale_or_unverified'])], NOW)['status'], 'data_unavailable')

    def test_only_remaining_et_day_counts_and_original_is_preserved(self):
        games = [self.game(['validation_insufficient']), self.game([], '2026-11-01T05:00:00Z'),
                 self.game([], NOW), {'starts_at': 'bad'}, {'starts_at': '2026-10-31T23:15:00Z'}]
        old = copy.deepcopy(games)
        r = summarize(games, NOW)
        self.assertEqual((r['scheduled_games'], r['forecasts'], r['missing_forecasts']), (2, 1, 1))
        self.assertEqual(games, old)
        self.assertEqual(summarize([], NOW)['status'], 'no_upcoming_games')

    def test_newer_price_wins_in_either_source_order_and_future_is_rejected(self):
        base = {'id': 'nba:2026-10-31:BOS:NYK', 'league': 'NBA', 'home': 'NYK', 'away': 'BOS',
                'home_name': 'Knicks', 'away_name': 'Celtics', 'starts_at': '2026-10-31T23:00:00Z',
                'book': 'FanDuel', 'home_odds': -150, 'away_odds': 130}
        old = dict(base, as_of='2026-10-31T17:00:00Z')
        fresh = dict(base, as_of=NOW, home_odds=-140)
        for rows in ([old, fresh], [fresh, old]):
            b = build_market(rows, aware(NOW))
            self.assertEqual(b[base['id']]['books']['FanDuel']['home'], -140)
        self.assertEqual(build_market([dict(base, as_of='2026-10-31T19:00:00Z')], aware(NOW)), {})

    def test_approved_decision_expires_at_earliest_input(self):
        fixture = fixtures.ProductionDecisionTests(); fixture.setUp()
        fixture.event['books']['FanDuel']['as_of'] = '2026-10-31T17:51:00Z'
        fixture.f['availability']['observed_at'] = '2026-10-31T17:45:00Z'
        r = decision(fixture.f, fixture.event, NOW, fixture.v)
        self.assertTrue(r['eligible'])
        self.assertEqual(aware(r['expires_at']), aware('2026-10-31T18:05:00Z'))
        fixture.f['availability']['observed_at'] = NOW
        r = decision(fixture.f, fixture.event, NOW, fixture.v)
        self.assertEqual(aware(r['expires_at']), aware('2026-10-31T18:11:00Z'))
