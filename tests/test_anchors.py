import unittest
from datetime import datetime, timedelta, timezone
from scripts.line_lab.anchors import build_shadow_anchor, devig, fit_shadow_weights, implied_american, price_diagnostic


class AnchorTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,28,12,tzinfo=timezone.utc)
        self.start=(self.now+timedelta(hours=3)).isoformat()
        self.retail={'book':'FanDuel','kind':'retail','home_odds':-120,'away_odds':110,
                     'as_of':self.now.isoformat(),'fetched_at':self.now.isoformat()}
    def test_devig_methods_sum_to_one_and_reject_invalid(self):
        q=[implied_american(-120),implied_american(110)]
        for method in ('multiplicative','power','shin'):
            values=devig(q,method)
            self.assertAlmostEqual(sum(values),1,places=9)
            self.assertTrue(0<values[0]<1)
        with self.assertRaises(ValueError):devig([.4,.4],'shin')
        with self.assertRaises(ValueError):implied_american(-80)
    def test_fallback_and_qualified_source_deduplication(self):
        fallback=build_shadow_anchor([self.retail],self.now.isoformat(),self.start)
        self.assertEqual(fallback['source'],'retail_median_not_sharp')
        sharp={**self.retail,'book':'Sharp A','kind':'sharp','rights_verified':True,'source_type_verified':True,'upstream_group':'source1'}
        duplicate={**sharp,'book':'Sharp B','home_odds':-125}
        result=build_shadow_anchor([self.retail,sharp,duplicate],self.now.isoformat(),self.start)
        self.assertEqual(result['source'],'qualified_shadow_consensus')
        self.assertEqual(result['upstream_groups'],['source1'])
        self.assertFalse(result['usable_for_staking'])
        unverified={**sharp,'rights_verified':False}
        self.assertEqual(build_shadow_anchor([unverified,self.retail],self.now.isoformat(),self.start)['source'],'retail_median_not_sharp')
    def test_future_or_thin_quotes_and_unknown_fees_are_rejected(self):
        future={**self.retail,'as_of':(self.now+timedelta(minutes=1)).isoformat()}
        self.assertEqual(build_shadow_anchor([future],self.now.isoformat(),self.start)['source'],'unavailable')
        exchange={**self.retail,'kind':'exchange','rights_verified':True,'source_type_verified':True,'upstream_group':'x'}
        self.assertEqual(build_shadow_anchor([exchange],self.now.isoformat(),self.start)['source'],'unavailable')
        exchange.update({'liquidity_verified':True,'available_units':3,'fee_fraction':.02})
        self.assertEqual(build_shadow_anchor([exchange],self.now.isoformat(),self.start)['source'],'qualified_shadow_consensus')
    def test_weights_require_prior_settled_observations(self):
        rows=[]
        for i in range(3):
            start=self.now+timedelta(days=i)
            rows.append({'game_id':str(i),'captured_at':(start-timedelta(hours=2)).isoformat(),
                         'source_as_of':(start-timedelta(hours=3)).isoformat(),'source_fetched_at':(start-timedelta(hours=2)).isoformat(),
                         'starts_at':start.isoformat(),'settled_at':(start+timedelta(hours=4)).isoformat(),
                         'rights_verified':True,'source_type_verified':True,'home_probability':.6,'home_win':i%2,'upstream_group':'a'})
        cutoff=(self.now+timedelta(days=1,hours=5)).isoformat()
        self.assertIsNone(fit_shadow_weights(rows,cutoff,min_games=3))
        result=fit_shadow_weights(rows,cutoff,min_games=2)
        self.assertEqual(result['counts']['a'],2);self.assertFalse(result['promoted'])
        with self.assertRaises(ValueError):build_shadow_anchor([self.retail],cutoff,self.start,weights={'weights':{'a':1},'training_cutoff':cutoff})
        rows[0]['source_fetched_at']=(self.now+timedelta(hours=1)).isoformat()
        self.assertIsNone(fit_shadow_weights(rows,cutoff,min_games=2))
    def test_arbitrage_is_only_an_unverified_diagnostic(self):
        self.assertTrue(price_diagnostic(120,120)['underround'])
        self.assertIn('no_execution',price_diagnostic(120,120)['status'])
