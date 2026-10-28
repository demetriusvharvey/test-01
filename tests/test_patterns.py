import sqlite3
from contextlib import closing
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scripts.line_lab.patterns import analyze, append_run, _side


class PatternTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.start=datetime(2026,1,1,22,tzinfo=timezone.utc)
    def tearDown(self):self.tmp.cleanup()
    def row(self,i):
        start=self.start+timedelta(days=i//3,minutes=i%3)
        return {'game_id':str(i),'league':'NBA','season':'2025','rights_verified':True,
                'forecast_at':(start-timedelta(hours=1)).isoformat(),'starts_at':start.isoformat(),
                'final_observed_at':(start+timedelta(hours=3)).isoformat(),
                'features_observed_at':(start-timedelta(hours=2)).isoformat(),
                'market_source_as_of':(start-timedelta(hours=2)).isoformat(),
                'market_fetched_at':(start-timedelta(hours=1,minutes=30)).isoformat(),
                'market_home_probability':.6,'home_win':0,'features':{'home_rest':0,'away_rest':2,'home_b2b':True,'away_b2b':False}}
    def test_batch_reports_insufficient_data_and_corrects_valid_family(self):
        rows=[self.row(i) for i in range(30)];cutoff=(self.start+timedelta(days=20)).isoformat()
        results=analyze(rows,cutoff)
        first=next(x for x in results if x['id']=='H010a' and x['league']=='NBA')
        self.assertEqual(first['games'],30);self.assertEqual(first['days'],10)
        self.assertIsNotNone(first['raw_p']);self.assertIsNotNone(first['adjusted_p']);self.assertFalse(first['promoted'])
        missing=next(x for x in results if x['id']=='H010c')
        self.assertEqual(missing['status'],'not_testable');self.assertIsNone(missing['raw_p'])
        self.assertEqual(len(results),23)
    def test_postgame_features_rights_and_duplicate_outcomes_rejected(self):
        row=self.row(0);cutoff=(self.start+timedelta(days=4)).isoformat()
        earlier=dict(row);earlier['forecast_at']=(self.start-timedelta(hours=2)).isoformat()
        earlier['features_observed_at']=(self.start-timedelta(hours=3)).isoformat()
        earlier['market_fetched_at']=(self.start-timedelta(hours=2)).isoformat()
        earlier['market_source_as_of']=(self.start-timedelta(hours=3)).isoformat()
        result=analyze([row,earlier],cutoff)[0];self.assertEqual(result['games'],1)
        row['features_observed_at']=(self.start+timedelta(hours=1)).isoformat()
        self.assertEqual(analyze([row],cutoff)[0]['games'],0)
        earlier['rights_verified']=False
        self.assertEqual(analyze([earlier],cutoff)[0]['games'],0)
    def test_all_batch_states_are_append_only(self):
        cutoff=(self.start+timedelta(days=5)).isoformat();rows=[self.row(0)];results=analyze(rows,cutoff)
        self.assertEqual(append_run(self.root,rows,results,cutoff),23)
        self.assertEqual(append_run(self.root,rows,results,cutoff),0)
        with closing(sqlite3.connect(self.root/'observations/pattern_tests/2026-01-06.sqlite')) as db:
            with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM pattern_runs')
    def test_expanded_patterns_require_the_registered_observed_conditions(self):
        row=self.row(0);row['features'].update({'home_last_margin':-22,'away_last_margin':5,
            'home_games':4,'away_games':6,'book_probability_range':.09})
        self.assertEqual(_side(row,'H013a'),'home');self.assertIsNone(_side(row,'H013b'))
        self.assertEqual(_side(row,'H013e'),'away');self.assertEqual(_side(row,'H013g'),'home')
        row['features']['away_last_margin']=None
        self.assertIsNone(_side(row,'H013a'))
        row['league']='NFL';row['features'].update({'home_rest':4,'away_rest':6})
        self.assertEqual(_side(row,'H013c'),'home')
        row['features'].update({'home_rest':14,'away_rest':6})
        self.assertEqual(_side(row,'H013d'),'home')


if __name__=='__main__':unittest.main()
