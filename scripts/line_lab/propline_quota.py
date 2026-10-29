"""Free-plan request controls; never upgrades service or stores credentials."""
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import timedelta
from .history import aware

DAILY_LIMIT=500  # Verified free allowance is 1,000/day; retain a safety margin.
OPERATIONAL_RESERVE=150
PURPOSE_LIMITS={'development':200,'research':30}
HEADERS='''CREATE TABLE IF NOT EXISTS quota_headers(key TEXT PRIMARY KEY,payload TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS pqh_no_update BEFORE UPDATE ON quota_headers BEGIN SELECT RAISE(ABORT,'immutable'); END;
CREATE TRIGGER IF NOT EXISTS pqh_no_delete BEFORE DELETE ON quota_headers BEGIN SELECT RAISE(ABORT,'immutable'); END;'''


def path_for(root,observed_at):
    return Path(root)/'observations/propline_quota'/(aware(observed_at).date().isoformat()+'.sqlite')


def record_headers(root,headers,observed_at):
    """Only documented numeric quota headers; no key, raw response or cookies."""
    if not root:return
    names={'limit':'X-Daily-Limit','used':'X-Daily-Used','remaining':'X-Daily-Remaining','reset':'X-Daily-Reset'}
    try:values={k:int(headers.get(name)) for k,name in names.items()}
    except (TypeError,ValueError,AttributeError):return
    if any(v<0 for v in values.values()) or values['limit']<1 or values['remaining']>values['limit']:return
    try:retry=int(headers.get('Retry-After',0))
    except (TypeError,ValueError):retry=0
    values['retry_until']=(aware(observed_at)+timedelta(seconds=max(0,min(retry,86400)))).isoformat()
    path=path_for(root,observed_at);path.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps({'observed_at':observed_at,**values},sort_keys=True)
    with closing(sqlite3.connect(path)) as db,db:
        db.executescript(HEADERS)
        db.execute('INSERT OR IGNORE INTO quota_headers VALUES (?,?)',(hashlib.sha256(payload.encode()).hexdigest(),payload))


def allowed(db,limit,purpose,observed_at):
    count=db.execute('SELECT count(*) FROM calls').fetchone()[0]
    if count>=limit:return False
    if purpose!='operational':
        if count>=max(0,limit-OPERATIONAL_RESERVE):return False
        used=db.execute('SELECT count(*) FROM calls WHERE endpoint LIKE ?',(purpose+':%',)).fetchone()[0]
        if used>=PURPOSE_LIMITS[purpose]:return False
    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='quota_headers'").fetchone():
        values=[json.loads(row[0]) for row in db.execute('SELECT payload FROM quota_headers')]
        values=[v for v in values if aware(v['observed_at'])<=aware(observed_at)]
        if values:
            latest=max(values,key=lambda v:aware(v['observed_at']))
            if latest['remaining']==0 or (latest.get('retry_until') and aware(latest['retry_until'])>aware(observed_at)):return False
    return True
