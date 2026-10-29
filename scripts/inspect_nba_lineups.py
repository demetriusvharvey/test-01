"""Inspect verified current-season play-by-play schema before lineup modeling."""
import argparse
import csv
import gzip
import io
import json
import sqlite3
from datetime import datetime,timezone
from pathlib import Path
from scripts.line_lab.backfill import fetch_and_archive


def run(root,output):
    year='2027';url=f'https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_pbp/play_by_play_{year}.csv'
    spec={'dataset':'nba_play_by_play','season':year,'url':url,
          'license':'CC-BY-4.0; upstream use review required','attribution':'SportsDataverse hoopR, ESPN source; research only'}
    path=Path(root)/f'observations/backfill/nba_play_by_play/{year}.sqlite'
    results,failures=fetch_and_archive(root,[spec]) if not path.exists() else ([],[])
    info={'url':url,'checked_at':datetime.now(timezone.utc).isoformat(),'failures':failures,'status':'unavailable'}
    if path.exists():
        with sqlite3.connect(path) as db:
            record=db.execute('SELECT content_gzip,columns_json,row_count,sha256,retrieved_at FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
        text=gzip.decompress(record[0]).decode('utf-8-sig');reader=csv.DictReader(io.StringIO(text));columns=reader.fieldnames
        samples=[];substitutions=0;games=set();types={}
        for row in reader:
            games.add(row.get('game_id'));kind=row.get('type_text') or row.get('type.text') or ''
            types[kind]=types.get(kind,0)+1
            if 'substitut' in str(row).lower():
                substitutions+=1
                if len(samples)<3:samples.append(row)
        info.update({'status':'inspected','columns':columns,'rows':record[2],'sha256':record[3],
                     'observed_at':record[4],'games':len(games),'substitution_rows':substitutions,
                     'event_types':types,'substitution_examples':samples})
    folder=Path(root)/'observations/nba_lineups';folder.mkdir(parents=True,exist_ok=True)
    (folder/'source_inspection.json').write_text(json.dumps(info,indent=2))
    lines=['# NBA lineup source inspection','',f'Status: {info["status"]}. Source: {url}.',
           f'Rows: {info.get("rows",0)}; games: {info.get("games",0)}; substitution rows: {info.get("substitution_rows",0)}.',
           'This is source inspection, not a confirmed lineup reconstruction, trained player rating or live pick change. Source-use qualifications remain unresolved.','',
           '```json',json.dumps(info,indent=2),'```','']
    Path(output).write_text('\n'.join(lines))
    print(json.dumps({k:v for k,v in info.items() if k not in ('substitution_examples','columns','event_types')}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();run(args.data_root,args.output)
