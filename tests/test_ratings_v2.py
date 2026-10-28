import unittest
from datetime import datetime, timedelta, timezone
from scripts.line_lab.ratings_v2 import ShadowElo, _eligible_games, observed_schedule_context, walk_forward_carryover


class RatingTests(unittest.TestCase):
    def setUp(self):self.now=datetime(2026,10,28,15,tzinfo=timezone.utc)
    def test_margin_rating_updates_and_preserves_neutral_site(self):
        s=ShadowElo('NFL',k=24,home_advantage=42)
        prior=s.predict('A','B','2025',False)['home_probability']
        neutral=s.predict('A','B','2025',True)['home_probability']
        self.assertGreater(prior,neutral)
        s.update({'home':'A','away':'B','season':'2025','home_score':31,'away_score':10})
        self.assertGreater(s.ratings['A'],1500);self.assertLess(s.ratings['B'],1500)
        self.assertFalse(s.predict('A','B','2025')['promoted'])
        s.predict('A','B','2026');old=s.ratings['A']
        s.update({'home':'A','away':'B','season':'2025','home_score':0,'away_score':50})
        self.assertEqual(s.ratings['A'],old)  # a late past-season result cannot roll the state back
    def test_carryover_selection_only_uses_observed_earlier_finals(self):
        rows=[]
        for year in range(2022,2026):
            for i in range(2):
                start=datetime(year,10,1+i,tzinfo=timezone.utc)
                rows.append({'league':'NFL','game_id':f'{year}-{i}','season':str(year),'home':'A','away':'B',
                  'home_score':20+i*7,'away_score':21,'rights_verified':True,
                  'forecast_at':(start-timedelta(hours=1)).isoformat(),'starts_at':start.isoformat(),
                  'final_observed_at':(start+timedelta(hours=4)).isoformat()})
        fit=walk_forward_carryover(rows,'NFL',self.now.isoformat(),min_games=8,min_seasons=4)
        self.assertIn(fit['candidate_carryover'],(0,.25,.5,.75,1));self.assertFalse(fit['promoted'])
        later=dict(rows[0]);later['forecast_at']=(datetime(2022,9,30,23,30,tzinfo=timezone.utc)).isoformat()
        self.assertEqual(_eligible_games([later,*rows],'NFL',self.now.isoformat())[0]['forecast_at'],rows[0]['forecast_at'])
        rows[0]['final_observed_at']=(self.now+timedelta(hours=1)).isoformat()
        self.assertIsNone(walk_forward_carryover(rows,'NFL',self.now.isoformat(),min_games=8,min_seasons=4))
    def test_rest_travel_and_future_source_gates(self):
        denver={'lat':39.75,'lon':-105.0,'timezone':'America/Denver','observed_at':'2026-10-25T12:00:00+00:00'}
        minneapolis={'lat':44.98,'lon':-93.27,'timezone':'America/Chicago','observed_at':'2026-10-25T12:00:00+00:00','rights_verified':True}
        prior={'home':'DEN','away':'GSW','starts_at':'2026-10-27T02:00:00+00:00',
               'final_observed_at':'2026-10-27T05:00:00+00:00','venue':denver,'rights_verified':True}
        upcoming={'starts_at':'2026-10-29T00:00:00+00:00','venue':minneapolis}
        ctx=observed_schedule_context([prior],'GSW',self.now.isoformat(),upcoming)
        self.assertEqual(ctx['rest_days'],1);self.assertFalse(ctx['back_to_back'])
        self.assertEqual(ctx['utc_offset_change_hours'],1);self.assertGreater(ctx['venue_distance_miles'],500)
        self.assertEqual(ctx['travel_itinerary'],'unknown')
        minneapolis['observed_at']=(self.now+timedelta(seconds=1)).isoformat()
        self.assertIsNone(observed_schedule_context([prior],'GSW',self.now.isoformat(),upcoming))


if __name__=='__main__':unittest.main()
