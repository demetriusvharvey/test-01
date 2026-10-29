import unittest
from datetime import date,timedelta
from scripts.line_lab.nba_efficiency import enrich_examples


class EfficiencyTests(unittest.TestCase):
    def test_same_day_and_future_box_scores_do_not_enter_features(self):
        games=[{'id':str(i),'league':'NBA','date':date(2025,1,1)+timedelta(days=i),'home':'A','away':'B'} for i in range(12)]
        stats={(g['date'],team):[float(i)]*8 for i,g in enumerate(games) for team in ('A','B')}
        rows=[{'game_id':g['id'],'date':g['date'].isoformat(),'vector':[0]} for g in games]
        before=enrich_examples(rows,games,stats)
        stats[(games[-1]['date'],'A')]=[999.]*8
        after=enrich_examples(rows,games,stats)
        self.assertEqual(before,after)
        self.assertEqual(len(before),2)
