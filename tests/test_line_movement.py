import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from scripts.line_lab.history import append_observations
from scripts.line_lab.line_movement import same_book_history


class LineMovementTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=self.tmp.name
        self.now=datetime(2026,10,28,20,tzinfo=timezone.utc);self.start=self.now+timedelta(hours=3)
        self.event={'id':'nba:g','league':'NBA','home':'A','away':'B','starts_at':self.start.isoformat(),'books':{}}
    def quote(self,hours_ago,home=-110,provider='feed'):
        stamp=(self.now-timedelta(hours=hours_ago)).isoformat()
        return {'id':'nba:g','league':'NBA','home':'A','away':'B','book':'FanDuel','provider':provider,
                'home_odds':home,'away_odds':100,'as_of':stamp,'fetched_at':stamp,'starts_at':self.start.isoformat()}
    def test_returns_only_observed_same_source_pregame_prices(self):
        one=self.quote(2,-110);two=self.quote(0,-120);other=self.quote(1,-130,'other')
        append_observations(self.root,[one,other,two],self.now.isoformat())
        self.event['books']['FanDuel']={'home':-120,'away':100,'as_of':two['as_of'],'fetched_at':two['fetched_at'],'provider':'feed'}
        out=same_book_history(self.root,self.event,'A','FanDuel',self.now.isoformat())
        self.assertEqual([p['odds'] for p in out['points']],[-110,-120])
        self.assertEqual(out['history_type'],'observed_not_opener_or_close')
        self.assertFalse(out['price_movement_is_evidence_of_edge'])
        self.assertIsNone(same_book_history(self.root,self.event,'C','FanDuel',self.now.isoformat()))
    def test_conflict_or_unmatched_current_price_is_rejected(self):
        one=self.quote(0,-110);two=self.quote(0,-120)
        append_observations(self.root,[one,two],self.now.isoformat())
        self.event['books']['FanDuel']={'home':-120,'away':100,'as_of':two['as_of'],'fetched_at':two['fetched_at'],'provider':'feed'}
        self.assertIsNone(same_book_history(self.root,self.event,'A','FanDuel',self.now.isoformat()))
        self.event['books']['FanDuel']['fetched_at']=(self.now+timedelta(seconds=1)).isoformat()
        self.assertIsNone(same_book_history(self.root,self.event,'A','FanDuel',self.now.isoformat()))


if __name__=='__main__':unittest.main()
