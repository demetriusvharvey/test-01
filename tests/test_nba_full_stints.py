import unittest
from scripts.line_lab.nba_full_stints import reconstruct_full


class FullStintTests(unittest.TestCase):
    def fixture(self):
        rosters={'1':{'101':{'starters':set('12345'),'roster':set('123456')},
                      '102':{'starters':set(str(p) for p in range(11,16)),'roster':set(str(p) for p in range(11,17))}}}
        rows=[];score=0;seq=0
        for q in range(1,5):
            for i in range(1,6):
                seq+=1;score+=2
                rows.append({'game_id':'1','game_date':'2026-10-20','season':'2027','season_type':'2','sequence_number':seq,
                             'period_number':q,'type_text':'Jump Shot','clock_display_value':f'{12-i}:00',
                             'home_team_id':'101','away_team_id':'102','team_id':'101','athlete_id_1':str(i),'athlete_id_2':str(i+10),
                             'home_score':score,'away_score':0})
            seq+=1;rows.append({**rows[-1],'sequence_number':seq,'type_text':'End Period','clock_display_value':'0:00'})
        seq+=1;rows.append({**rows[-1],'sequence_number':seq,'type_text':'End Game'})
        minutes={'1':{str(p):48. for p in list(range(1,6))+list(range(11,16))}}
        return rows,rosters,minutes

    def test_uniqueness_and_per_player_minute_checks(self):
        rows,rosters,minutes=self.fixture();stints,report=reconstruct_full(rows,rosters,minutes)
        self.assertEqual(report['accepted_games'],1)
        self.assertEqual(len(stints),4);self.assertEqual(sum(s['seconds'] for s in stints),2880)
        self.assertEqual(sum(s['home_points'] for s in stints),40)
        minutes['1']['1']=40.
        self.assertEqual(reconstruct_full(rows,rosters,minutes)[0],[])

    def test_no_guessing_a_quiet_fifth_player_and_no_overtime(self):
        rows,rosters,minutes=self.fixture()
        for row in rows:
            if row['period_number']==3 and row['athlete_id_1']=='5':row['athlete_id_1']='';row['athlete_id_2']=''
        stints,report=reconstruct_full(rows,rosters,minutes)
        self.assertEqual(stints,[]);self.assertIn('nonunique_period_starters',report['rejections'])
        rows,rosters,minutes=self.fixture();rows[-1]['period_number']=5
        self.assertEqual(reconstruct_full(rows,rosters,minutes)[0],[])
