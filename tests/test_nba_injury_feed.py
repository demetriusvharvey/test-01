import io
import json
import unittest
from unittest.mock import Mock

from scripts.line_lab.nba_injury_feed import (
    attach_nba_summaries, attach_nfl_summaries, fetch_nba_injuries, fetch_nfl_injuries, summarize_by_team, summarize_positions_by_team, injury_quality_counts,
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

    def test_nfl_current_report_is_context_only_and_has_no_player_data(self):
        payload={'sport':'football_nfl','count':2,'players':[
            {'team_abbr':'KC','player_id':'espn:1','player_name':'Private One','position':'QB','status_code':'out','status_since':'2026-10-28T17:00:00Z'},
            {'team_abbr':'BUF','player_id':'espn:2','player_name':'Private Two','status_code':'questionable','status_since':'2026-10-28T17:00:00Z'}]}
        event={'id':'nfl:test','league':'NFL','away':'KC','home':'BUF','away_name':'Kansas City Chiefs','home_name':'Buffalo Bills','starts_at':'2026-10-28T23:00:00Z'}
        board={'picks':[{'id':'nfl:test'}]}
        attach_nfl_summaries(board,{'nfl:test':event},payload,self.now)
        context=board['picks'][0]['nfl_provider_availability_context']
        self.assertEqual(context['teams']['away']['counts']['out'],1)
        self.assertEqual(context['teams']['home']['counts']['questionable'],1)
        self.assertFalse(context['used_in_prediction']);self.assertFalse(context['incomplete'])
        self.assertNotIn('Private One',json.dumps(board));self.assertNotIn('espn:1',json.dumps(board))
        board={'picks':[{'id':'nfl:test'}]}
        attach_nfl_summaries(board,{'nfl:test':event},payload,'2026-10-28T23:00:00Z')
        self.assertNotIn('nfl_provider_availability_context',board['picks'][0])
        opener=Mock(return_value=io.BytesIO(json.dumps(payload).encode()))
        fetch_nfl_injuries('private-key',True,opener)
        self.assertTrue(opener.call_args.args[0].full_url.endswith('/football_nfl/injuries'))
        self.assertNotIn('private-key',opener.call_args.args[0].full_url)

    def test_all_nfl_positions_are_counted_and_missing_positions_remain_unknown(self):
        positions=['QB','RB','WR','TE','OT','G','C','DE','DT','LB','CB','S','K','P',None]
        payload={'sport':'football_nfl','count':len(positions),'players':[
            {'team_abbr':'KC','player_id':f'espn:{i}','position':position,'status_code':'out','status_since':'2026-10-28T17:00:00Z'}
            for i,position in enumerate(positions)]}
        result=summarize_positions_by_team(payload,self.now,'NFL')['KC']
        for position in positions:
            self.assertEqual(result[position or 'UNKNOWN']['out'],1)
        event={'id':'nfl:test','league':'NFL','away':'KC','home':'BUF','away_name':'Kansas City Chiefs','home_name':'Buffalo Bills','starts_at':'2026-10-28T23:00:00Z'}
        board={'picks':[{'id':'nfl:test'}]};attach_nfl_summaries(board,{'nfl:test':event},payload,self.now)
        self.assertEqual(board['picks'][0]['nfl_provider_availability_context']['teams']['away']['counts']['out'],len(positions))
        quality=injury_quality_counts(payload,self.now,'NFL')
        self.assertEqual(quality['missing_position'],1);self.assertEqual(quality['rows'],len(positions))
        self.assertNotIn('espn:',json.dumps(quality))

    def test_espn_team_codes_are_mapped_by_league_before_aggregating(self):
        nba={'sport':'basketball_nba','count':6,'players':[
            {'team_abbr':team,'player_id':f'espn:{i}','position':'G','status_code':'out','status_since':'2026-10-28T17:00:00Z'}
            for i,team in enumerate(['GS','NY','NO','SA','UTAH','WSH'])]}
        summaries,incomplete=summarize_by_team(nba,self.now,'NBA')
        self.assertFalse(incomplete)
        for team in ('GSW','NYK','NOP','SAS','UTA','WAS'):self.assertEqual(summaries[team]['out'],1)
        self.assertEqual(injury_quality_counts(nba,self.now,'NBA')['unknown_team'],0)
        nfl={'sport':'football_nfl','count':2,'players':[
            {'team_abbr':'NO','player_id':'espn:1','position':'WR','status_code':'out','status_since':'2026-10-28T17:00:00Z'},
            {'team_abbr':'WSH','player_id':'espn:2','position':'CB','status_code':'questionable','status_since':'2026-10-28T17:00:00Z'}]}
        summaries,incomplete=summarize_by_team(nfl,self.now,'NFL')
        self.assertFalse(incomplete);self.assertEqual(summaries['NO']['out'],1);self.assertEqual(summaries['WAS']['questionable'],1)
        self.assertEqual(injury_quality_counts(nfl,self.now,'NFL')['unknown_team'],0)


if __name__ == '__main__':
    unittest.main()
