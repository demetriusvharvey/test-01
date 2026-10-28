"""Versioned source-asset backfill; retrospective data never enters live picks."""
import csv
import gzip
import hashlib
import io
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

NBA_SEASONS=('2022-23','2023-24','2024-25','2025-26','2026-27')
NFL_SEASONS=range(2021,2027)
NFL_BASE='https://github.com/nflverse/nflverse-data/releases/download'
SCHEMA='''
CREATE TABLE IF NOT EXISTS assets (
  sha256 TEXT PRIMARY KEY, dataset TEXT NOT NULL, season TEXT NOT NULL,
  source_url TEXT NOT NULL, retrieved_at TEXT NOT NULL, source_last_modified TEXT,
  source_etag TEXT, license TEXT NOT NULL, attribution TEXT NOT NULL,
  knowledge_status TEXT NOT NULL, format TEXT NOT NULL, columns_json TEXT NOT NULL,
  row_count INTEGER NOT NULL, content_gzip BLOB NOT NULL
);
CREATE TRIGGER IF NOT EXISTS assets_no_update BEFORE UPDATE ON assets
BEGIN SELECT RAISE(ABORT, 'backfill assets are append-only'); END;
CREATE TRIGGER IF NOT EXISTS assets_no_delete BEFORE DELETE ON assets
BEGIN SELECT RAISE(ABORT, 'backfill assets are append-only'); END;
'''

def catalog():
    assets=[{'dataset':'nfl_schedules','season':'all','url':NFL_BASE+'/schedules/games.csv',
             'attribution':'Lee Sharpe and nflverse, CC BY 4.0','license':'CC-BY-4.0'}]
    for year in NFL_SEASONS:
        for dataset,tag,prefix in [('nfl_pbp','pbp','play_by_play'),('nfl_injuries','injuries','injuries'),('nfl_depth_charts','depth_charts','depth_charts'),('nfl_snap_counts','snap_counts','snap_counts')]:
            compressed=(dataset in ('nfl_pbp','nfl_snap_counts') or dataset=='nfl_injuries' and year>=2023 or dataset=='nfl_depth_charts' and year>=2024)
            filename=f'{prefix}_{year}.csv'+('.gz' if compressed else '')
            credit='nflverse, CC BY 4.0'
            if dataset=='nfl_snap_counts': credit='Pro Football Reference via nflverse, CC BY 4.0; underlying terms require review'
            assets.append({'dataset':dataset,'season':str(year),'url':f'{NFL_BASE}/{tag}/{filename}','attribution':credit,'license':'CC-BY-4.0'})
    for season in NBA_SEASONS:
        assets.append({'dataset':'nba_team_game_boxscores','season':season,
                       'url':f'https://boxscorelab.com/downloads/{season}-team-game-results.csv',
                       'attribution':'BoxScore Lab, boxscorelab.com, CC BY 4.0; data through source build date',
                       'license':'CC-BY-4.0; upstream NBA gambling-use terms unresolved'})
    return assets

def inspect_csv(payload,compressed):
    """Count rows without loading the uncompressed CSV into memory."""
    raw=io.BytesIO(payload)
    if compressed: raw=gzip.GzipFile(fileobj=raw,mode='rb')
    with io.TextIOWrapper(raw,encoding='utf-8-sig',newline='') as text:
        reader=csv.reader(text);header=next(reader,None)
        if not header or len(set(header))!=len(header): raise ValueError('empty or duplicate-column CSV header')
        count=0
        for row in reader:
            if len(row)!=len(header): raise ValueError('inconsistent CSV row')
            count+=1
    if not count: raise ValueError('empty data set')
    return header,count

def archive_asset(root, spec, payload, retrieved_at, last_modified=None, etag=None):
    compressed=spec['url'].endswith('.gz')
    cols,count=inspect_csv(payload,compressed)
    raw_digest=hashlib.sha256(payload).hexdigest()
    saved=payload if compressed else gzip.compress(payload,mtime=0)
    path=Path(root)/'observations'/'backfill'/spec['dataset']/(spec['season']+'.sqlite')
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript(SCHEMA)
        cursor=db.execute('INSERT OR IGNORE INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (raw_digest,spec['dataset'],spec['season'],spec['url'],retrieved_at,last_modified,etag,
             spec['license'],spec['attribution'],'retrospective_only','csv.gz',json.dumps(cols),count,saved))
        return {'dataset':spec['dataset'],'season':spec['season'],'sha256':raw_digest,
                'rows':count,'columns':len(cols),'new':bool(cursor.rowcount)}

def fetch_and_archive(root, specs=None, fetch=None):
    """Failure-isolate downloads and emit only safe, non-secret diagnostics."""
    specs=catalog() if specs is None else specs
    if fetch is None:
        def fetch(url):
            req=Request(url,headers={'User-Agent':'MoneylineResearch/1.0','Accept':'application/octet-stream,text/csv'})
            with urlopen(req,timeout=90) as response:
                data=response.read(35_000_001)
                if len(data)>35_000_000: raise ValueError('source file exceeds 35 MB cap')
                return data,response.headers.get('Last-Modified'),response.headers.get('ETag')
    results=[];failures=[]
    for spec in specs:
        try:
            payload,last_modified,etag=fetch(spec['url'])
            results.append(archive_asset(root,spec,payload,datetime.now(timezone.utc).isoformat(),last_modified,etag))
        except Exception as exc:
            failures.append({'dataset':spec['dataset'],'season':spec['season'],'error':type(exc).__name__})
    return results,failures
