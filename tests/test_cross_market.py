import copy
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scripts.line_lab.cross_market import archive_market_snapshots, cross_market_gap, fit_margin_distribution, parse_featured_markets, spread_to_win_prob
from scripts.line_lab.odds_api import record_call, should_call


class CrossMarketTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.now=datetime(2026,10,28,1,30,tzinfo=timezone.utc)
        self.start=self.now+timedelta(hours=2)
        self.payload=[{'id':'test','home_team':'Los Angeles Lakers','away_team':'Portland Trail Blazers',
          'commence_time':self.start.isoformat(),'bookmakers':[{'key':'fanduel','last_update':self.now.isoformat(),
          'markets':[{'key':'spreads','last_update':self.now.isoformat(),'outcomes':[
             {'name':'Los Angeles Lakers','price':-110,'point':-3.5},{'name':'Portland Trail Blazers','price':-110,'point':3.5}]},
          {'key':'totals','last_update':self.now.isoformat(),'outcomes':[
             {'name':'Over','price':-110,'point':220.5},{'name':'Under','price':-110,'point':220.5}]}]}]}]
    def tearDown(self):self.tmp.cleanup()
    def test_complete_markets_are_archived_once_and_immutable(self):
        rows=parse_featured_markets(self.payload,'NBA',self.now.isoformat(),{'fanduel':'FanDuel'})
        self.assertEqual({r['market'] for r in rows},{'spreads','totals'})
        self.assertEqual(archive_market_snapshots(self.root,rows),2)
        self.assertEqual(archive_market_snapshots(self.root,rows),0)
        with sqlite3.connect(self.root/'observations/cross_market/2026-10-28.sqlite') as db:
            with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM market_quotes')
    def test_invalid_market_is_isolated(self):
        bad=copy.deepcopy(self.payload);bad[0]['bookmakers'][0]['markets'][0]['outcomes'][0]['name']='unknown'
        rows=parse_featured_markets(bad,'NBA',self.now.isoformat(),{'fanduel':'FanDuel'})
        self.assertEqual([x['market'] for x in rows],['totals'])
        bad[0]['bookmakers'][0]['markets'][1]['outcomes'][1]['point']=221.5
        self.assertEqual(parse_featured_markets(bad,'NBA',self.now.isoformat(),{'fanduel':'FanDuel'}),[])
        self.assertEqual(parse_featured_markets(self.payload,'NBA',(self.start+timedelta(seconds=1)).isoformat(),{'fanduel':'FanDuel'}),[])
    def test_walkforward_distribution_has_no_future_information(self):
        rows=[]
        for i,margin in enumerate([3,7,-3,10,0,-7]):
            start=self.now+timedelta(days=i)
            rows.append({'league':'NFL','game_id':str(i),'season':str(2024+i%2),
                'source_as_of':(start-timedelta(hours=3)).isoformat(), 'captured_at':(start-timedelta(hours=1)).isoformat(),
                'starts_at':start.isoformat(),'settled_at':(start+timedelta(hours=4)).isoformat(),
                'home_spread':-3,'total':45,'home_score':20+margin,'away_score':20,'rights_verified':True})
        cutoff=(self.now+timedelta(days=7)).isoformat()
        fit=fit_margin_distribution(rows,cutoff,'NFL',min_games=6,min_seasons=2)
        self.assertEqual(fit['games'],6);self.assertFalse(fit['promoted'])
        estimate=spread_to_win_prob(fit,-3,45,(self.now+timedelta(days=8)).isoformat())
        self.assertEqual(estimate['status'],'shadow_unvalidated')
        self.assertGreater(estimate['home_probability'],0)
        self.assertIsNone(spread_to_win_prob(fit,-3,45,cutoff))
        rows[0]['source_as_of']=(self.now+timedelta(hours=1)).isoformat()
        self.assertIsNone(fit_margin_distribution(rows,cutoff,'NFL',min_games=6,min_seasons=2))
    def test_cross_market_comparison_requires_same_game_book_and_time(self):
        q={'game_id':'game','book':'FanDuel','as_of':self.now.isoformat(),'fetched_at':self.now.isoformat(),'home_odds':-110,'away_odds':-110}
        spread={'game_id':'game','book':'FanDuel','as_of':self.now.isoformat(),'fetched_at':self.now.isoformat()}
        estimate={'home_probability':.55,'status':'shadow_unvalidated'}
        result=cross_market_gap(q,spread,estimate,self.now.isoformat(),self.start.isoformat(),.04)
        self.assertTrue(result['threshold_exceeded']);self.assertFalse(result['betting_signal'])
        spread['book']='Other'
        self.assertIsNone(cross_market_gap(q,spread,estimate,self.now.isoformat(),self.start.isoformat(),.04))
    def test_budget_counts_market_credits_not_http_calls(self):
        record_call(self.root,'NBA',self.now.isoformat(),'ok',remaining=65,used=1,cost=3)
        self.assertFalse(should_call(self.root,'NFL',self.now.isoformat(),monthly_limit=360,reserve=64,next_cost=3))
        self.assertTrue(should_call(self.root,'NFL',self.now.isoformat(),monthly_limit=360,reserve=60,next_cost=3))
        self.assertFalse(should_call(self.root,'NFL',self.now.isoformat(),monthly_limit=5,reserve=0,next_cost=3))


if __name__=='__main__':unittest.main()
