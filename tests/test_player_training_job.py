import json
import tempfile
import unittest
from pathlib import Path
from scripts.research_player_impact import run


class PlayerTrainingJobTests(unittest.TestCase):
    def test_missing_data_records_insufficient_status_without_fake_metrics(self):
        with tempfile.TemporaryDirectory() as root:
            report=run(root,'2026-10-29T12:00:00+00:00')
            self.assertIn('| NBA | 0 | 0 | 0 | insufficient verified input |',report)
            self.assertNotIn('validation log loss',report)
            self.assertTrue((Path(root)/'observations/model_registry.sqlite').exists())

    def test_invalid_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'observations/player_exposures.json';p.parent.mkdir()
            p.write_text(json.dumps({'not':'a dataset'}))
            report=run(root,'2026-10-29T12:00:00+00:00')
            self.assertIn('invalid_input',report)
            self.assertNotIn('research artifact; not promoted',report)


if __name__=='__main__':unittest.main()
