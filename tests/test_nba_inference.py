import math
import tempfile
import unittest
from scripts.line_lab.nba_inference import probability,record_nba_predictions


class NBAInferenceTests(unittest.TestCase):
    def test_standardization_and_calibration_math(self):
        model={'features':['x','y'],'mean':[1.,2.],'scale':[2.,4.],'weights':[.4,-.2],
               'intercept':.1,'calibration_intercept':-.1,'calibration_weight':.9}
        expected=1/(1+math.exp(-(-.1+.9*(.1+.4*(3-1)/2-.2*(6-2)/4))))
        p=probability(model,[3.,6.])
        self.assertAlmostEqual(p,expected);self.assertAlmostEqual(p+(1-p),1)
        with self.assertRaises(ValueError):probability(model,[math.nan,6.])
        with self.assertRaises(ValueError):probability(model,[1.])
    def test_missing_model_does_not_fabricate_forecast(self):
        with tempfile.TemporaryDirectory() as root:
            result=record_nba_predictions(root,[],[],'2026-10-29T12:00:00+00:00')
            self.assertEqual(result,{'status':'model_unavailable','predictions':[]})
