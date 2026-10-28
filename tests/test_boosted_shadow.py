import unittest
import tempfile
from datetime import datetime,timedelta,timezone
from scripts.line_lab.boosted_shadow import fit_boosted_shadow,predict_boosted_shadow,explain_boosted
from scripts.line_lab.model_stack import append_trial,fit_elastic_net_shadow,latest_candidates,record_challenger_forecasts


class BoostedShadowTests(unittest.TestCase):
    def setUp(self):
        self.cutoff=datetime(2026,1,1,tzinfo=timezone.utc);self.rows=[]
        for year in (2023,2024,2025):
            for i in range(8):
                start=datetime(year,10,i+1,tzinfo=timezone.utc)
                self.rows.append({'game_id':f'{year}-{i}','league':'NFL','season':str(year),'rights_verified':True,
                    'feature_observed_at':(start-timedelta(hours=2)).isoformat(),'forecast_at':(start-timedelta(hours=1)).isoformat(),
                    'starts_at':start.isoformat(),'final_observed_at':(start+timedelta(hours=4)).isoformat(),
                    'home_win':i%2,'baseline_probability':.5,
                    'features':{'rating_difference':100 if i%2 else -100,'home_advantage':42,'games_played_difference':i}})
    def fit(self):
        return fit_boosted_shadow(self.rows,'NFL',self.cutoff.isoformat(),min_training=16,min_validation=8,min_seasons=3,min_leaf=2)
    def test_prior_only_fit_is_monotonic_and_explains_additive_terms(self):
        model=self.fit();self.assertEqual(model['validation_season'],'2025');self.assertEqual(model['inner_training_games'],16)
        self.assertFalse(model['promoted']);self.assertGreater(len(model['trees']),0)
        now=(self.cutoff+timedelta(days=1)).isoformat()
        low={'rating_difference':-200,'home_advantage':42,'games_played_difference':3}
        high={**low,'rating_difference':200}
        p1=predict_boosted_shadow(model,low,now,self.cutoff.isoformat())
        p2=predict_boosted_shadow(model,high,now,self.cutoff.isoformat())
        self.assertLessEqual(p1,p2)
        explanation=explain_boosted(model,high,now,self.cutoff.isoformat())
        self.assertIn('not SHAP',explanation['method']);self.assertAlmostEqual(explanation['probability'],p2)
        self.assertIsNone(predict_boosted_shadow(model,high,self.cutoff.isoformat(),self.cutoff.isoformat()))
    def test_future_outcomes_and_unregistered_features_are_rejected(self):
        self.rows[0]['final_observed_at']=(self.cutoff+timedelta(days=1)).isoformat()
        self.assertIsNone(self.fit())
        with self.assertRaises(ValueError):
            fit_boosted_shadow(self.rows,'NFL',self.cutoff.isoformat(),features=('market_probability',))
    def test_registry_and_future_logging_keep_both_challengers_separate(self):
        boost=self.fit();elastic=fit_elastic_net_shadow(self.rows,'NFL',self.cutoff.isoformat(),min_training=16,min_validation=8)
        now=self.cutoff+timedelta(days=1)
        with tempfile.TemporaryDirectory() as root:
            a=append_trial(root,'NFL',self.rows,self.cutoff.isoformat(),elastic,family='pure-elasticnet-v1')
            b=append_trial(root,'NFL',self.rows,self.cutoff.isoformat(),boost,family='pure-stumpboost-v1')
            self.assertNotEqual(a,b);self.assertEqual(len(latest_candidates(root,'NFL',now.isoformat())),2)
            event={'id':'nfl:test','league':'NFL','home':'A','away':'B','starts_at':(now+timedelta(hours=2)).isoformat()}
            ratings={'NFL':{'ratings':{'A':1500,'B':1450},'games_played':{'A':5,'B':5},'home_advantage':42}}
            self.assertEqual(record_challenger_forecasts(root,{event['id']:event},ratings,now.isoformat()),2)
            self.assertEqual(record_challenger_forecasts(root,{event['id']:event},ratings,now.isoformat()),0)


if __name__=='__main__':unittest.main()
