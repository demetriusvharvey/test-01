import copy,json,sqlite3,tempfile,unittest
from datetime import date,datetime,timedelta,timezone
from scripts.line_lab.production import decision,metrics,archive_forecasts,apply_pipeline,legacy_metrics
from scripts.line_lab.league_forecast import examples,infer
from scripts.line_lab.ledger_v2 import snapshot_hash
from scripts.line_lab.espn_injuries import parse
from scripts.line_lab.forecast_data import nfl_team_stats

NOW='2026-10-31T18:00:00+00:00'
START='2026-10-31T23:00:00+00:00'

class ProductionDecisionTests(unittest.TestCase):
    def setUp(self):
        self.event={'id':'nba:2026-10-31:BOS:NYK','league':'NBA','starts_at':START,'home':'NYK','away':'BOS',
                    'books':{'FanDuel':{'home':-150,'away':130,'as_of':NOW,'fetched_at':NOW,'provider':'manual-verified'}}}
        self.f={'home_probability':.8,'artifact_hash':'a','predicted_at':NOW,'availability_used':True,
                'probability_lower_bound':.72,'probability_upper_bound':.88,
                'availability':{'verified':True,'incomplete':False,'observed_at':NOW}}
        self.v={'betting_approved':True,'artifact_hash':'a','league':'NBA','out_of_sample_games':500,
                'calibration_passed':True,'positive_edge_validated':True,'evidence_hash':'e','evaluated_at':NOW,
                'uncertainty_validated':True}

    def test_real_edge_and_negative_ev(self):
        r=decision(self.f,self.event,NOW,self.v)
        self.assertTrue(r['eligible']);self.assertAlmostEqual(r['pricing']['break_even'],.6)
        self.assertAlmostEqual(r['pricing']['proportional_no_vig'],.6/(.6+100/230))
        self.f.update(home_probability=.55,probability_lower_bound=.51)
        r=decision(self.f,self.event,NOW,self.v)
        self.assertFalse(r['eligible']);self.assertLess(r['pricing']['estimated_ev'],0)

    def test_zero_picks_for_missing_stale_future_or_unverified_prices(self):
        for change in ({'as_of':'2026-10-31T16:00:00+00:00'}, {'as_of':'2026-10-31T19:00:00+00:00'}, {'fetched_at':None}, {'provider':None}):
            event=copy.deepcopy(self.event);event['books']['FanDuel'].update(change)
            self.assertFalse(decision(self.f,event,NOW,self.v)['eligible'])
        self.event['books']={};self.assertFalse(decision(self.f,self.event,NOW,self.v)['eligible'])

    def test_missing_injury_qb_uncertainty_validation_and_future_start(self):
        for key in ('availability','probability_lower_bound','availability_used'):
            f=copy.deepcopy(self.f);f.pop(key);self.assertFalse(decision(f,self.event,NOW,self.v)['eligible'])
        self.assertFalse(decision(self.f,self.event,NOW,{})['eligible'])
        self.event['league']='NFL';self.v['league']='NFL'
        self.assertIn('starting_quarterbacks_unconfirmed',decision(self.f,self.event,NOW,self.v)['reasons'])
        self.event['starts_at']=NOW;self.assertFalse(decision(self.f,self.event,NOW,self.v)['eligible'])

    def test_validation_is_bound_to_exact_artifact_and_league(self):
        self.v['artifact_hash']='b';self.assertFalse(decision(self.f,self.event,NOW,self.v)['eligible'])
        self.v['artifact_hash']='a';self.v['league']='NFL';self.assertFalse(decision(self.f,self.event,NOW,self.v)['eligible'])
        self.v['league']='NBA';self.v['evaluated_at']=START
        self.assertFalse(decision(self.f,self.event,NOW,self.v)['eligible'])

class FeatureTests(unittest.TestCase):
    def games(self,league='NBA'):
        return [{'id':f'{league.lower()}:2026-10-{i:02}:A:B','league':league,'date':date(2026,10,i),
                 'home':'B','away':'A','home_score':100+i,'away_score':90,'season':'2026-27' if league=='NBA' else '2026','neutral':False}
                for i in range(1,20)]
    def test_later_and_same_day_results_cannot_change_earlier_features(self):
        gs=self.games();before=examples(gs,'NBA');gs[-1]['home_score']=400
        after=examples(gs,'NBA');self.assertEqual(before[-1]['vector'],after[-1]['vector'])
        self.assertLess(before[-1]['feature_cutoff'],before[-1]['date'])
        self.assertEqual(before[:-1],after[:-1])
    def test_duplicates_and_league_separation(self):
        gs=self.games();self.assertEqual(examples(gs+[gs[0]],'NBA'),examples(gs,'NBA'))
        bad={**gs[0],'home_score':0}
        with self.assertRaises(ValueError):examples(gs+[bad],'NBA')
        self.assertEqual(examples(gs+self.games('NFL'),'NBA'),examples(gs,'NBA'))
        self.assertTrue(examples(self.games('NFL'),'NFL'))
    def test_artifact_hash_and_training_cutoff(self):
        row=examples(self.games(),'NBA')[-1]
        artifact={'league':'NBA','model_version':'test','exported_at':NOW,'training_cutoff':'2026-09-01',
                  'components':{},'weights':{'elo':1},'calibration':{'intercept':0,'weight':1},
                  'calibration_status':'retrospective_only','validation':{}}
        artifact['artifact_hash']=snapshot_hash(artifact)
        self.assertAlmostEqual(infer(artifact,row,NOW)['home_probability'],row['elo'])
        artifact['training_cutoff']=row['date']
        with self.assertRaises(ValueError):infer(artifact,row,NOW)
        artifact['training_cutoff']='2026-09-02'
        with self.assertRaises(ValueError):infer(artifact,row,NOW)
    def test_nfl_epa_parser(self):
        text='season_type,play_type,qb_kneel,qb_spike,game_date,posteam,defteam,epa,success\n'
        text+='REG,pass,0,0,2026-10-01,BUF,NYJ,0.4,1\n'*10
        text+='REG,run,0,0,2026-10-01,NYJ,BUF,-0.2,0\n'*10
        stats=nfl_team_stats(text);self.assertAlmostEqual(stats[(date(2026,10,1),'BUF')][0],.4)
        self.assertAlmostEqual(stats[(date(2026,10,1),'BUF')][1],-.2)

class InjuryTests(unittest.TestCase):
    def payload(self,status='Out',team='NYK'):
        return {'status':'success','timestamp':NOW,'injuries':[{'displayName':'New York Knicks','injuries':[
            {'status':status,'date':'2026-10-31T16:00:00Z','athlete':{'team':{'abbreviation':team},'position':{'abbreviation':'PG'},
             'links':[{'href':'https://www.espn.com/nba/player/_/id/123/player'}]}}]}]}
    def test_explicit_identity_team_and_uncertainty(self):
        row=parse(self.payload('Questionable'),'NBA',NOW)['players'][0]
        self.assertEqual(row['player_id'],'espn:123');self.assertEqual(row['status_code'],'questionable')
        self.assertEqual(parse(self.payload(),'NBA',NOW)['players'][0]['status_code'],'out')
        wrong=parse(self.payload(team='BOS'),'NBA',NOW)
        self.assertEqual(wrong['players'],[]);self.assertEqual(wrong['parse_errors'],1)
    def test_missing_stale_future_and_unknown(self):
        with self.assertRaises(ValueError):parse({},'NBA',NOW)
        for stamp in ('2026-10-31T17:00:00Z','2026-10-31T19:00:00Z'):
            p=self.payload();p['timestamp']=stamp
            with self.assertRaises(ValueError):parse(p,'NBA',NOW)
        p=parse(self.payload('Unknown'),'NBA',NOW);self.assertFalse(p['complete_availability']);self.assertEqual(p['players'],[])

class ArchiveTests(unittest.TestCase):
    def test_immutable_forecasts_grade_first_prediction_and_no_fabricated_roi(self):
        f={'id':'nba:2026-10-31:BOS:NYK','artifact_hash':'a','model_version':'m','starts_at':START,
           'predicted_at':NOW,'home_probability':.8,'baseline_elo_probability':.6}
        with tempfile.TemporaryDirectory() as root:
            archive_forecasts(root,[f],[],NOW)
            other={**f,'predicted_at':'2026-10-31T18:10:00+00:00','home_probability':.2}
            archive_forecasts(root,[other],[],other['predicted_at'])
            final={'id':f['id'],'home_score':90,'away_score':100}
            r=archive_forecasts(root,[],[final],'2026-11-01T03:00:00Z')
            self.assertEqual(r['snapshots'],2);self.assertEqual(r['models']['m:a']['losses'],1)
            self.assertAlmostEqual(r['models']['m:a']['brier'],.64)
            with sqlite3.connect(root+'/observations/production_forecasts/ledger.sqlite') as db:
                with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM forecasts')
                with self.assertRaises(sqlite3.IntegrityError):db.execute('UPDATE outcomes SET payload="{}"')
    def test_metrics_denominator_and_home_probability_orientation(self):
        rows=[{'probability':.8,'outcome':'loss'},{'probability':.6,'outcome':'win'}, {'probability':.9,'outcome':'pending'}]
        m=metrics(rows);self.assertEqual(m['sample_size'],2);self.assertEqual(m['accuracy'],.5)
        self.assertEqual(metrics([{'probability':.2,'outcome':'loss'}])['accuracy'],1.)
        self.assertIsNone(metrics([])['brier'])

class IntegrationTests(unittest.TestCase):
    def test_production_entry_never_forces_top_three(self):
        from scripts.line_lab.winners import make_daily_winners
        self.assertEqual(make_daily_winners([{'id':'x'}],{},datetime.fromisoformat(NOW),[]),[])

    def test_latest_injury_fingerprint_change_preserves_original(self):
        f={'id':'nba:2026-10-31:BOS:NYK','artifact_hash':'a','model_version':'m','starts_at':START,
           'predicted_at':NOW,'home_probability':.8,'availability':{'status_fingerprint':'one'}}
        with tempfile.TemporaryDirectory() as root:
            archive_forecasts(root,[f],[],NOW)
            new={**f,'predicted_at':'2026-10-31T18:10:00Z','availability':{'status_fingerprint':'two'}}
            archive_forecasts(root,[new],[],new['predicted_at'])
            self.assertTrue(new['injury_changed_since_previous_forecast'])
            with sqlite3.connect(root+'/observations/production_forecasts/ledger.sqlite') as db:
                original=json.loads(db.execute('SELECT payload FROM forecasts ORDER BY rowid LIMIT 1').fetchone()[0])
            self.assertEqual(original['availability']['status_fingerprint'],'one')

    def test_failed_refresh_does_not_restore_stale_recommendations(self):
        from scripts.line_lab.board_freshness import protect_last_success
        old={'generated_at':NOW,'games':[{'id':'x'}],'picks':[{'starts_at':START}],
             'selection_policy':{'recommendations':1},'accuracy':{'wins':5,'losses':4}}
        current={'generated_at':NOW,'games':[],'picks':[],'selection_policy':{'recommendations':0},
                 'errors':['NBA score source unavailable','NFL score source unavailable'],
                 'accuracy':{'wins':5,'losses':5}}
        b=protect_last_success(current,old,'2026-10-31T18:10:00Z')
        self.assertEqual(b['picks'],[]);self.assertEqual(b['accuracy']['losses'],5)

    def test_same_teams_separate_leagues_do_not_share_models_or_venue_defaults(self):
        board={'games':[{'id':'nfl:2026-10-31:BUF:NYJ','league':'NFL','starts_at':START,'home':'Jets','away':'Bills','predicted_winner':'Jets'}],
               'errors':[],'picks':[]}
        apply_pipeline(board,{},[],NOW)
        self.assertEqual(board['games'][0]['forecast_status'],'venue_status_unverified')
        self.assertNotIn('predicted_winner',board['games'][0])
        self.assertEqual(board['picks'],[])

    def test_priced_nfl_slate_retains_schedule_venue_metadata(self):
        from scripts.line_lab.report import render_board
        event={'id':'nfl:2026-10-31:BUF:NYJ','league':'NFL','starts_at':START,
               'home_name':'Jets','away_name':'Bills','books':{}}
        for neutral in (True,False):
            scheduled=[{'id':event['id'],'league':'NFL','starts_at':START,'home':'Jets','away':'Bills','neutral':neutral}]
            b=render_board({event['id']:event},[],datetime.fromisoformat(NOW),[],scheduled=scheduled)
            self.assertIs(b['games'][0]['neutral'],neutral)

    def test_benchmark_and_candidate_are_scored_on_frozen_matched_games(self):
        f={'id':'nba:2026-10-31:BOS:NYK','artifact_hash':'a','model_version':'m','starts_at':START,
           'predicted_at':NOW,'home_probability':.8,'baseline_elo_probability':.6,
           'research_model':{'artifact_hash':'c','model_identity_hash':'fixed','model_version':'challenger','home_probability':.3}}
        with tempfile.TemporaryDirectory() as root:
            archive_forecasts(root,[f],[],NOW)
            report=archive_forecasts(root,[],[{'id':f['id'],'home_score':100,'away_score':90}], '2026-11-01T03:00:00Z')
            self.assertEqual(report['models']['challenger:fixed']['sample_size'],1)
            self.assertAlmostEqual(report['models']['challenger:fixed']['brier'],.49)
            self.assertAlmostEqual(report['models']['m:a']['matched_elo']['brier'],.16)

if __name__=='__main__':unittest.main()
