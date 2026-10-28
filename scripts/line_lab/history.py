"""Append-only, point-in-time quote observations and last-observed price proxies."""
import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS snapshots (
  row_id INTEGER PRIMARY KEY, snapshot_key TEXT NOT NULL UNIQUE,
  provider TEXT NOT NULL, provider_event_id TEXT, game_id TEXT NOT NULL,
  league TEXT NOT NULL, book TEXT NOT NULL, market TEXT NOT NULL,
  home TEXT NOT NULL, away TEXT NOT NULL, home_odds INTEGER NOT NULL,
  away_odds INTEGER NOT NULL, source_as_of TEXT NOT NULL,
  fetched_at TEXT NOT NULL, starts_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS snapshot_event ON snapshots(game_id,provider,book,market,fetched_at);
CREATE TRIGGER IF NOT EXISTS snapshots_no_update BEFORE UPDATE ON snapshots
BEGIN SELECT RAISE(ABORT, 'snapshots are append-only'); END;
CREATE TRIGGER IF NOT EXISTS snapshots_no_delete BEFORE DELETE ON snapshots
BEGIN SELECT RAISE(ABORT, 'snapshots are append-only'); END;
'''
CLOSE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS closes (
  close_key TEXT PRIMARY KEY, game_id TEXT NOT NULL, provider TEXT NOT NULL,
  book TEXT NOT NULL, market TEXT NOT NULL, home_odds INTEGER NOT NULL,
  away_odds INTEGER NOT NULL, source_as_of TEXT NOT NULL, fetched_at TEXT NOT NULL,
  starts_at TEXT NOT NULL, finalized_at TEXT NOT NULL, source_age_seconds INTEGER NOT NULL,
  observed_gap_seconds INTEGER NOT NULL, label TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS closes_no_update BEFORE UPDATE ON closes
BEGIN SELECT RAISE(ABORT, 'closes are append-only'); END;
CREATE TRIGGER IF NOT EXISTS closes_no_delete BEFORE DELETE ON closes
BEGIN SELECT RAISE(ABORT, 'closes are append-only'); END;
'''

def aware(value):
    if not isinstance(value,str): raise ValueError('timestamp missing')
    value=datetime.fromisoformat(value.replace('Z','+00:00'))
    if value.tzinfo is None or value.utcoffset() is None: raise ValueError('timestamp is not timezone-aware')
    return value.astimezone(timezone.utc)

def valid_observation(item, fetched_at, max_age=timedelta(minutes=95)):
    """Reject invalid, stale, future, post-start, or one-sided quotes."""
    try:
        observed=aware(fetched_at); source=aware(item['as_of']); start=aware(item['starts_at'])
        if source>observed or observed-source>max_age or start<=observed: return False
        if any(not isinstance(item[k],int) or isinstance(item[k],bool) or abs(item[k])<100 for k in ('home_odds','away_odds')): return False
        if not all(item.get(k) for k in ('id','league','home','away','book','provider')): return False
        return item['home']!=item['away'] and item['league'] in ('NBA','NFL')
    except (KeyError,TypeError,ValueError,OverflowError): return False

def _open(path,schema):
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    db.executescript(schema)
    return db

def append_observations(root, events, fetched_at):
    observed=aware(fetched_at)
    path=Path(root)/'observations'/'odds'/(observed.date().isoformat()+'.sqlite')
    added=0
    with closing(_open(path,SCHEMA)) as db, db:
        for e in events:
            stamp=e.get('fetched_at',fetched_at)
            if not valid_observation(e,stamp): continue
            values=[e['provider'],e.get('provider_event_id',''),e['id'],e['league'],e['book'],'h2h',
                    e['home'],e['away'],e['home_odds'],e['away_odds'],aware(e['as_of']).isoformat(),
                    aware(stamp).isoformat(),aware(e['starts_at']).isoformat()]
            key=hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()
            cursor=db.execute('INSERT OR IGNORE INTO snapshots(snapshot_key,provider,provider_event_id,game_id,league,book,market,home,away,home_odds,away_odds,source_as_of,fetched_at,starts_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',[key]+values)
            added+=cursor.rowcount
    return added

def finalize_closing_proxies(root, now, confirmed_starts, lookback_days=7):
    """Freeze the last observed pregame quote; never claim an actual or sharp close."""
    current=aware(now); base=Path(root)/'observations'/'odds'; grouped={}
    for day_delta in range(lookback_days+1):
        path=base/((current.date()-timedelta(days=day_delta)).isoformat()+'.sqlite')
        if not path.exists(): continue
        with closing(sqlite3.connect(path)) as db:
            rows=db.execute('SELECT game_id,provider,book,market,home_odds,away_odds,source_as_of,fetched_at,starts_at FROM snapshots').fetchall()
        for row in rows:
            game,provider,book,market,h,a,source,fetched,start=row
            try:
                verified=aware(confirmed_starts[game])
                if abs((verified-aware(start)).total_seconds())>20*60: continue
                if not (aware(source)<=aware(fetched)<min(aware(start),verified)<=current): continue
            except (KeyError,ValueError): continue
            k=(game,provider,book,market)
            if k not in grouped or aware(fetched)>aware(grouped[k][7]): grouped[k]=row
    if not grouped: return 0
    added=0
    # Partition by the known scheduled game start, so the same game cannot be
    # written into different daily files just because it was finalized later.
    for key,row in grouped.items():
        game,provider,book,market,h,a,source,fetched,start=row
        verified=aware(confirmed_starts[game])
        path=Path(root)/'observations'/'closes'/(verified.date().isoformat()+'.sqlite')
        key_hash=hashlib.sha256(json.dumps(key,separators=(',',':')).encode()).hexdigest()
        observed_gap=int((verified-aware(fetched)).total_seconds())
        source_age=int((verified-aware(source)).total_seconds())
        with closing(_open(path,CLOSE_SCHEMA)) as db, db:
            cursor=db.execute('INSERT OR IGNORE INTO closes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (key_hash,game,provider,book,market,h,a,source,fetched,verified.isoformat(),current.isoformat(),source_age,observed_gap,'last_observed_pregame_not_certified_close'))
            added+=cursor.rowcount
    return added
