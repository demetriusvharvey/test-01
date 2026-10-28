import gzip
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from scripts.refresh_nfl_shadow import refresh


class NflRefreshResilienceTests(unittest.TestCase):
    def test_injury_reports_survive_a_separate_play_by_play_outage(self):
        stamp='2026-10-28T12:00:00+00:00'
        csv=('season,week,team,gsis_id,position,full_name,report_status,practice_status,date_modified\n'
             '2026,8,BAL,00-1,QB,Example,Questionable,Limited,2026-10-28\n').encode()
        def fetcher(url):
            if '/pbp/' in url:raise OSError('source unavailable')
            if '/injuries/' in url:return gzip.compress(csv),stamp
            raise AssertionError(url)
        with tempfile.TemporaryDirectory() as root:
            result=refresh(root,datetime(2026,10,28,tzinfo=timezone.utc),fetcher)
            self.assertEqual(result,{'quarterbacks':False,'injuries':True})
            with closing(sqlite3.connect(Path(root)/'observations/nfl_availability/2026-10-28.sqlite')) as db:
                self.assertEqual(db.execute('SELECT report_status FROM injury_observations').fetchone()[0],'Questionable')


if __name__=='__main__':unittest.main()
