import copy
import unittest
from scripts.line_lab.nba_stints import reconstruct,starter_rosters,clock_seconds


class StintTests(unittest.TestCase):
    def fixture(self):
        rosters={'1':{'101':{'starters':set('12345'),'roster':set('123456')},
                      '102':{'starters':set(str(i) for i in range(11,16)),'roster':set(str(i) for i in range(11,17))}}}
        base={'game_id':'1','game_date':'2026-10-20','season':'2027','season_type':'2',
              'home_team_id':'101','away_team_id':'102','period_number':'1','team_id':'',
              'athlete_id_1':'','athlete_id_2':''}
        events=[]
        for i,kind,clock,home,away,extra in (
            (1,'Jumpball','12:00',0,0,{}),(2,'Jump Shot','7:00',2,0,{}),
            (3,'Substitution','6:00',2,0,{'team_id':'101','athlete_id_1':'6','athlete_id_2':'1'}),
            (4,'Jump Shot','1:00',2,2,{}),(5,'End Period','0.0',2,2,{}),
            (6,'End Game','0:00',100,90,{'period_number':'4'})):
            events.append({**base,'sequence_number':i,'type_text':kind,'clock_display_value':clock,
                           'home_score':home,'away_score':away,**extra})
        return events,rosters

    def test_explicit_substitution_preserves_duration_and_scores(self):
        events,rosters=self.fixture();stints,quality=reconstruct(events,rosters)
        self.assertEqual(quality['accepted_games'],1)
        self.assertEqual(sum(s['seconds'] for s in stints),720)
        self.assertEqual(sum(s['home_points'] for s in stints),2)
        self.assertIn('1',stints[0]['home_players']);self.assertNotIn('1',stints[1]['home_players'])
        self.assertIn('6',stints[1]['home_players'])
        self.assertEqual(len(stints),2)

    def test_unknown_membership_bad_clocks_and_missing_final_are_rejected(self):
        for change in ('membership','clock','final','starters'):
            events,rosters=self.fixture()
            if change=='membership':events[2]['athlete_id_2']='99'
            elif change=='clock':events[3]['clock_display_value']='10:00'
            elif change=='final':events=events[:-1]
            else:rosters={}
            stints,quality=reconstruct(events,rosters)
            self.assertEqual(stints,[]);self.assertEqual(quality['rejected_games'],1)

    def test_zero_duration_scoring_and_later_quarter_unknowns_not_guessed(self):
        events,rosters=self.fixture()
        events.insert(3,{**events[1],'sequence_number':3.5,'clock_display_value':'6:00','home_score':3})
        events.insert(4,{**events[2],'sequence_number':3.6,'athlete_id_1':'1','athlete_id_2':'6','home_score':3})
        # Duplicate/truncated source sequence is invalid as well as ambiguous time.
        self.assertEqual(reconstruct(events,rosters)[0],[])
        self.assertEqual(clock_seconds('0.4'),.4)
        self.assertEqual(clock_seconds('12:00'),720)
        with self.assertRaises(ValueError):clock_seconds('1:75')

    def test_starter_source_requires_five_unique_players_per_team(self):
        text='game_id,team_id,athlete_id,starter\n'+''.join(f'1,{team},{p},true\n' for team,players in (('101',range(1,6)),('102',range(11,16))) for p in players)
        self.assertIn('1',starter_rosters(text))
        self.assertEqual(starter_rosters(text+'1,101,1,true\n'),{})
