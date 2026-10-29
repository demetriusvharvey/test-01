import json
import tempfile
import unittest
from datetime import datetime,timedelta,timezone

from scripts.line_lab.availability_features import nfl_position_features
from scripts.line_lab.position_status_model import FEATURES,fit_position_shadow,predict_position_shadow
from scripts.line_lab.experiment import record_forecasts,record_outcomes
from scripts.line_lab.model_stack import append_trial,record_challenger_forecasts
from scripts.line_lab.challenger_evaluation import read_inputs,evaluate


class PositionStatusTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,28,17,tzinfo=timezone.utc)
        self.event={'id':'nfl:test','league':'NFL','home':'A','away':'B',
                    'home_name':'Home','away_name':'Away','starts_at':(self.now+timedelta(hours=3)).isoformat()}
        self.context={'source':'nflverse injury and practice reports','used_in_prediction':False,
                      'incomplete':False,'latest_observed_at':self.now.isoformat(),'teams':{
            'home':{'team':'Home','total_entries':2,'entries':[
                {'name':'Home OL','position':'OT','report_status':'Out','observed_at':self.now.isoformat()},
                {'name':'Home CB','position':'CB','report_status':'Questionable','observed_at':self.now.isoformat()}]},
            'away':{'team':'Away','total_entries':1,'entries':[
                {'name':'Away WR','position':'WR','report_status':'Out','observed_at':self.now.isoformat()}]}}}
        self.cutoff=datetime(2026,1,1,tzinfo=timezone.utc);self.rows=[]
        for year in (2023,2024,2025):
            for i in range(8):
                start=datetime(year,10,i+1,tzinfo=timezone.utc)
                features=dict.fromkeys(FEATURES,0)
                features['line_out_difference']=-2 if i%2 else 2
                self.rows.append({'game_id':f'{year}-{i}','league':'NFL','season':str(year),
                    'rights_verified':True,'feature_observed_at':(start-timedelta(hours=2)).isoformat(),
                    'forecast_at':(start-timedelta(hours=1)).isoformat(),'starts_at':start.isoformat(),
                    'final_observed_at':(start+timedelta(hours=4)).isoformat(),'home_win':i%2,
                    'baseline_probability':.5,'features':features})

    def test_all_position_groups_and_missingness_are_explicit(self):
        snapshot=nfl_position_features(self.event,self.context,self.now.isoformat())
        self.assertEqual(snapshot['features']['line_out_difference'],1)
        self.assertEqual(snapshot['features']['receiver_out_difference'],-1)
        self.assertEqual(snapshot['features']['secondary_questionable_difference'],1)
        self.assertEqual(len(snapshot['features']),27)
        self.context['teams']['home']['total_entries']=3
        self.assertIsNone(nfl_position_features(self.event,self.context,self.now.isoformat()))
        self.context['teams']['home']['total_entries']=2
        self.context['latest_observed_at']=(self.now+timedelta(seconds=1)).isoformat()
        self.assertIsNone(nfl_position_features(self.event,self.context,self.now.isoformat()))

    def test_chronological_training_and_future_prediction_gate(self):
        fit=fit_position_shadow(self.rows,'NFL',self.cutoff.isoformat(),16,8,3)
        self.assertEqual(fit['validation_games'],8)
        self.assertEqual(fit['inner_training_games'],16)
        self.assertFalse(fit['promoted'])
        future=(self.cutoff+timedelta(hours=1)).isoformat()
        self.assertIsNotNone(predict_position_shadow(fit,.5,self.rows[0]['features'],future,self.cutoff.isoformat()))
        self.assertIsNone(predict_position_shadow(fit,.5,self.rows[0]['features'],self.cutoff.isoformat(),self.cutoff.isoformat()))
        self.rows[0]['rights_verified']=False
        self.assertIsNone(fit_position_shadow(self.rows,'NFL',self.cutoff.isoformat(),16,8,3))

    def test_stale_reports_never_enter_training_or_predictions(self):
        fresh=fit_position_shadow(self.rows,'NFL',self.cutoff.isoformat(),16,8,3)
        self.assertIsNotNone(fresh)
        stale_rows=[dict(row) for row in self.rows]
        stale_rows[0]['feature_observed_at']=(datetime.fromisoformat(
            stale_rows[0]['forecast_at'])-timedelta(hours=31)).isoformat()
        self.assertIsNone(fit_position_shadow(
            stale_rows,'NFL',self.cutoff.isoformat(),16,8,3))
        future=(self.cutoff+timedelta(hours=1)).isoformat()
        self.assertIsNone(predict_position_shadow(
            fresh,.5,self.rows[0]['features'],future,
            (self.cutoff-timedelta(hours=31)).isoformat()))
        self.assertIsNotNone(predict_position_shadow(
            fresh,.5,self.rows[0]['features'],future,
            (self.cutoff-timedelta(hours=1)).isoformat()))
        self.assertIsNone(predict_position_shadow(
            fresh,.5,self.rows[0]['features'],future,
            (self.cutoff+timedelta(hours=2)).isoformat()))

    def test_frozen_report_is_matched_before_shadow_evaluation(self):
        fit=fit_position_shadow(self.rows,'NFL',self.cutoff.isoformat(),16,8,3)
        snapshot=nfl_position_features(self.event,self.context,self.now.isoformat())
        event={**self.event,'books':{f'book{i}':{'home':-110,'away':-110,'as_of':self.now.isoformat()} for i in range(3)}}
        model={'ratings':{'A':1500,'B':1500},'last':{},'margins':{},'games_played':{'A':5,'B':5},
               'home_advantage':0,'rest_weight':0,'form_weight':0,'source_hashes':{'games.csv':'verified-hash'}}
        with tempfile.TemporaryDirectory() as root:
            append_trial(root,'NFL',self.rows,self.cutoff.isoformat(),fit,family=fit['model_version'])
            shadow={event['id']:{'nfl_position_status':snapshot}}
            self.assertEqual(record_forecasts(root,{event['id']:event},{'NFL':model},self.now.isoformat(),shadow),1)
            self.assertEqual(record_challenger_forecasts(root,{event['id']:event},{'NFL':model},self.now.isoformat(),position_contexts={event['id']:snapshot}),1)
            final={'id':event['id'],'home':'A','away':'B','home_score':24,'away_score':17,'source':'nflverse'}
            settled=(self.now+timedelta(hours=7)).isoformat();record_outcomes(root,[final],settled)
            baseline,candidates,trials,outcomes=read_inputs(root,settled)
            result=next(r for r in evaluate(baseline,candidates,trials,outcomes,settled)
                        if r['model_version']==fit['model_version'])
            self.assertEqual(result['games'],1);self.assertFalse(result['promoted'])
            candidates[0]['feature_json']=json.dumps({'line_out_difference':99})
            result=next(r for r in evaluate(baseline,candidates,trials,outcomes,settled)
                        if r['model_version']==fit['model_version'])
            self.assertEqual(result['games'],0)


if __name__=='__main__':unittest.main()
