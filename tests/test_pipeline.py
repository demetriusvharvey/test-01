import unittest
from datetime import date, datetime, timedelta, timezone
from scripts.pipeline import (parse_book_html, parse_nba_csv, parse_nfl_locations, build_ratings,
                              grade_ledger, build_market, choose_candidates, game_id, render_board, append_referee_assignments,
                              feature_passes, parse_espn_results, apply_same_day_finals, backfill_initial_books)

class PipelineTests(unittest.TestCase):
    def setUp(self): self.now=datetime(2026,10,28,1,30,tzinfo=timezone.utc)
    def test_parse_sportsbook_quotes_with_timestamp(self):
        html='''<div>Last updated: October 28, 2026 at 1:00 AM UTC</div><table><tr><th>Matchup (away @ home)</th><th>Time</th><th>Away ML</th><th>Home ML</th></tr><tr><td>Portland Trail Blazers @ Los Angeles Lakers</td><td>Oct 27, 11:10 PM EDT</td><td>+108</td><td>-126 ★</td></tr></table>'''
        rows,stamp=parse_book_html(html,'FanDuel','NBA',self.now)
        self.assertEqual(rows[0]['home_odds'],-126)
        self.assertEqual(rows[0]['id'],'nba:2026-10-27:POR:LAL')
        self.assertEqual(stamp.hour,1)
        with self.assertRaises(ValueError): parse_book_html(html.replace('Last updated:', 'No timestamp:'),'FanDuel','NBA',self.now)
    def test_training_avoids_same_day_future_data(self):
        games=[{'id':'1','league':'NBA','date':date(2026,10,26),'season':'2026-27','home':'LAL','away':'POR','home_score':100,'away_score':90,'neutral':False},{'id':'2','league':'NBA','date':date(2026,10,27),'season':'2026-27','home':'LAL','away':'POR','home_score':50,'away_score':130,'neutral':False}]
        model=build_ratings(games,date(2026,10,27),'NBA')
        self.assertGreater(model['ratings']['LAL'],1500)
        self.assertEqual(model['last']['LAL'],date(2026,10,26))
    def test_immutable_predictions_are_graded_once_and_ties_void(self):
        pick={'id':'nfl:2026-10-27:A:B','team_code':'B','outcome':'pending','probability':.6}
        final={'id':pick['id'],'home':'B','away':'A','home_score':20,'away_score':10}
        self.assertEqual(grade_ledger([pick],[final],self.now),1)
        self.assertEqual(pick['outcome'],'win')
        final['home_score']=0
        self.assertEqual(grade_ledger([pick],[final],self.now),0)
        self.assertEqual(pick['probability'],.6)
        tied={'id':'tied','team_code':'A','outcome':'pending'}
        grade_ledger([tied],[{'id':'tied','home':'B','away':'A','home_score':17,'away_score':17}],self.now)
        self.assertEqual(tied['outcome'],'void')
    def test_stale_odds_are_not_used(self):
        item={'id':'a','league':'NBA','home':'LAL','away':'POR','home_name':'Los Angeles Lakers','away_name':'Portland Trail Blazers','starts_at':(self.now+timedelta(hours=2)).isoformat(),'book':'FanDuel','home_odds':-126,'away_odds':108,'as_of':(self.now-timedelta(hours=3)).isoformat()}
        self.assertEqual(build_market([item],self.now),{})
    def test_prices_from_different_snapshot_windows_are_not_compared(self):
        base={'id':'a','league':'NBA','home':'LAL','away':'POR','home_name':'Los Angeles Lakers','away_name':'Portland Trail Blazers','starts_at':(self.now+timedelta(hours=2)).isoformat(),'home_odds':-126,'away_odds':108}
        rows=[{**base,'book':'FanDuel','as_of':(self.now-timedelta(hours=1)).isoformat()},
              {**base,'book':'DraftKings','as_of':self.now.isoformat()},
              {**base,'book':'Caesars','as_of':(self.now-timedelta(minutes=10)).isoformat()}]
        markets=build_market(rows,self.now)
        self.assertEqual(set(markets['a']['books']),{'DraftKings','Caesars'})
    def test_selection_is_frozen_once_and_shows_best_book(self):
        from scripts.pipeline import BOOKS
        start=self.now+timedelta(hours=2)
        event={'id':'nba:2026-10-27:POR:LAL','league':'NBA','home':'LAL','away':'POR','home_name':'Los Angeles Lakers','away_name':'Portland Trail Blazers','starts_at':start.isoformat(),'books':{}}
        for i,(_,name) in enumerate(BOOKS[:4]):
            event['books'][name]={'home':-105 if i==2 else -110,'away':-110,'as_of':self.now.isoformat()}
        model={'ratings':{'LAL':1800,'POR':1300},'last':{'LAL':date(2026,10,25),'POR':date(2026,10,23)},'home_advantage':55,'rest_weight':8}
        markets={event['id']:event}; models={'NBA':model}
        picks=choose_candidates(markets,models,self.now,[])
        self.assertEqual(len(picks),1)
        self.assertEqual(picks[0]['team_code'],'LAL')
        self.assertEqual(picks[0]['initial_best_odds'],-105)
        self.assertEqual(choose_candidates(markets,models,self.now,picks),[])
        self.assertEqual(render_board(markets,picks,self.now,[])['picks'],[])
        self.assertFalse(render_board(markets,picks,self.now,[])['history'][0]['recommendation_eligible'])
        picks[0]['validated_selection']=True
        board=render_board(markets,picks,self.now,[])
        self.assertEqual(board['picks'][0]['best'],-105)
        self.assertEqual(len(board['picks'][0]['books']),6)
        self.assertAlmostEqual(board['picks'][0]['retail_reference_probability'],.5)
        self.assertAlmostEqual(board['picks'][0]['retail_price_edge'],.5-105/205)
        self.assertIsNone(board['accuracy']['percent'])
        self.assertEqual(board['history'][0]['initial_books'][2]['odds'],-105)
        self.assertNotIn('probability',board['picks'][0])
        self.assertNotIn('probability',board['history'][0])
        self.assertNotIn('edge',board['history'][0])
        event['books']['BetMGM']['home']=-125
        updated=render_board(markets,picks,self.now,[])
        self.assertEqual(updated['history'][0]['initial_books'][2]['odds'],-105)
        self.assertNotEqual(updated['picks'][0]['books'][2]['odds'],-105)
    def test_features_require_improvement_on_both_historical_periods(self):
        def metric(score,count=250): return {'validation_brier':score,'validation_count':count}
        baseline=metric(.240); improved=metric(.238); worse=metric(.241)
        self.assertTrue(feature_passes(baseline,improved,baseline,improved,200))
        self.assertFalse(feature_passes(baseline,improved,baseline,worse,200))
        self.assertFalse(feature_passes(baseline,worse,baseline,improved,200))
        self.assertFalse(feature_passes(baseline,improved,baseline,metric(.238,199),200))
    def test_legacy_quotes_require_exact_pick_time_and_best_price(self):
        pick={'id':'a','predicted_at':'at-pick','initial_best_odds':-125}
        snapshots=[{'id':'a','predicted_at':'wrong-time','initial_books':[{'name':'Book','odds':-125}]}]
        self.assertEqual(backfill_initial_books([pick],snapshots),0)
        snapshots[0]['predicted_at']='at-pick';snapshots[0]['initial_books'][0]['odds']=-126
        self.assertEqual(backfill_initial_books([pick],snapshots),0)
        snapshots[0]['initial_books'][0]['odds']=-125
        self.assertEqual(backfill_initial_books([pick],snapshots),1)
        self.assertEqual(backfill_initial_books([pick],snapshots),0)
    def test_only_confirmed_same_day_finals_update_team_ratings_once(self):
        payload={'events':[{'date':'2026-10-28T00:00:00Z','season':{'year':2027,'type':2},'competitions':[{'status':{'type':{'completed':True,'name':'STATUS_FINAL'}},'competitors':[{'homeAway':'home','team':{'displayName':'Los Angeles Lakers'},'score':'110'},{'homeAway':'away','team':{'displayName':'Portland Trail Blazers'},'score':'100'}]}]}]}
        finals=parse_espn_results(payload,'NBA')
        self.assertEqual(len(finals),1)
        model=build_ratings([],date(2026,10,27),'NBA')
        model['last_season']='2026-27'
        added=apply_same_day_finals({'NBA':model},finals+finals,date(2026,10,27),{},self.now)
        self.assertEqual(added['NBA'],1)
        self.assertGreater(model['ratings']['LAL'],1500)
        self.assertEqual(model['margins']['LAL'],[10])
        payload['events'][0]['competitions'][0]['status']['type']={'completed':False,'name':'STATUS_IN_PROGRESS'}
        self.assertEqual(parse_espn_results(payload,'NBA'),[])
    def test_referees_are_archived_without_duplicate_or_unverified_rows(self):
        history=[]
        report={'status':'ok','date_expected':'2026-10-27','games':[{'matchup':'Portland @ L.A. Lakers','crew_chief':'Scott Foster','referee':'Che Flores','umpire':'Nate Cearley'}]}
        self.assertEqual(append_referee_assignments(history,report,self.now),1)
        self.assertEqual(append_referee_assignments(history,report,self.now),0)
        report['status']='stale_or_date_unverified'
        self.assertEqual(append_referee_assignments(history,report,self.now),0)
        self.assertEqual(len(history),1)
    def test_nfl_neutral_is_read_from_schedule(self):
        csv='gameday,home_team,away_team,location\n2026-11-01,LA,NYG,Neutral\n'
        self.assertTrue(parse_nfl_locations(csv)['nfl:2026-11-01:NYG:LA'])

if __name__=='__main__': unittest.main()
