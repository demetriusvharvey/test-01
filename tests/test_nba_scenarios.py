import math
import unittest
from datetime import date,timedelta
from scripts.line_lab.nba_scenarios import conditional_forecasts


class ScenarioTests(unittest.TestCase):
    def test_current_ids_drive_explicit_unweighted_scenarios(self):
        now='2026-10-29T12:30:00+00:00';stamp='2026-10-29T12:00:00+00:00'
        rosters={};players=[]
        for team,offset in (('PHI',0),('IND',10)):
            ids=[str(i+offset) for i in range(10)]
            rosters[team]={'player_ids':ids,'team':team,'verified':True,'source':'fixture','observed_at':stamp}
            for day in range(6):
                for i,p in enumerate(ids):
                    players.append({'date':date(2026,10,20)+timedelta(days=day),'team':team,
                                    'player_id':p,'minutes':24.,'points':40. if team=='PHI' and i==0 else 10.})
        event={'home':'PHI','away':'IND','starts_at':'2026-10-30T00:00:00+00:00'}
        model={'model_version':'nba-rotation-logistic-v1','exported_at':'2026-10-28T00:00:00+00:00','features':[str(i) for i in range(17)]}
        payload={'sport':'basketball_nba','count':1,'players':[{'team_abbr':'PHI','player_id':'espn:0','status_code':'questionable','status_since':stamp}]}
        predict=lambda model,x:1/(1+math.exp(-x[-3]))
        result=conditional_forecasts(model,[0.]*14,event,players,rosters,payload,stamp,now,predict)
        self.assertEqual(result['status'],'conditional_research_only')
        self.assertGreater(result['scenarios'][0]['home_probability'],result['scenarios'][1]['home_probability'])
        self.assertNotIn('weight',result['scenarios'][0])
        payload['players'][0]['player_id']='other:0'
        self.assertEqual(conditional_forecasts(model,[0.]*14,event,players,rosters,payload,stamp,now,predict)['status'],'unmatched_injury_identity')
