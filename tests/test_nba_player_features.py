import unittest
from datetime import date,timedelta
from scripts.line_lab.nba_player_features import BOX_STATS,FEATURES,allocate_minutes,historical_features,current_summary,difference
from scripts.line_lab.nba_lineup import project_rotation
from scripts.line_lab.nba_rotation import parse_players
from scripts.line_lab.nba_scenarios import conditional_forecasts


class PlayerFeatureTests(unittest.TestCase):
    def fixture(self):
        day=date(2026,10,20);players=[];games=[]
        for i in range(4):
            games.append({'id':str(i),'date':day+timedelta(days=i),'league':'NBA','home':'PHI','away':'IND'})
            for team,offset in (('PHI',0),('IND',10)):
                for p in range(10):
                    players.append({'date':day+timedelta(days=i),'team':team,'player_id':str(p+offset),
                                    'minutes':24.,'points':10.,**{k:(10. if k=='blocks' and team=='PHI' and p==0 else 1.) for k in BOX_STATS}})
        return games,players

    def test_shared_training_and_inference_features_and_no_same_day_leakage(self):
        games,players=self.fixture();before=historical_features(games,players)
        self.assertNotIn('0',before)
        summaries={};now='2026-10-23T12:00:00+00:00';start='2026-10-24T00:00:00+00:00'
        for team,offset in (('PHI',0),('IND',10)):
            roster={'team':team,'player_ids':[str(p+offset) for p in range(10)],'verified':True,'source':'fixture','observed_at':now}
            statuses={'complete':True,'players':{},'observed_at':now}
            rotation=project_rotation(players,roster,statuses,now,start)
            summaries[team]=current_summary(players,rotation,now)
        self.assertEqual(before['3']['vector'],difference(summaries['PHI'],summaries['IND']))
        for r in players:
            if r['date']>=date(2026,10,23):r['blocks']=999.;r['points']=999.;r['team']='BOS'
        self.assertEqual(before,historical_features(games,players))

    def test_missing_metrics_are_unknown_and_minutes_are_conserved(self):
        parsed=parse_players('game_date,athlete_id,team_abbreviation,minutes,points\n2026-10-20,1,PHI,30,20\n')
        self.assertIsNone(parsed[0]['blocks'])
        games,players=self.fixture()
        for r in players:r['blocks']=None
        self.assertEqual(historical_features(games,players),{})
        estimates=[{'player_id':str(p),'weight':100. if p==0 else 1.} for p in range(14)]
        rotation=allocate_minutes(estimates)
        self.assertEqual(len(rotation),12)
        self.assertAlmostEqual(sum(p['minutes'] for p in rotation),240.)
        self.assertTrue(all(0<p['minutes']<=48 for p in rotation))

    def test_non_scoring_player_stats_change_injury_scenarios(self):
        games,players=self.fixture();now='2026-10-23T12:00:00+00:00'
        roster={team:{'team':team,'player_ids':[str(p+offset) for p in range(10)],'verified':True,'source':'fixture','observed_at':now}
                for team,offset in (('PHI',0),('IND',10))}
        event={'home':'PHI','away':'IND','starts_at':'2026-10-24T00:00:00+00:00'}
        model={'model_version':'nba-player-box-logistic-v1','exported_at':'2026-10-22T12:00:00+00:00','features':[str(p) for p in range(14)]+list(FEATURES)}
        payload={'sport':'basketball_nba','count':1,'players':[{'team_abbr':'PHI','player_id':'espn:0','status_code':'questionable','status_since':now}]}
        result=conditional_forecasts(model,[0.]*14,event,players,roster,payload,now,now,lambda m,x:.6)
        self.assertEqual(result['scenario_count'],2)
        a,b=result['scenarios']
        self.assertAlmostEqual(a['features']['rotation_scoring_difference'],b['features']['rotation_scoring_difference'])
        self.assertGreater(a['features']['projected_blocks_difference'],b['features']['projected_blocks_difference'])
        players[0]['blocks']=None
        self.assertEqual(conditional_forecasts(model,[0.]*14,event,players,roster,payload,now,now,lambda m,x:.6)['status'],'player_metrics_unavailable')


    def test_season_frozen_player_values_never_consume_same_season_ratings(self):
        games,players=self.fixture()
        for g in games:g['season']='2026-27'
        ids=sorted({p['player_id'] for p in players})
        rating={'features':ids,'weights':[5. if p=='0' else 0. for p in ids],
                'player_training_minutes':dict.fromkeys(ids,200.),
                'trained_before_season':'2026-27','training_seasons':['2025-26']}
        rows=historical_features(games,players,{'2026-27':rating})
        self.assertEqual(len(rows['3']['vector']),14)
        self.assertGreater(rows['3']['vector'][-1],0)
        rating['training_seasons']=['2026-27']
        self.assertEqual(historical_features(games,players,{'2026-27':rating}),{})

    def test_stint_feature_scenarios_match_the_historical_definition(self):
        games,players=self.fixture();now='2026-10-23T12:00:00+00:00'
        event={'home':'PHI','away':'IND','season':'2026-27','starts_at':'2026-10-24T00:00:00+00:00'}
        rosters={team:{'team':team,'player_ids':[str(p+offset) for p in range(10)],'verified':True,'source':'fixture','observed_at':now}
                 for team,offset in (('PHI',0),('IND',10))}
        ids=sorted({r['player_id'] for r in players})
        rating={'features':ids,'weights':[5. if p=='0' else 0. for p in ids],
                'player_training_minutes':dict.fromkeys(ids,200.),'trained_before_season':'2026-27',
                'training_seasons':['2025-26'],'exported_at':'2026-10-22T12:00:00+00:00'}
        model={'model_version':'nba-stint-feature-logistic-v1','exported_at':'2026-10-22T12:00:00+00:00',
               'features':[str(i) for i in range(14)]+list(FEATURES)+['lineup_stint_strength_difference']}
        payload={'sport':'basketball_nba','count':1,'players':[{'team_abbr':'PHI','player_id':'espn:0','status_code':'questionable','status_since':now}]}
        r=conditional_forecasts(model,[0.]*14,event,players,rosters,payload,now,now,lambda m,x:.6,rating)
        self.assertEqual(r['status'],'conditional_research_only')
        self.assertGreater(r['scenarios'][0]['features']['lineup_stint_strength_difference'],r['scenarios'][1]['features']['lineup_stint_strength_difference'])
        self.assertTrue(r['season_rating_hash'])
        rating['training_seasons']=['2026-27']
        self.assertEqual(conditional_forecasts(model,[0.]*14,event,players,rosters,payload,now,now,lambda m,x:.6,rating)['status'],'season_frozen_rating_unavailable')
