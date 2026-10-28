import unittest
from datetime import datetime,timedelta,timezone
from scripts.line_lab.trust_models import eligible_samples,fit_trust_timing_shadow,predict_trust_timing_shadow


class TrustModelTests(unittest.TestCase):
    def setUp(self):
        self.cutoff=datetime(2026,1,1,tzinfo=timezone.utc);self.rows=[]
        self.features={'model_edge':.03,'price_edge':.02,'source_disagreement':.03,'hours_to_start':2,
                       'line_movement':.01,'model_uncertainty':.06,'news_age_hours':1,'games_played':8,'liquidity':10}
        for year in (2023,2024,2025):
            for i in range(8):
                start=datetime(year,10,1+i,tzinfo=timezone.utc)
                self.rows.append({'game_id':f'{year}-{i}','league':'NFL','season':str(year),'side':'home',
                    'predicted_at':(start-timedelta(hours=2)).isoformat(),'starts_at':start.isoformat(),
                    'feature_observed_at':(start-timedelta(hours=3)).isoformat(),
                    'quote_source_at':(start-timedelta(hours=3)).isoformat(),'quote_observed_at':(start-timedelta(hours=2)).isoformat(),
                    'anchor_source_at':(start-timedelta(hours=3)).isoformat(),'anchor_observed_at':(start-timedelta(hours=2)).isoformat(),
                    'close_source_at':(start-timedelta(minutes=2)).isoformat(),'close_observed_at':(start-timedelta(minutes=1)).isoformat(),
                    'close_certified_at':(start+timedelta(minutes=5)).isoformat(),
                    'rights_verified':True,'independent_sharp':True,'close_certified':True,'liquidity_verified':True,'news_verified':True,
                    'anchor_probability':.5,'close_probability':.55 if i%2 else .45,'decimal_odds':2,
                    'features':{**self.features,'model_edge':.06 if i%2 else -.02}})
    def fit(self):return fit_trust_timing_shadow(self.rows,'NFL',self.cutoff.isoformat(),min_training=16,min_validation=8)
    def test_prior_season_training_remains_shadow_only(self):
        model=self.fit();self.assertEqual(model['validation_season'],'2025');self.assertEqual(model['inner_training_games'],16)
        future=(self.cutoff+timedelta(days=1)).isoformat()
        result=predict_trust_timing_shadow(model,self.features,self.cutoff.isoformat(),future)
        self.assertTrue(0<result['positive_clv_probability']<1)
        self.assertFalse(result['staking_allowed']);self.assertEqual(result['timing_recommendation'],'unknown')
        self.assertIsNone(predict_trust_timing_shadow(model,self.features,self.cutoff.isoformat(),self.cutoff.isoformat()))
    def test_missing_or_lookahead_sharp_data_cannot_train(self):
        self.rows[0]['close_certified_at']=(self.cutoff+timedelta(days=1)).isoformat()
        self.assertIsNone(self.fit())
        self.rows[1]['independent_sharp']=False
        self.assertEqual(len(eligible_samples(self.rows,'NFL',self.cutoff.isoformat())),22)
        invalid={**self.features,'liquidity':0};model=fit_trust_timing_shadow(self.rows,'NFL',self.cutoff.isoformat(),min_training=14,min_validation=8)
        self.assertIsNone(predict_trust_timing_shadow(model,invalid,self.cutoff.isoformat(),(self.cutoff+timedelta(days=1)).isoformat()))
    def test_first_candidate_is_fixed_before_labels_are_inspected(self):
        row=self.rows[0];later={**row,'predicted_at':(datetime.fromisoformat(row['predicted_at'])+timedelta(minutes=1)).isoformat()}
        row['close_certified']=False
        eligible=eligible_samples([later,row],'NFL',self.cutoff.isoformat())
        self.assertEqual(eligible,[])


if __name__=='__main__':unittest.main()
