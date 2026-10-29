import unittest
from datetime import date
from scripts.line_lab.nba_lineup import project_rotation


class LineupTests(unittest.TestCase):
    def test_out_player_removed_minutes_conserved_and_questionable_unweighted(self):
        ids=[str(i) for i in range(10)]
        players=[{'player_id':p,'team':'A','date':date(2026,10,27),'minutes':30.,'points':10.} for p in ids]
        roster={'player_ids':ids,'team':'A','verified':True,'source':'fixture','observed_at':'2026-10-29T12:00:00+00:00'}
        status={'complete':True,'observed_at':'2026-10-29T12:00:00+00:00','players':{'0':'out','1':'questionable'}}
        result=project_rotation(players,roster,status,'2026-10-29T12:30:00+00:00','2026-10-30T00:00:00+00:00')
        self.assertEqual(result['unavailable_players'],['0'])
        self.assertEqual(result['unresolved_players'],['1'])
        self.assertAlmostEqual(sum(p['minutes'] for p in result['players']),240)
        self.assertNotIn('0',[p['player_id'] for p in result['players']])
        status['players']['bad-id']='out'
        self.assertIsNone(project_rotation(players,roster,status,'2026-10-29T12:30:00+00:00','2026-10-30T00:00:00+00:00'))
