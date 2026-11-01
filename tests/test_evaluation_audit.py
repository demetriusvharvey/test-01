import copy
import unittest
from scripts.line_lab.evaluation_audit import audit_fold
from scripts.line_lab.production import metrics


def fold():
    rows = [{'id':str(i),'date':f'2026-10-{i:02d}','feature_cutoff':'2026-09-30',
             'probability':.7,'elo':.6,'home_win':int(i%2==0)} for i in range(1,21)]
    scores = lambda key: metrics([{'probability':r[key],'outcome':'win' if r['home_win'] else 'loss'} for r in rows])
    return {'season':'2026','training_end':'2024-12-31','tuning_end':'2025-06-30',
            'calibration_end':'2025-12-31','test_start':'2026-10-01','test_end':'2026-10-20',
            'predictions':rows,'ensemble':scores('probability'),'elo':scores('elo')}


class HistoricalEvaluationAuditTests(unittest.TestCase):
    def test_reproducible_paired_intervals_and_home_baseline(self):
        a = audit_fold(fold(),iterations=100)
        self.assertEqual(a,audit_fold(fold(),iterations=100))
        self.assertEqual(a['always_home_winner']['accuracy'],.5)
        self.assertIsNone(a['betting_roi'])
        self.assertAlmostEqual(a['candidate']['brier']-a['simple_fixed_elo']['brier'],.03)
        low,high=a['paired_intervals_95']['brier_difference']
        self.assertLess(low,.03);self.assertGreater(high,.03)

    def test_duplicates_future_features_and_changed_denominators_fail(self):
        for change in ('duplicate','feature','boundary','denominator'):
            f = copy.deepcopy(fold())
            if change=='duplicate':f['predictions'].append(f['predictions'][0])
            elif change=='feature':f['predictions'][0]['feature_cutoff']='2026-10-01'
            elif change=='boundary':f['calibration_end']='2026-10-02'
            else:f['ensemble']['sample_size']=1
            with self.subTest(change=change),self.assertRaises(ValueError):audit_fold(f)


if __name__=='__main__':unittest.main()
