import io
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import Mock
from scripts.line_lab.propline_scores import fetch_scores,fetch_events,parse_scores,parse_event_starts,restrict_public_results,use_provider,reserve_call


class PropLineScoreTests(unittest.TestCase):
    def setUp(self):
        self.now='2026-10-28T23:00:00+00:00'
        self.row={'id':'123','sport_key':'basketball_nba','home_team':'Indiana Pacers',
                  'away_team':'Philadelphia 76ers','commence_time':'2026-10-28T22:00:00Z',
                  'status':'in_progress','home_score':50,'away_score':45}

    def test_key_stays_in_the_header_and_out_of_the_url(self):
        opener=Mock(side_effect=lambda *args,**kwargs:io.BytesIO(json.dumps([self.row]).encode()))
        payload,observed=fetch_scores('private-key','NBA',opener)
        request=opener.call_args.args[0]
        self.assertEqual(request.get_header('X-api-key'),'private-key')
        self.assertNotIn('private-key',request.full_url)
        self.assertEqual(payload[0]['id'],'123');self.assertTrue(observed)
        fetch_events('private-key','NBA',opener)
        self.assertTrue(opener.call_args.args[0].full_url.endswith('/basketball_nba/events'))
        self.assertNotIn('private-key',opener.call_args.args[0].full_url)

    def test_adding_a_key_enables_the_source_and_explicit_opt_out_works(self):
        self.assertFalse(use_provider('',''))
        self.assertTrue(use_provider('private-key',''))
        self.assertFalse(use_provider('private-key','',injury_only=True))
        self.assertTrue(use_provider('private-key','true',injury_only=True))
        self.assertTrue(use_provider('','true'))  # enabled but missing key fails closed
        self.assertFalse(use_provider('private-key','false'))

    def test_daily_budget_counts_failures_without_storing_keys_or_payloads(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertTrue(reserve_call(root,'scores_nba',self.now,daily_limit=2))
            self.assertTrue(reserve_call(root,'injuries_nba',self.now,daily_limit=2))
            self.assertFalse(reserve_call(root,'scores_nfl',self.now,daily_limit=2))
            self.assertTrue(reserve_call(root,'scores_nfl','2026-10-29T00:00:00Z',daily_limit=2))
            path=Path(root)/'observations/propline_quota/2026-10-28.sqlite'
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM calls').fetchone()[0],2)
                with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM calls')

    def test_in_progress_postponed_expired_and_unknown_are_not_final(self):
        starts,finals,conflicts,blocked=parse_scores([self.row],'NBA',self.now)
        self.assertEqual(len(starts),1);self.assertEqual(finals,[]);self.assertEqual(conflicts,[])
        self.assertEqual(blocked,['nba:2026-10-28:PHI:IND'])
        for status in ('postponed','cancelled','expired','unrecognized'):
            self.assertEqual(parse_scores([{**self.row,'status':status}],'NBA',self.now)[:2],({},[]))
            self.assertEqual(parse_scores([{**self.row,'status':status}],'NBA',self.now)[3],['nba:2026-10-28:PHI:IND'])

    def test_only_complete_explicit_finals_count_and_duplicates_conflict(self):
        final={**self.row,'status':'final','home_score':110,'away_score':112}
        starts,finals,conflicts,blocked=parse_scores([final],'NBA',self.now)
        self.assertEqual(len(starts),1);self.assertEqual(finals[0]['source'],'PropLine scores')
        self.assertEqual(finals[0]['away'],'PHI');self.assertEqual(conflicts,[])
        changed={**final,'home_score':111}
        self.assertEqual(parse_scores([final,changed],'NBA',self.now)[2],['nba:2026-10-28:PHI:IND'])
        self.assertEqual(parse_scores([{**final,'commence_time':'2026-10-29T01:00:00Z'}],'NBA',self.now)[1],[])

    def test_upcoming_schedule_ignores_past_and_conflicting_events(self):
        event={**self.row,'commence_time':'2026-10-29T02:00:00Z'}
        event.pop('status')
        starts,conflicts=parse_event_starts([event,self.row],'NBA',self.now)
        self.assertEqual(len(starts),1);self.assertEqual(conflicts,[])
        changed={**event,'commence_time':'2026-10-29T03:00:00Z'}
        starts,conflicts=parse_event_starts([event,changed],'NBA',self.now)
        self.assertEqual(starts,{});self.assertEqual(len(conflicts),1)

    def test_public_history_keeps_only_selected_provider_results(self):
        rows=[{'id':'one','source':'PropLine scores'},{'id':'two','source':'PropLine scores'},
              {'id':'two','source':'nflverse'}]
        self.assertEqual(restrict_public_results(rows,{'one'}),[rows[0],rows[2]])


if __name__=='__main__':unittest.main()
