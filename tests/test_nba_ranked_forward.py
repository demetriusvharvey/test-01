import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from scripts.line_lab.nba_ranked_forward import record_ranked,evaluate_ranked


class RankedForwardTests(unittest.TestCase):
    def fixture(self,all_disagree=False):
        now='2026-10-29T12:00:00+00:00';scheduled=[];rows=[]
        for i in range(4):
            game=f'nba:2026-10-29:A{i}:H{i}';start=f'2026-10-29T23:0{i}:00+00:00'
            scheduled.append({'id':game,'league':'NBA','starts_at':start})
            ps=(.4,.6) if i==3 or all_disagree else (.6,.8)
            context={'status':'conditional_research_only','model_version':'nba-rotation-logistic-v1','model_hash':'fixture',
                     'injury_observed_at':now,'uncertain_players':1,'exhaustive_listed_uncertainty':True,
                     'consistent_winner':None if min(ps)<.5<max(ps) else f'H{i}',
                     'scenarios':[{'scenario':str(j),'home_probability':p,'away_probability':1-p} for j,p in enumerate(ps)]}
            rows.append({'game_id':game,'home':f'H{i}','away':f'A{i}','starts_at':start,'predicted_at':now,
                         'model_exported_at':'2026-10-28T12:00:00+00:00','model_input_hash':'fixture','features':{'x':1},
                         'input_data_observed_at':'2026-10-29T11:00:00+00:00','model_version':'nba-efficiency-logistic-v1',
                         'home_probability':(.6,.7,.8,.9)[i],'away_probability':1-(.6,.7,.8,.9)[i],
                         'baseline_elo_probability':(.7,.6,.8,.55)[i],'availability_scenarios':context})
        return rows,scheduled,now

    def test_incomplete_data_retries_and_frozen_records_do_not_change(self):
        rows,slate,now=self.fixture()
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(record_ranked(root,rows[:-1],slate,now)['added'],0)
            missing=evaluate_ranked(root,now)['data_coverage']['nba-efficiency-logistic-v1']
            self.assertEqual(missing['audited_days_without_decision'],1)
            self.assertEqual(missing['unavailable_attempts'],1)
            self.assertEqual(record_ranked(root,rows,slate,now)['added'],2)
            self.assertEqual(record_ranked(root,rows,slate,now)['added'],0)
            r=evaluate_ranked(root,now)
            self.assertEqual(r['models']['nba-rotation-logistic-v1']['winner_record']['pending'],3)
            self.assertEqual(r['models']['nba-rotation-logistic-v1']['scenario_abstentions'],1)
            self.assertEqual(r['data_coverage']['nba-rotation-logistic-v1']['audited_days_without_decision'],0)
            self.assertIsNone(r['models']['nba-rotation-logistic-v1']['winner_record']['accuracy'])
            self.assertEqual(r['models']['nba-rotation-logistic-v1']['fully_settled_day_comparison']['complete_days'],0)
            self.assertIsNone(r['models']['nba-rotation-logistic-v1']['fully_settled_day_comparison']['accuracy_difference'])
            path=Path(root)/'observations/nba_ranked_forecasts/2026-10-29.sqlite'
            with sqlite3.connect(path) as db:
                before=db.execute('SELECT payload FROM decisions ORDER BY key').fetchall()
                with self.assertRaises(sqlite3.IntegrityError):db.execute("UPDATE decisions SET payload='{}'")
            rows[0]['home_probability']=.99;rows[0]['away_probability']=.01
            record_ranked(root,rows,slate,now)
            with sqlite3.connect(path) as db:self.assertEqual(before,db.execute('SELECT payload FROM decisions ORDER BY key').fetchall())

    def test_all_scenario_disagreement_is_zero_picks_not_missing_data(self):
        rows,slate,now=self.fixture(all_disagree=True)
        with tempfile.TemporaryDirectory() as root:
            record_ranked(root,rows,slate,now)
            r=evaluate_ranked(root,now)['models']['nba-rotation-logistic-v1']
            self.assertEqual(r['winner_record']['pending'],0)
            self.assertEqual(r['scenario_abstentions'],4)
            self.assertIsNone(r['winner_record']['accuracy'])

    def test_confirmed_outcomes_only_and_ties_are_not_losses(self):
        rows,slate,now=self.fixture()
        with tempfile.TemporaryDirectory() as root:
            record_ranked(root,rows,slate,now)
            folder=Path(root)/'observations/nba_ml_predictions';folder.mkdir(parents=True)
            final_now='2026-10-30T04:00:00+00:00'
            with sqlite3.connect(folder/'confirmed_outcomes.sqlite') as db:
                db.execute('CREATE TABLE outcomes(game_id TEXT PRIMARY KEY,payload TEXT)')
                for i,row in enumerate(rows):
                    final={'game_id':row['game_id'],'home':row['home'],'away':row['away'],'starts_at':row['starts_at'],
                           'home_score':100,'away_score':100 if i==0 else 90,'confirmed_at':final_now,'source':'confirmed fixture'}
                    db.execute('INSERT INTO outcomes VALUES (?,?)',(row['game_id'],json.dumps(final)))
            model=evaluate_ranked(root,final_now)['models']['nba-rotation-logistic-v1']
            self.assertEqual(model['winner_record']['wins'],2)
            self.assertEqual(model['winner_record']['voids'],1)
            self.assertEqual(model['winner_record']['losses'],0)
            self.assertEqual(model['winner_record'],model['matched_elo_record'])
            self.assertEqual(model['fully_settled_day_comparison']['complete_days'],1)
            self.assertEqual(model['fully_settled_day_comparison']['accuracy_difference'],0.)


    def test_mismatched_identity_and_stale_injury_report_are_not_a_forecast(self):
        rows,slate,now=self.fixture()
        with tempfile.TemporaryDirectory() as root:
            rows[0]['home']='WRONG'
            self.assertEqual(record_ranked(root,rows,slate,now)['added'],0)
        rows,slate,now=self.fixture()
        with tempfile.TemporaryDirectory() as root:
            for row in rows:row['availability_scenarios']['injury_observed_at']='2026-10-28T12:00:00+00:00'
            self.assertEqual(record_ranked(root,rows,slate,now)['added'],1)
            report=evaluate_ranked(root,now)
            self.assertNotIn('nba-rotation-logistic-v1',report['models'])

    def test_one_early_final_does_not_establish_a_paired_day_advantage(self):
        rows,slate,now=self.fixture()
        with tempfile.TemporaryDirectory() as root:
            record_ranked(root,rows,slate,now)
            folder=Path(root)/'observations/nba_ml_predictions';folder.mkdir(parents=True)
            final_now='2026-10-30T04:00:00+00:00';row=rows[3]
            final={'game_id':row['game_id'],'home':row['home'],'away':row['away'],'starts_at':row['starts_at'],
                   'home_score':110,'away_score':90,'confirmed_at':final_now,'source':'confirmed fixture'}
            with sqlite3.connect(folder/'confirmed_outcomes.sqlite') as db:
                db.execute('CREATE TABLE outcomes(game_id TEXT PRIMARY KEY,payload TEXT)')
                db.execute('INSERT INTO outcomes VALUES (?,?)',(row['game_id'],json.dumps(final)))
            m=evaluate_ranked(root,final_now)['models']['nba-efficiency-logistic-v1']
            self.assertEqual(m['winner_record']['wins'],1)
            self.assertEqual(m['review_status'],'insufficient_forward_sample')
            self.assertEqual(m['fully_settled_day_comparison']['complete_days'],0)
            self.assertIsNone(m['fully_settled_day_comparison']['accuracy_difference'])
