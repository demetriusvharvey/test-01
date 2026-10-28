import unittest
from datetime import date
from scripts.line_lab.schedule_context import observed_rest_context


class ScheduleContextTests(unittest.TestCase):
    def test_reports_days_only_from_prior_observed_game_dates(self):
        event={'home':'A','away':'B','home_name':'Team A','away_name':'Team B','starts_at':'2026-10-29T00:00:00+00:00'}
        model={'last':{'A':date(2026,10,27),'B':date(2026,10,25)}}
        r=observed_rest_context(event,model,'2026-10-28T12:00:00+00:00')
        self.assertEqual(r['teams']['home']['rest_days'],0)
        self.assertTrue(r['teams']['home']['back_to_back'])
        self.assertEqual(r['teams']['away']['rest_days'],2)
        self.assertEqual(r['travel'],'unknown');self.assertFalse(r['used_in_prediction'])
    def test_future_or_unknown_dates_do_not_become_rest(self):
        event={'home':'A','away':'B','home_name':'A','away_name':'B','starts_at':'2026-10-29T00:00:00+00:00'}
        result=observed_rest_context(event,{'last':{'A':date(2026,10,29)}},'2026-10-28T12:00:00+00:00')
        self.assertIsNone(result['teams']['home']);self.assertIsNone(result['teams']['away'])
        self.assertIsNone(observed_rest_context(event,{'last':{}},'2026-10-29T00:00:00+00:00'))


if __name__=='__main__':unittest.main()
