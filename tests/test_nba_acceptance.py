import unittest
from scripts.line_lab.nba_acceptance import check_predictions


class NBAAcceptanceTests(unittest.TestCase):
    def test_empty_and_missing_injury_path_cannot_pass(self):
        now='2026-10-29T12:00:00+00:00'
        self.assertEqual(check_predictions([],now)['status'],'incomplete')
        p={'game_id':'fixture','starts_at':'2026-10-29T23:00:00+00:00',
           'predicted_at':now,'model_exported_at':'2026-10-29T11:00:00+00:00',
           'home_probability':.6,'away_probability':.4}
        self.assertEqual(check_predictions([p],now)['status'],'incomplete')
