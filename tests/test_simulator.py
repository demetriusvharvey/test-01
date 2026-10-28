import unittest
from datetime import date
from scripts.line_lab.simulator import ScoreHistory, as_of_histories, backtest_scores, score_metrics


def game(league, day, i, h=110, a=103, season='2025-26'):
    return {'league':league,'id':f'{league}:{day}:{i}','date':day,'season':season,
            'home':'A','away':'B','home_score':h,'away_score':a,'neutral':False}


class ScoreSimulatorTests(unittest.TestCase):
    def setUp(self):
        self.games=[game('NBA',date(2025,1,1).fromordinal(date(2025,1,1).toordinal()+i),i,
                         h=105+i%23,a=98+i%21) for i in range(250)]

    def test_reproducible_scores_and_probabilities(self):
        hist=as_of_histories(self.games,date(2026,1,1))['NBA']
        a=hist.simulate('A','B',draws=5000,seed=44)
        self.assertEqual(a,hist.simulate('A','B',draws=5000,seed=44))
        self.assertEqual(a['home_wins']+a['away_wins']+a['ties'],5000)
        self.assertEqual(a['ties'],0)
        self.assertGreater(a['median_home_score'],a['median_away_score'])
        self.assertEqual(a['reference_games'],250)

    def test_no_same_day_or_future_scores(self):
        first=as_of_histories(self.games,date(2025,9,7))['NBA']
        injected=self.games+[game('NBA',date(2025,9,7),999,250,0)]
        self.assertEqual(first.simulate('A','B',draws=5000),
                         as_of_histories(injected,date(2025,9,7))['NBA'].simulate('A','B',draws=5000))

    def test_walk_forward_does_not_use_current_game(self):
        rows=backtest_scores(self.games,'NBA',draws=5000)
        changed=[dict(g) for g in self.games]
        changed[220]['home_score']=1;changed[220]['away_score']=240
        second=backtest_scores(changed,'NBA',draws=5000)
        self.assertEqual(rows[0]['probability'],second[0]['probability'])
        self.assertNotEqual(rows[-1]['probability'],second[-1]['probability'])
        self.assertEqual(score_metrics([])['games'],0)

    def test_nfl_ties_and_validity(self):
        hist=ScoreHistory('NFL')
        for i in range(90):hist.add(game('NFL',date(2025,1,1),i,21,21))
        result=hist.simulate('A','B',draws=5000)
        self.assertEqual(result['ties'],5000)
        self.assertEqual(result['home_probability'],.5)
        with self.assertRaises(ValueError):hist.simulate('A','B',draws=100)
        self.assertIsNone(ScoreHistory('NFL').simulate('A','B',draws=5000))


if __name__=='__main__':unittest.main()
