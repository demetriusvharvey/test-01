"""Exercise saved NBA ML inference against the published real schedule."""
import argparse
import json
from pathlib import Path
from datetime import datetime,timezone
from scripts.research_simulator import load_games
from scripts.line_lab.nba_inference import record_nba_predictions


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();games,_=load_games(args.data_root)
    board=json.loads(Path('dist/board.json').read_text());now=datetime.now(timezone.utc).isoformat()
    result=record_nba_predictions(args.data_root,games,board.get('games',[]),now)
    lines=['# NBA trained-model inference verification','',f'Run: {now}. Status: {result["status"]}.',
           'Actual scheduled games and trained efficiency logistic artifact. Research outputs only; not the public pick list. No injury adjustment or validated future accuracy is claimed.','',
           '| Game | Home probability | Away probability | Model |','|---|---:|---:|---|']
    for row in result['predictions']:
        lines.append(f"| {row['away']} at {row['home']} | {row['home_probability']:.4f} | {row['away_probability']:.4f} | {row['model_version']} |")
    lines+=['','Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.','']
    Path(args.output).write_text('\n'.join(lines))
