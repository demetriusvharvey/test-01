"""Track update gaps without assuming that a scheduler ran on time."""
import sqlite3
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from .history import aware

SCHEMA='''
CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY, started_at TEXT NOT NULL UNIQUE);
CREATE TRIGGER IF NOT EXISTS runs_no_update BEFORE UPDATE ON runs BEGIN SELECT RAISE(ABORT,'runs are append-only'); END;
CREATE TRIGGER IF NOT EXISTS runs_no_delete BEFORE DELETE ON runs BEGIN SELECT RAISE(ABORT,'runs are append-only'); END;
'''

def record_run(root, started_at, gap_threshold=timedelta(minutes=100)):
    path=Path(root)/'observations'/'runs.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    stamp=aware(started_at)
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript(SCHEMA)
        last=db.execute('SELECT started_at FROM runs ORDER BY started_at DESC LIMIT 1').fetchone()
        db.execute('INSERT OR IGNORE INTO runs(started_at) VALUES (?)',(stamp.isoformat(),))
    return bool(last and stamp-aware(last[0])>gap_threshold)
