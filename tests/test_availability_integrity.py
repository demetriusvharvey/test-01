import copy
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from scripts.line_lab.espn_injuries import parse
from scripts.line_lab.nba_injury_feed import attach_nba_summaries
from scripts.line_lab.nfl_depth import parse_depth,collect_depth,game_context,team_url
from scripts.line_lab.production import decision,apply_pipeline
from scripts.line_lab.history import valid_observation
from scripts.line_lab.market import build_market
from tests import test_production_forecast as fixtures
NOW,START=fixtures.NOW,fixtures.START


class AvailabilityIntegrityTests(unittest.TestCase):
    def test_conflicting_statuses_are_quarantined_regardless_of_row_order(self):
        p=fixtures.InjuryTests().payload('Out')
        first=p['injuries'][0]['injuries'][0]
        second={**first,'status':'Questionable'}
        for rows in ([first,second],[second,first],[first,second,first]):
            p['injuries'][0]['injuries']=rows
            r=parse(p,'NBA',NOW)
            self.assertEqual(r['players'],[])
            self.assertEqual(r['conflicting_players'],1)
            self.assertGreater(r['parse_errors'],0)

    def test_partial_feed_cannot_become_complete_when_both_teams_have_entries(self):
        p=fixtures.InjuryTests().payload('Out')
        other=copy.deepcopy(p['injuries'][0]);other['displayName']='Boston Celtics'
        a=other['injuries'][0]['athlete'];a['id']='234';a['links']=[];a['team']['abbreviation']='BOS'
        p['injuries'].append(other)
        normalized=parse(p,'NBA',NOW)
        event={'id':'nba:2026-10-31:BOS:NYK','league':'NBA','home':'NYK','away':'BOS',
               'home_name':'New York Knicks','away_name':'Boston Celtics','starts_at':START}
        b={'picks':[{'id':event['id']}]}
        attach_nba_summaries(b,{event['id']:event},normalized,NOW)
        c=b['picks'][0]['nba_availability_context']
        self.assertTrue(all(v['report_present'] for v in c['teams'].values()))
        self.assertTrue(c['incomplete']);self.assertEqual(c['coverage_status'],'unverified')
        self.assertEqual(c['source_url'],normalized['source_url'])
        self.assertEqual(c['source_sha256'],normalized['source_sha256'])
        self.assertEqual(c['game_id'],event['id'])
        self.assertEqual(c['lineup_status'],'unknown')

    def test_same_player_on_multiple_teams_is_not_silently_assigned(self):
        p=fixtures.InjuryTests().payload('Out')
        other=copy.deepcopy(p['injuries'][0]);other['displayName']='Boston Celtics'
        other['injuries'][0]['athlete']['team']['abbreviation']='BOS'
        p['injuries'].append(other)
        r=parse(p,'NBA',NOW)
        self.assertEqual(r['players'],[]);self.assertGreater(r['parse_errors'],0)

    def test_malformed_rows_do_not_crash_the_fallback(self):
        p=fixtures.InjuryTests().payload();p['injuries'].extend([None,{'displayName':'unknown'}])
        p['injuries'][0]['injuries'].extend([None,{'athlete':[]}])
        r=parse(p,'NBA',NOW);self.assertEqual(r['count'],1);self.assertGreaterEqual(r['parse_errors'],4)


class QuoteIdentityTests(unittest.TestCase):
    def setUp(self):
        t=fixtures.ProductionDecisionTests();t.setUp();self.f,self.event,self.v=t.f,t.event,t.v

    def test_wrong_game_team_market_book_and_missing_identity_never_qualify(self):
        for key,value in [('game_id','nba:other'),('home_team','BOS'),('away_team','NYK'),
                          ('league','NFL'),('book','DraftKings'),('market','spreads')]:
            e=copy.deepcopy(self.event);e['books']['FanDuel'][key]=value
            r=decision(self.f,e,NOW,self.v)
            self.assertFalse(r['eligible']);self.assertIn('odds_identity_mismatch',r['reasons'])
        e=copy.deepcopy(self.event);e['books']['FanDuel'].pop('game_id')
        self.assertFalse(decision(self.f,e,NOW,self.v)['eligible'])

    def test_other_book_cannot_supply_a_fanduel_recommendation(self):
        self.event['books']['DraftKings']=self.event['books'].pop('FanDuel')
        r=decision(self.f,self.event,NOW,self.v)
        self.assertFalse(r['eligible']);self.assertIsNone(r['pricing'])

    def test_missing_availability_still_reports_independent_odds_and_lineup_failures(self):
        self.f.pop('availability');self.event['books']={}
        reasons=decision(self.f,self.event,NOW,self.v)['reasons']
        self.assertIn('injury_information_unverified',reasons)
        self.assertIn('starting_lineups_unconfirmed',reasons)
        self.assertIn('odds_missing_stale_or_unverified',reasons)
        self.assertNotIn('invalid_or_missing_input',reasons)

    def test_ingestion_checks_canonical_game_identity_and_preserves_quote_metadata(self):
        row={'id':self.event['id'],'league':'NBA','home':'NYK','away':'BOS','starts_at':START,
             'home_name':'Knicks','away_name':'Celtics','home_odds':-150,'away_odds':130,
             'book':'FanDuel','provider':'agentbets','as_of':NOW,'fetched_at':NOW,
             'provider_event_id':'source123','source_url':'https://agentbets.ai/odds/fanduel/nba'}
        self.assertTrue(valid_observation(row,NOW))
        for change in ({'home':'BOS','away':'NYK'},{'id':'nba:2026-10-30:BOS:NYK'},{'market':'spreads'}):
            self.assertFalse(valid_observation({**row,**change},NOW))
        e=build_market([row],datetime.fromisoformat(NOW))[row['id']]
        self.assertTrue(decision(self.f,e,NOW,self.v)['eligible'])
        self.assertEqual(e['books']['FanDuel']['provider_event_id'],'source123')


class DepthTests(unittest.TestCase):
    def payload(self,team='BUF'):
        return {'status':'success','timestamp':NOW,'team':{'abbreviation':team},
                'depthchart':[{'positions':{'qb':{'position':{'abbreviation':'QB'},
                            'athletes':[{'id':'123'},{'id':'456'}]}}}]}

    def event(self):
        return {'id':'nfl:2026-10-31:NYJ:BUF','league':'NFL','home':'BUF','away':'NYJ','starts_at':START}

    def test_depth_is_projected_and_absent_injury_is_unknown(self):
        b=parse_depth(self.payload(),'BUF',NOW);j=parse_depth(self.payload('NYJ'),'NYJ',NOW)
        r=game_context(self.event(),{'BUF':b,'NYJ':j},None,NOW)
        self.assertEqual(r['starter_status'],'projected');self.assertFalse(r['starting_quarterbacks_confirmed'])
        self.assertEqual(r['teams']['home']['availability_status'],'unknown')
        self.assertEqual(b['projected_player_id'],'espn:123');self.assertFalse(b['confirmed'])
        injuries={'sport':'football_nfl','observation_timestamp':NOW,'players':[
            {'player_id':'espn:123','team_abbr':'BUF','status_code':'out','source_updated_at':NOW}]}
        r=game_context(self.event(),{'BUF':b,'NYJ':j},injuries,NOW)
        self.assertEqual(r['teams']['home']['availability_status'],'out')
        self.assertEqual(r['teams']['away']['availability_status'],'unknown')
        injuries['observation_timestamp']='2026-10-31T16:00:00Z'
        self.assertEqual(game_context(self.event(),{'BUF':b},injuries,NOW)['teams']['home']['availability_status'],'unknown')

    def test_wrong_team_conflicting_depth_and_future_or_stale_source_are_rejected(self):
        for p in (self.payload('NYJ'),{**self.payload(),'timestamp':START},
                  {**self.payload(),'timestamp':'2026-10-31T16:00:00Z'}):
            with self.assertRaises(ValueError):parse_depth(p,'BUF',NOW)
        p=self.payload();p['depthchart'].append({'positions':{'qb':{'position':{'abbreviation':'QB'},'athletes':[{'id':'789'}]}}})
        with self.assertRaises(ValueError):parse_depth(p,'BUF',NOW)

    def test_espn_aliases_and_old_report_cannot_mark_qb_available(self):
        self.assertIn('/lar/',team_url('LA'));self.assertIn('/wsh/',team_url('WAS'))
        b=parse_depth(self.payload(),'BUF',NOW)
        injuries={'sport':'football_nfl','observation_timestamp':NOW,'players':[
            {'player_id':'espn:123','team_abbr':'BUF','status_code':'available','source_updated_at':'2026-10-28T16:00:00Z'}]}
        c=game_context(self.event(),{'BUF':b},injuries,NOW)['teams']['home']
        self.assertEqual(c['availability_status'],'unknown');self.assertEqual(c['availability_reason'],'report_stale')
        self.assertEqual(c['last_reported_status'],'available')

    def test_collect_is_bounded_cached_and_append_only(self):
        event=self.event();current=datetime.fromisoformat(NOW)
        class FixedDateTime(datetime):
            @classmethod
            def now(cls,tz=None):return current
        def get(url,timeout):return json.dumps(self.payload('BUF' if '/buf/' in url else 'NYJ'))
        with tempfile.TemporaryDirectory() as root,patch('scripts.line_lab.nfl_depth.datetime',FixedDateTime):
            d,errors=collect_depth([event,event],NOW,get,root)
            self.assertEqual(set(d),{'BUF','NYJ'});self.assertEqual(errors,[])
            def unexpected(*args):raise AssertionError('cache missed')
            again,errors=collect_depth([event],NOW,unexpected,root)
            self.assertEqual(d,again)
            with sqlite3.connect(root+'/observations/nfl_depth/ledger.sqlite') as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0],2)
                with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM snapshots')
            after=game_context(event,d,None,'2026-10-31T19:01:00Z')
            self.assertEqual(after['starter_status'],'unknown')
