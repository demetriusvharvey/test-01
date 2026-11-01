import copy
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime
from scripts.line_lab.production import archive_forecasts, apply_pipeline
from scripts.line_lab.forecast_evaluation import evaluate, wilson


NOW = '2026-10-31T18:00:00Z'
START = '2026-10-31T23:00:00Z'
AFTER = '2026-11-01T03:00:00Z'


def forecast(**changes):
    return dict(id='nba:2026-10-31:BOS:NYK', league='NBA', artifact_hash='a',
                model_version='m', predicted_at=NOW, starts_at=START,
                home_probability=.8, baseline_elo_probability=.6,
                baseline_elo_kind='production_incumbent', **changes)


def final(**changes):
    result = dict(id='nba:2026-10-31:BOS:NYK', home='NYK', away='BOS',
                  starts_at=START, source='ESPN final', home_score=100, away_score=90)
    result.update(changes)
    return result


class ForwardIntegrityTests(unittest.TestCase):
    def test_future_outcomes_and_forecasts_cannot_leak_into_as_of_report(self):
        outcome = {**final(), 'observed_at': AFTER}
        before = evaluate([forecast()], [outcome], NOW)
        self.assertEqual(before['models']['m:a']['sample_size'], 0)
        self.assertEqual(before['diagnostics']['future_outcomes'], 1)
        report = evaluate([forecast()], [outcome], AFTER)
        self.assertEqual(report['models']['m:a']['wins'], 1)
        future = evaluate([forecast()], [], '2026-10-31T17:00:00Z')
        self.assertEqual(future['models'], {})

    def test_first_forecast_uses_instants_not_lexical_timezone_order(self):
        earlier = forecast(); earlier.update(predicted_at='2026-10-31T14:00:00-04:00', home_probability=.2)
        later = forecast(); later.update(predicted_at='2026-10-31T17:30:00-01:00', home_probability=.8)
        report = evaluate([later, earlier], [{**final(), 'observed_at': AFTER}], AFTER)
        self.assertEqual(report['models']['m:a']['losses'], 1)
        self.assertAlmostEqual(report['models']['m:a']['brier'], .64)

    def test_legacy_fixed_elo_is_not_mislabeled_as_matched_incumbent(self):
        old = forecast(); old.pop('baseline_elo_kind')
        report = evaluate([old], [{**final(), 'observed_at': AFTER}], AFTER)['models']['m:a']
        self.assertEqual(report['sample_size'], 1)
        self.assertEqual(report['matched_elo']['sample_size'], 0)
        self.assertEqual(report['legacy_fixed_elo']['sample_size'], 1)
        self.assertIsNone(report['paired_brier_difference'])

    def test_conflicting_results_are_preserved_and_diagnosed(self):
        with tempfile.TemporaryDirectory() as root:
            archive_forecasts(root, [forecast()], [], NOW)
            archive_forecasts(root, [], [final()], AFTER)
            report = archive_forecasts(root, [], [final(home_score=90, away_score=100)], AFTER)
            self.assertEqual(report['models']['m:a']['sample_size'], 0)
            self.assertEqual(report['diagnostics']['conflicting_result_forecasts'], 1)
            with sqlite3.connect(root+'/observations/production_forecasts/ledger.sqlite') as db:
                self.assertEqual(db.execute('select count(*) from outcome_confirmations').fetchone()[0], 2)
                self.assertEqual(json.loads(db.execute('select payload from outcomes').fetchone()[0])['home_score'], 100)

    def test_bad_finals_do_not_settle_or_abort_unrelated_work(self):
        for bad in (final(home='BOS'), final(home_score=True), final(home_score=-1),
                    final(home_score=10.5), final(starts_at='2026-11-02T03:00:00Z')):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as root:
                archive_forecasts(root, [forecast()], [], NOW)
                report = archive_forecasts(root, [], [bad], AFTER)
                self.assertEqual(report['models']['m:a']['pending'], 1)

    def test_score_only_payload_is_rejected_and_tie_is_explicitly_void(self):
        with tempfile.TemporaryDirectory() as root:
            archive_forecasts(root, [forecast()], [], NOW)
            report = archive_forecasts(root, [], [{'id':forecast()['id'], 'home_score':100, 'away_score':90}], AFTER)
            self.assertEqual(report['models']['m:a']['pending'], 1)
            report = archive_forecasts(root, [], [final(home_score=90)], AFTER)
            self.assertEqual(report['models']['m:a']['void'], 1)
            self.assertEqual(report['models']['m:a']['pending'], 0)
            self.assertEqual(report['models']['m:a']['sample_size'], 0)

    def test_changed_start_time_stays_pending_with_diagnostic(self):
        with tempfile.TemporaryDirectory() as root:
            archive_forecasts(root, [forecast()], [], NOW)
            report = archive_forecasts(root, [], [final(starts_at='2026-11-01T01:00:00Z')], AFTER)
            self.assertEqual(report['models']['m:a']['pending'], 1)
            self.assertEqual(report['diagnostics']['unmatched_final_timing_forecasts'], 1)

    def test_matched_candidate_and_benchmark_have_same_denominator(self):
        a = forecast()
        b = forecast(); b.update(id='nba:2026-10-31:LAL:LAC', baseline_elo_probability=None)
        results = [{**final(), 'observed_at':AFTER},
                   {**final(id=b['id'], home='LAC', away='LAL', home_score=90, away_score=100), 'observed_at':AFTER}]
        report = evaluate([a,b], results, AFTER)['models']['m:a']
        self.assertEqual(report['sample_size'], 2)
        self.assertEqual(report['matched_candidate']['sample_size'], 1)
        self.assertEqual(report['matched_elo']['sample_size'], 1)
        self.assertAlmostEqual(report['paired_brier_difference'], -.12)
        self.assertEqual(report['home_team_baseline']['accuracy'], 1.)

    def test_accuracy_interval_reflects_small_sample(self):
        low, high = wilson(5, 9)
        self.assertLess(low, .3); self.assertGreater(high, .8)
        self.assertIsNone(wilson(0, 0))

    def test_parser_datetime_final_can_be_archived_and_replayed(self):
        with tempfile.TemporaryDirectory() as root:
            archive_forecasts(root, [forecast()], [], NOW)
            row = final(starts_at=datetime.fromisoformat(START.replace('Z','+00:00')))
            row['date'] = row['starts_at'].date()
            report = archive_forecasts(root, [], [row], AFTER)
            self.assertEqual(report['models']['m:a']['wins'], 1)

    def test_conflicting_equal_instant_predictions_do_not_pick_row_order(self):
        a = forecast(); b = forecast();b.update(home_probability=.2,predicted_at='2026-10-31T14:00:00-04:00')
        report = evaluate([a,b], [{**final(),'observed_at':AFTER}], AFTER)
        self.assertEqual(report['models']['m:a']['pending'],1)
        self.assertEqual(report['diagnostics']['unscored_conflicting_forecasts'],1)


class InferenceBoundaryTests(unittest.TestCase):
    def board(self):
        return {'games':[{'id':forecast()['id'], 'league':'NBA', 'starts_at':START,
                          'home':'Knicks', 'away':'Celtics'}]}

    def test_actual_incumbent_is_frozen_separately_from_fixed_elo(self):
        row = {'game_id':forecast()['id'], 'elo':.55}
        with patch('scripts.line_lab.production.examples', return_value=[row]), \
             patch('scripts.line_lab.production.project_home', return_value=.75), \
             patch('scripts.line_lab.production.feature_snapshot', return_value={}), \
             patch('scripts.line_lab.production.infer', return_value={'home_probability':.6, 'validation':{}}):
            b = apply_pipeline(self.board(), {'NBA':{}}, [], NOW)
        f = b['research_forecasts'][0]
        self.assertEqual(f['baseline_elo_probability'], .75)
        self.assertEqual(f['baseline_fixed_elo_probability'], .55)
        self.assertEqual(f['home_probability'], .75)
        self.assertEqual(f['fallback_reason'], 'challenger_not_approved')
        self.assertEqual(b['inference_diagnostics']['fallback_reasons']['challenger_not_approved'], 1)

    def test_blocked_or_started_game_clears_old_forecast(self):
        for blocked, now in ((('NBA',),NOW), ((),AFTER)):
            b = self.board();b['games'][0].update(forecast={'home_probability':.9},predicted_winner='Knicks')
            apply_pipeline(b, {}, [], now, blocked=blocked)
            self.assertNotIn('forecast', b['games'][0])
            self.assertNotIn('predicted_winner', b['games'][0])

    def test_approved_prediction_does_not_contain_recursive_research_model(self):
        candidate = {'home_probability':.65,'artifact_hash':'c','model_version':'candidate',
                     'calibration_status':'test', 'validation':{}}
        # Keep real artifact loading/other runtime behavior; only substitute its
        # approval state through a copy of the loaded artifact in infer.
        def approved(a, row, now):
            a['validation']['prediction_approved'] = True
            return copy.deepcopy(candidate)
        with patch('scripts.line_lab.production.examples', return_value=[{'game_id':forecast()['id'],'elo':.55}]), \
             patch('scripts.line_lab.production.project_home', return_value=.75), \
             patch('scripts.line_lab.production.infer', side_effect=approved):
            b = apply_pipeline(self.board(), {'NBA':{}}, [], NOW)
        self.assertNotIn('research_model', b['research_forecasts'][0])
        json.dumps(b, allow_nan=False)


if __name__ == '__main__':
    unittest.main()
