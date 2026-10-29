"""Fixed-config sklearn logistic/gradient-boosting comparison; no promotion."""
import argparse
import gzip
import hashlib
import json
import sqlite3
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scripts.research_simulator import load_games
from scripts.line_lab.nba_statistical import examples,FEATURES
from scripts.line_lab.nba_efficiency import parse_team_stats,enrich_examples,METRICS
from scripts.line_lab.simulator import score_metrics
import numpy as np


def evaluate(rows,season):
    earlier=sorted({r['season'] for r in rows if r['season']<season})
    if len(earlier)<2:return None
    train=[r for r in rows if r['season']<earlier[-1]]
    calibration=[r for r in rows if r['season']==earlier[-1]]
    test=[r for r in rows if r['season']==season]
    if len(train)<500 or len(calibration)<200 or not test:return None
    x=lambda data:[r['vector'] for r in data];y=lambda data:[r['home_win'] for r in data]
    metrics=lambda p:score_metrics([{'probability':float(v),'outcome':r['home_win']} for v,r in zip(p,test)])
    result={'test_season':season,'training_games':len(train),'calibration_games':len(calibration),
            'elo':metrics([r['elo'] for r in test])}
    models={'logistic':make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=1000,random_state=42)),
            'boosting':HistGradientBoostingClassifier(max_iter=100,max_depth=3,min_samples_leaf=40,l2_regularization=1,early_stopping=False,random_state=42)}
    logit=lambda p:np.log(np.clip(p,1e-6,1-1e-6)/(1-np.clip(p,1e-6,1-1e-6))).reshape(-1,1)
    for name,model in models.items():
        model.fit(x(train),y(train))
        calibrator=LogisticRegression(C=1,max_iter=1000,random_state=42)
        calibrator.fit(logit(model.predict_proba(x(calibration))[:,1]),y(calibration))
        p=model.predict_proba(x(test))[:,1]
        result[name]={'raw':metrics(p),'calibrated':metrics(calibrator.predict_proba(logit(p))[:,1])}
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();games,sources=load_games(args.data_root);stats={}
    for file in sorted((Path(args.data_root)/'observations/backfill/nba_team_game_boxscores').glob('*.sqlite')):
        with sqlite3.connect(file) as db:
            row=db.execute('SELECT content_gzip FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
        if row:stats.update(parse_team_stats(gzip.decompress(row[0]).decode('utf-8-sig')))
    rows=enrich_examples(examples(games),games,stats)
    results=[r for season in sorted({r['season'] for r in rows})[2:] if (r:=evaluate(rows,season))]
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    folder=Path(args.data_root)/'observations/nba_statistical'/digest;folder.mkdir(parents=True,exist_ok=True)
    (folder/'boosting_evaluation.json').write_text(json.dumps({'features':list(FEATURES)+list(METRICS),'sources':sources,'results':results},indent=2))
    lines=['# NBA efficiency model comparison','',
           'Fixed-config sklearn logistic and histogram gradient boosting, trained before a distinct calibration season and evaluated in later seasons. No random game splits or test-driven promotion. Archive already inspected; not an untouched holdout. Player/injury inputs unavailable; no market baseline or wagering-source qualification. Research only.','',
           '| Season | Test games | Logistic Brier | Boosting Brier | Elo Brier | Logistic accuracy | Boosting accuracy |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for r in results:
        a,b=r['logistic']['calibrated'],r['boosting']['calibrated']
        lines.append(f"| {r['test_season']} | {a['games']} | {a['brier']:.4f} | {b['brier']:.4f} | {r['elo']['brier']:.4f} | {a['accuracy']:.4f} | {b['accuracy']:.4f} |")
    lines+=['',f'Input hash: {digest}. Detailed results: data branch observations/nba_statistical/{digest}/boosting_evaluation.json.','',
            'Features include earlier Elo, scoring, rest and home court plus earlier offensive/defensive efficiency, effective FG%, estimated possessions, turnover/rebounding proxies, FT rate and 3P%. Rebounding is a per-possession proxy, not rebound-chance percentage. No player-adjusted rating is implied.','']
    Path(args.output).write_text('\n'.join(lines))


if __name__=='__main__':main()
