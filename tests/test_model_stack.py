import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime,timedelta,timezone
from pathlib import Path
from scripts.line_lab.model_stack import append_trial,eligible_rows,fit_elastic_net_shadow,latest_candidate,predict_elastic_shadow,record_challenger_forecasts


class ModelStackTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.cutoff=datetime(2026,1,1,tzinfo=timezone.utc);self.rows=[]
        for year in (2023,2024,2025):
            for i in range(4):
                start=datetime(year,10,1+i,tzinfo=timezone.utc)
                self.rows.append({'game_id':f'{year}-{i}','league':'NFL','season':str(year),'rights_verified':True,
                    'feature_observed_at':(start-timedelta(hours=2)).isoformat(),'forecast_at':(start-timedelta(hours=1)).isoformat(),
                    'starts_at':start.isoformat(),'final_observed_at':(start+timedelta(hours=4)).isoformat(),
                    'home_win':i%2,'baseline_probability':.5,
                    'features':{'rating_difference':20 if i%2 else -20,'home_advantage':42,'games_played_difference':i}})
    def tearDown(self):self.tmp.cleanup()
    def fit(self):return fit_elastic_net_shadow(self.rows,'NFL',self.cutoff.isoformat(),min_training=8,min_validation=4,min_seasons=3)
    def test_pure_challenger_uses_later_season_for_inner_validation(self):
        model=self.fit();self.assertEqual(model['validation_season'],'2025');self.assertEqual(model['inner_training_games'],8)
        self.assertFalse(model['promoted']);self.assertEqual(model['baseline_comparison_games'],4)
        self.assertIsNotNone(model['validation_paired_candidate_log_loss'])
        future=(self.cutoff+timedelta(days=1)).isoformat()
        p=predict_elastic_shadow(model,self.rows[1]['features'],future,self.cutoff.isoformat())
        self.assertTrue(0<p<1)
        self.assertIsNone(predict_elastic_shadow(model,self.rows[1]['features'],self.cutoff.isoformat(),self.cutoff.isoformat()))
        with self.assertRaises(ValueError):eligible_rows(self.rows,'NFL',future,features=('market_probability',))
    def test_future_outcomes_and_unverified_sources_never_train(self):
        self.rows[0]['final_observed_at']=(self.cutoff+timedelta(days=1)).isoformat()
        self.assertIsNone(self.fit())
        self.rows[1]['rights_verified']=False
        self.assertEqual(len(eligible_rows(self.rows,'NFL',self.cutoff.isoformat())),10)
    def test_registry_and_challenger_forecasts_are_immutable_paper_only(self):
        model=self.fit();now=self.cutoff+timedelta(days=1)
        model_id=append_trial(self.root,'NFL',self.rows,self.cutoff.isoformat(),model)
        self.assertEqual(latest_candidate(self.root,'NFL',now.isoformat())[0],model_id)
        event={'id':'nfl:test','league':'NFL','home':'A','away':'B','starts_at':(now+timedelta(hours=2)).isoformat()}
        ratings={'NFL':{'ratings':{'A':1500,'B':1450},'games_played':{'A':5,'B':5},'home_advantage':42}}
        self.assertEqual(record_challenger_forecasts(self.root,{event['id']:event},ratings,now.isoformat()),1)
        self.assertEqual(record_challenger_forecasts(self.root,{event['id']:event},ratings,now.isoformat()),0)
        with closing(sqlite3.connect(self.root/'observations/challenger_forecasts/2026-01-02.sqlite')) as db:
            row=db.execute('SELECT status,probability FROM challenger_forecasts').fetchone()
            self.assertEqual(row[0],'shadow_unvalidated');self.assertTrue(0<row[1]<1)
            with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM challenger_forecasts')


if __name__=='__main__':unittest.main()
