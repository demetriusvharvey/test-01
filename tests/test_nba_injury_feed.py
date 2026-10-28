import io
import json
import unittest
from unittest.mock import Mock

from scripts.line_lab.nba_injury_feed import (
    attach_nba_summaries, fetch_nba_injuries, summarize_by_team,
)


class NbaInjuryFeedTests(unittest.TestCase):
    def setUp(self):
        self.now = '2026-10-28T18:00:00+00:00'
        self.payload = {'sport': 'basketball_nba', 'count': 4, 'players': [
            {'team_abbr': 'PHI', 'player_name': 'Player One', 'player_id': 'espn:1',
             'status_code': 'out', 'status_since': '2026-10-28T17:00:00Z'},
            {'team_abbr': 'IND', 'player_name': 'Player Two', 'player_id': 'espn:2',
             'status_code': 'questionable', 'source_updated_at': '2026-10-28T17:15:00Z'},
            {'team_abbr': 'IND', 'player_name': 'Player Three', 'player_id': 'espn:3',
             'status_code': 'out', 'source_updated_at': '2026-10-28T18:01:00Z'},
            {'team_abbr': 'IND', 'player_name': 'Player Four', 'player_id': 'espn:4',
             'status_code': 'doubtful', 'status_since': '2026-10-28T16:00:00Z'},
        ]}
        self.event = {'id': 'nba:test', 'league': 'NBA', 'away': 'PHI', 'home': 'IND',
                      'away_name': 'Philadelphia 76ers', 'home_name': 'Indiana Pacers',
                      'starts_at': '2026-10-28T23:00:00Z'}

    def test_disabled_connector_never_calls_provider_and_uses_header_when_enabled(self):
        opener = Mock()
        self.assertIsNone(fetch_nba_injuries('private-key', False, opener))
        self.assertIsNone(fetch_nba_injuries('', True, opener))
        opener.assert_not_called()
        opener.return_value = io.BytesIO(json.dumps(self.payload).encode())
        payload, stamp = fetch_nba_injuries('private-key', True, opener)
        request = opener.call_args.args[0]
        self.assertEqual(request.get_header('X-api-key'), 'private-key')
        self.assertNotIn('private-key', request.full_url)
        self.assertEqual(payload['count'], 4)
        self.assertTrue(stamp)

    def test_only_valid_point_in_time_counts_are_published(self):
        board = {'picks': [{'id': 'nba:test'}], 'watchlist': [{'id': 'nba:test'}]}
        attach_nba_summaries(board, {'nba:test': self.event}, self.payload, self.now)
        context = board['picks'][0]['nba_availability_context']
        self.assertEqual(context['teams']['away']['counts']['out'], 1)
        self.assertEqual(context['teams']['home']['counts']['questionable'], 1)
        self.assertEqual(context['teams']['home']['counts']['out'], 0)
        self.assertTrue(context['incomplete'])
        self.assertFalse(context['used_in_prediction'])
        self.assertEqual(context, board['watchlist'][0]['nba_availability_context'])
        self.assertNotIn('Player One', json.dumps(board))
        self.assertNotIn('espn:1', json.dumps(board))

    def test_conflicting_duplicates_and_postgame_context_are_rejected(self):
        duplicate = dict(self.payload['players'][0], status_code='questionable')
        self.payload['players'].append(duplicate)
        self.payload['count'] += 1
        summaries, incomplete = summarize_by_team(self.payload, self.now)
        self.assertEqual(summaries['PHI']['out'], 0)
        self.assertEqual(summaries['PHI']['questionable'], 0)
        self.assertTrue(incomplete)
        board = {'picks': [{'id': 'nba:test'}]}
        attach_nba_summaries(board, {'nba:test': self.event}, self.payload, '2026-10-28T23:00:00Z')
        self.assertNotIn('nba_availability_context', board['picks'][0])

    def test_malformed_or_partial_payload_does_not_imply_a_clean_report(self):
        self.payload['count'] = 200
        with self.assertRaises(ValueError):
            summarize_by_team(self.payload, self.now)
        with self.assertRaises(ValueError):
            summarize_by_team({'sport': 'football_nfl', 'players': [], 'count': 0}, self.now)


if __name__ == '__main__':
    unittest.main()
