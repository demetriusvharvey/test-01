import unittest
from datetime import date,timedelta
from scripts.line_lab.nba_statistical import examples,evaluate_season


class NBAStatisticalTests(unittest.TestCase):
    def games(self):
        return [{'id':f'{year}-{i}','league':'NBA','season':str(year),'date':date(year,1,1)+timedelta(days=i),
                 'home':'A','away':'B','home_score':100+i%11,'away_score':98+i%13,'neutral':False}
                for year in (2022,2023,2024) for i in range(35)]
    def test_future_result_cannot_change_earlier_features(self):
        games=self.games();first=examples(games)
        games[-1]['home_score']=200;second=examples(games)
        self.assertEqual(first[:-1],second[:-1])
        self.assertEqual(first[-1]['vector'],second[-1]['vector'])
    def test_separate_training_calibration_and_test_seasons(self):
        result=evaluate_season(examples(self.games()),'2024',10,10)
        self.assertEqual(result['calibration_season'],'2023')
        self.assertEqual(result['artifact']['trained_through_season'],'2022')
        self.assertEqual(result['calibrated_logistic']['games'],result['elo']['games'])
        self.assertFalse(result['artifact']['promoted'])
