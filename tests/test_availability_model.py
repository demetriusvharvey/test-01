import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from scripts.line_lab.availability_features import availability_features
from scripts.line_lab.availability_model import fit_availability_shadow, predict_availability_shadow
from scripts.line_lab.experiment import record_forecasts, record_outcomes
from scripts.line_lab.model_stack import append_trial, record_challenger_forecasts
from scripts.line_lab.challenger_evaluation import read_inputs, evaluate


class AvailabilityModelTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,28,17,tzinfo=timezone.utc)
        self.event={'id':'nfl:test','league':'NFL','home':'A','away':'B',
                    'home_name':'Home','away_name':'Away','starts_at':(self.now+timedelta(hours=3)).isoformat()}
        self.nfl={'source':'nflverse injury and practice reports','used_in_prediction':False,
                  'incomplete':False,'latest_observed_at':self.now.isoformat(),'teams':{
                      'home':{'team':'Home','total_entries':1,'entries':[{'report_status':'Out','observed_at':self.now.isoformat()}]},
                      'away':{'team':'Away','total_entries':1,'entries':[{'report_status':'Questionable','observed_at':self.now.isoformat()}]}}}
        self.cutoff=datetime(2026,1,1,tzinfo=timezone.utc);self.rows=[]
        for year in (2023,2024,2025):
            for i in range(8):
                start=datetime(year,10,i+1,tzinfo=timezone.utc)
                self.rows.append({'game_id':f'{year}-{i}','league':'NFL','season':str(year),'rights_verified':True,
                    'feature_observed_at':(start-timedelta(hours=2)).isoformat(),'forecast_at':(start-timedelta(hours=1)).isoformat(),
                    'starts_at':start.isoformat(),'final_observed_at':(start+timedelta(hours=4)).isoformat(),
                    'home_win':i%2,'baseline_probability':.5,'features':{'out_difference':-2 if i%2 else 2,
                    'doubtful_difference':0,'questionable_difference':0}})

    def test_report_features_are_point_in_time_and_require_both_sides(self):
        features=availability_features(self.event,self.nfl,self.now.isoformat())
        self.assertEqual(features['features'],{'out_difference':1,'doubtful_difference':0,'questionable_difference':-1})
        self.assertFalse(features['used_in_prediction'])
        self.nfl['teams']['away']['entries']=[];self.nfl['teams']['away']['total_entries']=0
        self.assertIsNone(availability_features(self.event,self.nfl,self.now.isoformat()))
        self.nfl['teams']['away']['entries']=[{'report_status':'Out','observed_at':(self.now+timedelta(seconds=1)).isoformat()}]
        self.nfl['teams']['away']['total_entries']=1
        self.assertIsNone(availability_features(self.event,self.nfl,self.now.isoformat()))

    def test_nba_missing_conflicted_or_future_reports_never_imply_health(self):
        event={**self.event,'league':'NBA'}
        context={'source':'PropLine, ESPN-sourced','used_in_prediction':False,'incomplete':False,
                 'observed_at':self.now.isoformat(),'teams':{
                     'home':{'team':'Home','counts':{'out':1,'doubtful':0,'questionable':0,'other':0}},
                     'away':{'team':'Away','counts':{'out':0,'doubtful':0,'questionable':1,'other':0}}}}
        self.assertIsNotNone(availability_features(event,context,self.now.isoformat()))
        context['incomplete']=True
        self.assertIsNone(availability_features(event,context,self.now.isoformat()))
        context['incomplete']=False;context['teams']['away']['counts']['questionable']=0
        self.assertIsNone(availability_features(event,context,self.now.isoformat()))
        context['teams']['away']['counts']['questionable']=1;context['observed_at']=(self.now+timedelta(seconds=1)).isoformat()
        self.assertIsNone(availability_features(event,context,self.now.isoformat()))

    def fit(self):
        return fit_availability_shadow(self.rows,'NFL',self.cutoff.isoformat(),min_training=16,min_validation=8,min_seasons=3)

    def test_challenger_trains_on_prior_valid_rows_only_and_never_promotes(self):
        model=self.fit()
        self.assertEqual(model['inner_training_games'],16);self.assertEqual(model['validation_games'],8)
        self.assertFalse(model['promoted']);self.assertEqual(model['model_version'],'availability-logistic-v1')
        earlier={'out_difference':-2,'doubtful_difference':0,'questionable_difference':0}
        later={**earlier,'out_difference':2};future=(self.cutoff+timedelta(hours=1)).isoformat()
        p1=predict_availability_shadow(model,.5,earlier,future,self.cutoff.isoformat())
        p2=predict_availability_shadow(model,.5,later,future,self.cutoff.isoformat())
        self.assertGreater(p1,p2)
        self.assertIsNone(predict_availability_shadow(model,.5,earlier,self.cutoff.isoformat(),self.cutoff.isoformat()))
        self.assertIsNone(predict_availability_shadow(model,.5,earlier,future,(self.cutoff+timedelta(hours=2)).isoformat()))
        self.rows[0]['rights_verified']=False
        self.assertIsNone(self.fit())

    def test_frozen_inputs_feed_a_matched_shadow_comparison(self):
        artifact=self.fit();context=availability_features(self.event,self.nfl,self.now.isoformat())
        event={**self.event,'books':{f'book{i}':{'home':-110,'away':-110,'as_of':self.now.isoformat()} for i in range(3)}}
        model={'ratings':{'A':1500,'B':1500},'last':{},'margins':{},'games_played':{'A':5,'B':5},
               'home_advantage':0,'rest_weight':0,'form_weight':0,'source_hashes':{'games.csv':'verified-hash'}}
        with tempfile.TemporaryDirectory() as root:
            append_trial(root,'NFL',self.rows,self.cutoff.isoformat(),artifact,family='availability-logistic-v1')
            shadow={event['id']:{'availability':context,'quarterback':None}}
            self.assertEqual(record_forecasts(root,{event['id']:event},{'NFL':model},self.now.isoformat(),shadow),1)
            self.assertEqual(record_challenger_forecasts(root,{event['id']:event},{'NFL':model},self.now.isoformat(),{event['id']:context}),1)
            final={'id':event['id'],'home':'A','away':'B','home_score':24,'away_score':17,'source':'nflverse'}
            settled=(self.now+timedelta(hours=7)).isoformat();record_outcomes(root,[final],settled)
            baseline,candidates,trials,outcomes=read_inputs(root,settled)
            results=evaluate(baseline,candidates,trials,outcomes,settled)
            result=next(r for r in results if r['league']=='NFL' and r['model_version']=='availability-logistic-v1')
            self.assertEqual(result['games'],1);self.assertFalse(result['promoted'])
            self.assertNotIn('player_name',json.dumps(baseline))
            candidates[0]['feature_json']=json.dumps({'out_difference':99})
            results=evaluate(baseline,candidates,trials,outcomes,settled)
            result=next(r for r in results if r['league']=='NFL' and r['model_version']=='availability-logistic-v1')
            self.assertEqual(result['games'],0)


if __name__=='__main__':unittest.main()
