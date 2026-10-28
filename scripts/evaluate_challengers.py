#!/usr/bin/env python3
"""Run the preregistered forward challenger comparison and preserve failures."""
import argparse
import sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.line_lab.challenger_evaluation import read_inputs,evaluate,append_results


def main():
    p=argparse.ArgumentParser();p.add_argument('--data-root',required=True);p.add_argument('--output',default='reports/challenger_forward.md');args=p.parse_args()
    now=datetime.now(timezone.utc).isoformat();baselines,candidates,trials,outcomes=read_inputs(args.data_root)
    results=evaluate(baselines,candidates,trials,outcomes,now);append_results(args.data_root,results,now)
    lines=['# Forward challenger comparison','',f'Run {now}. The challenger and baseline must share the same recorded pregame timestamp.','',
           '| League | Challenger | Matched settled games | Excluded first forecasts | Log loss difference | Brier difference | Adjusted p | Status |',
           '| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |']
    def fmt(v):return '—' if v is None else f'{v:.4f}'
    for r in results:
        lines.append(f"| {r['league']} | {r['model_version']} | {r['games']} | {r['excluded']} | {fmt(r['logloss_difference'])} | {fmt(r['brier_difference'])} | {fmt(r['adjusted_p'])} | {r['status']} |")
    lines.extend(['','Negative differences favor the challenger. The registered game-day-block test needs at least 30 games on 10 days. Exclusions include pending games, unmatched timestamps, missing or unqualified sources and ties. NBA inputs remain blocked pending rights review.',
                  '', 'This is prospective research against the frozen team baseline, not a sharp-market or profitability comparison. A favorable result is not promotion: replication, an untouched later holdout and the registered sharp-market and paper-ROI conditions are still required. No wagers are placed.',''])
    Path(args.output).parent.mkdir(parents=True,exist_ok=True);Path(args.output).write_text('\n'.join(lines),encoding='utf-8')
    print('Forward challenger evaluation:',len(candidates),'forecast snapshots;',sum(x['games'] for x in results),'matched settled games')


if __name__=='__main__':main()
