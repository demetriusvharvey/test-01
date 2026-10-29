import unittest
from scripts.line_lab.board_freshness import protect_last_success


class BoardFreshnessTests(unittest.TestCase):
    def test_total_outage_keeps_recent_snapshot_without_faking_freshness(self):
        previous={'generated_at':'2026-10-29T12:00:00+00:00','games':[{'id':'g'}],
                  'picks':[{'id':'future','starts_at':'2026-10-29T23:00:00+00:00'},
                           {'id':'started','starts_at':'2026-10-29T12:15:00+00:00'}]}
        current={'generated_at':'2026-10-29T12:30:00+00:00','games':[],'picks':[],
                 'errors':['NBA score source unavailable (ValueError)','NFL score source unavailable (ValueError)']}
        result=protect_last_success(current,previous,current['generated_at'])
        self.assertEqual(result['generated_at'],previous['generated_at'])
        self.assertEqual(result['refresh_status']['status'],'stale')
        self.assertEqual([p['id'] for p in result['picks']],['future'])
        self.assertTrue(result['picks'][0]['data_stale'])
        self.assertNotIn('data_stale',previous['games'][0])
        self.assertEqual(protect_last_success(current,previous,'2026-10-29T14:00:00+00:00')['games'],[])

    def test_verified_empty_schedule_does_not_resurrect_old_games(self):
        current={'generated_at':'2026-10-29T12:30:00+00:00','games':[],'picks':[],'errors':[]}
        old={'generated_at':'2026-10-29T12:00:00+00:00','games':[{'id':'old'}]}
        result=protect_last_success(current,old,current['generated_at'])
        self.assertEqual(result['games'],[])
        self.assertEqual(result['refresh_status']['status'],'ok')
