"""Import free player boxes and evaluate a prior-appearance rotation proxy."""
import argparse
import gzip
import json
import sqlite3
from pathlib import Path
from scripts.line_lab.backfill import fetch_and_archive
from scripts.line_lab.nba_rotation import parse_players,rotation_features
from scripts.line_lab.nba_efficiency import parse_team_stats,enrich_examples
from scripts.line_lab.nba_statistical import examples
from scripts.research_simulator import load_games
from scripts.research_nba_boosting import evaluate


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();base=Path(args.data_root)/'observations/backfill';specs=[]
    for year in range(2023,2028):
        if year<2027 and (base/'nba_player_boxscores'/f'{year}.sqlite').exists():continue
        specs.append({'dataset':'nba_player_boxscores','season':str(year),
                      'url':f'https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_player_boxscores/player_box_{year}.csv',
                      'license':'CC-BY-4.0; upstream use review required','attribution':'SportsDataverse hoopR NBA, ESPN source'})
    _,failures=fetch_and_archive(args.data_root,specs)
    players=[];provenance=[];stats={}
    for dataset in ('nba_player_boxscores','nba_team_game_boxscores'):
        for file in sorted((base/dataset).glob('*.sqlite')):
            with sqlite3.connect(file) as db:
                row=db.execute('SELECT content_gzip,source_url,sha256,retrieved_at,columns_json FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            if not row:continue
            text=gzip.decompress(row[0]).decode('utf-8-sig')
            if dataset=='nba_player_boxscores':
                parsed=parse_players(text);players.extend(parsed)
                provenance.append({'url':row[1],'sha256':row[2],'observed_at':row[3],'parsed_player_rows':len(parsed),'columns':json.loads(row[4])})
            else:stats.update(parse_team_stats(text))
    games,_=load_games(args.data_root);rotation=rotation_features(games,players)
    rows=enrich_examples(examples(games),games,stats)
    matched=[r for r in rows if r['game_id'] in rotation]
    extended=[{**r,'vector':r['vector']+rotation[r['game_id']]['vector']} for r in matched]
    results=[]
    for season in sorted({r['season'] for r in matched})[2:]:
        baseline=evaluate(matched,season);candidate=evaluate(extended,season)
        if baseline and candidate:results.append({'season':season,'without_rotation':baseline,'with_rotation':candidate})
    artifact=Path(args.data_root)/'observations/nba_rotation';artifact.mkdir(parents=True,exist_ok=True)
    (artifact/'evaluation.json').write_text(json.dumps({'sources':provenance,'failures':failures,'results':results},indent=2))
    lines=['# NBA player rotation research','',
           'Free SportsDataverse player box imports. Projections use only earlier appearances; membership is inferred, not a verified pregame roster. Historical injuries, trades before first appearance and confirmed lineups remain unknown. No public pick is changed.','',
           f'Parsed player rows: {len(players)}. Rotation-covered games: {len(rotation)}. Matched modeling examples: {len(matched)}. Source failures: {len(failures)}.','',
           '| Season | Games | Baseline logistic Brier | Rotation logistic Brier | Rotation accuracy |',
           '|---|---:|---:|---:|---:|']
    for r in results:
        b,c=r['without_rotation']['logistic']['calibrated'],r['with_rotation']['logistic']['calibrated']
        lines.append(f"| {r['season']} | {c['games']} | {b['brier']:.4f} | {c['brier']:.4f} | {c['accuracy']:.4f} |")
    lines+=['','This is a chronological exploratory comparison on already inspected archives, not independent validation or proof of player impact. Scoring/minute proxies do not measure defense or replacement effects. Source rights remain qualified, not automatically approved by a repository license.','',
            'Source manifest, hashes, column schemas and full results: data branch observations/nba_rotation/evaluation.json.','']
    Path(args.output).write_text('\n'.join(lines))


if __name__=='__main__':main()
