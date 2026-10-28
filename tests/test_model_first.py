import math
import sqlite3
from contextlib import closing
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from scripts.line_lab.constants import BOOKS
from scripts.line_lab.market import choose_candidates, decimal_odds
from scripts.line_lab.experiment import record_forecasts, record_outcomes, build_scoreboard, read_forecasts
from scripts.line_lab.guard import assess_disagreement, disagreement_curve
from scripts.line_lab.calibration import eligible_past_rows, fit_platt_shadow, fit_sharp_blend_shadow, predict_shadow, bootstrap_shadow_interval
from scripts.line_lab.statistics import bh_adjust, paired_block_test
from scripts.line_lab.nfl_shadow import qb_summaries, build_nfl_shadow_context, save_qb_snapshot
from scripts.line_lab.backfill import archive_asset

class ModelFirstTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.now=datetime(2026,10,28,1,30,tzinfo=timezone.utc)
        self.event={'id':'nba:2026-10-27:POR:LAL','league':'NBA','home':'LAL','away':'POR','home_name':'Los Angeles Lakers','away_name':'Portland Trail Blazers','starts_at':(self.now+timedelta(hours=2)).isoformat(),'books':{}}
        for i,(_,name) in enumerate(BOOKS[:4]):
            self.event['books'][name]={'home':-105 if i==2 else -110,'away':-110,'as_of':self.now.isoformat()}
        self.model={'ratings':{'LAL':1800,'POR':1300},'last':{'LAL':date(2026,10,25),'POR':date(2026,10,23)},'margins':{},'home_advantage':55,'rest_weight':0,'form_weight':0}
        self.markets={self.event['id']:self.event};self.models={'NBA':self.model}
    def tearDown(self):self.tmp.cleanup()
    def test_probability_is_independent_of_bookmakers_and_all_picks_are_paper(self):
        before=choose_candidates(self.markets,self.models,self.now,[])
        self.assertEqual(len(before),1)
        self.assertEqual(before[0]['model'],'pure-elo-v1')
        self.assertEqual(before[0]['mode'],'paper');self.assertFalse(before[0]['staking_allowed'])
        self.assertAlmostEqual(before[0]['estimated_ev'],before[0]['probability']*decimal_odds(-105)-1,places=4)
        for book in self.event['books'].values():book['away']=+350
        after=choose_candidates(self.markets,self.models,self.now,[])
        self.assertEqual(before[0]['team_code'],after[0]['team_code'])
        self.assertEqual(before[0]['probability'],after[0]['probability'])
        self.assertEqual(before[0]['estimated_ev'],after[0]['estimated_ev'])
    def test_forecasts_and_outcomes_are_frozen_and_sharp_metrics_remain_empty(self):
        self.assertEqual(record_forecasts(self.root,self.markets,self.models,self.now.isoformat()),1)
        self.assertEqual(record_forecasts(self.root,self.markets,self.models,self.now.isoformat()),0)
        forecast=read_forecasts(self.root)[0]
        self.assertIsNone(forecast['sharp_probability']);self.assertIsNone(forecast['fitted_sharp_blend'])
        self.assertIn('FanDuel',forecast['market_snapshot']);self.assertIn('home_rating',forecast['feature_snapshot'])
        self.assertIn('untrained',forecast['guard_snapshot']);self.assertIn('"staking_allowed":false',forecast['guard_snapshot'])
        final={'id':self.event['id'],'home':'LAL','away':'POR','home_score':120,'away_score':100}
        self.assertEqual(record_outcomes(self.root,[final],self.now.isoformat()),0)
        after=self.now+timedelta(hours=4)
        self.assertEqual(record_outcomes(self.root,[final],after.isoformat()),1)
        self.assertEqual(record_outcomes(self.root,[final],after.isoformat()),0)
        paper=[{'id':self.event['id'],'model':'pure-elo-v1','league':'NBA','outcome':'win','initial_best_odds':-105,'pick_day':'2026-10-27'}]
        report=build_scoreboard(self.root,paper)['NBA']
        self.assertEqual(report['forecast_games'],1);self.assertEqual(report['paper_picks'],1)
        self.assertAlmostEqual(report['paper_roi'],100/105,places=4)
        self.assertIsNone(report['sharp_clv']);self.assertIsNone(report['paper_roi_interval'])
        self.assertEqual(report['verdict'],'inconclusive');self.assertFalse(report['staking_allowed'])
        with closing(sqlite3.connect(self.root/'observations/forecasts/2026-10-28.sqlite')) as db:
            with self.assertRaises(sqlite3.IntegrityError):db.execute('UPDATE forecasts SET pure_probability=.99')
    def test_nonfinal_and_mismatched_teams_do_not_count(self):
        record_forecasts(self.root,self.markets,self.models,self.now.isoformat())
        final={'id':self.event['id'],'home':'POR','away':'LAL','home_score':100,'away_score':120}
        self.assertEqual(record_outcomes(self.root,[final],(self.now+timedelta(hours=4)).isoformat()),0)
        self.assertEqual(build_scoreboard(self.root,[])['NBA']['forecast_games'],0)
    def test_disagreement_is_descriptive_and_cannot_authorize_staking(self):
        guard=assess_disagreement(.75,.55,'NFL')
        self.assertFalse(guard['staking_allowed']);self.assertEqual(guard['real_stake_units'],0)
        self.assertEqual(guard['quarterback_status'],'unknown')
        curve=disagreement_curve([{'model_probability':.75,'sharp_probability':.6,'outcome':1},
                                  {'model_probability':.45,'sharp_probability':None,'outcome':0}])
        self.assertEqual(curve['above_0.10']['games'],1)
        self.assertEqual(sum(x['games'] for x in curve.values()),1)
    def test_calibration_and_blend_only_use_settled_prior_sharp_data(self):
        rows=[]
        for i in range(8):
            start=self.now+timedelta(days=i)
            rows.append({'game_id':str(i),'captured_at':(start-timedelta(hours=1)).isoformat(),
                         'starts_at':start.isoformat(),'settled_at':(start+timedelta(hours=3)).isoformat(),
                         'pure_probability':.55 if i%2 else .45,'sharp_probability':.52,
                         'sharp_as_of':(start-timedelta(hours=2)).isoformat(),'anchor_type':'sharp','outcome':i%2})
        cutoff=(self.now+timedelta(days=6,hours=4)).isoformat()
        self.assertEqual(len(eligible_past_rows(rows,cutoff,True)),7)
        self.assertIsNone(fit_sharp_blend_shadow(rows,cutoff))
        fit=fit_sharp_blend_shadow(rows,cutoff,min_games=5)
        self.assertFalse(fit['promoted']);self.assertEqual(fit['games'],7)
        self.assertTrue(0<predict_shadow(fit,.6,.55)<1)
        self.assertIsNone(predict_shadow(fit,.6))
        rows[0]['sharp_as_of']=(self.now+timedelta(hours=1)).isoformat()
        self.assertEqual(len(eligible_past_rows(rows,cutoff,True)),6)
        self.assertEqual(fit_platt_shadow(rows,cutoff,min_games=5)['games'],7)
        interval=bootstrap_shadow_interval(rows,cutoff,.6,min_games=5,min_days=5,draws=8)
        self.assertFalse(interval['promoted']);self.assertLessEqual(interval['interval'][0],interval['interval'][1])
    def test_paired_test_and_multiple_testing_are_conservative_with_small_samples(self):
        self.assertIsNone(paired_block_test({'one_day':[.1]*100}))
        values={f'day{i}':[-.1,-.1,-.1] for i in range(10)}
        result=paired_block_test(values,iterations=1000)
        self.assertEqual(result['games'],30);self.assertLess(result['p_value'],.05)
        adjusted=bh_adjust([.01,.04,None,.03])
        self.assertAlmostEqual(adjusted[0],.03);self.assertAlmostEqual(adjusted[1],.04)
        self.assertIsNone(adjusted[2]);self.assertAlmostEqual(adjusted[3],.04)
    def test_nfl_qb_context_uses_only_previously_completed_games_and_observed_assets(self):
        schedule=('game_id,gameday,home_team,away_team,home_score,away_score,home_qb_id,away_qb_id\n'
                  'old,2026-10-25,BAL,CLE,20,10,qb1,qb2\n'
                  'same,2026-10-27,BAL,CLE,30,10,qb1,qb2\n'
                  'future,2026-11-01,BAL,CLE,,,qb1,qb2\n')
        pbp=('game_id,posteam,passer_player_id,pass_attempt,qb_epa,epa,cpoe\n'
             'old,BAL,qb1,1,1.0,1.0,3.0\n'
             'same,BAL,qb1,1,100,100,30\n'
             'future,BAL,qb1,1,100,100,30\n')
        observed=(self.now-timedelta(minutes=10)).isoformat()
        summary=qb_summaries(pbp,schedule,observed,observed,self.now.isoformat())
        self.assertEqual(summary[('BAL','qb1')]['pass_plays'],1)
        self.assertEqual(summary[('BAL','qb1')]['epa_per_pass'],1.0)
        self.assertEqual(qb_summaries(pbp,schedule,(self.now+timedelta(seconds=1)).isoformat(),observed,self.now.isoformat()),{})
        spec={'dataset':'nfl_pbp','season':'2026','url':'https://example.org/pbp.csv','attribution':'test','license':'CC-BY-4.0'}
        archive_asset(self.root,spec,pbp.encode(),observed)
        contexts=build_nfl_shadow_context(self.root,schedule,observed,self.now.isoformat())
        entry=contexts['nfl:2026-11-01:CLE:BAL']
        self.assertFalse(entry['used_in_prediction']);self.assertEqual(entry['starter_status'],'unconfirmed')
        self.assertEqual(entry['home_qb']['pass_plays'],1)
        self.assertEqual(save_qb_snapshot(self.root,2026,summary,observed,observed,'pbp-hash','schedule-hash'),1)
        newer=build_nfl_shadow_context(self.root,schedule,observed,self.now.isoformat())
        self.assertEqual(newer['nfl:2026-11-01:CLE:BAL']['source_sha256'],'pbp-hash')
        stale=build_nfl_shadow_context(self.root,schedule,observed,(self.now+timedelta(hours=49)).isoformat())
        self.assertEqual(stale,{})
    def test_shadow_context_never_changes_the_pure_forecast(self):
        record_forecasts(self.root,self.markets,self.models,self.now.isoformat(),{})
        later=self.now+timedelta(minutes=1)
        context={self.event['id']:{'status':'shadow_only','home_qb':{'epa_per_pass':9},'used_in_prediction':False}}
        record_forecasts(self.root,self.markets,self.models,later.isoformat(),context)
        rows=read_forecasts(self.root)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['pure_probability'],rows[1]['pure_probability'])

if __name__=='__main__':unittest.main()
