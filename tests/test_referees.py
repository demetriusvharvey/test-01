import unittest
from datetime import datetime,timedelta,timezone
from scripts.line_lab.referees import assignment_as_of, prospective_effect, retrospective_nfl_summary, current_official_crew


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
    def test_current_nba_crew_requires_exact_match_and_prestart_observation(self):
        event={'league':'NBA','away':'POR','home':'LAL','starts_at':'2026-10-29T02:00:00+00:00'}
        report={'status':'ok','date_expected':'2026-10-28','games':[{'matchup':'Portland @ L.A. Lakers',
                'crew_chief':'One','referee':'Two','umpire':'Three'}]}
        row=current_official_crew(report,event,'2026-10-28T12:00:00+00:00','2026-10-28T13:00:00+00:00')
        self.assertEqual(row['crew_chief'],'One');self.assertFalse(row['used_in_prediction'])
        self.assertTrue(row['assignment_can_change'])
        self.assertIsNone(current_official_crew(report,event,'2026-10-28T14:00:00+00:00','2026-10-28T13:00:00+00:00'))
        report['games'][0]['matchup']='Portland @ Los Angeles'
        self.assertIsNone(current_official_crew(report,event,'2026-10-28T12:00:00+00:00','2026-10-28T13:00:00+00:00'))
        report['games'][0]['matchup']='Portland @ L.A. Lakers';report['games'].append(dict(report['games'][0]))
        self.assertIsNone(current_official_crew(report,event,'2026-10-28T12:00:00+00:00','2026-10-28T13:00:00+00:00'))


if __name__=='__main__':unittest.main()
