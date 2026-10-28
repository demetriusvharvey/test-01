import unittest
from datetime import date, datetime, timedelta, timezone
from scripts.pipeline import (parse_book_html, parse_nba_csv, parse_nfl_locations, build_ratings,
                              grade_ledger, build_market, choose_candidates, game_id)

class PipelineTests(unittest.TestCase):
    def setUp(self): self.now=datetime(2026,10,28,1,30,tzinfo=timezone.utc)
    def test_parse_sportsbook_quotes_with_timestamp(self):
        html='''<div>Last updated: October 28, 2026 at 1:00 AM UTC</div><table><tr><th>Matchup (away @ home)</th><th>Time</th><th>Away ML</th><th>Home ML</th></tr><tr><td>Portland Trail Blazers @ Los Angeles Lakers</td><td>Oct 27, 11:10 PM EDT</td><td>+108</td><td>-126 ★</td></tr></table>'''
        rows,stamp=parse_book_html(html,'FanDuel','NBA',self.now)
        self.assertEqual(rows[0]['home_odds'],-126)
        self.assertEqual(rows[0]['id'],'nba:2026-10-27:POR:LAL')
        self.assertEqual(stamp.hour,1)
        with self.assertRaises(ValueError): parse_book_html(html.replace('Last updated:', 'No timestamp:'),'FanDuel','NBA',self.now)
    def test_training_avoids_same_day_future_data(self):
        games=[{'id':'1','league':'NBA','date':date(2026,10,26),'season':'2026-27','home':'LAL','away':'POR','home_score':100,'away_score':90,'neutral':False},{'id':'2','league':'NBA','date':date(2026,10,27),'season':'2026-27','home':'LAL','away':'POR','home_score':50,'away_score':130,'neutral':False}]
        model=build_ratings(games,date(2026,10,27),'NBA')
        self.assertGreater(model['ratings']['LAL'],1500)
        self.assertEqual(model['last']['LAL'],date(2026,10,26))
    def test_immutable_predictions_are_graded_once_and_ties_void(self):
        pick={'id':'nfl:2026-10-27:A:B','team_code':'B','outcome':'pending','probability':.6}
        final={'id':pick['id'],'home':'B','away':'A','home_score':20,'away_score':10}
        self.assertEqual(grade_ledger([pick],[final],self.now),1)
        self.assertEqual(pick['outcome'],'win')
        final['home_score']=0
        self.assertEqual(grade_ledger([pick],[final],self.now),0)
        self.assertEqual(pick['probability'],.6)
        tied={'id':'tied','team_code':'A','outcome':'pending'}
        grade_ledger([tied],[{'id':'tied','home':'B','away':'A','home_score':17,'away_score':17}],self.now)
        self.assertEqual(tied['outcome'],'void')
    def test_stale_odds_are_not_used(self):
        item={'id':'a','league':'NBA','home':'LAL','away':'POR','home_name':'Los Angeles Lakers','away_name':'Portland Trail Blazers','starts_at':(self.now+timedelta(hours=2)).isoformat(),'book':'FanDuel','home_odds':-126,'away_odds':108,'as_of':(self.now-timedelta(hours=3)).isoformat()}
        self.assertEqual(build_market([item],self.now),{})
    def test_nfl_neutral_is_read_from_schedule(self):
        csv='gameday,home_team,away_team,location\n2026-11-01,LA,NYG,Neutral\n'
        self.assertTrue(parse_nfl_locations(csv)['nfl:2026-11-01:NYG:LA'])

if __name__=='__main__': unittest.main()
