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
CREATE TABLE IF NOT EXISTS slate_confirmations (
 confirmation_key TEXT PRIMARY KEY, game_id TEXT NOT NULL, observed_at TEXT NOT NULL,
 home TEXT NOT NULL, away TEXT NOT NULL, home_score INTEGER NOT NULL,
 away_score INTEGER NOT NULL, source TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS sc_no_update BEFORE UPDATE ON slate_confirmations BEGIN SELECT RAISE(ABORT,'immutable confirmation'); END;
CREATE TRIGGER IF NOT EXISTS sc_no_delete BEFORE DELETE ON slate_confirmations BEGIN SELECT RAISE(ABORT,'immutable confirmation'); END;
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
                snapshot['inputs']['home_games']=model.get('games_played',{}).get(home)
                snapshot['inputs']['away_games']=model.get('games_played',{}).get(away)
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
                identity=[final['id'],final['home'],final['away'],*scores,final['source']]
                confirmation=hashlib.sha256(json.dumps(identity,separators=(',',':')).encode()).hexdigest()
                db.execute('INSERT OR IGNORE INTO slate_confirmations VALUES (?,?,?,?,?,?,?,?)',
                    (confirmation,final['id'],current.isoformat(),final['home'],final['away'],*scores,final['source']))
            except (KeyError,TypeError,ValueError):continue
    return {'forecasts_added':added,'outcomes_added':graded}


def read_slate_inputs(root,as_of):
    """Adapt independent frozen inputs to the paired challenger evaluator."""
    path=Path(root)/'observations'/'slate_archive.sqlite'
    if not path.exists():return [],{}
    cutoff=aware(as_of);forecasts=[];outcomes={}
    with closing(sqlite3.connect(path)) as db:
        db.row_factory=sqlite3.Row
        for row in db.execute('SELECT * FROM slate_forecasts'):
            try:
                r=dict(row)
                if aware(r['captured_at'])>cutoff:continue
                snapshot=json.loads(r['snapshot']);features=snapshot['inputs']
                features={**features,'shadow_context':{'nfl_position_status':snapshot.get('injury_features')}}
                forecasts.append({**r,'pure_probability':r['probability'],
                                  'feature_snapshot':json.dumps(features,sort_keys=True)})
            except (KeyError,TypeError,ValueError):continue
        observations={}
        # Read old archives without requiring a schema mutation during research.
        tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        rows=list(db.execute('SELECT * FROM slate_outcomes'))
        if 'slate_confirmations' in tables:rows+=list(db.execute('SELECT * FROM slate_confirmations'))
        for row in rows:
            try:
                r=dict(row)
                if aware(r['observed_at'])<=cutoff:observations.setdefault(r['game_id'],[]).append(r)
            except (KeyError,TypeError,ValueError):continue
        for key,values in observations.items():
            signatures={(v['home'],v['away'],v['home_score'],v['away_score']) for v in values}
            certified=[v for v in values if v['source']=='nflverse']
            if len(signatures)==1 and certified:
                # The source becomes eligible only when corroboration was
                # actually observed; never backdate a later confirmation.
                outcomes[key]=min(certified,key=lambda v:aware(v['observed_at']))
    return forecasts,outcomes
