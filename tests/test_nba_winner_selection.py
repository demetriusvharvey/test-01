import math
import unittest
from datetime import date,timedelta
from scripts.line_lab.nba_winner_selection import rank_winners,compare_historical,selection_metrics,MODELS


class WinnerSelectionTests(unittest.TestCase):
    def fixture(self,days=30):
        games=[];records=[]
        for day in range(days):
            d=date(2025,1,1)+timedelta(days=day)
            for i in range(4):
                y=int(i in (0,2));game=f'{day}-{i}'
                games.append({'id':game,'league':'NBA','date':d,'season':'2024-25','home':f'H{i}','away':f'A{i}',
                              'home_score':110 if y else 100,'away_score':100 if y else 110})
                records.append({'game_id':game,'date':d.isoformat(),'season':'2024-25','home_win':y,
                                'probabilities':{'elo':(.9,.8,.7,.6)[i],'team14':(.9,.8,.7,.6)[i],
                                                 'player27':(.8,.05,.6,.1)[i],'lineup30':.51}})
        return records,games

    def test_complete_slates_and_matched_selected_results(self):
        rows,games=self.fixture();results=compare_historical(rows,games)[0]
        self.assertEqual(results['complete_days'],30)
        self.assertEqual(results['models']['elo']['primary']['games'],90)
        self.assertAlmostEqual(results['models']['elo']['primary']['accuracy'],2/3)
        self.assertEqual(results['models']['player27']['primary']['accuracy'],1.)
        self.assertEqual(results,compare_historical(rows,games)[0])
        missing=compare_historical(rows[1:],games)[0]
        self.assertEqual(missing['excluded_incomplete_days'],1)
        self.assertEqual(missing['models']['elo']['primary']['games'],87)

    def test_ties_thresholds_small_samples_and_invalid_data(self):
        row={'game_id':'g','home':'H','away':'A','home_probability':.5}
        self.assertEqual(rank_winners([row]),[])
        self.assertEqual(rank_winners([{**row,'home_probability':.6}],.8),[])
        self.assertIsNone(selection_metrics([])['accuracy'])
        with self.assertRaises(ValueError):rank_winners([{**row,'home_probability':math.nan}])
        rows,games=self.fixture(2);result=compare_historical(rows,games)[0]
        self.assertIsNone(result['models']['elo']['accuracy_interval'])
        with self.assertRaises(ValueError):compare_historical(rows+[rows[0]],games)
