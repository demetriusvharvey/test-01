"""Run and record the player-exposure learner only on supplied verified records."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from scripts.line_lab.player_impact import eligible_player_rows,fit_player_impact
from scripts.line_lab.model_stack import append_trial


def run(root,now):
    path=Path(root)/'observations'/'player_exposures.json'
    records=[];error=None
    if path.exists():
        try:
            if path.stat().st_size>50_000_000:raise ValueError('dataset size limit')
            records=json.loads(path.read_text())
            if not isinstance(records,list) or any(not isinstance(row,dict) for row in records):
                raise ValueError('expected a list of records')
        except (ValueError,OSError,UnicodeError):
            records=[];error='invalid_input'
    lines=['# Player-impact training status','',f'Checked {now}.',
           'This job never changes public picks. Counts are unique eligible games, not repeated forecast snapshots.','',
           '| League | Input records | Eligible games | Seasons | Status |',
           '|---|---:|---:|---:|---|']
    for league in ('NBA','NFL'):
        eligible=eligible_player_rows(records,league,now)
        artifact=fit_player_impact(records,league,now) if not error else None
        append_trial(root,league,records,now,artifact,error=error,family='player-exposure-logistic-v1')
        status='research artifact; not promoted' if artifact else error or 'insufficient verified input'
        lines.append(f"| {league} | {sum(r.get('league')==league for r in records)} | {len(eligible)} | {len({r['season'] for r in eligible})} | {status} |")
        if artifact:
            lines.extend(['',f"{league}: validation log loss {artifact['validation']['log_loss']:.5f}; baseline {artifact['baseline_validation']['log_loss']:.5f}; {artifact['validation_games']} validation games. This is not an untouched test."])
    lines.extend(['','Required input: observations/player_exposures.json with verified pregame expected shares, player/team identities, roster verification, source-use qualification and chronological observation/result timestamps. Final minutes/snaps are not accepted as pregame projections. No source is enabled or approved by the presence of this file. Missing data remains missing.','',
                  'Default thresholds: three seasons, 500 earlier training games, 100 later validation games, 20 training appearances per estimated player. Unknown-player effects remain unavailable. No trained player model or improvement is implied when these thresholds fail.',''])
    return '\n'.join(lines)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args()
    result=run(args.data_root,datetime.now(timezone.utc).isoformat())
    Path(args.output).write_text(result)
