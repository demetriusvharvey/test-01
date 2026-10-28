import unittest
from datetime import datetime,timedelta,timezone
from scripts.line_lab.market import moneyline_calculation,build_market


class MoneylineCalculationTests(unittest.TestCase):
    def test_negative_moneyline_returns(self):
        a=moneyline_calculation(-150,750,probability=.62,other_side=130)
        self.assertEqual(a['winning_profit'],500)
        self.assertEqual(a['total_payout'],1250)
        self.assertAlmostEqual(a['break_even'],.6)
        self.assertAlmostEqual(a['proportional_no_vig'],.6/(.6+100/230))
        self.assertEqual(moneyline_calculation(-200,750)['winning_profit'],375)

    def test_ev_is_not_win_probability(self):
        self.assertEqual(moneyline_calculation(150,100,probability=.5)['estimated_profit'],25)
        self.assertAlmostEqual(moneyline_calculation(150,100,probability=.5)['estimated_ev'],.25)

    def test_reject_invalid_values(self):
        for price,stake in ((-99,100),(0,100),(True,100),(150,0),(150,float('nan'))):
            with self.assertRaises(ValueError):moneyline_calculation(price,stake)

    def test_near_start_quote_can_be_displayed_without_becoming_eligible(self):
        now=datetime(2026,10,28,22,45,tzinfo=timezone.utc)
        event={'id':'nba:2026-10-28:PHI:IND','league':'NBA','home':'IND','away':'PHI',
               'home_name':'Indiana Pacers','away_name':'Philadelphia 76ers',
               'starts_at':(now+timedelta(minutes=15)).isoformat(),
               'as_of':(now-timedelta(minutes=5)).isoformat(),'book':'FanDuel',
               'home_odds':130,'away_odds':-150}
        self.assertEqual(build_market([event],now),{})
        self.assertEqual(build_market([event],now,min_lead_minutes=0)[event['id']]['books']['FanDuel']['away'],-150)


if __name__=='__main__':unittest.main()
