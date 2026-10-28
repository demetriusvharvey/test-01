#!/usr/bin/env python3
"""Replay frozen candidates with a documented source-rights allowlist."""
import argparse
import hashlib
import json
import re
import sqlite3
import sys
from contextlib import closing
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.line_lab.experiment import read_forecasts
from scripts.line_lab.history import aware
from scripts.line_lab.paper_backtest import replay

SCHEMA='''
CREATE TABLE IF NOT EXISTS replay_runs (
 run_key TEXT PRIMARY KEY, completed_at TEXT NOT NULL, league TEXT NOT NULL,
 input_hash TEXT NOT NULL, result_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS replay_no_update BEFORE UPDATE ON replay_runs BEGIN SELECT RAISE(ABORT,'replay runs are append-only'); END;
CREATE TRIGGER IF NOT EXISTS replay_no_delete BEFORE DELETE ON replay_runs BEGIN SELECT RAISE(ABORT,'replay runs are append-only'); END;
'''


def approved(policy,league,provider,predicted,feature_snapshot):
    expected={'NFL':'nflverse+espn','NBA':'boxscorelab+espn'}.get(league)
    hashes=feature_snapshot.get('source_text_sha256',{})
    if not isinstance(hashes,dict):return None
    values=[v for k,v in hashes.items() if (league=='NFL' and k=='games.csv') or (league=='NBA' and re.fullmatch(r'\d{4}-\d{2}',k))]
    if not expected or not values or not all(isinstance(v,str) and re.fullmatch(r'[0-9a-f]{64}',v) for v in values):return None
    for item in policy.get('approved_sources',[]):
        try:
            if item.get('league')!=league or item.get('quote_provider')!=provider or item.get('rights_verified') is not True:continue
            if not item.get('rights_evidence') or item.get('feature_source')!=expected or not isinstance(item.get('outcome_sources'),list):continue
            if aware(item['reviewed_at'])>aware(predicted):continue
            return item
        except (KeyError,TypeError,ValueError):continue
    return None


def load_inputs(data_root,ledger_path,policy_path):
    root=Path(data_root);forecasts=read_forecasts(root)
    baseline={(f['game_id'],f['league'],f['captured_at']):f for f in forecasts}
    outcomes={};path=root/'observations'/'forecast_outcomes.sqlite'
    if path.exists():
        with closing(sqlite3.connect(path)) as db:
            db.row_factory=sqlite3.Row;outcomes={r['game_id']:dict(r) for r in db.execute('SELECT * FROM outcomes')}
    try:ledger=json.loads(Path(ledger_path).read_text(encoding='utf-8'))
    except (FileNotFoundError,ValueError):ledger=[]
    try:policy=json.loads(Path(policy_path).read_text(encoding='utf-8'))
    except (FileNotFoundError,ValueError):policy={'approved_sources':[]}
    frozen={(p.get('id'),p.get('predicted_at'),p.get('team_code')):p for p in ledger
            if p.get('ledger_version')==2 and p.get('mode')=='paper'}
    candidates=[]
    for path in sorted((root/'observations'/'candidates').glob('*.sqlite')):
        with closing(sqlite3.connect(path)) as db:
            db.row_factory=sqlite3.Row;candidates.extend(dict(r) for r in db.execute("SELECT * FROM candidates WHERE decision='selected_paper'"))
    rows=[]
    for candidate in candidates:
        try:
            detail=json.loads(candidate['detail_json']);pick=frozen.get((candidate['game_id'],candidate['captured_at'],detail['team']))
            base=baseline.get((candidate['game_id'],candidate['league'],candidate['captured_at']))
            if not pick or not base:continue
            quote=detail['books'][candidate['book']];side=candidate['side']
            if side not in ('home','away') or quote[side]!=candidate['price']:continue
            if detail['team']!=base[side] or aware(base['starts_at'])!=aware(candidate['starts_at']):continue
            if pick.get('observed_price')!=candidate['price']:continue
            expected_probability=base['pure_probability'] if side=='home' else 1-base['pure_probability']
            if abs(candidate['model_probability']-expected_probability)>1e-9:continue
            features=json.loads(base['feature_snapshot'])
            auth=approved(policy,candidate['league'],quote.get('provider'),candidate['captured_at'],features)
            out=outcomes.get(candidate['game_id']);status='pending';outcome_ok=False;observed=None
            if out and (out['home'],out['away'])==(base['home'],base['away']):
                outcome_ok=bool(auth and out.get('source') in auth['outcome_sources'])
                observed=out['observed_at']
                if out['home_score']!=out['away_score']:
                    winner='home' if out['home_score']>out['away_score'] else 'away'
                    status='win' if winner==side else 'loss'
                else:status='tie_unconfirmed'
            rows.append({'game_id':candidate['game_id'],'league':candidate['league'],'selection':'selected_paper',
                'side':side,'book':candidate['book'],'predicted_at':candidate['captured_at'],'starts_at':candidate['starts_at'],
                'feature_observed_at':base['captured_at'],'source_as_of':quote['as_of'],'fetched_at':quote['fetched_at'],
                'home_odds':quote['home'],'away_odds':quote['away'],'model_probability':candidate['model_probability'],
                'rights_verified':bool(auth),'result_status':status,'result_observed_at':observed,
                'outcome_rights_verified':outcome_ok})
        except (KeyError,TypeError,ValueError):continue
    return rows


def save_run(root,league,rows,result,now):
    path=Path(root)/'observations'/'paper_replay.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    key=hashlib.sha256((league+'|'+now+'|'+digest).encode()).hexdigest()
    with closing(sqlite3.connect(path)) as db,db:
        db.executescript(SCHEMA)
        db.execute('INSERT OR IGNORE INTO replay_runs VALUES (?,?,?,?,?)',(key,now,league,digest,json.dumps(result,sort_keys=True)))


def render(results,now):
    def number(x):return '—' if x is None else f'{x:.4f}'
    def percent(x):return '—' if x is None else f'{100*x:+.1f}%'
    def interval(x):return '—' if x is None else f'{100*x[0]:+.1f}% to {100*x[1]:+.1f}%'
    lines=['# Prospective paper replay','',f'Run {now}. This is a chronological replay of frozen model-first paper picks, not actual wagers.',
           'The preregistered scenario uses 100 units, at most 1 unit per pick, 3 units per local game day and a 2% haircut to the quoted net winning payout. Limits, slippage and fills are hypothetical.', '',
           '| League | Archived selections | Rights-qualified | Settled / pending | Model / same-book Brier | Paired log loss difference | Paper ROI (95% interval) | Certified sharp CLV (n) | Maximum drawdown |',
           '| --- | ---: | ---: | ---: | --- | ---: | --- | --- | ---: |']
    for league in ('NBA','NFL'):
        r=results[league]
        lines.append(f"| {league} | {r['forecast_candidates']} | {r['qualified_candidates']} | {r['settled']} / {r['pending_or_unresolved']} | {number(r['model_brier'])} / {number(r['market_brier'])} | {number(r['paired_logloss_difference'])} | {percent(r['paper_roi'])} ({interval(r['paper_roi_interval'])}) | {percent(r['sharp_clv'])} ({r['sharp_close_samples']}) | {number(r['max_drawdown_units'])} units |")
    lines += ['', 'Negative paired log-loss difference favors the model; same-book retail is descriptive, not an independent sharp comparator. Intervals require at least 30 settled games on 10 distinct days. Ties or cancellations are unresolved unless the relevant settlement rule is explicitly verified.',
              '', 'The source-rights allowlist is empty until each provider and model-input use is documented and approved; unverified sources cannot become a retrospective betting backtest. No certified sharp-close feed is configured. Results do not promote a model or authorize a stake.', '']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',required=True)
    parser.add_argument('--ledger',default=str(ROOT/'data/predictions.json'))
    parser.add_argument('--policy',default=str(ROOT/'data/research_permissions.json'))
    parser.add_argument('--output',default='reports/paper_backtest.md');args=parser.parse_args()
    now=datetime.now(timezone.utc).isoformat();rows=load_inputs(args.data_root,args.ledger,args.policy)
    results={league:replay([r for r in rows if r['league']==league],now) for league in ('NBA','NFL')}
    for league in results:save_run(args.data_root,league,[r for r in rows if r['league']==league],results[league],now)
    Path(args.output).parent.mkdir(parents=True,exist_ok=True);Path(args.output).write_text(render(results,now),encoding='utf-8')
    print('Paper replay:',len(rows),'frozen candidates;',sum(r['qualified_candidates'] for r in results.values()),'rights-qualified; no real bets')


if __name__=='__main__':main()
