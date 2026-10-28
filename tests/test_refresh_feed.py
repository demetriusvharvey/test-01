import unittest
from datetime import date
from scripts.refresh_feed import parse_referees, parse_odds

class FeedTests(unittest.TestCase):
    def test_ref_assignment_requires_correct_date(self):
        html = '<h1>NBA Referee Assignments</h1><h3>October 27, 2026</h3><table><tr><th>Game</th><th>Crew Chief</th><th>Referee</th><th>Umpire</th><th>Alternate</th></tr><tr><td>Portland @ L.A. Lakers</td><td>Scott Foster</td><td>Che Flores</td><td>Nate Cearley</td><td></td></tr></table>'
        good = parse_referees(html, date(2026, 10, 27))
        self.assertEqual(good['status'], 'ok')
        self.assertEqual(good['games'][0]['crew_chief'], 'Scott Foster')
        self.assertEqual(parse_referees(html, date(2026, 10, 28))['status'], 'stale_or_date_unverified')
    def test_price_parser_requires_two_sides_at_fanduel(self):
        event = {'home_team':'H','away_team':'A','bookmakers':[{'key':'fanduel','last_update':'stamp','markets':[{'key':'h2h','outcomes':[{'name':'H','price':-164},{'name':'A','price':138}]}]}]}
        self.assertEqual(parse_odds([event], 'basketball_nba')[0]['price_home'], -164)
        event['bookmakers'][0]['markets'][0]['outcomes'].pop()
        self.assertEqual(parse_odds([event], 'basketball_nba'), [])

if __name__ == '__main__':
    unittest.main()
