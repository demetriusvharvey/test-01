import unittest
from scripts.research_nba_lineups import training_cohort,known,vocabulary


class StintTrainingTests(unittest.TestCase):
    def test_low_sample_players_are_nuisance_controls_not_zero_or_recursive_deletion(self):
        rows=[{'seconds':60.,'home_players':['1','2','3','4','5'],'away_players':['11','12','13','14','15']},
              {'seconds':60.,'home_players':['6','2','3','4','5'],'away_players':['11','12','13','14','15']}]
        training,names,minutes=training_cohort(rows)
        self.assertEqual(len(training),2)
        self.assertIn('1',names);self.assertIn('6',names)
        self.assertEqual(minutes['1'],1.)
        supported,_=vocabulary(training)
        self.assertEqual(supported,[])
        self.assertEqual(known(rows,supported),[])
