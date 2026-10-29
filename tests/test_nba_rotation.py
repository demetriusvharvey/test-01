import unittest
from datetime import date,timedelta
from scripts.line_lab.nba_rotation import rotation_features


class RotationTests(unittest.TestCase):
    def test_same_game_minutes_and_future_team_cannot_change_earlier_projection(self):
        day=date(2026,1,1);players=[];games=[]
        for i in range(4):
            games.append({'id':str(i),'date':day+timedelta(days=i),'league':'NBA','home':'A','away':'B'})
            for team in ('A','B'):
                for p in range(8):
                    players.append({'date':day+timedelta(days=i),'team':team,'player_id':team+str(p),'minutes':30.,'points':12.+p})
        first=rotation_features(games,players)
        for row in players:
            if row['date']==day+timedelta(days=3):row['points']=90.;row['team']='C'
        self.assertEqual(first,rotation_features(games,players))
        self.assertNotIn('0',first)
        self.assertIn('1',first)
        self.assertIn('unknown',first['1']['injury_status'])
