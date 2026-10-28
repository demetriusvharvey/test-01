#!/usr/bin/env python3
"""Train only eligible past-only challengers and record all attempted runs."""
import argparse
import json
import sqlite3
import sys
from contextlib import closing
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.line_lab.constants import ET
from scripts.line_lab.experiment import read_forecasts,corroborated_nfl_outcomes
from scripts.line_lab.history import aware
from scripts.line_lab.model_stack import append_trial,fit_elastic_net_shadow
from scripts.line_lab.boosted_shadow import fit_boosted_shadow


def load_training_rows(root,as_of=None):
    forecasts=read_forecasts(root);path=Path(root)/'observations'/'forecast_outcomes.sqlite';outcomes={}
    if path.exists():
        with closing(sqlite3.connect(path)) as db:
            db.row_factory=sqlite3.Row;outcomes={r['game_id']:dict(r) for r in db.execute('SELECT * FROM outcomes')}
    confirmed=corroborated_nfl_outcomes(root,as_of or datetime.now(timezone.utc).isoformat())
    rows=[]
    for forecast in forecasts:
        out=confirmed.get(forecast['game_id']) if forecast['league']=='NFL' else outcomes.get(forecast['game_id'])
        if not out or out['home_score']==out['away_score'] or (out['home'],out['away'])!=(forecast['home'],forecast['away']):continue
        try:
            f=json.loads(forecast['feature_snapshot']);start=aware(forecast['starts_at']);day=start.astimezone(ET).date()
            home_games,away_games=f['home_games'],f['away_games']
            if not isinstance(home_games,int) or not isinstance(away_games,int):continue
            year=day.year if day.month>=8 else day.year-1
            # NBA inputs have unresolved upstream use restrictions. NFL rows
            # require a labeled nflverse final and a captured schedule hash.
            rights=(forecast['league']=='NFL' and out.get('source')=='nflverse' and bool(f.get('source_text_sha256',{}).get('games.csv')))
            rows.append({'game_id':forecast['game_id'],'league':forecast['league'],'season':str(year),
                         'feature_observed_at':forecast['captured_at'],'forecast_at':forecast['captured_at'],
                         'starts_at':forecast['starts_at'],'final_observed_at':out['observed_at'],
                         'home_win':int(out['home_score']>out['away_score']),'rights_verified':rights,
                         'baseline_probability':forecast['pure_probability'],
                         'features':{'rating_difference':f['home_rating']-f['away_rating'],
                           'home_advantage':0 if f.get('neutral') else f['home_advantage'],
                           'games_played_difference':home_games-away_games}})
        except (KeyError,TypeError,ValueError):continue
    return rows,len(forecasts),len(outcomes)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',required=True);parser.add_argument('--output',default='reports/model_registry.md');args=parser.parse_args()
    now=datetime.now(timezone.utc).isoformat();rows,forecasts,outcomes=load_training_rows(args.data_root,now)
    lines=['# Weekly model challenger registry','',f'Run {now}: {forecasts} forecast snapshots, {outcomes} outcome records, {len(rows)} matched rows before eligibility.', '',
           '| League | Model | Status | Eligible training games | Validation season | Promoted |','| --- | --- | --- | ---: | --- | --- |']
    for league in ('NBA','NFL'):
        for family,fit in (('pure-elasticnet-v1',fit_elastic_net_shadow),('pure-stumpboost-v1',fit_boosted_shadow)):
            try:
                candidate=fit(rows,league,now)
                trial=append_trial(args.data_root,league,rows,now,candidate,family=family)
                lines.append(f"| {league} | {family} | {'shadow candidate' if candidate else 'insufficient data'} | {candidate['training_games'] if candidate else 0} | {candidate['validation_season'] if candidate else '—'} | no |")
                print('Challenger',league,family,'candidate' if candidate else 'insufficient data','trial',trial)
            except Exception as exc:
                trial=append_trial(args.data_root,league,rows,now,error=type(exc).__name__,family=family)
                lines.append(f'| {league} | {family} | failed: {type(exc).__name__} | — | — | no |')
                print('Challenger',league,family,'failed',type(exc).__name__,'trial',trial)
    lines += ['', 'Both pure challengers use rating difference, home advantage and games-played difference, without odds, an anchor, spreads or totals. The fixed-grid monotonic boosted-stump model is a standard-library research implementation, not XGBoost, LightGBM, CatBoost or Optuna. Inner validation uses a later prior season; the artifact is refit only on data settled before this run, then may produce separately logged future shadow forecasts. It is never automatically promoted by training alone.',
              '', 'The default training gate requires at least 500 earlier training games, 100 validation games and three seasons with eligible point-in-time data. Eligibility and missingness can make the useful sample much smaller than raw snapshot counts. NBA inputs are blocked pending rights review. No model-vs-sharp or profit result is assumed.', '']
    Path(args.output).parent.mkdir(parents=True,exist_ok=True);Path(args.output).write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':main()
