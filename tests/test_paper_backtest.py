import json
import tempfile
import unittest
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from scripts.backtest_shadow import load_inputs
from scripts.line_lab.experiment import record_forecasts,record_outcomes
from scripts.line_lab.market import choose_candidates
from scripts.line_lab.trust import record_candidates
from scripts.line_lab.paper_backtest import replay


class PaperReplayTests(unittest.TestCase):
    def setUp(self):
        self.start=datetime(2026,10,28,23,tzinfo=timezone.utc);self.cutoff=self.start+timedelta(days=2)
    def row(self,game='1',day=0,side='home',status='win'):
        start=self.start+timedelta(days=day);pred=start-timedelta(hours=2)
        return {'game_id':game,'league':'NBA','selection':'selected_paper','side':side,
                'book':'FanDuel','predicted_at':pred.isoformat(),'starts_at':start.isoformat(),
                'feature_observed_at':(pred-timedelta(minutes=10)).isoformat(),
                'source_as_of':(pred-timedelta(minutes=10)).isoformat(),'fetched_at':pred.isoformat(),
                'home_odds':100,'away_odds':-110,'model_probability':.6,'rights_verified':True,
                'result_status':status,'result_observed_at':(start+timedelta(hours=3)).isoformat(),
                'outcome_rights_verified':True}
    def test_slippage_is_scenario_and_returns_compare_same_book(self):
        result=replay([self.row()],self.cutoff.isoformat())
        self.assertEqual(result['settled'],1);self.assertAlmostEqual(result['paper_profit_units'],.98)
        self.assertAlmostEqual(result['paper_roi'],.98);self.assertEqual(result['sharp_close_samples'],0)
        self.assertIsNone(result['sharp_clv']);self.assertIsNone(result['paper_roi_interval'])
        self.assertAlmostEqual(result['model_brier'],.16);self.assertEqual(result['pending_or_unresolved'],0)
        self.assertTrue(result['assumptions']['no_actual_wagers']);self.assertFalse(result['validated_profitable'])
    def test_no_future_data_unapproved_rights_or_second_forecast(self):
        row=self.row();late=dict(row);late['fetched_at']=(self.start+timedelta(minutes=1)).isoformat()
        invalid=dict(row);invalid['game_id']='2';invalid['rights_verified']=False
        later=dict(row);later['predicted_at']=(self.start-timedelta(hours=1)).isoformat();later['result_status']='loss'
        out=replay([later,row,invalid],self.cutoff.isoformat())
        self.assertEqual(out['forecast_candidates'],2);self.assertEqual(out['settled'],1);self.assertEqual(out['wins'],1)
        self.assertEqual(replay([late],self.cutoff.isoformat())['qualified_candidates'],0)
    def test_cap_and_pending_stakes_are_not_graded_or_refunded(self):
        rows=[self.row(str(i),status='unknown_tie') for i in range(5)]
        out=replay(rows,self.cutoff.isoformat(),initial_bankroll=100,daily_cap=3)
        self.assertEqual(out['pending_or_unresolved'],3);self.assertEqual(out['excluded']['daily_cap_or_cash'],2)
        self.assertEqual(out['cash_units'],97);self.assertEqual(out['reserved_units'],3);self.assertIsNone(out['paper_roi'])
    def test_sharp_close_must_be_independent_certified_and_pregame(self):
        row=self.row();row['sharp_close']={'rights_verified':True,'independent':True,'certified_close':True,
            'source':'verified fixture','as_of':(self.start-timedelta(minutes=2)).isoformat(),
            'observed_at':(self.start-timedelta(minutes=1)).isoformat(),'selected_probability':.55}
        good=replay([row],self.cutoff.isoformat());self.assertAlmostEqual(good['sharp_clv'],1.98*.55-1)
        row['sharp_close']['independent']=False
        self.assertIsNone(replay([row],self.cutoff.isoformat())['sharp_clv'])
    def test_void_requires_verified_settlement_rule(self):
        row=self.row(status='void');self.assertEqual(replay([row],self.cutoff.isoformat())['pending_or_unresolved'],1)
        row['settlement_rule_verified']=True;result=replay([row],self.cutoff.isoformat())
        self.assertEqual(result['verified_voids'],1);self.assertEqual(result['cash_units'],100)
        self.assertEqual(result['settled'],0);self.assertIsNone(result['paper_roi'])
    def test_loader_requires_matching_frozen_pick_and_explicit_source_policy(self):
        now=datetime(2026,10,28,16,tzinfo=timezone.utc);start=now+timedelta(hours=5)
        event={'id':'nfl:2026-10-28:BUF:NE','league':'NFL','home':'NE','away':'BUF',
               'home_name':'New England Patriots','away_name':'Buffalo Bills','starts_at':start.isoformat(),'neutral':False,'books':{}}
        for name in ('FanDuel','DraftKings','BetMGM'):
            event['books'][name]={'home':-110,'away':-110,'as_of':now.isoformat(),'fetched_at':now.isoformat(),'provider':'test_provider'}
        model={'ratings':{'NE':1800,'BUF':1300},'last':{'NE':date(2026,10,20),'BUF':date(2026,10,20)},
               'home_advantage':42,'rest_weight':0,'games_played':{'NE':6,'BUF':6},'source_hashes':{'games.csv':'a'*64}}
        markets={event['id']:event};models={'NFL':model}
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);ledger=root/'ledger.json';policy=root/'policy.json'
            picks=choose_candidates(markets,models,now,[]);self.assertEqual(len(picks),1)
            record_forecasts(root,markets,models,now.isoformat());record_candidates(root,markets,models,now.isoformat(),[],picks)
            ledger.write_text(json.dumps(picks));policy.write_text(json.dumps({'approved_sources':[]}))
            final={'id':event['id'],'home':'NE','away':'BUF','home_score':21,'away_score':14,'source':'nflverse'}
            record_outcomes(root,[final],(start+timedelta(hours=4)).isoformat())
            unapproved=load_inputs(root,ledger,policy);self.assertEqual(len(unapproved),1);self.assertFalse(unapproved[0]['rights_verified'])
            entry={'league':'NFL','quote_provider':'test_provider','feature_source':'nflverse+espn','outcome_sources':['nflverse'],
                   'rights_verified':True,'rights_evidence':'fixture only','reviewed_at':(now-timedelta(days=1)).isoformat()}
            policy.write_text(json.dumps({'approved_sources':[entry]}));rows=load_inputs(root,ledger,policy)
            self.assertTrue(rows[0]['rights_verified']);self.assertEqual(replay(rows,(start+timedelta(days=1)).isoformat())['settled'],1)
            ledger.write_text('[]');self.assertEqual(load_inputs(root,ledger,policy),[])


if __name__=='__main__':unittest.main()
