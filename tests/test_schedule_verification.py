import unittest
from scripts.line_lab.schedule_verification import reconcile, collect, attach_published_starts

NOW = '2026-11-05T13:00:00Z'
KEY = 'nba:2026-11-06:PHI:CLE'


class ScheduleVerificationTests(unittest.TestCase):
    def test_later_published_time_is_display_only_and_has_source_evidence(self):
        earlier = '2026-11-07T00:30:00Z'
        later = '2026-11-07T00:50:00Z'
        board = {'games': [{'id': KEY, 'starts_at': earlier}]}
        report = {'status': 'checked', 'source_url': 'https://example.org/schedule',
                  'observed_at': NOW, 'published_starts': {KEY: later}}
        attach_published_starts(board, [report])
        self.assertEqual(board['games'][0]['scheduled_starts_at'], later)
        self.assertEqual(board['games'][0]['starts_at'], earlier)
        self.assertEqual(board['games'][0]['schedule_source_url'], report['source_url'])
        report['published_starts'][KEY] = '2026-11-07T01:00:00Z'
        board = {'games': [{'id': KEY, 'starts_at': earlier}]}
        attach_published_starts(board, [report])
        self.assertNotIn('scheduled_starts_at', board['games'][0])

    def test_earlier_corroboration_corrects_estimated_tipoff_without_mutation(self):
        starts = {KEY: '2026-11-07T00:40:00Z'}
        result, changes, conflicts = reconcile(starts, {KEY: '2026-11-07T00:30:00Z'}, NOW)
        self.assertEqual(result[KEY], '2026-11-07T00:30:00+00:00')
        self.assertEqual(starts[KEY], '2026-11-07T00:40:00Z')
        self.assertIn(KEY, changes)
        self.assertEqual(conflicts, [])

    def test_never_extend_existing_deadline_or_insert_unmatched_game(self):
        starts = {KEY: '2026-11-07T00:30:00Z'}
        result, changes, conflicts = reconcile(starts, {KEY: '2026-11-07T00:40:00Z', 'other': NOW}, NOW)
        self.assertEqual(result, starts)
        self.assertEqual(changes, {})
        self.assertEqual(conflicts, [])

    def test_large_disagreement_or_already_started_reference_quarantines(self):
        starts = {KEY: '2026-11-07T00:40:00Z'}
        for stamp in ['2026-11-07T00:00:00Z', NOW]:
            result, _, conflicts = reconcile(starts, {KEY: stamp}, NOW)
            self.assertNotIn(KEY, result)
            self.assertEqual(conflicts, [KEY])

    def test_historical_starts_are_preserved(self):
        starts = {KEY: '2026-11-04T00:40:00Z'}
        self.assertEqual(reconcile(starts, {KEY: NOW}, NOW), (starts, {}, []))

    def test_failed_optional_source_is_reported_without_erasing_schedule(self):
        calls = []
        def unavailable(url, timeout):
            calls.append(url)
            raise OSError('source unavailable')
        starts = {KEY: '2026-11-07T00:40:00Z'}
        result, reports = collect(starts, NOW, unavailable)
        self.assertEqual(result, starts)
        self.assertEqual(len(set(calls)), 4)
        self.assertEqual(len(reports), 4)
        self.assertTrue(all(r['status'] == 'unavailable' for r in reports))
        self.assertTrue(all('20261105' in url or '20261106' in url for url in calls))
