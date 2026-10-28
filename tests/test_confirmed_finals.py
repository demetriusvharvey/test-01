import unittest
from datetime import datetime, timedelta, timezone
from scripts.line_lab.ingest import qualify_final_results


class ConfirmedFinalTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,28,22,tzinfo=timezone.utc)
        self.final={'id':'nfl:one','home':'A','away':'B','home_score':21,'away_score':14,
                    'starts_at':self.now-timedelta(hours=4),'source':'ESPN final'}
        self.supplement={'id':'nfl:one','home':'A','away':'B','home_score':21,'away_score':14,'source':'nflverse'}

    def test_a_score_without_a_confirmed_final_status_is_not_graded(self):
        finals,explicit,conflicts=qualify_final_results([self.supplement],[],self.now)
        self.assertEqual(finals,[]);self.assertEqual(explicit,[]);self.assertEqual(conflicts,[])

    def test_agreeing_sources_allow_a_final_and_record_corroboration(self):
        finals,explicit,conflicts=qualify_final_results([self.supplement],[self.final],self.now)
        self.assertEqual([r['source'] for r in finals],['ESPN final','nflverse'])
        self.assertEqual(len(explicit),1);self.assertEqual(conflicts,[])

    def test_disagreement_or_a_future_start_never_grades(self):
        conflicting={**self.supplement,'home_score':17}
        finals,explicit,conflicts=qualify_final_results([conflicting],[self.final],self.now)
        self.assertEqual(finals,[]);self.assertEqual(explicit,[]);self.assertEqual(conflicts,['nfl:one'])
        future={**self.final,'starts_at':self.now+timedelta(seconds=1)}
        self.assertEqual(qualify_final_results([self.supplement],[future],self.now)[0],[])


if __name__=='__main__':unittest.main()
