#!/usr/bin/env python3
"""Run the preregistered pattern batch against captured forward observations."""
import argparse
import json
import sqlite3
import sys
from contextlib import closing
from datetime import date, datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.line_lab.constants import ET
from scripts.line_lab.experiment import read_forecasts
from scripts.line_lab.history import aware
from scripts.line_lab.patterns import analyze, append_run


def load_rows(root):
    forecasts=read_forecasts(root);path=Path(root)/'observations'/'forecast_outcomes.sqlite';outcomes={}
    if path.exists():
        with closing(sqlite3.connect(path)) as db:
            db.row_factory=sqlite3.Row
            outcomes={r['game_id']:dict(r) for r in db.execute('SELECT * FROM outcomes')}
    rows=[]
    for forecast in forecasts:
        out=outcomes.get(forecast['game_id'])
        if not out or out['home_score']==out['away_score'] or (out['home'],out['away'])!=(forecast['home'],forecast['away']):continue
        try:
            features=json.loads(forecast['feature_snapshot']);market=json.loads(forecast['market_snapshot'])
            quotes=list(market.values())
            if not quotes or any(not q.get('fetched_at') or not q.get('provider') for q in quotes):continue
            source=max(aware(q['as_of']) for q in quotes);fetched=max(aware(q['fetched_at']) for q in quotes)
            start=aware(forecast['starts_at']);day=start.astimezone(ET).date();last_h=date.fromisoformat(features['home_last']);last_a=date.fromisoformat(features['away_last'])
            if last_h>day or last_a>day:continue
            home_rest=max(0,(day-last_h).days-1);away_rest=max(0,(day-last_a).days-1)
            year=day.year if day.month>=8 else day.year-1
            # NBA upstream data rights remain unresolved; AgentBets bulk archive
            # rights are not verified. No source is promoted by implication.
            rights=(forecast['league']=='NFL' and all(q['provider']=='the_odds_api' for q in quotes))
            rows.append({'game_id':forecast['game_id'],'league':forecast['league'],'season':str(year),
                'forecast_at':forecast['captured_at'],'starts_at':forecast['starts_at'],'final_observed_at':out['observed_at'],
                'features_observed_at':forecast['captured_at'],'market_source_as_of':source.isoformat(),'market_fetched_at':fetched.isoformat(),
                'market_home_probability':forecast['retail_probability'],'home_win':int(out['home_score']>out['away_score']),
                'rights_verified':rights,'features':{'home_rest':home_rest,'away_rest':away_rest,
                    'home_b2b':home_rest==0,'away_b2b':away_rest==0,'home_team':forecast['home']}})
        except (KeyError,TypeError,ValueError,OverflowError):continue
    return rows,len(forecasts),len(outcomes)


def render(results,cutoff,forecast_count,outcome_count,raw_rows):
    lines=['# Pattern research report','',f'As of {cutoff}: {forecast_count} archived forecast snapshots, {outcome_count} separately observed outcomes, {raw_rows} matched rows before rights/time eligibility.',
           'All results are shadow-only. No pattern is promoted; insufficient data is not a failure or a success. H010 is one Benjamini–Hochberg family across the definitions and leagues below. Only valid tests enter the correction.', '',
           '| Hypothesis | League | Definition | Games / days | Mean win-minus-market | 95% day-block interval | Raw p | Adjusted p | Holdout | Status |',
           '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |']
    for r in results:
        effect='—' if r['effect'] is None else f"{100*r['effect']:+.2f} pp"
        interval='—' if r['interval'] is None else f"{100*r['interval'][0]:+.2f} to {100*r['interval'][1]:+.2f} pp"
        raw='—' if r['raw_p'] is None else f"{r['raw_p']:.4f}"
        q='—' if r['adjusted_p'] is None else f"{r['adjusted_p']:.4f}"
        lines.append(f"| {r['id']} | {r['league']} | {r['description']} | {r['games']} / {r['days']} | {effect} | {interval} | {raw} | {q} | {r['holdout']} | {r['status']} |")
    lines += ['', 'A result requires at least 30 games over 10 distinct game days even for an exploratory day-block test. Publication-time gaps, missing features, unsettled games and sources without verified rights are excluded. Day-block sign randomization assumes exchangeable signs across days; serial dependence and assumptions need review. For promotion, require two separate season replications, a genuinely untouched later holdout and the broader model-first validation gate.',
              '', 'A blank p-value means no qualified test was possible. Definitions and directions are in [HYPOTHESES.md](HYPOTHESES.md). Future reports must retain failures, all attempted variants, raw/adjusted p-values and sample counts.', '']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',required=True);parser.add_argument('--output',default='PATTERN_REPORT.md');args=parser.parse_args()
    now=datetime.now(timezone.utc).isoformat();rows,forecasts,outcomes=load_rows(args.data_root);results=analyze(rows,now)
    count=append_run(args.data_root,rows,results,now)
    Path(args.output).write_text(render(results,now,forecasts,outcomes,len(rows)),encoding='utf-8')
    print('Pattern research:',forecasts,'forecast snapshots;',outcomes,'outcomes;',len(rows),'matched rows;',count,'logged test states. No promotion.')


if __name__=='__main__':main()
