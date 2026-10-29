import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from scripts.line_lab.nba_forward import evaluate_saved


class NBAForwardTests(unittest.TestCase):
    def test_earliest_forecast_paired_final_and_idempotence(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)/'observations/nba_ml_predictions';folder.mkdir(parents=True)
            row={'game_id':'nba:2026-10-29:CLE:ATL','model_version':'test','model_input_hash':'hash',
                 'home':'ATL','away':'CLE','starts_at':'2026-10-29T23:00:00+00:00',
                 'predicted_at':'2026-10-29T12:00:00+00:00','model_exported_at':'2026-10-28T12:00:00+00:00',
                 'input_data_observed_at':'2026-10-29T11:00:00+00:00','features':{'x':1},
                 'home_probability':.6,'away_probability':.4,'baseline_elo_probability':.55}
            with sqlite3.connect(folder/'2026-10-29.sqlite') as db:
                db.execute('CREATE TABLE predictions (payload TEXT)')
                for r in (row,{**row,'predicted_at':'2026-10-29T14:00:00+00:00','home_probability':.9,'away_probability':.1}):
                    db.execute('INSERT INTO predictions VALUES (?)',(json.dumps(r),))
            now='2026-10-30T04:00:00+00:00'
            self.assertEqual(evaluate_saved(root,[],now)['models']['test']['pending'],1)
            final={'id':row['game_id'],'home':'ATL','away':'CLE','starts_at':row['starts_at'],
                   'home_score':110,'away_score':100,'source':'confirmed fixture'}
            result=evaluate_saved(root,[final],now)['models']['test']
            self.assertEqual(result['model']['games'],1)
            self.assertAlmostEqual(result['model']['brier'],.16)
            self.assertAlmostEqual(result['elo']['brier'],.2025)
            self.assertEqual(evaluate_saved(root,[final],now)['models']['test']['model'],result['model'])
            with self.assertRaises(ValueError):evaluate_saved(root,[{**final,'away_score':120}],now)
            self.assertFalse(evaluate_saved(root,[],now)['promoted'])

    def test_invalid_source_tie_and_postgame_prediction_are_not_losses(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)/'observations/nba_ml_predictions';folder.mkdir(parents=True)
            row={'game_id':'nba:2026-10-29:CLE:ATL','model_version':'test','model_input_hash':'hash',
                 'home':'ATL','away':'CLE','starts_at':'2026-10-29T23:00:00+00:00',
                 'predicted_at':'2026-10-29T12:00:00+00:00','model_exported_at':'2026-10-28T12:00:00+00:00',
                 'input_data_observed_at':'2026-10-29T11:00:00+00:00','features':{'x':1},
                 'home_probability':.6,'away_probability':.4,'baseline_elo_probability':.55}
            with sqlite3.connect(folder/'2026-10-29.sqlite') as db:
                db.execute('CREATE TABLE predictions (payload TEXT)')
                for r in (row,{**row,'predicted_at':'2026-10-30T00:00:00+00:00'}):
                    db.execute('INSERT INTO predictions VALUES (?)',(json.dumps(r),))
            final={'id':row['game_id'],'home':'ATL','away':'CLE','starts_at':row['starts_at'],'home_score':100,'away_score':100}
            now='2026-10-30T04:00:00+00:00'
            self.assertEqual(evaluate_saved(root,[final],now)['models']['test']['pending'],1)
            result=evaluate_saved(root,[{**final,'source':'fixture'}],now)
            self.assertEqual(result['invalid_forecasts'],1)
            self.assertEqual(result['models']['test']['void'],1)
            self.assertEqual(result['models']['test']['model']['games'],0)


    def test_conditional_winners_freeze_earliest_and_track_disagreement(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)/'observations/nba_ml_predictions';folder.mkdir(parents=True)
            now='2026-10-30T04:00:00+00:00'
            row={'game_id':'nba:2026-10-29:CLE:ATL','model_version':'team-model','model_input_hash':'hash',
                 'home':'ATL','away':'CLE','starts_at':'2026-10-29T23:00:00+00:00',
                 'predicted_at':'2026-10-29T12:00:00+00:00','model_exported_at':'2026-10-28T12:00:00+00:00',
                 'input_data_observed_at':'2026-10-29T11:00:00+00:00','features':{'x':1},
                 'home_probability':.6,'away_probability':.4,'baseline_elo_probability':.55}
            context={'status':'conditional_research_only','model_version':'rotation-test','model_hash':'model-hash',
                     'injury_observed_at':'2026-10-29T11:00:00+00:00','exhaustive_listed_uncertainty':True,
                     'uncertain_players':1,'consistent_winner':'CLE',
                     'scenarios':[{'home_probability':p,'away_probability':1-p} for p in (.3,.4)]}
            mixed={**context,'model_version':'multistat-test','consistent_winner':None,
                   'scenarios':[{'home_probability':p,'away_probability':1-p} for p in (.4,.6)]}
            first={**row,'availability_scenarios':context,'player_box_scenarios':mixed}
            later={**row,'predicted_at':'2026-10-29T13:00:00+00:00','availability_scenarios':{
                **context,'consistent_winner':'ATL','scenarios':[{'home_probability':p,'away_probability':1-p} for p in (.6,.7)]}}
            with sqlite3.connect(folder/'2026-10-29.sqlite') as db:
                db.execute('CREATE TABLE predictions(payload TEXT)')
                for r in (later,first):db.execute('INSERT INTO predictions VALUES (?)',(json.dumps(r),))
            final={'id':row['game_id'],'home':'ATL','away':'CLE','starts_at':row['starts_at'],
                   'home_score':110,'away_score':100,'source':'fixture'}
            r=evaluate_saved(root,[final],now)['conditional_winner_records']
            self.assertEqual(r['rotation-test']['losses'],1)
            self.assertEqual(r['rotation-test']['accuracy'],0.)
            self.assertEqual(r['multistat-test']['abstained'],1)
            self.assertEqual(r['multistat-test']['settled_predictions'],0)
            self.assertNotIn('brier',r['rotation-test'])
            self.assertEqual(evaluate_saved(root,[],now)['conditional_winner_records'],r)
