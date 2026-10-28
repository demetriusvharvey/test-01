import unittest
from datetime import datetime,timedelta,timezone
from scripts.line_lab.validation import assess_forward,validation_gates,progress_from_ledger


def observation(day=0):
    start=datetime(2026,10,28,23,tzinfo=timezone.utc)+timedelta(days=day)
    t=lambda hours:(start+timedelta(hours=hours)).isoformat()
    return {'id':str(day),'predicted_at':t(-5),'starts_at':t(0),'final_observed_at':t(4),
            'sharp_source_at':t(-6),'sharp_observed_at':t(-5.5),'close_source_at':t(-.1),
            'close_observed_at':t(-.05),'rights_verified':True,'independent_sharp':True,
            'closing_certified':True,'sharp_source':'test fixture only','result':1,
            'model_probability':.6,'sharp_pregame_probability':.55,'sharp_close_probability':.58,'price':100}


class ValidationTests(unittest.TestCase):
    def test_rejects_lookahead_unverified_close_and_duplicate(self):
        good=observation();late=observation(1);late['sharp_observed_at']=late['final_observed_at']
        unknown=observation(2);unknown['closing_certified']=False
        summary=assess_forward([good,good,late,unknown])
        self.assertEqual(summary['eligible_games'],1)
        self.assertEqual(summary['excluded_games'],2)
        self.assertAlmostEqual(summary['sharp_clv'],.16)
        self.assertEqual(summary['paper_roi'],1)
        self.assertIsNone(summary['sharp_clv_interval'])

    def test_missing_data_never_passes_and_no_automatic_wager(self):
        summary=assess_forward([]);gates=validation_gates({'NBA':summary})
        self.assertFalse(gates['NBA']['evidence_bar_met'])
        self.assertFalse(gates['NBA']['staking_allowed'])
        self.assertFalse(gates['NFL']['automatic_promotion'])
        ledger=[{'league':'NBA','ledger_version':2,'mode':'paper','model':'pure-elo-v1','outcome':'win'},
                {'league':'NBA','model':'legacy','outcome':'loss'}]
        self.assertEqual(progress_from_ledger(ledger)['NBA']['settled_paper_picks'],1)
        self.assertEqual(progress_from_ledger(ledger)['NBA']['verified_sharp_closes'],0)


if __name__=='__main__':unittest.main()
