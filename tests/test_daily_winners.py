import unittest
from datetime import date,datetime,timedelta,timezone
from scripts.line_lab.winners import make_daily_winners,render_winners
from scripts.line_lab.ledger import grade_ledger
from scripts.line_lab.ledger_v2 import validate_transition


class WinnerForecastTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,28,15,tzinfo=timezone.utc)
        self.model={'ratings':{'A':1800,'B':1300,'C':1600,'D':1400,'E':1501,'F':1500,'G':1900,'H':1250},
                    'last':{},'margins':{},'home_advantage':40,'rest_weight':0,'form_weight':0,
                    'source_hashes':{'2025-26':'abc'}}
        self.scheduled=[{'id':f'nba:2026-10-28:{away}:{home}','league':'NBA','home':home,'away':away,
                         'starts_at':(self.now+timedelta(hours=3)).isoformat(),'books':{}}
                        for home,away in (('A','B'),('C','D'),('E','F'),('G','H'))]

    def test_top_winners_with_no_odds_and_immutable_daily_cap(self):
        picks=make_daily_winners(self.scheduled,{'NBA':self.model},self.now,[])
        self.assertEqual(len(picks),3)
        self.assertEqual([x['team'] for x in picks],['G','A','C'])
        self.assertEqual(picks,make_daily_winners(self.scheduled,{'NBA':self.model},self.now,[]))
        self.assertEqual(make_daily_winners(self.scheduled,{'NBA':self.model},self.now+timedelta(hours=1),picks),[])
        self.assertTrue(validate_transition(picks,picks))
        board={'games':self.scheduled,'history':[],'errors':[]}
        render_winners(board,picks,self.now,{'NBA':self.model})
        self.assertEqual(len(board['picks']),3)
        self.assertEqual(board['picks'][0]['prediction_integrity'],'verified')
        self.assertIsNone(board['accuracy']['percent'])
        self.assertTrue(all(x['books'][0]['odds'] is None for x in board['picks']))
        self.assertEqual(board['games'][0]['predicted_winner'],'A')

    def test_price_cannot_change_winner_and_pregame_forecast_is_frozen(self):
        first=make_daily_winners(self.scheduled,{'NBA':self.model},self.now,[])
        self.scheduled[0]['books']={'FanDuel':{'home':-10000,'away':+5000,'as_of':self.now.isoformat()}}
        self.assertEqual(first,make_daily_winners(self.scheduled,{'NBA':self.model},self.now,[]))
        changed=[dict(x) for x in first]
        changed[0]['team']='wrong'
        with self.assertRaises(ValueError):validate_transition(first,changed)

    def test_only_confirmed_final_grades_saved_winner(self):
        picks=make_daily_winners(self.scheduled,{'NBA':self.model},self.now,[])
        self.assertEqual(grade_ledger(picks,[],self.now),0)
        g=picks[0]
        final={'id':g['id'],'home':'G','away':'H','home_score':100,'away_score':110}
        self.assertEqual(grade_ledger(picks,[final],self.now+timedelta(hours=4)),1)
        self.assertEqual(g['outcome'],'loss')
        self.assertEqual(grade_ledger(picks,[final],self.now+timedelta(hours=5)),0)

    def test_missing_source_or_no_games_does_not_invent_winner(self):
        model={**self.model,'source_hashes':None}
        self.assertEqual(make_daily_winners(self.scheduled,{'NBA':model},self.now,[]),[])
        self.assertEqual(make_daily_winners([],{'NBA':self.model},self.now,[]),[])


if __name__=='__main__':unittest.main()
