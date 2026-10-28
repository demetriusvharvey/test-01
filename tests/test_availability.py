import sqlite3
from contextlib import closing
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scripts.line_lab.availability import capture_nfl_injuries, estimate_play_rate, news_freshness, nfl_statuses_as_of, scenario_mixture, nfl_report_context


class AvailabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.now=datetime(2026,10,28,12,tzinfo=timezone.utc);self.start=self.now+timedelta(days=4)
        self.csv=('season,week,team,gsis_id,position,full_name,report_status,practice_status,date_modified\n'
                  '2026,8,MIN,00-001,QB,Test QB,Questionable,Limited,2026-10-28 10:00\n'
                  '2026,8,MIN,00-002,WR,Test WR,Out,Did Not Participate,2026-10-28 10:00\n')
    def tearDown(self):self.tmp.cleanup()
    def test_injury_context_is_week_matched_and_never_assumes_health_or_starters(self):
        self.assertEqual(capture_nfl_injuries(self.root,self.csv,2026,self.now.isoformat(),'sha'),2)
        event={'id':'nfl:2026-11-01:DET:MIN','league':'NFL','home':'MIN','away':'DET',
               'home_name':'Minnesota','away_name':'Detroit','starts_at':self.start.isoformat()}
        schedule='season,week,gameday,home_team,away_team\n2026,8,2026-11-01,MIN,DET\n'
        result=nfl_report_context(self.root,event,schedule,self.now.isoformat(),self.now.isoformat())
        self.assertEqual(len(result['teams']['home']['entries']),2)
        self.assertEqual(result['teams']['home']['entries'][0]['position'],'QB')
        self.assertEqual(result['teams']['away']['entries'],[])
        self.assertEqual(result['starter_status'],'unconfirmed');self.assertFalse(result['used_in_prediction'])
        self.assertIsNone(nfl_report_context(self.root,event,schedule,(self.now+timedelta(hours=1)).isoformat(),self.now.isoformat()))
    def test_nfl_injuries_use_observation_time_and_age(self):
        self.assertEqual(capture_nfl_injuries(self.root,self.csv,2026,self.now.isoformat(),'sha'),2)
        self.assertEqual(capture_nfl_injuries(self.root,self.csv,2026,self.now.isoformat(),'sha'),0)
        self.assertEqual(nfl_statuses_as_of(self.root,2026,8,'MIN',(self.now-timedelta(seconds=1)).isoformat(),self.start.isoformat()),{})
        rows=nfl_statuses_as_of(self.root,2026,8,'MIN',(self.now+timedelta(hours=1)).isoformat(),self.start.isoformat())
        self.assertEqual(rows['00-001']['report_status'],'questionable')
        self.assertEqual(rows['00-001']['source_modified_raw'],'2026-10-28 10:00')
        self.assertEqual(nfl_statuses_as_of(self.root,2026,8,'MIN',(self.now+timedelta(hours=31)).isoformat(),self.start.isoformat()),{})
        with closing(sqlite3.connect(self.root/'observations/nfl_availability/2026-10-28.sqlite')) as db:
            with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM injury_observations')
    def test_conflicting_simultaneous_status_is_unknown(self):
        data=self.csv+'2026,8,MIN,00-001,QB,Test QB,Out,Did Not Participate,2026-10-28 10:01\n'
        capture_nfl_injuries(self.root,data,2026,self.now.isoformat(),'sha')
        value=nfl_statuses_as_of(self.root,2026,8,'MIN',self.now.isoformat(),self.start.isoformat())['00-001']
        self.assertTrue(value['status_conflict']);self.assertIsNone(value['report_status'])
    def test_play_rate_requires_prior_verified_participation(self):
        records=[]
        for i in range(4):
            start=self.now+timedelta(days=i)
            records.append({'game_id':str(i),'player_id':'p','report_observed_at':(start-timedelta(hours=1)).isoformat(),
              'starts_at':start.isoformat(),'participation_observed_at':(start+timedelta(hours=3)).isoformat(),
              'played':i%2,'status':'questionable','rights_verified':True})
        cutoff=(self.now+timedelta(days=2,hours=4)).isoformat()
        fit=estimate_play_rate(records,'questionable',cutoff,min_records=3)
        self.assertEqual(fit['bucket_n'],3);self.assertFalse(fit['promoted'])
        records[0]['report_observed_at']=(self.now+timedelta(hours=1)).isoformat()
        self.assertIsNone(estimate_play_rate(records,'questionable',cutoff,min_records=3))
    def test_explicit_scenarios_cannot_hide_missing_player_effects(self):
        scenarios=[{'weight':.75,'unavailable_players':[]},{'weight':.25,'unavailable_players':['star']}]
        result=scenario_mixture(.6,scenarios,{'star':-.5},self.now.isoformat(),self.now.isoformat())
        self.assertLess(result['expected_probability'],.6);self.assertGreater(result['scenario_variance'],0)
        self.assertFalse(result['staking_allowed'])
        self.assertIsNone(scenario_mixture(.6,scenarios,{},self.now.isoformat(),self.now.isoformat()))
        self.assertIsNone(scenario_mixture(.6,scenarios,{'star':-.5},self.start.isoformat(),self.now.isoformat()))
        scenarios[0]['weight']=.5
        self.assertIsNone(scenario_mixture(.6,scenarios,{'star':-.5},self.now.isoformat(),self.now.isoformat()))
    def test_news_after_quote_is_a_warning_not_a_stake_signal(self):
        self.assertEqual(news_freshness(self.now.isoformat(),(self.now-timedelta(hours=1)).isoformat(),self.now.isoformat()),'news_newer_than_quote')
        self.assertEqual(news_freshness(self.start.isoformat(),self.now.isoformat(),self.now.isoformat()),'unknown')


if __name__=='__main__':unittest.main()
