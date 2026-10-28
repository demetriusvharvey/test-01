import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from scripts.line_lab.trust import record_candidates, quarter_kelly_paper, paper_exposure, simulate_paper_paths


class TrustTests(unittest.TestCase):
    def test_candidates_are_immutable_include_both_sides_and_skips(self):
        now='2026-10-28T20:00:00+00:00'
        event={'id':'NBA-1','league':'NBA','home':'A','away':'B',
               'starts_at':'2026-10-28T22:00:00+00:00',
               'books':{'one':{'home':-120,'away':105},'two':{'home':-125,'away':110},
                        'three':{'home':-130,'away':108}}}
        with tempfile.TemporaryDirectory() as root, patch('scripts.line_lab.trust.project_home',return_value=.6):
            chosen=[{'id':'NBA-1','team_code':'A'}]
            self.assertEqual(record_candidates(root,{'NBA-1':event},{'NBA':{'x':1}},now,[],chosen),2)
            self.assertEqual(record_candidates(root,{'NBA-1':event},{'NBA':{'x':1}},now,[],chosen),0)
            dbpath=Path(root)/'observations/candidates/2026-10-28.sqlite'
            with closing(sqlite3.connect(dbpath)) as db:
                rows=db.execute('SELECT side,decision,trust_probability,timing FROM candidates ORDER BY side').fetchall()
                self.assertEqual(rows,[('away','below_paper_threshold',None,'unknown'),('home','selected_paper',None,'unknown')])
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute("UPDATE candidates SET decision='selected_paper'")

    def test_kelly_is_only_available_for_an_explicitly_calibrated_scenario(self):
        self.assertIsNone(quarter_kelly_paper(.6,100))
        self.assertEqual(quarter_kelly_paper(.6,100,True,.01),.01)
        self.assertEqual(quarter_kelly_paper(.4,100,True,.01),0)
        with self.assertRaises(ValueError):quarter_kelly_paper(1.1,100,True)

    def test_exposure_and_seeded_simulation_are_paper_scenarios(self):
        old=[{'units':1,'same_group':True},{'units':2,'same_group':False}]
        self.assertEqual(paper_exposure(2,old,5,2,0,10),1)
        self.assertEqual(paper_exposure(2,old,5,2,10,10),0)
        self.assertEqual(simulate_paper_paths(.5,100,.1,5,50,3),simulate_paper_paths(.5,100,.1,5,50,3))
        self.assertIn('hypothetical',simulate_paper_paths(.5,100,.1,5,50,3)['assumption'])


if __name__=='__main__':unittest.main()
