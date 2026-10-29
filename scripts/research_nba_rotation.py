"""Import free player boxes and evaluate a prior-appearance rotation proxy."""
import argparse
import gzip
import json
import sqlite3
from pathlib import Path
from scripts.line_lab.backfill import fetch_and_archive
from scripts.line_lab.nba_rotation import parse_players,rotation_features
from scripts.line_lab.nba_efficiency import parse_team_stats,enrich_examples
from scripts.line_lab.nba_efficiency import METRICS
from scripts.line_lab.nba_statistical import examples,FEATURES
from scripts.research_simulator import load_games
from scripts.research_nba_boosting import evaluate
from scripts.line_lab.nba_lineup import parse_current_rosters


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();base=Path(args.data_root)/'observations/backfill';specs=[]
    specs.append({'dataset':'nba_roster_snapshots','season':'2027',
                  'url':'https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_rosters/rosters_2027.csv',
                  'license':'CC-BY-4.0; upstream use review required','attribution':'SportsDataverse hoopR NBA, ESPN source; current capture only'})
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
    artifact=Path(args.data_root)/'observations/nba_rotation';artifact.mkdir(parents=True,exist_ok=True)
    names=list(FEATURES)+list(METRICS)+['rotation_scoring_difference','top_five_share_difference','experienced_share_difference']
    results=[]
    for season in sorted({r['season'] for r in matched})[2:]:
        baseline=evaluate(matched,season);candidate=evaluate(extended,season,artifact,names)
        if baseline and candidate:results.append({'season':season,'without_rotation':baseline,'with_rotation':candidate})
    if results:
        latest=sorted(r['season'] for r in results)[-1]
        model=json.loads((artifact/latest/'logistic.json').read_text())
        (artifact/'current_candidate.json').write_text(json.dumps(model,sort_keys=True))
    (artifact/'evaluation.json').write_text(json.dumps({'sources':provenance,'failures':failures,'results':results},indent=2))
    roster_path=base/'nba_roster_snapshots/2027.sqlite';roster_info=None
    if roster_path.exists():
        with sqlite3.connect(roster_path) as db:
            record=db.execute('SELECT source_url,sha256,retrieved_at,columns_json,row_count FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            content=db.execute('SELECT content_gzip FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
        if record:
            rosters=parse_current_rosters(gzip.decompress(content[0]).decode('utf-8-sig'),record[2],record[0])
            known={p['player_id'] for p in players}
            roster_ids={p for roster in rosters.values() for p in roster['player_ids']}
            roster_info={'url':record[0],'sha256':record[1],'observed_at':record[2],
                         'columns':json.loads(record[3]),'rows':record[4],
                         'teams_parsed':len(rosters),'current_ids_with_box_history':len(roster_ids&known),
                         'current_ids_without_box_history':len(roster_ids-known),
                         'injury_identity_crosswalk_verified':False}
            (artifact/'current_roster_source.json').write_text(json.dumps(roster_info,indent=2))
    lines=['# NBA player rotation research','',
           'Free SportsDataverse player box imports. Projections use only earlier appearances; membership is inferred, not a verified pregame roster. Historical injuries, trades before first appearance and confirmed lineups remain unknown. No public pick is changed.','',
           f'Parsed player rows: {len(players)}. Rotation-covered games: {len(rotation)}. Matched modeling examples: {len(matched)}. Source failures: {len(failures)}.',
           f"Current roster snapshot: {roster_info['rows'] if roster_info else 0} source rows; {roster_info['teams_parsed'] if roster_info else 0} teams; {roster_info['current_ids_with_box_history'] if roster_info else 0} current IDs matched to historical box scores. Injury crosswalk unverified.",'',
           '| Season | Games | Baseline logistic Brier | Rotation logistic Brier | Rotation accuracy |',
           '|---|---:|---:|---:|---:|']
    for r in results:
        b,c=r['without_rotation']['logistic']['calibrated'],r['with_rotation']['logistic']['calibrated']
        lines.append(f"| {r['season']} | {c['games']} | {b['brier']:.4f} | {c['brier']:.4f} | {c['accuracy']:.4f} |")
    lines+=['','This is a chronological exploratory comparison on already inspected archives, not independent validation or proof of player impact. Scoring/minute proxies do not measure defense or replacement effects. Source rights remain qualified, not automatically approved by a repository license.','',
            'Source manifest, hashes, column schemas and full results: data branch observations/nba_rotation/evaluation.json.','']
    Path(args.output).write_text('\n'.join(lines))


if __name__=='__main__':main()
