import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from scripts.line_lab.ingest import get


class RetryTests(unittest.TestCase):
    def test_transient_failure_retries_then_succeeds(self):
        with patch('scripts.line_lab.ingest.urlopen',side_effect=[URLError('temporary'),io.BytesIO(b'ok')]) as call, patch('scripts.line_lab.ingest.time.sleep') as sleep:
            self.assertEqual(get('https://example.test/public'),'ok')
            self.assertEqual(call.call_count,2);sleep.assert_called_once_with(.2)

    def test_permanent_http_error_is_not_retried(self):
        error=HTTPError('https://example.test/public',404,'missing',{},None)
        with patch('scripts.line_lab.ingest.urlopen',side_effect=error) as call, patch('scripts.line_lab.ingest.time.sleep') as sleep:
            with self.assertRaises(HTTPError):get('https://example.test/public')
            self.assertEqual(call.call_count,1);sleep.assert_not_called()

    def test_transient_retries_have_a_limit(self):
        error=HTTPError('https://example.test/public',503,'down',{},None)
        with patch('scripts.line_lab.ingest.urlopen',side_effect=error) as call, patch('scripts.line_lab.ingest.time.sleep') as sleep:
            with self.assertRaises(HTTPError):get('https://example.test/public')
            self.assertEqual(call.call_count,3);self.assertEqual(sleep.call_count,2)


if __name__=='__main__':unittest.main()
