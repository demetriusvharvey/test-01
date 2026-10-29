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
from scripts.line_lab.nba_acceptance import check_predictions


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args()
    from scripts.line_lab.nba_refresh import refresh_current_sources
    print('NBA current source refresh:',json.dumps(refresh_current_sources(args.data_root,datetime.now(timezone.utc).isoformat()),sort_keys=True))
    games,_=load_games(args.data_root)
    board=json.loads(Path('dist/board.json').read_text());now=datetime.now(timezone.utc).isoformat()
    payload=None;observed=None
    key=os.environ.get('PROPLINE_API_KEY','').strip()
    if use_provider(key,os.environ.get('PROPLINE_ENABLED',''),False):
        if reserve_call(args.data_root,'injuries_nba',now):
            payload,observed=fetch_nba_injuries(key,True)
    now=datetime.now(timezone.utc).isoformat()
    result=record_nba_predictions(args.data_root,games,board.get('games',[]),now,payload,observed)
    acceptance=check_predictions(result['predictions'],now)
    output=Path(args.data_root)/'observations/nba_rotation/inference_acceptance.json'
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(acceptance,indent=2))
    lines=['# NBA trained-model inference verification','',f'Run: {now}. Status: {result["status"]}.',
           'Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.','',
           '| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |','|---|---:|---:|---|---:|---|---|']
    for row in result['predictions']:
        context=row.get('availability_scenarios') or {}
        bounds=context.get('home_scenario_range')
        interval=f'{bounds[0]:.4f}–{bounds[1]:.4f}' if bounds else 'unavailable'
        lines.append(f"| {row['away']} at {row['home']} | {row['home_probability']:.4f} | {row['away_probability']:.4f} | {context.get('status','rotation_model_unavailable')} | {context.get('scenario_count',0)} | {interval} | {context.get('consistent_winner') or 'unresolved'} |")
        diagnostic=row.get('availability_scenarios',{}).get('join_diagnostics')
        if diagnostic:lines.append('\nAggregate join diagnostics: '+json.dumps(diagnostic,sort_keys=True)+'\n')
    lines+=['','Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.','']
    lines+=['## Multi-stat availability scenarios','',
            '| Game | Status | Scenarios | Home sensitivity range | Consistent winner |',
            '|---|---|---:|---|---|']
    for row in result['predictions']:
        context=row.get('player_box_scenarios') or {}
        bounds=context.get('home_scenario_range')
        interval=f'{bounds[0]:.4f}–{bounds[1]:.4f}' if bounds else 'unavailable'
        lines.append(f"| {row['away']} at {row['home']} | {context.get('status','model_unavailable')} | {context.get('scenario_count',0)} | {interval} | {context.get('consistent_winner') or 'unresolved'} |")
    lines+=['## Implementation acceptance','',f"Status: {acceptance['status']}; today’s games checked: {acceptance['games_checked']}.",
            'This verifies model inference and conditional injury integration. It does not establish causal injury impacts, confirmed lineups, predictive interval coverage, wagering permissions, profitability or production promotion.','']
    lines.extend(f"- {'PASS' if c['passed'] else 'MISSING'}: {c['check']}" for c in acceptance['checks'])
    Path(args.output).write_text('\n'.join(lines))
