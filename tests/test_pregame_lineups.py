import copy,json,sqlite3,tempfile,unittest
from datetime import datetime
from unittest.mock import patch
from scripts.line_lab.pregame_lineups import parse_summary,event_mapping,collect,archive
from scripts.line_lab.nfl_depth import explicit_espn_id,game_context,parse_depth
from tests import test_availability_integrity as fixtures

NOW='2026-11-01T19:00:00+00:00';START='2026-11-01T20:30:00+00:00'

class PregameLineupTests(unittest.TestCase):
    def event(self):return {'id':'nba:2026-11-01:BOS:ORL','league':'NBA','home':'ORL','away':'BOS','starts_at':START}
    def summary(self):
        teams=[{'homeAway':s,'team':{'abbreviation':t}} for s,t in [('home','ORL'),('away','BOS')]]
        state={'name':'STATUS_SCHEDULED','state':'pre','completed':False}
        return {'header':{'id':'123','competitions':[{'date':START,'status':{'type':state},'competitors':teams}]},
                'meta':{'gameState':'pre'},'boxscore':{'players':[
                    {'team':{'abbreviation':t},'statistics':[{'athletes':[
                        {'athlete':{'id':str(offset+i)},'starter':i<5} for i in range(8)]}]} for t,offset in [('ORL',100),('BOS',200)]]}}
    def scoreboard(self):
        return {'events':[{'id':'123','date':START,'status':{'type':{'name':'STATUS_SCHEDULED','state':'pre','completed':False}},
            'competitions':[{'competitors':[{'homeAway':'home','team':{'displayName':'Orlando Magic'}},
                                          {'homeAway':'away','team':{'displayName':'Boston Celtics'}}]}]}]}
    def test_provider_flags_are_observed_but_never_confirmed(self):
        r=parse_summary(self.summary(),self.event(),'123',NOW)
        self.assertEqual(r['lineup_status'],'listed_unconfirmed');self.assertEqual(r['teams']['home']['listed_count'],5)
        self.assertFalse(r['confirmed']);self.assertFalse(r['used_in_prediction']);self.assertFalse(r['training_eligible'])
        self.assertIsNone(r['source_timestamp']);self.assertEqual(r['observed_at'],NOW)
        self.assertEqual(len(r['source_sha256']),64)
    def test_missing_and_partial_lists_are_unknown(self):
        p=self.summary();p['boxscore']={}
        self.assertEqual(parse_summary(p,self.event(),'123',NOW)['lineup_status'],'unknown')
        p=self.summary();p['boxscore']['players'][0]['statistics'][0]['athletes'][0]['starter']=False
        self.assertEqual(parse_summary(p,self.event(),'123',NOW)['lineup_status'],'unknown')
    def test_completed_live_and_late_fetches_never_become_pregame_evidence(self):
        for state in ({'name':'STATUS_FINAL','state':'post','completed':True},{'name':'STATUS_IN_PROGRESS','state':'in','completed':False}):
            p=self.summary();p['header']['competitions'][0]['status']['type']=state
            with self.assertRaises(ValueError):parse_summary(p,self.event(),'123',NOW)
        with self.assertRaises(ValueError):parse_summary(self.summary(),self.event(),'123',START)
    def test_wrong_game_teams_start_and_future_source_are_rejected(self):
        p=self.summary();p['header']['id']='456'
        with self.assertRaises(ValueError):parse_summary(p,self.event(),'123',NOW)
        p=self.summary();p['header']['competitions'][0]['competitors'][0]['team']['abbreviation']='NYK'
        with self.assertRaises(ValueError):parse_summary(p,self.event(),'123',NOW)
        p=self.summary();p['header']['competitions'][0]['date']='2026-11-01T22:00:00Z'
        with self.assertRaises(ValueError):parse_summary(p,self.event(),'123',NOW)
        for stamp in (START,'2026-11-01T18:00:00Z'):
            p=self.summary();p['meta']['lastUpdatedAt']=stamp
            with self.assertRaises(ValueError):parse_summary(p,self.event(),'123',NOW)
    def test_conflicting_flags_or_cross_team_ids_stay_unknown(self):
        p=self.summary();a=p['boxscore']['players'][0]['statistics'][0]['athletes'];a.append({**a[0],'starter':False})
        self.assertEqual(parse_summary(p,self.event(),'123',NOW)['reason'],'conflicting_starter_evidence')
        p=self.summary();p['boxscore']['players'][1]['statistics'][0]['athletes'][0]['athlete']['id']='100'
        self.assertEqual(parse_summary(p,self.event(),'123',NOW)['reason'],'conflicting_starter_evidence')
    def test_event_mapping_requires_unique_scheduled_exact_match(self):
        p=self.scoreboard();self.assertEqual(event_mapping(p,[self.event()]),{self.event()['id']:'123'})
        other={**p['events'][0],'id':'456'};p['events'].append(other)
        self.assertEqual(event_mapping(p,[self.event()]),{})
        p=self.scoreboard();p['events'][0]['date']='2026-11-01T22:00:00Z'
        self.assertEqual(event_mapping(p,[self.event()]),{})
    def test_bounded_collection_and_append_only_provenance(self):
        event=self.event();calls=[]
        class FixedDateTime(datetime):
            @classmethod
            def now(cls,tz=None):return datetime.fromisoformat(NOW)
        def get(url,timeout):
            calls.append(url);return json.dumps(self.scoreboard() if 'scoreboard?' in url else self.summary())
        with tempfile.TemporaryDirectory() as root,patch('scripts.line_lab.pregame_lineups.datetime',FixedDateTime):
            r=collect([event],NOW,get,root);self.assertEqual(len(calls),2)
            self.assertEqual(r[event['id']]['lineup_status'],'listed_unconfirmed')
            with sqlite3.connect(root+'/observations/pregame_lineups/ledger.sqlite') as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0],1)
                with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM snapshots')
            calls.clear();r=collect([event],'2026-11-01T10:00:00Z',get,root)
            self.assertEqual(calls,[]);self.assertEqual(r[event['id']]['reason'],'outside_two_hour_collection_window')
    def test_unavailable_source_is_explicit_and_not_healthy(self):
        def get(*args):raise OSError('offline')
        r=collect([self.event()],NOW,get)
        self.assertEqual(r[self.event()['id']]['reason'],'source_event_mapping_unavailable')
        self.assertFalse(r[self.event()['id']]['confirmed'])

    def test_malformed_scoreboard_is_recorded_as_unknown(self):
        for payload in ([],{'events':[None,{'competitions':[None]}]}):
            def get(*args):return json.dumps(payload)
            r=collect([self.event()],NOW,get)
            self.assertEqual(r[self.event()['id']]['reason'],'source_event_mapping_unavailable')

    def test_stale_summary_keeps_requested_source_identity_without_claiming_lineups(self):
        p=self.summary();p['meta']['lastUpdatedAt']='2026-11-01T18:00:00Z'
        def get(url,timeout):return json.dumps(self.scoreboard() if 'scoreboard?' in url else p)
        r=collect([self.event()],NOW,get)[self.event()['id']]
        self.assertEqual(r['reason'],'summary_unavailable_or_rejected')
        self.assertEqual(r['source_event_id'],'123');self.assertTrue(r['source_url'].endswith('event=123'))
        self.assertFalse(r['confirmed'])

class QuarterbackIdentityTests(unittest.TestCase):
    def setup_context(self):
        f=fixtures.DepthTests();event=f.event();depth={'BUF':parse_depth(f.payload(),'BUF',fixtures.NOW)}
        return event,depth
    def test_explicit_id_join_and_conflict_quarantine(self):
        event,depth=self.setup_context()
        rows=[{'player_id':'provider-999','espn_athlete_id':'123','team_abbr':'BUF','status_code':'out','source_updated_at':fixtures.NOW}]
        payload={'sport':'football_nfl','observation_timestamp':fixtures.NOW,'players':rows}
        r=game_context(event,depth,payload,fixtures.NOW)['teams']['home']
        self.assertEqual(r['availability_status'],'out');self.assertEqual(r['matched_report_rows'],1)
        rows.append({**rows[0],'status_code':'available'})
        r=game_context(event,depth,payload,fixtures.NOW)['teams']['home']
        self.assertEqual(r['availability_status'],'unknown');self.assertEqual(r['availability_reason'],'conflicting_reported_statuses')
    def test_unqualified_provider_ids_and_mismatched_explicit_ids_are_not_coerced(self):
        self.assertIsNone(explicit_espn_id({'player_id':'123'}))
        self.assertIsNone(explicit_espn_id({'player_id':'espn:123','espn_athlete_id':'456'}))
        event,depth=self.setup_context()
        payload={'sport':'football_nfl','observation_timestamp':fixtures.NOW,'players':[
            {'player_id':'espn:123','espn_athlete_id':'456','team_abbr':'BUF','status_code':'available','source_updated_at':fixtures.NOW}]}
        r=game_context(event,depth,payload,fixtures.NOW)['teams']['home']
        self.assertEqual(r['availability_status'],'unknown');self.assertEqual(r['availability_reason'],'player_identity_conflict')
