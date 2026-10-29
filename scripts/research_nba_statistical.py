"""Train NBA logistic and calibrate on a distinct historical season."""
import argparse
import hashlib
import json
from pathlib import Path
from scripts.research_simulator import load_games
from scripts.line_lab.nba_statistical import examples,evaluate_season


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();games,sources=load_games(args.data_root)
    rows=examples(games);results=[]
    for season in sorted({r['season'] for r in rows})[2:]:
        result=evaluate_season(rows,season)
        if result:results.append(result)
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    artifact=Path(args.data_root)/'observations/nba_statistical'/digest
    artifact.mkdir(parents=True,exist_ok=True)
    (artifact/'evaluation.json').write_text(json.dumps({'input_hash':digest,'sources':sources,'results':results},sort_keys=True,indent=2))
    lines=['# NBA statistical baseline evaluation','',
           'Real archived scores; all features use earlier game dates. Logistic trains on earlier seasons, Platt calibration uses a separate later season, and testing uses the next season. These archives were inspected previously: chronological, not untouched. No injury input, source permission or betting edge is implied. Research only.','',
           '| Test season | Training | Calibration | Test games | Calibrated accuracy | Calibrated Brier | Elo Brier | Calibrated log loss | Elo log loss |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in results:
        m,e=r['calibrated_logistic'],r['elo']
        lines.append(f"| {r['test_season']} | {r['training_games']} | {r['calibration_games']} | {m['games']} | {m['accuracy']:.4f} | {m['brier']:.4f} | {e['brier']:.4f} | {m['log_loss']:.4f} | {e['log_loss']:.4f} |")
    lines+=['',f'Input SHA-256: {digest}. Detailed metrics, reliability bins and artifacts are on the data branch under observations/nba_statistical/'+digest+'/evaluation.json.','',
            'This evaluates the score-based NBA logistic baseline, not full player-aware Phase 2. Player/lineup inputs, gradient boosting, source-use qualification and independent future confirmation remain open. No production promotion occurs.','']
    Path(args.output).write_text('\n'.join(lines))
    print(json.dumps({'examples':len(rows),'evaluated_seasons':len(results)}))


if __name__=='__main__':main()
