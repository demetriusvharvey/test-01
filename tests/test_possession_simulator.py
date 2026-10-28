import unittest
from datetime import date, timedelta
from scripts.line_lab.possession_simulator import (
    nba_observations, nfl_drive_observations, ProcessHistory, walk_forward)

NBA_HEADER = 'season,team,game_date,opponent,home,points,field_goals_made,field_goal_attempts,three_point_makes,free_throws_made,free_throw_attempts,offensive_rebounds,turnovers\n'


def nba_csv(day='2025-01-01', a_points=90):
    return NBA_HEADER + (
        f'2024-25,LAL,{day},BOS,true,110,40,85,10,20,25,10,12\n'
        f'2024-25,BOS,{day},LAL,false,{a_points},35,80,10,{a_points-80},20,10,12\n')


def nfl_csv():
    fields='game_id,game_date,home_team,away_team,fixed_drive,posteam,posteam_score,posteam_score_post,play_id,season,play_deleted\n'
    rows=[]
    for team in ('KC','BUF'):
        for i in range(1,7):
            pts=7 if team=='KC' and i==1 else 3 if team=='BUF' and i==1 else 0
            prior=0
            rows.extend([f'2025_01_BUF_KC,2025-09-07,KC,BUF,{team}-{i},{team},{prior},{prior},1,2025,0',
                         f'2025_01_BUF_KC,2025-09-07,KC,BUF,{team}-{i},{team},{prior},{prior+pts},2,2025,0'])
    return fields+'\n'.join(rows)+'\n'


class ScoringProcessTests(unittest.TestCase):
    def test_nba_boxscore_pair_and_incomplete_columns(self):
        rows=nba_observations(nba_csv())
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['home_score'],110)
        self.assertEqual(sum(rows[0]['events'][0].values()),rows[0]['counts'][0])
        self.assertEqual(sum(k*v for k,v in rows[0]['events'][0].items()),110)
        with self.assertRaises(ValueError):nba_observations('team,points\nLAL,110\n')

    def test_nfl_drive_outcomes_from_score_changes(self):
        games=nfl_drive_observations(nfl_csv())
        self.assertEqual(len(games),1)
        self.assertEqual(games[0]['counts'],(6,6))
        self.assertEqual(games[0]['events'][0][7],1)
        self.assertEqual(games[0]['events'][1][3],1)
        with self.assertRaises(ValueError):nfl_drive_observations('game_id,score\nx,7\n')

    def test_deterministic_simulations_and_no_same_day_leakage(self):
        history=ProcessHistory('NBA')
        base=nba_observations(nba_csv())[0]
        for n in range(210):
            game={**base,'id':f'NBA-{n}','date':date(2024,1,1)+timedelta(days=n)}
            history.add(game)
        result=history.simulate('LAL','BOS',5000,11)
        self.assertEqual(result,history.simulate('LAL','BOS',5000,11))
        self.assertEqual(result['home_wins']+result['away_wins'],5000)
        self.assertEqual(result['scoring_unit'],'estimated box-score possession')
        with self.assertRaises(ValueError):history.simulate('LAL','BOS',50)
        with self.assertRaises(ValueError):history.add({**base,'date':date(2023,1,1)})
        # Walk-forward cannot use the final under evaluation, even if two games share a day.
        games=[{**base,'id':f'NBA-{n}','date':date(2024,1,1)+timedelta(days=n)} for n in range(203)]
        games[-1]['season']='2025-26'
        official=[{**g,'home_score':110,'away_score':90} for g in games]
        first=walk_forward(games,official,'2025-26')
        official[-1]['home_score'],official[-1]['away_score']=90,110
        second=walk_forward(games,official,'2025-26')
        self.assertEqual(first[0]['probability'],second[0]['probability'])
        self.assertNotEqual(first[0]['outcome'],second[0]['outcome'])


if __name__=='__main__':unittest.main()
