#!/usr/bin/env python3
"""Record the preregistered trust/timing research attempt; never promote it."""
import argparse
import hashlib
import json
import sqlite3
import sys
from contextlib import closing
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.line_lab.trust_models import fit_trust_timing_shadow

SCHEMA='''
CREATE TABLE IF NOT EXISTS trust_trials (
 trial_id TEXT PRIMARY KEY, completed_at TEXT NOT NULL, league TEXT NOT NULL,
 input_hash TEXT NOT NULL, status TEXT NOT NULL, artifact_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trust_trials_no_update BEFORE UPDATE ON trust_trials BEGIN SELECT RAISE(ABORT,'trust trials are append-only'); END;
CREATE TRIGGER IF NOT EXISTS trust_trials_no_delete BEFORE DELETE ON trust_trials BEGIN SELECT RAISE(ABORT,'trust trials are append-only'); END;
'''


def read_labels(root):
    rows=[]
    for path in sorted((Path(root)/'observations'/'trust_samples').glob('*.sqlite')):
        with closing(sqlite3.connect(path)) as db:
            for (payload,) in db.execute('SELECT sample_json FROM trust_samples'):
                try:
                    value=json.loads(payload)
                    if isinstance(value,dict):rows.append(value)
                except (ValueError,TypeError):continue
    return rows


def save_trial(root,league,rows,now,artifact=None,error=None):
    path=Path(root)/'observations'/'trust_trials.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
    key=hashlib.sha256((league+'|'+now+'|'+digest).encode()).hexdigest()
    status='failed' if error else 'shadow_candidate' if artifact else 'insufficient_data'
    with closing(sqlite3.connect(path)) as db,db:
        db.executescript(SCHEMA)
        db.execute('INSERT OR IGNORE INTO trust_trials VALUES (?,?,?,?,?,?)',
                   (key,now,league,digest,status,json.dumps(artifact or {'reason':error or 'insufficient certified sharp data','promoted':False},sort_keys=True)))
    return status


def main():
    p=argparse.ArgumentParser();p.add_argument('--data-root',required=True);p.add_argument('--output',default='reports/trust_timing.md');args=p.parse_args()
    now=datetime.now(timezone.utc).isoformat();error=None
    try:rows=read_labels(args.data_root)
    except (sqlite3.Error,OSError) as exc:rows=[];error=type(exc).__name__
    lines=['# Shadow trust and timing research','',f'Run {now}: {len(rows)} labeled source rows before eligibility checks.', '',
           '| League | Status | Training games | Inner validation | Promoted |','| --- | --- | ---: | --- | --- |']
    for league in ('NBA','NFL'):
        try:
            if error:raise ValueError(error)
            artifact=fit_trust_timing_shadow(rows,league,now);status=save_trial(args.data_root,league,rows,now,artifact)
            lines.append(f"| {league} | {status} | {artifact['training_games'] if artifact else 0} | {artifact['validation_season'] if artifact else '—'} | no |")
        except Exception as exc:
            status=save_trial(args.data_root,league,rows,now,error=type(exc).__name__)
            lines.append(f'| {league} | {status}: {type(exc).__name__} | — | — | no |')
    lines.extend(['', 'The models require qualified pregame independent sharp anchors and certified close observations. The first pregame candidate per side is fixed before labels are inspected; the last prior season is an inner validation set, not a final holdout.',
                  '', 'No sharp-label feed is configured. Outputs are research-only, not bet-now/wait recommendations, user stakes or proof of profit. Expected EV, live candidate forecasts, source-specific label capture and promotion remain unimplemented until qualified data and validation exist.', ''])
    Path(args.output).parent.mkdir(parents=True,exist_ok=True);Path(args.output).write_text('\n'.join(lines),encoding='utf-8')
    print('Trust/timing research:',len(rows),'source rows; no automatic promotion')


if __name__=='__main__':main()
