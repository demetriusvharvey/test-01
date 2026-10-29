import copy
import unittest
from scripts.line_lab.injury_changes import annotate_injury_changes


def game(when, home_out=1, incomplete=False):
    return {'id':'nba:test','nba_availability_context':{
        'source':'PropLine, ESPN-sourced','observed_at':when,
        'incomplete':incomplete,'teams':{
            'home':{'team':'Home','report_present':True,'counts':{'out':home_out,'doubtful':0,'questionable':1}},
            'away':{'team':'Away','report_present':True,'counts':{'out':0,'doubtful':0,'questionable':1}}}}}


class InjuryChangeTests(unittest.TestCase):
    def setUp(self):
        self.before={'games':[game('2026-10-28T20:00:00Z')]}

    def test_changed_count_is_compared_at_newer_timestamp(self):
        after={'games':[game('2026-10-28T20:15:00Z',2)]}
        self.assertEqual(annotate_injury_changes(after,self.before),1)
        data=after['games'][0]['injury_change']
        self.assertEqual(data['status'],'changed')
        self.assertEqual(data['count_differences']['home']['out'],1)
        self.assertNotIn('injury_change',self.before['games'][0])

    def test_unchanged_and_same_timestamp_not_invented(self):
        after={'games':[game('2026-10-28T20:15:00Z')]}
        self.assertEqual(annotate_injury_changes(after,self.before),0)
        self.assertEqual(after['games'][0]['injury_change']['status'],'unchanged')
        same={'games':[game('2026-10-28T20:00:00Z',2)]}
        self.assertEqual(annotate_injury_changes(same,self.before),0)
        self.assertNotIn('injury_change',same['games'][0])

    def test_incomplete_snapshot_blocks_comparison(self):
        after={'games':[game('2026-10-28T20:15:00Z',0,True)]}
        self.assertEqual(annotate_injury_changes(after,self.before),0)
        self.assertEqual(after['games'][0]['injury_change']['status'],'comparison_unavailable')

    def test_invalid_team_and_provider_never_report_change(self):
        after={'games':[game('2026-10-28T20:15:00Z',0)]}
        after['games'][0]['nba_availability_context']['teams']['home']['team']='Wrong'
        self.assertEqual(annotate_injury_changes(after,self.before),0)
        self.assertEqual(after['games'][0]['injury_change']['status'],'comparison_unavailable')
        changed=copy.deepcopy(after)
        changed['games'][0]['nba_availability_context']['source']='unrelated'
        self.assertEqual(annotate_injury_changes(changed,self.before),0)


if __name__=='__main__':
    unittest.main()
