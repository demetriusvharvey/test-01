import json
import sqlite3
import tempfile
import unittest
from scripts.line_lab.propline_scores import reserve_call,QUOTA
from scripts.line_lab.propline_quota import record_headers,path_for


class ProviderQuotaTests(unittest.TestCase):
    now='2026-10-29T12:00:00+00:00'
    def test_development_cannot_consume_operational_reserve(self):
        with tempfile.TemporaryDirectory() as root:
            path=path_for(root,self.now);path.parent.mkdir(parents=True)
            with sqlite3.connect(path) as db:
                db.executescript(QUOTA)
                db.executemany('INSERT INTO calls VALUES (?,?,?)',[(str(i),'scores_nba',self.now) for i in range(350)])
            self.assertFalse(reserve_call(root,'events_nba',self.now,purpose='development'))
            self.assertFalse(reserve_call(root,'events_nba',self.now,purpose='research'))
            self.assertTrue(reserve_call(root,'events_nba',self.now,purpose='operational'))
            self.assertFalse(reserve_call(root,'events_nba',self.now,daily_limit=1001))

    def test_research_has_its_own_limit_and_no_secrets_are_saved(self):
        with tempfile.TemporaryDirectory() as root:
            for _ in range(30):self.assertTrue(reserve_call(root,'injuries_nba',self.now,purpose='research'))
            self.assertFalse(reserve_call(root,'injuries_nba',self.now,purpose='research'))
            self.assertTrue(reserve_call(root,'scores_nba',self.now,purpose='operational'))
            record_headers(root,{'X-Daily-Limit':'1000','X-Daily-Used':'800','X-Daily-Remaining':'200','X-Daily-Reset':'1793318400','X-API-Key':'never-store'},self.now)
            with sqlite3.connect(path_for(root,self.now)) as db:
                payload=db.execute('SELECT payload FROM quota_headers').fetchone()[0]
                self.assertNotIn('never-store',payload)
                self.assertEqual(json.loads(payload)['remaining'],200)

    def test_provider_remaining_zero_stops_calls_until_utc_reset(self):
        with tempfile.TemporaryDirectory() as root:
            record_headers(root,{'X-Daily-Limit':'1000','X-Daily-Used':'1000','X-Daily-Remaining':'0','X-Daily-Reset':'1793318400'},self.now)
            self.assertFalse(reserve_call(root,'scores_nba',self.now))
            self.assertTrue(reserve_call(root,'scores_nba','2026-10-30T00:01:00+00:00'))

    def test_provider_retry_after_is_honored_without_retrying(self):
        with tempfile.TemporaryDirectory() as root:
            record_headers(root,{'X-Daily-Limit':'1000','X-Daily-Used':'1','X-Daily-Remaining':'999',
                                 'X-Daily-Reset':'1793318400','Retry-After':'60'},self.now)
            self.assertFalse(reserve_call(root,'scores_nba','2026-10-29T12:00:30+00:00'))
            self.assertTrue(reserve_call(root,'scores_nba','2026-10-29T12:01:01+00:00'))
