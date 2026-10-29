import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from scripts.line_lab.slate_archive import archive_slate
from scripts.research_models import load_availability_rows
from scripts.line_lab.position_status_model import FEATURES
from scripts.line_lab.model_stack import append_trial,record_challenger_forecasts
from scripts.line_lab.challenger_evaluation import read_inputs,evaluate


class SlateArchiveTests(unittest.TestCase):
    def test_unpriced_game_is_saved_immutably_and_feeds_future_training(self):
        game={'id':'nfl:2026-10-29:A:B','league':'NFL','home':'Home','away':'Away',
              'starts_at':'2026-10-30T00:00:00+00:00','neutral':False}
        model={'ratings':{'A':1500,'B':1600},'last':{},'home_advantage':42,
               'rest_weight':0,'source_hashes':{'games.csv':'hash'},'games_played':{'A':6,'B':6}}
        now='2026-10-29T12:00:00+00:00'
        context={'schema':'nfl-position-status-v1','source':'nflverse injury and practice reports',
                 'observed_at':now,'used_in_prediction':False,'features':dict.fromkeys(FEATURES,0)}
        with tempfile.TemporaryDirectory() as root:
            result=archive_slate(root,[game],{'NFL':model},[],now,injury_features={game['id']:context})
            self.assertEqual(result['forecasts_added'],1)
            artifact={'model_version':'nfl-position-status-logistic-v1','promoted':False,
                      'features':list(FEATURES),'weights':[0.0]*len(FEATURES),'intercept':0.0,
                      'trained_before':'2026-10-28T00:00:00+00:00'}
            append_trial(root,'NFL',[],'2026-10-28T01:00:00+00:00',artifact,family=artifact['model_version'])
            event={**game,'home':'B','away':'A'}
            self.assertEqual(record_challenger_forecasts(root,{game['id']:event},{'NFL':model},now,
                            position_contexts={game['id']:context}),1)
            self.assertEqual(archive_slate(root,[game],{'NFL':model},[],now,injury_features={game['id']:context})['forecasts_added'],0)
            final={'id':game['id'],'home':'B','away':'A','home_score':24,'away_score':17,'source':'nflverse'}
            self.assertEqual(archive_slate(root,[],{},[final],'2026-10-30T04:00:00+00:00')['outcomes_added'],1)
            rows=load_availability_rows(root,'2026-10-31T00:00:00+00:00','nfl_position_status','nfl-position-status-v1')
            self.assertEqual(len(rows),1);self.assertTrue(rows[0]['rights_verified'])
            self.assertEqual(rows[0]['home_win'],1)
            as_of='2026-10-31T00:00:00+00:00'
            baseline,candidates,trials,outcomes=read_inputs(root,as_of)
            result=next(r for r in evaluate(baseline,candidates,trials,outcomes,as_of)
                        if r['model_version']==artifact['model_version'])
            self.assertEqual(result['games'],1)
            self.assertAlmostEqual(result['brier_difference'],0.0)
            with sqlite3.connect(Path(root)/'observations/slate_archive.sqlite') as db:
                with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM slate_forecasts')

    def test_unknown_nfl_venue_and_blocked_history_do_not_create_forecasts(self):
        model={'ratings':{'A':1500,'B':1600},'last':{},'home_advantage':42,'rest_weight':0,'source_hashes':{'games.csv':'hash'}}
        game={'id':'nfl:2026-10-29:A:B','league':'NFL','starts_at':'2026-10-30T00:00:00+00:00'}
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(archive_slate(root,[game],{'NFL':model},[],'2026-10-29T12:00:00+00:00')['forecasts_added'],0)
            game['neutral']=False
            self.assertEqual(archive_slate(root,[game],{'NFL':model},[],'2026-10-29T12:00:00+00:00',blocked=['NFL'])['forecasts_added'],0)


if __name__=='__main__':unittest.main()
