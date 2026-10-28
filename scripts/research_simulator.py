"""Retrospective walk-forward score-simulator evaluation from archived assets."""
import argparse
import gzip
import json
import math
import sqlite3
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from scripts.line_lab.ingest import parse_nba_csv, parse_nfl_csv
from scripts.line_lab.model import build_ratings, project_home
from scripts.line_lab.simulator import backtest_scores, score_metrics


def load_games(root):
    base=Path(root)/'observations'/'backfill';games=[];sources=[]
    for dataset,parser in (('nba_team_game_boxscores',parse_nba_csv),('nfl_schedules',parse_nfl_csv)):
        for path in sorted((base/dataset).glob('*.sqlite')):
            with closing(sqlite3.connect(path)) as db:
                row=db.execute('SELECT content_gzip,source_url,sha256,retrieved_at FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            if not row:continue
            text=gzip.decompress(row[0]).decode('utf-8-sig')
            parsed=parser(text);games.extend(parsed)
            sources.append({'url':row[1],'sha256':row[2],'retrieved_at':row[3],'parsed_games':len(parsed)})
    dedup={}
    for g in games:
        if g['id'] in dedup and g!=dedup[g['id']]:raise ValueError('conflicting historical game: '+g['id'])
        dedup[g['id']]=g
    return list(dedup.values()),sources


def compare(games,league,first_test_season,draws=5000):
    league_games=[g for g in games if g['league']==league]
    rows=backtest_scores(league_games,league,first_test_season,draws)
    lookup={g['id']:g for g in league_games};byday=defaultdict(list)
    for row in rows:byday[lookup[row['game_id']]['date']].append(row)
    elo=[];home=[]
    for day,items in sorted(byday.items()):
        rating=build_ratings(league_games,day,league)
        for item in items:
            game=lookup[item['game_id']]
            p=project_home(rating,game['home'],game['away'],
                           datetime.combine(day,datetime.min.time(),timezone.utc),game.get('neutral',False))
            if p is None:continue
            elo.append({'probability':p,'outcome':item['outcome']})
            home.append({'probability':.5,'outcome':item['outcome']})
    return {'score_bootstrap':score_metrics(rows),'elo':score_metrics(elo),
            'uninformative_home_baseline':score_metrics(home),
            'seasons':sorted({str(r['season']) for r in rows}),
            'comparison_games':len(elo),'first_test_season':first_test_season,
            'draws_per_game':draws,'notes':'Retrospective final-score inputs; time-ordered within the dataset, no documented pregame publication timestamps. No historical NBA odds or matched-time market comparison. This is not an untouched holdout or evidence of ROI.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();games,sources=load_games(args.data_root)
    results={league:compare(games,league,start) for league,start in (('NBA','2025-26'),('NFL','2024'))}
    lines=['# Score-simulation challenger evaluation','',
           'The score bootstrap draws paired historical score variation around earlier team offense/defense estimates. It is not a drive, possession, player or injury simulator. It does not affect the live selection engine. Simulation count reduces Monte Carlo noise, not model error.','',
           '| League | Test seasons | Games | Simulator accuracy | Simulator Brier | Simulator log loss | Elo games | Elo Brier | Home baseline Brier |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    fmt=lambda n:'—' if n is None else f'{n:.4f}'
    for league,r in results.items():
        s,e,h=(r[key] for key in ('score_bootstrap','elo','uninformative_home_baseline'))
        lines.append(f"| {league} | {', '.join(r['seasons']) or 'none'} | {s['games']} | {fmt(s['accuracy'])} | {fmt(s['brier'])} | {fmt(s['log_loss'])} | {e['games']} | {fmt(e['brier'])} | {fmt(h['brier'])} |")
    lines.extend(['','These baselines may cover a slightly different set when ratings are unavailable; compare only matched games before promoting. Historical odds, lineup and injury timing are insufficient for a betting ROI or validated edge. The tested seasons have been inspected in prior research, so they are not untouched.','',
                  'Archived source files (each read as the most recently archived retrospective version):',''])
    lines.extend(f"- {s['url']} — {s['parsed_games']} games; archived {s['retrieved_at']}; SHA-256 `{s['sha256']}`" for s in sources)
    lines.extend(['','## Machine-readable results','','```json',json.dumps(results,indent=2,sort_keys=True),'```',''])
    Path(args.output).write_text('\n'.join(lines))
    print(json.dumps({k:{x:r['score_bootstrap'][x] for x in ('games','brier','log_loss')} for k,r in results.items()},sort_keys=True))


if __name__=='__main__':main()
