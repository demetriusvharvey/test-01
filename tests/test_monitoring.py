import json
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from scripts.line_lab.monitoring import summarize_drift,population_stability,build_monitoring


class MonitoringTests(unittest.TestCase):
    def test_drift_uses_distinct_pregame_first_observations(self):
        now=datetime(2026,10,28,tzinfo=timezone.utc);rows=[]
        for i,days in enumerate((20,19,2,1)):
            captured=now-timedelta(days=days)
            rows.append({'game_id':str(i),'league':'NBA','captured_at':captured.isoformat(),
                         'starts_at':(captured+timedelta(hours=2)).isoformat(),
                         'feature_snapshot':json.dumps({'home_rating':1500+i*10,'away_rating':1500}),
                         'pure_probability':.55})
        post=dict(rows[0]);post['captured_at']=now.isoformat()
        future=dict(rows[0]);future['game_id']='future';future['captured_at']=(now+timedelta(days=1)).isoformat()
        result=summarize_drift(rows+[post,future],now.isoformat(),2,2)['NBA']
        self.assertEqual((result['reference_games'],result['current_games']),(2,2))
        self.assertIn(result['status'],('review','descriptive'))
        self.assertAlmostEqual(population_stability([1,2,3],[1,2,3],[1,2]),0)
        self.assertEqual(summarize_drift(rows,now.isoformat())['NBA']['status'],'insufficient_data')

    def test_missing_quotes_are_not_fresh(self):
        with tempfile.TemporaryDirectory() as root:
            result=build_monitoring(root,'2026-10-28T20:00:00+00:00',{},[])
        self.assertEqual(result['source_freshness'],'no_quotes')
        self.assertIsNone(result['latest_quote_at'])
        self.assertEqual(result['alerts'],'display_only')


if __name__=='__main__':unittest.main()
