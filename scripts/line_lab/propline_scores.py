"""Optional source for schedules and explicitly final game results.

Credentials are sent only in an HTTPS header. Provider responses are kept in
memory; they are not published as a raw data set. A status of ``expired`` is
not a final score, and unknown or conflicting games are rejected.
"""
import json
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from .constants import ET, game_id, team_code
from .history import aware

SPORTS={'NBA':'basketball_nba','NFL':'football_nfl'}
VALID={'upcoming','in_progress','final','postponed','cancelled','canceled','expired'}
QUOTA='''
CREATE TABLE IF NOT EXISTS calls (call_id TEXT PRIMARY KEY, endpoint TEXT NOT NULL, reserved_at TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS calls_no_update BEFORE UPDATE ON calls BEGIN SELECT RAISE(ABORT,'quota is append-only'); END;
CREATE TRIGGER IF NOT EXISTS calls_no_delete BEFORE DELETE ON calls BEGIN SELECT RAISE(ABORT,'quota is append-only'); END;
'''


def use_provider(key,setting,injury_only=False):
    choice=str(setting or '').strip().lower()
    return choice in ('true','1','yes') or (bool(str(key or '').strip()) and choice in ('','auto') and not injury_only)


def reserve_call(root,endpoint,observed_at,daily_limit=200):
    """Reserve a conservative daily request budget before calling the provider."""
    if not root or endpoint not in ('scores_nba','scores_nfl','events_nba','events_nfl','injuries_nba','injuries_nfl') or not isinstance(daily_limit,int) or isinstance(daily_limit,bool) or daily_limit<1:
        return False
    now=aware(observed_at);path=Path(root)/'observations'/'propline_quota'/(now.date().isoformat()+'.sqlite')
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path)) as db:
        db.executescript(QUOTA);db.execute('BEGIN IMMEDIATE')
        count=db.execute('SELECT count(*) FROM calls').fetchone()[0]
        if count>=daily_limit:
            db.rollback();return False
        db.execute('INSERT INTO calls VALUES (?,?,?)',(uuid.uuid4().hex,endpoint,now.isoformat()))
        db.commit();return True


def _fetch(key,league,endpoint,opener):
    if not key or league not in SPORTS:raise ValueError('missing key or unsupported league')
    request=Request(f'https://api.prop-line.com/v1/sports/{SPORTS[league]}/{endpoint}',
                    headers={'X-API-Key':key,'Accept':'application/json'})
    with opener(request,timeout=15) as response:
        body=response.read(5_000_001)
    if len(body)>5_000_000:raise ValueError('score response too large')
    return json.loads(body),datetime.now(timezone.utc).isoformat()


def fetch_scores(key,league,opener=urlopen):
    return _fetch(key,league,'scores?days_from=3',opener)


def fetch_events(key,league,opener=urlopen):
    return _fetch(key,league,'events',opener)


def parse_event_starts(payload,league,observed_at):
    """Parse the provider's documented upcoming-event list, not its odds feed."""
    now=aware(observed_at)
    if league not in SPORTS or not isinstance(payload,list):raise ValueError('invalid events response')
    grouped={}
    for raw in payload:
        try:
            if not isinstance(raw,dict) or raw.get('sport_key') not in (SPORTS[league],'americanfootball_nfl' if league=='NFL' else SPORTS[league]):continue
            if raw.get('status','upcoming')!='upcoming':continue
            home=team_code(raw['home_team'],league);away=team_code(raw['away_team'],league)
            start=aware(raw['commence_time'])
            if not home or not away or home==away or start<=now:continue
            identifier=game_id(league,start.astimezone(ET).date(),away,home)
            grouped.setdefault(identifier,set()).add(start.isoformat())
        except (KeyError,TypeError,ValueError,OverflowError):continue
    return ({k:next(iter(v)) for k,v in grouped.items() if len(v)==1},
            sorted(k for k,v in grouped.items() if len(v)!=1))


def parse_scores(payload,league,observed_at):
    now=aware(observed_at)
    if league not in SPORTS or not isinstance(payload,list):raise ValueError('invalid score response')
    grouped={}
    for raw in payload:
        try:
            if not isinstance(raw,dict):continue
            sport=raw.get('sport_key')
            if sport not in (SPORTS[league],'americanfootball_nfl' if league=='NFL' else SPORTS[league]):continue
            status=raw['status']
            if not isinstance(status,str):continue
            home=team_code(raw['home_team'],league);away=team_code(raw['away_team'],league)
            start=aware(raw['commence_time'])
            if not home or not away or home==away:continue
            identifier=game_id(league,start.astimezone(ET).date(),away,home)
            score=(raw.get('home_score'),raw.get('away_score'))
            if any(v is not None and (not isinstance(v,int) or isinstance(v,bool) or v<0) for v in score):continue
            if status=='final' and (start>now or any(not isinstance(v,int) or isinstance(v,bool) or v<0 for v in score)):
                continue
            value={'id':identifier,'league':league,'home':home,'away':away,'starts_at':start,
                   'status':status,'home_score':score[0],'away_score':score[1],
                   'provider_event_id':str(raw.get('id') or ''),'source':'PropLine scores'}
            grouped.setdefault(identifier,[]).append(value)
        except (KeyError,TypeError,ValueError,OverflowError):continue
    starts={};finals=[];conflicts=[];blocked=[]
    for identifier,values in grouped.items():
        signatures={(v['home'],v['away'],v['starts_at'],v['status'],v['home_score'],v['away_score']) for v in values}
        if len(signatures)!=1:
            conflicts.append(identifier);blocked.append(identifier);continue
        row=values[0]
        if row['status']!='upcoming':blocked.append(identifier)
        if row['status'] in ('upcoming','in_progress','final'):
            starts[identifier]=row['starts_at'].isoformat()
        if row['status']=='final':
            finals.append({k:v for k,v in row.items() if k!='status'})
    return starts,finals,sorted(conflicts),sorted(blocked)


def restrict_public_results(finals,recorded_ids):
    """Keep only selected-game provider values in the public project history."""
    recorded=set(recorded_ids)
    return [row for row in finals if row.get('source')!='PropLine scores' or row.get('id') in recorded]
