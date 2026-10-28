"""Chronological retrospective validation of independent scoring processes."""
import argparse
import gzip
import json
import sqlite3
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from scripts.line_lab.model import build_ratings, project_home
from scripts.line_lab.possession_simulator import nba_observations, nfl_drive_observations, walk_forward
from scripts.line_lab.simulator import score_metrics
from scripts.research_simulator import load_games


def load_units(root,league):
    dataset='nba_team_game_boxscores' if league=='NBA' else 'nfl_pbp'
    parser=nba_observations if league=='NBA' else nfl_drive_observations
    output=[];sources=[]
    for file in sorted((Path(root)/'observations'/'backfill'/dataset).glob('*.sqlite')):
        with closing(sqlite3.connect(file)) as db:
            row=db.execute('SELECT content_gzip,source_url,sha256,retrieved_at,row_count,license FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
        if not row:continue
        data,url,digest,retrieved,rows,license=row
        parsed=parser(gzip.decompress(data).decode('utf-8-sig'))
        output.extend(parsed)
        sources.append({'url':url,'sha256':digest,'retrieved_at':retrieved,'source_rows':rows,
                        'parsed_games':len(parsed),'license':license})
    dedup={}
    for game in output:
        if game['id'] in dedup and game!=dedup[game['id']]:raise ValueError('conflicting archived source game')
        dedup[game['id']]=game
    return list(dedup.values()),sources


def compare(games,observations,first_season,draws=5000):
    forecasts=walk_forward(observations,games,first_season,draws)
    matched=[];baseline=[];lookup={g['id']:g for g in games}
    byday=defaultdict(list)
    for row in forecasts:byday[lookup[row['game_id']]['date']].append(row)
    for day,rows in sorted(byday.items()):
        rating=build_ratings(games,day,observations[0]['league'])
        for r in rows:
            g=lookup[r['game_id']]
            elo=project_home(rating,g['home'],g['away'],datetime.combine(day,datetime.min.time(),timezone.utc),g.get('neutral',False))
            if elo is not None:
                matched.append(r)
                baseline.append({'probability':elo,'outcome':r['outcome']})
    return {'simulator':score_metrics(matched),'elo_matched':score_metrics(baseline),
            'forecasted_games':len(forecasts),'test_seasons':sorted({r['season'] for r in forecasts}),
            'draws_per_game':draws,'winner':'simulator' if matched and score_metrics(matched)['brier']<score_metrics(baseline)['brier'] else 'elo_or_insufficient'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();games,_=load_games(args.data_root);results={}
    for league,season in (('NBA','2026-27'),('NFL','2025')):
        observations,sources=load_units(args.data_root,league)
        results[league]={'sources':sources,'observations':len(observations)}
        if observations:
            results[league]['evaluation']=compare([g for g in games if g['league']==league],observations,season)
    fmt=lambda x:'—' if x is None else f'{x:.4f}'
    lines=['# Independent scoring-process simulator evaluation','',
           'Research-only challenger. The NBA model estimates possessions from box scores rather than reconstructing play-by-play. NFL outcomes represent observed *offensive* drive scoring; defensive and return scores are not modeled. No current player availability, market prices, RotoBot outputs, or game-specific injury scenarios are used. The site does not use these probabilities for picks.','',
           '| League | Archived source games | Matched test games | Simulator Brier | Elo Brier | Simulator log loss | Elo log loss |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for league,entry in results.items():
        e=entry.get('evaluation',{});s=e.get('simulator',{});b=e.get('elo_matched',{})
        lines.append(f"| {league} | {entry['observations']} | {s.get('games',0)} | {fmt(s.get('brier'))} | {fmt(b.get('brier'))} | {fmt(s.get('log_loss'))} | {fmt(b.get('log_loss'))} |")
    lines.extend(['','Matched chronological evaluation uses the same games for Elo and challenger. The seasons and sources have been inspected before; this is exploratory, not a fresh untouched holdout. Simulation count reduces sampling noise, not estimation error. NBA upstream data rights for wagering remain unresolved, so this asset is not connected to published betting opportunities. NFL pregame roster and all-position injury scenarios are missing; NFL challenger also stays research-only. No historical betting ROI is claimed.','',
                  '## Source provenance',''])
    for league,entry in results.items():
        for s in entry['sources']:
            lines.append(f"- {league} {s['url']} — {s['parsed_games']} parsed games, {s['source_rows']} rows, archived {s['retrieved_at']}, SHA-256 `{s['sha256']}`, license `{s['license']}`")
    lines.extend(['','## Machine-readable results','','```json',json.dumps(results,indent=2,sort_keys=True),'```',''])
    Path(args.output).write_text('\n'.join(lines));print(json.dumps({x:y.get('evaluation',{}) for x,y in results.items()},sort_keys=True))

if __name__=='__main__':main()
