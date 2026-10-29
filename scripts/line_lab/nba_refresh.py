"""Bounded, cached current-season NBA source refresh; no historical redownload."""
import gzip
import json
import sqlite3
import time
from pathlib import Path
from datetime import timedelta
from urllib.request import Request,urlopen
from .history import aware
from .constants import ET
from .backfill import fetch_and_archive,catalog
from .nba_lineup import parse_current_rosters
from .nba_rotation import parse_players
from .nba_efficiency import parse_team_stats


def roster_observed_at(root,source,content_hash,fallback):
    path=Path(root)/'observations/nba_source_checks.sqlite'
    if not path.exists():return fallback
    with sqlite3.connect(path) as db:
        row=db.execute('SELECT checked_at FROM checks WHERE source=? AND content_hash=? AND success=1 ORDER BY checked_at DESC LIMIT 1',
                       (source,content_hash)).fetchone()
    return row[0] if row else fallback


def refresh_current_sources(root,now,fetch=None):
    current=aware(now);day=current.astimezone(ET).date();year=day.year+int(day.month>=8)
    season=f'{year-1}-{str(year)[-2:]}'
    specs=[s for s in catalog() if s['dataset']=='nba_team_game_boxscores' and s['season']==season]
    for dataset,tag,name in (('nba_player_boxscores','espn_nba_player_boxscores','player_box'),
                             ('nba_roster_snapshots','espn_nba_rosters','rosters')):
        specs.append({'dataset':dataset,'season':str(year),
                      'url':f'https://github.com/sportsdataverse/sportsdataverse-data/releases/download/{tag}/{name}_{year}.csv',
                      'license':'CC-BY-4.0; upstream use review required','attribution':'SportsDataverse, ESPN source'})
    path=Path(root)/'observations/nba_source_checks.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    results=[]
    with sqlite3.connect(path) as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS checks(source TEXT,checked_at TEXT,success INTEGER,content_hash TEXT,error TEXT,PRIMARY KEY(source,checked_at));
        CREATE TRIGGER IF NOT EXISTS nsc_no_update BEFORE UPDATE ON checks BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS nsc_no_delete BEFORE DELETE ON checks BEGIN SELECT RAISE(ABORT,'immutable'); END;''')
        for spec in specs:
            prior=db.execute('SELECT checked_at,success FROM checks WHERE source=? ORDER BY checked_at DESC LIMIT 1',(spec['url'],)).fetchone()
            if prior and current-aware(prior[0])<timedelta(hours=12 if prior[1] else 3):
                results.append({'dataset':spec['dataset'],'status':'cached' if prior[1] else 'retry_backoff'});continue
            def download(url):
                for attempt in range(2):
                    try:
                        if fetch:payload,modified,etag=fetch(url)
                        else:
                            with urlopen(Request(url,headers={'User-Agent':'MoneylineResearch/1.0','Accept':'text/csv'}),timeout=20) as response:
                                payload=response.read(35_000_001);modified=response.headers.get('Last-Modified');etag=response.headers.get('ETag')
                        if len(payload)>35_000_000:raise ValueError('source too large')
                        text=(gzip.decompress(payload) if url.endswith('.gz') else payload).decode('utf-8-sig')
                        if spec['dataset']=='nba_roster_snapshots':
                            parsed=parse_current_rosters(text,now,url)
                            if len(parsed)!=30 or not all(r['verified'] for r in parsed.values()):raise ValueError('incomplete roster snapshot')
                        elif not (parse_players(text) if spec['dataset']=='nba_player_boxscores' else parse_team_stats(text)):
                            raise ValueError('no valid source rows')
                        return payload,modified,etag
                    except Exception:
                        if attempt:raise
                        if not fetch:time.sleep(1)
            good,bad=fetch_and_archive(root,[spec],download)
            value=good[0] if good else None
            db.execute('INSERT INTO checks VALUES (?,?,?,?,?)',(spec['url'],now,int(bool(value)),value['sha256'] if value else None,bad[0]['error'] if bad else None))
            results.append({'dataset':spec['dataset'],'status':'refreshed' if value else 'unavailable'})
    return results
