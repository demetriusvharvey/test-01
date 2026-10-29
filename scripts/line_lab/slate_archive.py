"""Append-only, odds-independent forecasts for every eligible scheduled game."""
import hashlib
import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path
from .history import aware
from .model import project_home
from .ledger_v2 import feature_snapshot

SCHEMA="""
CREATE TABLE IF NOT EXISTS slate_forecasts (
 forecast_key TEXT PRIMARY KEY, game_id TEXT NOT NULL, league TEXT NOT NULL,
 captured_at TEXT NOT NULL, starts_at TEXT NOT NULL, home TEXT NOT NULL,
 away TEXT NOT NULL, probability REAL NOT NULL, snapshot TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS slate_outcomes (
 game_id TEXT PRIMARY KEY, observed_at TEXT NOT NULL, home TEXT NOT NULL,
 away TEXT NOT NULL, home_score INTEGER NOT NULL, away_score INTEGER NOT NULL,
 source TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS sf_no_update BEFORE UPDATE ON slate_forecasts BEGIN SELECT RAISE(ABORT,'immutable forecast'); END;
CREATE TRIGGER IF NOT EXISTS sf_no_delete BEFORE DELETE ON slate_forecasts BEGIN SELECT RAISE(ABORT,'immutable forecast'); END;
CREATE TRIGGER IF NOT EXISTS so_no_update BEFORE UPDATE ON slate_outcomes BEGIN SELECT RAISE(ABORT,'immutable outcome'); END;
CREATE TRIGGER IF NOT EXISTS so_no_delete BEFORE DELETE ON slate_outcomes BEGIN SELECT RAISE(ABORT,'immutable outcome'); END;
"""


def archive_slate(root,games,models,finals,now,blocked=(),injury_features=None):
    """Capture all games without a book-count or value gate.

    Finals must come from the pipeline's explicit-final qualification step.
    Existing snapshots are never rewritten. A missing injury input stays null.
    """
    current=aware(now);path=Path(root)/'observations'/'slate_archive.sqlite'
    path.parent.mkdir(parents=True,exist_ok=True);added=0;graded=0
    with closing(sqlite3.connect(path)) as db,db:
        db.executescript(SCHEMA)
        for game in games:
            try:
                league=game['league'];start=aware(game['starts_at'])
                if league in blocked or start<=current:continue
                prefix,day,away,home=game['id'].split(':')
                if prefix.upper()!=league or home==away:continue
                model=models[league]
                if not model.get('source_hashes'):continue
                # Unknown NFL venue status must not become assumed home field.
                if league=='NFL' and 'neutral' not in game:continue
                event={'home':home,'away':away,'starts_at':game['starts_at'],'neutral':game.get('neutral',False)}
                p=project_home(model,home,away,start,event['neutral'])
                if p is None or not math.isfinite(p) or not 0<p<1:continue
                snapshot={'model_version':'pure-elo-v1','inputs':feature_snapshot(event,model),
                          'source_hashes':model['source_hashes'],
                          'injury_features':(injury_features or {}).get(game['id']),
                          'injuries_used_in_probability':False}
                content=json.dumps(snapshot,sort_keys=True,separators=(',',':'))
                key=hashlib.sha256((game['id']+'|'+current.isoformat()+'|'+content).encode()).hexdigest()
                added+=db.execute('INSERT OR IGNORE INTO slate_forecasts VALUES (?,?,?,?,?,?,?,?,?)',
                    (key,game['id'],league,current.isoformat(),start.isoformat(),home,away,p,content)).rowcount
            except (KeyError,TypeError,ValueError,OverflowError):continue
        for final in sorted(finals,key=lambda value:value.get('source')!='nflverse'):
            try:
                row=db.execute('SELECT home,away,starts_at FROM slate_forecasts WHERE game_id=? LIMIT 1',(final['id'],)).fetchone()
                if not row or (final['home'],final['away'])!=row[:2] or aware(row[2])>current:continue
                scores=(final['home_score'],final['away_score'])
                if any(not isinstance(s,int) or isinstance(s,bool) or s<0 for s in scores):continue
                graded+=db.execute('INSERT OR IGNORE INTO slate_outcomes VALUES (?,?,?,?,?,?,?)',
                    (final['id'],current.isoformat(),final['home'],final['away'],*scores,final['source'])).rowcount
            except (KeyError,TypeError,ValueError):continue
    return {'forecasts_added':added,'outcomes_added':graded}
