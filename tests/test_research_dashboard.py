import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from scripts.line_lab.patterns import SCHEMA
from scripts.line_lab.research_dashboard import research_dashboard


class DashboardTests(unittest.TestCase):
    def test_empty_dashboard_does_not_invent_results(self):
        with tempfile.TemporaryDirectory() as root:
            result=research_dashboard(root,'2026-10-28T12:00:00+00:00')
        self.assertEqual(result['patterns'],[]);self.assertEqual(result['paper_replay'],{})
    def test_latest_prior_run_is_selected_and_future_run_is_excluded(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'observations/pattern_tests/2026-10-28.sqlite';path.parent.mkdir(parents=True)
            with sqlite3.connect(path) as db:
                db.executescript(SCHEMA)
                for key,stamp,n in [('a','2026-10-28T10:00:00+00:00',3),('b','2026-10-28T13:00:00+00:00',10)]:
                    db.execute('INSERT INTO pattern_runs VALUES (?,?,?,?,?,?)',(key,stamp,'hash','H010a','NBA',json.dumps({'id':'H010a','league':'NBA','games':n})))
            result=research_dashboard(root,'2026-10-28T12:00:00+00:00')
            self.assertEqual(result['patterns'][0]['games'],3)


if __name__=='__main__':unittest.main()
