import tempfile
import unittest
from unittest.mock import patch
from scripts.line_lab.nba_refresh import refresh_current_sources,roster_observed_at


class NBARefreshTests(unittest.TestCase):
    def test_successful_checks_cached_and_same_content_reobserved(self):
        with tempfile.TemporaryDirectory() as root:
            def archive(root,specs,fetch):
                return [{'sha256':'same-content'}],[]
            with patch('scripts.line_lab.nba_refresh.fetch_and_archive',side_effect=archive) as ingest:
                result=refresh_current_sources(root,'2026-10-29T12:00:00+00:00')
                self.assertEqual([r['status'] for r in result],['refreshed']*3)
                self.assertEqual(ingest.call_count,3)
                self.assertEqual([r['status'] for r in refresh_current_sources(root,'2026-10-29T13:00:00+00:00')],['cached']*3)
                self.assertEqual(ingest.call_count,3)
                refresh_current_sources(root,'2026-10-30T01:00:00+00:00')
                self.assertEqual(ingest.call_count,6)
            source='https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_rosters/rosters_2027.csv'
            self.assertEqual(roster_observed_at(root,source,'same-content','old'),'2026-10-30T01:00:00+00:00')
            self.assertEqual(roster_observed_at(root,source,'different-content','old'),'old')

    def test_failures_back_off_without_freshening_roster(self):
        with tempfile.TemporaryDirectory() as root:
            with patch('scripts.line_lab.nba_refresh.fetch_and_archive',return_value=([],[{'error':'OSError'}])) as ingest:
                self.assertEqual([r['status'] for r in refresh_current_sources(root,'2026-10-29T12:00:00+00:00')],['unavailable']*3)
                self.assertEqual([r['status'] for r in refresh_current_sources(root,'2026-10-29T13:00:00+00:00')],['retry_backoff']*3)
                self.assertEqual(ingest.call_count,3)
                refresh_current_sources(root,'2026-10-29T16:00:00+00:00')
                self.assertEqual(ingest.call_count,6)
            source='https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_rosters/rosters_2027.csv'
            self.assertEqual(roster_observed_at(root,source,'hash','old'),'old')

    def test_bad_source_data_has_bounded_retries_and_is_not_archived(self):
        with tempfile.TemporaryDirectory() as root:
            calls=[]
            def fetch(url):
                calls.append(url)
                return b'wrong,columns\n1,2\n',None,None
            result=refresh_current_sources(root,'2026-10-29T12:00:00+00:00',fetch)
            self.assertEqual(len(calls),6)
            self.assertEqual([r['status'] for r in result],['unavailable']*3)
