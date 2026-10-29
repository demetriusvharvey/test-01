"""Exercise saved NBA ML inference against the published real schedule."""
import argparse
import json
import os
from pathlib import Path
from datetime import datetime,timezone
from scripts.research_simulator import load_games
from scripts.line_lab.nba_inference import record_nba_predictions
from scripts.line_lab.nba_injury_feed import fetch_nba_injuries
from scripts.line_lab.propline_scores import use_provider,reserve_call


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();games,_=load_games(args.data_root)
    board=json.loads(Path('dist/board.json').read_text());now=datetime.now(timezone.utc).isoformat()
    payload=None;observed=None
    key=os.environ.get('PROPLINE_API_KEY','').strip()
    if use_provider(key,os.environ.get('PROPLINE_ENABLED',''),False):
        if reserve_call(args.data_root,'injuries_nba',now):
            payload,observed=fetch_nba_injuries(key,True)
    now=datetime.now(timezone.utc).isoformat()
    result=record_nba_predictions(args.data_root,games,board.get('games',[]),now,payload,observed)
    lines=['# NBA trained-model inference verification','',f'Run: {now}. Status: {result["status"]}.',
           'Actual scheduled games and trained efficiency logistic artifact. Research outputs only; not the public pick list. No injury adjustment or validated future accuracy is claimed.','',
           '| Game | Home probability | Away probability | Availability scenario status |','|---|---:|---:|---|']
    for row in result['predictions']:
        lines.append(f"| {row['away']} at {row['home']} | {row['home_probability']:.4f} | {row['away_probability']:.4f} | {row.get('availability_scenarios',{}).get('status','rotation_model_unavailable')} |")
    lines+=['','Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.','']
    Path(args.output).write_text('\n'.join(lines))
