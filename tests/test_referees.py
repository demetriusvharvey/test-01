import unittest
from datetime import datetime,timedelta,timezone
from scripts.line_lab.referees import assignment_as_of, prospective_effect, retrospective_nfl_summary


class RefereeTests(unittest.TestCase):
    def setUp(self):self.now=datetime(2026,10,28,12,tzinfo=timezone.utc)
    def test_only_earlier_announced_current_crew_is_used(self):
        history=[{'game_date':'2026-10-28','matchup':'A @ B','crew':['A','B','C'],'observed_at':(self.now-timedelta(hours=1)).isoformat()},
                 {'game_date':'2026-10-28','matchup':'A @ B','crew':['D','E','F'],'observed_at':(self.now+timedelta(hours=1)).isoformat()}]
        result=assignment_as_of(history,'2026-10-28','A @ B',self.now.isoformat(),(self.now+timedelta(hours=2)).isoformat())
        self.assertEqual(result['crew'],['A','B','C'])
        self.assertIsNone(assignment_as_of(history,'2026-10-28','C @ D',self.now.isoformat(),(self.now+timedelta(hours=2)).isoformat()))
    def test_descriptive_rate_includes_all_refs_and_no_promotion(self):
        row={'season':'2025','game_type':'REG','referee':'Ref A','home_score':'20','away_score':'10',
             'home_moneyline':'-120','away_moneyline':'110','location':'Home'}
        second={**row,'referee':'Ref B','home_score':'10','away_score':'20'}
        summary=retrospective_nfl_summary([row,second])
        self.assertEqual(summary['games'],2);self.assertEqual(len(summary['officials']),2)
        self.assertEqual(summary['officials'][0]['verdict'],'descriptive_only')
        self.assertIsNone(summary['officials'][0]['adjusted_p'])
        lo,hi=summary['officials'][0]['interval'];self.assertLess(lo,hi)
    def test_prospective_effect_needs_matching_pregame_times(self):
        start=self.now+timedelta(days=1)
        row={'game_id':'one','referee':'Ref A','rights_verified':True,'assignment_observed_at':(start-timedelta(hours=3)).isoformat(),
             'market_source_as_of':(start-timedelta(hours=3)).isoformat(),'market_fetched_at':(start-timedelta(hours=2)).isoformat(),
             'forecast_at':(start-timedelta(hours=1)).isoformat(),'starts_at':start.isoformat(),
             'final_observed_at':(start+timedelta(hours=3)).isoformat(),'home_win':1,'market_home_probability':.55}
        cutoff=(start+timedelta(days=1)).isoformat()
        value=prospective_effect([row,row],'Ref A',cutoff)
        self.assertEqual(value['n'],1);self.assertFalse(value['promoted'])
        row['market_fetched_at']=(start+timedelta(minutes=1)).isoformat()
        self.assertIsNone(prospective_effect([row],'Ref A',cutoff))


if __name__=='__main__':unittest.main()
