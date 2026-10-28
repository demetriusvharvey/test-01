import unittest
from scripts.line_lab.watchlist import render_watchlist


class WatchlistTests(unittest.TestCase):
    def test_shows_requested_side_and_fresh_prices_without_creating_prediction(self):
        event={'id':'nba:2026-10-28:PHI:IND','league':'NBA','home':'IND','away':'PHI',
               'home_name':'Indiana Pacers','away_name':'Philadelphia 76ers',
               'starts_at':'2026-10-28T23:00:00+00:00',
               'books':{'FanDuel':{'home':180,'away':-215,'as_of':'2026-10-28T17:00:00+00:00'},
                        'DraftKings':{'home':160,'away':-200,'as_of':'2026-10-28T17:00:00+00:00'}}}
        request={'id':event['id'],'team_code':'PHI'}
        rows=render_watchlist({event['id']:event},[request,request],'2026-10-28T17:30:00+00:00')
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['team'],'Philadelphia 76ers')
        self.assertEqual(rows[0]['best'],-200);self.assertTrue(rows[0]['watching'])
        self.assertNotIn('outcome',rows[0]);self.assertNotIn('probability',rows[0])
        self.assertEqual(render_watchlist({event['id']:event},[request],'2026-10-28T23:00:00+00:00'),[])
        self.assertEqual(render_watchlist({event['id']:event},[{**request,'team_code':'LAL'}],'2026-10-28T17:30:00+00:00'),[])


if __name__=='__main__':unittest.main()
