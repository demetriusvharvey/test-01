#!/usr/bin/env python3
"""Create a clearly retrospective descriptive report from a stored NFL asset."""
import argparse
import csv
import gzip
import io
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.line_lab.referees import retrospective_nfl_summary


def render(report,source_time,digest):
    lines=['# Referee research report','',
           '**No referee effect is approved for predictions or betting.** This report is descriptive; source assignment and betting-line publication times are not verified.', '',
           f"NFL 2021–2025 regular season, non-neutral games: **{report['games']}** settled non-ties; {report['excluded_ties']} tied games excluded. Snapshot retrieved {source_time}; SHA-256 `{digest}`.",
           f"Observed league home-win rate: {100*report.get('league_home_win_rate',0):.1f}%. The shrunken column uses an empirical league prior of {report.get('prior_strength',20)} games. Home-rate intervals are approximate 95% posterior-normal intervals; market residual intervals are approximate 95% normal intervals. Neither is a causal effect or holdout test.", '',
           '| Referee | Games | Home wins | Shrunk home win rate | Approx. 95% interval | Retrospective market rows | Home result minus market | Adjusted p | Holdout / verdict |',
           '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for r in report['officials']:
        market='—' if r['retrospective_market_residual'] is None else f"{100*r['retrospective_market_residual']:+.1f} pp"
        if r['market_interval'] is not None:market+=f" ({100*r['market_interval'][0]:+.1f} to {100*r['market_interval'][1]:+.1f})"
        low,high=r['interval']
        lines.append(f"| {r['referee']} | {r['games']} | {r['home_wins']} | {100*r['shrunken_home_win_rate']:.1f}% | {100*low:.1f}–{100*high:.1f}% | {r['market_games']} | {market} | — | not tested / descriptive only |")
    lines += ['', 'The market column uses the two moneylines found in the later nflverse schedule snapshot, proportionally devigged. Their bookmaker, first-observed time and true close are not established; do not use them for point-in-time backtests or claim CLV. Home/away imbalance, team quality, assignment selection and chance can all affect these descriptive rates.',
              '', 'NBA historical officiating/injury datasets with verified publication timestamps and suitable reuse rights are unavailable. Current NBA assignments are archived when observed, but unknown at pick time unless an earlier matching snapshot exists. Foul/penalty pace, officiating-team interactions, NBA crew effects, calibrated referee features, multiple-testing-adjusted p-values, two-season replication and untouched holdout are **not yet available**.',
              '', 'Source: nflverse/Lee Sharpe schedule snapshot (CC BY 4.0 as documented by nflverse; underlying provider terms require review). Protocol: [HYPOTHESES.md](HYPOTHESES.md), H009. No hypothesis test was run for this descriptive table.', '']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser();p.add_argument('--database',required=True);p.add_argument('--output',default='REFEREE_REPORT.md');args=p.parse_args()
    with closing(sqlite3.connect(args.database)) as db:
        row=db.execute('SELECT retrieved_at,sha256,content_gzip FROM assets WHERE dataset=? ORDER BY retrieved_at DESC LIMIT 1',('nfl_schedules',)).fetchone()
    if not row:raise SystemExit('No NFL schedule asset found')
    rows=csv.DictReader(io.StringIO(gzip.decompress(row[2]).decode('utf-8-sig')))
    report=retrospective_nfl_summary(rows)
    if not report['games']:raise SystemExit('No eligible descriptive games')
    Path(args.output).write_text(render(report,row[0],row[1]),encoding='utf-8')
    print('Retrospective NFL referee summary:',report['games'],'games;',len(report['officials']),'officials. No test or promotion.')


if __name__=='__main__':main()
