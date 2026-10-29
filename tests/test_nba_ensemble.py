import math
import unittest
from datetime import date,timedelta
from scripts.line_lab.nba_ensemble import mix,walk_forward,conditional_ensemble,COMPONENTS


class EnsembleTests(unittest.TestCase):
    def test_probability_math_and_missing_components_fail_closed(self):
        weights={'elo':.5,'team':.5,'rotation':0.,'multi_stat':0.}
        self.assertAlmostEqual(mix(weights,{'elo':.6,'team':.8}),.7)
        with self.assertRaises(ValueError):mix({**weights,'elo':math.nan},{'elo':.6,'team':.8})
        with self.assertRaises(ValueError):mix({**weights,'elo':.9},{'elo':.6,'team':.8})
        with self.assertRaises(KeyError):mix(weights,{'elo':.6})

    def test_weights_only_use_earlier_seasons_and_are_reproducible(self):
        rows=[]
        for season,year in (('2024-25',2024),('2025-26',2025)):
            for i in range(8):
                y=i%2
                rows.append({'game_id':f'{season}:{i}','date':(date(year,10,1)+timedelta(days=i)).isoformat(),
                             'season':season,'home_win':y,'probabilities':dict(zip(COMPONENTS,(.9 if y else .1,.5,.5,.5)))})
        first=walk_forward(rows,min_games=8,min_days=8)
        self.assertEqual(first[0]['model']['weights']['elo'],1.)
        self.assertEqual(first,walk_forward(rows,min_games=8,min_days=8))
        for r in rows[8:]:r['home_win']=1-r['home_win']
        second=walk_forward(rows,min_games=8,min_days=8)
        self.assertEqual(first[0]['model'],second[0]['model'])
        self.assertGreater(second[0]['ensemble']['log_loss'],first[0]['ensemble']['log_loss'])
        with self.assertRaises(ValueError):walk_forward(rows+[rows[0]],8,8)

    def test_scenarios_aligned_and_team_only_not_called_injury_adjusted(self):
        now='2026-10-29T12:00:00+00:00';event={'home':'ATL','away':'CLE'}
        model={'model_version':'nba-convex-ensemble-v1','promoted':False,'exported_at':'2026-10-29T11:00:00+00:00',
               'weights':{'elo':.5,'team':0.,'rotation':.5,'multi_stat':0.}}
        context={'status':'conditional_research_only','exhaustive_listed_uncertainty':True,
                 'injury_observed_at':now,'uncertain_players':1,'model_hash':'hash','model_version':'nba-rotation-logistic-v1',
                 'scenarios':[{'scenario':str(i),'home_probability':p,'away_probability':1-p} for i,p in enumerate((.4,.8))]}
        result=conditional_ensemble(model,.6,.6,context,None,event,now)
        self.assertEqual(result['home_scenario_range'],[.5,.7])
        self.assertIsNone(result['consistent_winner'])
        self.assertTrue(result['injury_components_used'])
        self.assertEqual(conditional_ensemble(model,.6,.6,None,None,event,now)['status'],'ensemble_component_unavailable')
        model['weights']={'elo':1.,'team':0.,'rotation':0.,'multi_stat':0.}
        result=conditional_ensemble(model,.6,.6,None,None,event,now)
        self.assertEqual(result['status'],'team_only_ensemble')
        self.assertFalse(result['injury_components_used'])
