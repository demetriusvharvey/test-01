import csv
import gzip
import io
import json
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from scripts.line_lab.backfill import archive_asset, catalog
from scripts.line_lab.history import append_observations, finalize_closing_proxies, valid_observation
from scripts.line_lab.ingest import parse_book_html
from scripts.line_lab.odds_api import parse_odds_api, record_call, should_call
from scripts.line_lab.quality import validate_and_deduplicate, reconcile_quotes
from scripts.line_lab.model import train_model
from scripts.line_lab.heartbeat import record_run
from scripts.line_lab.ingest import parse_espn_starts

FIXTURES=Path(__file__).parent/'fixtures'
NOW=datetime(2026,10,28,1,30,tzinfo=timezone.utc)

class StorageAndSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        data=json.loads((FIXTURES/'the_odds_api_nba.json').read_text())
        self.events=parse_odds_api(data,'NBA',NOW.isoformat())
    def tearDown(self): self.tmp.cleanup()
    def test_both_provider_formats_and_book_alias(self):
        html=(FIXTURES/'agentbets_nba.html').read_text()
        rows,asof=parse_book_html(html,'FanDuel','NBA',NOW)
        self.assertEqual(rows[0]['home_odds'],-126)
        self.assertEqual(rows[0]['id'],self.events[0]['id'])
        self.assertEqual({x['book'] for x in self.events},{'FanDuel','Caesars'})
        self.assertTrue(valid_observation(self.events[0],NOW.isoformat()))
    def test_incomplete_stale_future_and_timezone_ambiguity_rejected(self):
        e=self.events[0].copy()
        for key,value in [('home_odds',None),('away_odds',-80),('as_of','2026-10-28T01:00:00'),('as_of','2026-10-28T02:00:00+00:00'),('as_of','2026-10-27T22:00:00+00:00'),('starts_at','2026-10-28T01:00:00+00:00')]:
            bad=e.copy();bad[key]=value
            self.assertFalse(valid_observation(bad,NOW.isoformat()),(key,value))
    def test_duplicates_and_material_provider_disagreement_are_quarantined(self):
        one=self.events[0];duplicate=one.copy()
        good,warnings=validate_and_deduplicate([one,duplicate],NOW.isoformat())
        self.assertEqual(len(good),1);self.assertEqual(warnings,[])
        duplicate['home_odds']=-160
        good,warnings=validate_and_deduplicate([one,duplicate],NOW.isoformat())
        self.assertEqual(good,[]);self.assertTrue(warnings)
        other=one.copy();other['provider']='agentbets';other['home_odds']=-180
        selected,warnings=reconcile_quotes([one,other])
        self.assertEqual(selected,[]);self.assertTrue(warnings)
    def test_append_only_idempotency_and_honest_pregame_closing_proxy(self):
        event=self.events[0]
        self.assertEqual(append_observations(self.root,[event,event],NOW.isoformat()),1)
        path=self.root/'observations/odds/2026-10-28.sqlite'
        with sqlite3.connect(path) as db:
            with self.assertRaises(sqlite3.IntegrityError): db.execute('DELETE FROM snapshots')
            self.assertEqual(db.execute('SELECT count(*) FROM snapshots').fetchone()[0],1)
        later='2026-10-28T03:30:00+00:00'
        self.assertEqual(finalize_closing_proxies(self.root,later,{}),0)
        verified={event['id']:'2026-10-28T03:00:00+00:00'}
        self.assertEqual(finalize_closing_proxies(self.root,later,verified),1)
        self.assertEqual(finalize_closing_proxies(self.root,later,verified),0)
        with sqlite3.connect(self.root/'observations/closes/2026-10-28.sqlite') as db:
            label,gap=db.execute('SELECT label,observed_gap_seconds FROM closes').fetchone()
        self.assertEqual(label,'last_observed_pregame_not_certified_close');self.assertEqual(gap,5400)
    def test_optional_api_is_quota_limited(self):
        self.assertTrue(should_call(self.root,'NBA',NOW.isoformat()))
        record_call(self.root,'NBA',NOW.isoformat(),'ok',remaining=70,used=10,cost=1)
        self.assertFalse(should_call(self.root,'NBA',(NOW+timedelta(hours=5)).isoformat()))
        self.assertTrue(should_call(self.root,'NBA',(NOW+timedelta(hours=7)).isoformat()))
        record_call(self.root,'NFL',NOW.isoformat(),'ok',remaining=50,used=11,cost=1)
        self.assertFalse(should_call(self.root,'NBA',(NOW+timedelta(hours=7)).isoformat()))
    def test_missed_schedule_is_flagged_and_postponed_start_not_verified(self):
        self.assertFalse(record_run(self.root,NOW.isoformat()))
        self.assertTrue(record_run(self.root,(NOW+timedelta(hours=3)).isoformat()))
        data={'events':[{'date':'2026-10-28T03:00:00Z','competitions':[{'status':{'type':{'name':'STATUS_POSTPONED'}},'competitors':[{'homeAway':'home','team':{'displayName':'Los Angeles Lakers'}},{'homeAway':'away','team':{'displayName':'Portland Trail Blazers'}}]}]}]}
        self.assertEqual(parse_espn_starts(data,'NBA'),{})
    def test_backfill_retains_every_column_and_is_retrospective(self):
        spec={'dataset':'nfl_schedules','season':'all','url':'https://example.org/games.csv','attribution':'test','license':'CC-BY-4.0'}
        payload=b'game_id,referee,wind,roof,home_moneyline,home_qb_name\ngame1,Ref,9,dome,-110,QB\n'
        result=archive_asset(self.root,spec,payload,NOW.isoformat())
        self.assertEqual(result['columns'],6);self.assertEqual(result['rows'],1)
        self.assertFalse(archive_asset(self.root,spec,payload,NOW.isoformat())['new'])
        with sqlite3.connect(self.root/'observations/backfill/nfl_schedules/all.sqlite') as db:
            status,columns,content=db.execute('SELECT knowledge_status,columns_json,content_gzip FROM assets').fetchone()
        self.assertEqual(status,'retrospective_only');self.assertEqual(json.loads(columns)[1],'referee')
        self.assertEqual(gzip.decompress(content),payload)
        self.assertEqual(sum(x['dataset']=='nba_team_game_boxscores' for x in catalog()),5)
    def test_exploratory_features_do_not_enter_production(self):
        games=[]
        for season,year in [('2024',2024),('2025',2025)]:
            for i in range(201):
                games.append({'id':f'{season}-{i:03}', 'league':'NFL','date':date(year,9,1)+timedelta(days=i//14),
                              'season':season,'home':'A','away':'B','home_score':28 if i%2 else 14,
                              'away_score':14 if i%2 else 28,'neutral':False})
        model=train_model(games,date(2026,1,1),'NFL')
        self.assertEqual(model['rest_weight'],0);self.assertEqual(model['form_weight'],0)
        self.assertEqual(model['candidate_testing'],'disabled');self.assertFalse(model['candidate_passed'])
        self.assertIsNone(model['holdout_season'])

    def test_full_update_writes_board_and_private_snapshot_without_a_key(self):
        from scripts.line_lab import runner
        fixed=NOW
        class FixedDateTime(datetime):
            @classmethod
            def now(cls,tz=None): return fixed.astimezone(tz or timezone.utc)
        nba='game_date,home,team,opponent,points,opponent_points,season\n2026-10-26,true,LAL,POR,110,100,2026-27\n'
        nfl='season,game_type,gameday,home_team,away_team,home_score,away_score,location\n2025,REG,2025-09-07,NE,BUF,14,21,Home\n'
        book=(FIXTURES/'agentbets_nba.html').read_text()
        refs='<p>October 27, 2026</p><table><tr><th>Game</th><th>Crew Chief</th><th>Referee</th><th>Umpire</th></tr><tr><td>Portland @ Lakers</td><td>A</td><td>B</td><td>C</td></tr></table>'
        scoreboard={'events':[{'date':'2026-10-28T03:00:00Z','competitions':[{'competitors':[{'homeAway':'home','team':{'displayName':'Los Angeles Lakers'}},{'homeAway':'away','team':{'displayName':'Portland Trail Blazers'}}]}]}]}
        def fake_get(url,timeout=25):
            if 'boxscorelab.com' in url:return nba
            if 'nflverse/nfldata' in url:return nfl
            if 'agentbets.ai/odds/' in url:return book if url.endswith('/nba') else book.replace('Portland Trail Blazers @ Los Angeles Lakers','Unknown @ Unknown')
            if 'official.nba.com' in url:return refs
            if 'basketball/nba' in url:return json.dumps(scoreboard)
            if 'football/nfl' in url:return json.dumps({'events':[]})
            raise AssertionError(url)
        (self.root/'dist').mkdir();(self.root/'data').mkdir()
        with patch.object(runner,'ROOT',self.root),patch.object(runner,'datetime',FixedDateTime),patch.object(runner,'get',side_effect=fake_get),patch.dict('os.environ',{'PICKS_DATA_ROOT':str(self.root/'store')},clear=True):
            runner.main()
        board=json.loads((self.root/'dist/board.json').read_text())
        self.assertEqual(board['source_status']['the_odds_api'],'missing_api_key')
        self.assertEqual(board['source_status']['odds_history'],'available')
        with sqlite3.connect(self.root/'store/observations/odds/2026-10-28.sqlite') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM snapshots').fetchone()[0],6)
        self.assertFalse(any('probability' in p for p in board['picks']))

if __name__=='__main__': unittest.main()
