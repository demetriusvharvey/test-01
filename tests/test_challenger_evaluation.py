import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from scripts.line_lab.challenger_evaluation import evaluate,append_results


class ChallengerEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.now='2026-10-29T02:00:00+00:00';self.start='2026-10-28T20:00:00+00:00';self.predicted='2026-10-28T17:00:00+00:00'
        self.baseline={'game_id':'g','league':'NFL','home':'A','away':'B','captured_at':self.predicted,
            'starts_at':self.start,'pure_probability':.6,'feature_snapshot':json.dumps({'source_text_sha256':{'games.csv':'abc'}})}
        self.candidate={'game_id':'g','league':'NFL','captured_at':self.predicted,'starts_at':self.start,'model_id':'v1','probability':.7}
        self.trials={'v1':{'completed_at':'2026-10-27T00:00:00+00:00','artifact':{'model_version':'pure-elasticnet-v1',
            'trained_before':'2026-10-27T00:00:00+00:00','promoted':False,'features':['rating_difference']}}}
        self.outcomes={'g':{'home':'A','away':'B','home_score':21,'away_score':14,
            'observed_at':'2026-10-28T23:00:00+00:00','source':'nflverse'}}
    def nfl(self,baselines=None,candidates=None,trials=None,outcomes=None):
        rows=evaluate(baselines if baselines is not None else [self.baseline],
                      candidates if candidates is not None else [self.candidate],
                      trials if trials is not None else self.trials,
                      outcomes if outcomes is not None else self.outcomes,self.now)
        return next(r for r in rows if r['league']=='NFL' and r['model_version']=='pure-elasticnet-v1')
    def test_matched_pregame_predictions_compare_and_remain_inconclusive(self):
        r=self.nfl();self.assertEqual(r['games'],1);self.assertLess(r['logloss_difference'],0)
        self.assertLess(r['brier_difference'],0);self.assertIsNone(r['adjusted_p'])
        self.assertFalse(r['promoted']);self.assertEqual(r['status'],'insufficient_data')
    def test_rejects_missing_baseline_unverified_source_and_training_after_pick(self):
        self.assertEqual(self.nfl(baselines=[])['games'],0)
        out={'g':{**self.outcomes['g'],'source':'unknown'}}
        self.assertEqual(self.nfl(outcomes=out)['games'],0)
        late={'v1':{**self.trials['v1'],'completed_at':'2026-10-28T18:00:00+00:00'}}
        self.assertEqual(self.nfl(trials=late)['games'],0)
    def test_first_forecast_fixed_before_outcomes_and_trials_append_only(self):
        later={**self.candidate,'captured_at':'2026-10-28T18:00:00+00:00'}
        self.assertEqual(self.nfl(candidates=[later,self.candidate])['games'],1)
        results=evaluate([self.baseline],[self.candidate],self.trials,self.outcomes,self.now)
        with tempfile.TemporaryDirectory() as root:
            append_results(root,results,self.now);append_results(root,results,self.now)
            with closing(sqlite3.connect(Path(root)/'observations/challenger_tests.sqlite')) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM challenger_tests').fetchone()[0],7)
                with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM challenger_tests')


if __name__=='__main__':unittest.main()
