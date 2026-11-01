"""Bounded ESPN pregame starter-list observations, never confirmation or impact.

A provider's starter flag without a confirmation/publication contract is listed,
unconfirmed evidence. No report, no listing and no zero counts imply health.
"""
import hashlib
import json
import sqlite3
from datetime import datetime,timedelta,timezone
from pathlib import Path
from .constants import ET,game_id,team_code
from .history import aware
from .nba_injury_feed import provider_team_code
from .public_fetch import prefetch

BASE='https://site.api.espn.com/apis/site/v2/sports/basketball/nba/'


def event_mapping(payload,events):
    """Match exact team/date identity and scheduled time; quarantine ambiguity."""
    if not isinstance(payload,dict) or not isinstance(payload.get('events'),list):raise ValueError('scoreboard schema')
    wanted={e['id']:e for e in events};matches={}
    for row in payload.get('events',[]):
        try:
            ident=str(row['id']);comp=row['competitions'][0]
            if not ident.isdigit():continue
            sides={c['homeAway']:c for c in comp['competitors']}
            home=team_code(sides['home']['team']['displayName'],'NBA');away=team_code(sides['away']['team']['displayName'],'NBA')
            start=aware(row['date']);key=game_id('NBA',start.astimezone(ET).date(),away,home)
            event=wanted.get(key)
            if not event or (home,away)!=(event['home'],event['away']):continue
            if abs((start-aware(event['starts_at'])).total_seconds())>20*60:continue
            state=comp.get('status',row.get('status',{})).get('type',{})
            if state.get('name')!='STATUS_SCHEDULED' or state.get('state')!='pre' or state.get('completed') is not False:continue
            matches.setdefault(key,set()).add(ident)
        except (KeyError,ValueError,TypeError,IndexError,AttributeError):continue
    return {key:next(iter(ids)) for key,ids in matches.items() if len(ids)==1}


def parse_summary(payload,event,source_event_id,observed_at):
    observed=aware(observed_at);start=aware(event['starts_at'])
    header=payload['header'];comps=header['competitions']
    if header['id']!=source_event_id or len(comps)!=1:raise ValueError('summary event identity')
    comp=comps[0];state=comp['status']['type'];source_start=aware(comp['date'])
    if comp.get('id',source_event_id)!=source_event_id:raise ValueError('competition identity mismatch')
    if (state.get('name')!='STATUS_SCHEDULED' or state.get('state')!='pre' or state.get('completed') is not False
            or payload.get('meta',{}).get('gameState')!='pre' or not observed<min(start,source_start)):
        raise ValueError('summary not pregame')
    if abs((start-source_start).total_seconds())>20*60:raise ValueError('summary start mismatch')
    sides={c['homeAway']:provider_team_code(c['team']['abbreviation'],'NBA') for c in comp['competitors']}
    if sides!={'home':event['home'],'away':event['away']}:raise ValueError('summary team mismatch')
    if event['id']!=game_id('NBA',source_start.astimezone(ET).date(),event['away'],event['home']):raise ValueError('summary day mismatch')
    source_time=payload.get('meta',{}).get('lastUpdatedAt')
    if source_time and not observed-timedelta(minutes=20)<=aware(source_time)<=observed:raise ValueError('summary stale or future')
    candidates={team:{} for team in sides.values()};invalid=False
    for group in payload.get('boxscore',{}).get('players',[]):
        team=provider_team_code(group['team']['abbreviation'],'NBA')
        if team not in candidates:raise ValueError('boxscore team mismatch')
        for statistics in group.get('statistics',[]):
            for row in statistics.get('athletes',[]):
                player=str(row.get('athlete',{}).get('id',''));starter=row.get('starter')
                if not player.isdigit() or type(starter) is not bool:invalid=True;continue
                candidates[team].setdefault(player,set()).add(starter)
    membership={}
    for team,players in candidates.items():
        for player in players:membership.setdefault(player,set()).add(team)
    if any(len(teams)>1 for teams in membership.values()):invalid=True
    teams={}
    for side,team in sides.items():
        values=candidates[team]
        if any(len(flags)!=1 for flags in values.values()):invalid=True
        ids=sorted('espn:'+player for player,flags in values.items() if flags=={True})
        teams[side]={'team':team,'listed_starters':ids,'listed_count':len(ids)}
    listed=not invalid and all(v['listed_count']==5 for v in teams.values())
    return {'schema':'pregame-listed-starters-v1','game_id':event['id'],'starts_at':event['starts_at'],
            'source_event_id':source_event_id,'source':'ESPN game summary','source_url':BASE+'summary?event='+source_event_id,
            'source_sha256':hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'source_timestamp':source_time,'observed_at':observed.isoformat(),'teams':teams,
            'lineup_status':'listed_unconfirmed' if listed else 'unknown',
            'reason':'provider_starter_flags_only' if listed else 'conflicting_starter_evidence' if invalid else 'lineups_not_published_or_incomplete',
            'confirmed':False,'used_in_prediction':False,'training_eligible':False,
            'note':'Retrieval time is not publication time; listed starters are not verified confirmed lineups.'}


def archive(root,rows):
    path=Path(root)/'observations/pregame_lineups/ledger.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(path) as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS snapshots(key TEXT PRIMARY KEY,game_id TEXT,payload TEXT);
        CREATE TRIGGER IF NOT EXISTS pl_no_update BEFORE UPDATE ON snapshots BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS pl_no_delete BEFORE DELETE ON snapshots BEGIN SELECT RAISE(ABORT,'immutable'); END;''')
        for row in rows:
            if not aware(row['observed_at'])<aware(row['starts_at']):continue
            text=json.dumps(row,sort_keys=True,allow_nan=False)
            db.execute('INSERT OR IGNORE INTO snapshots VALUES (?,?,?)',(hashlib.sha256(text.encode()).hexdigest(),row['game_id'],text))


def collect(events,now,getter,root=None):
    current=aware(now);result={};due=[]
    for event in events:
        if event.get('league')!='NBA' or not current<aware(event['starts_at']):continue
        result[event['id']]={'game_id':event['id'],'starts_at':event['starts_at'],'observed_at':now,
            'lineup_status':'unknown','reason':'outside_two_hour_collection_window','confirmed':False,
            'used_in_prediction':False,'training_eligible':False}
        if aware(event['starts_at'])-current<=timedelta(hours=2):due.append(event)
    days=sorted({aware(e['starts_at']).astimezone(ET).date().strftime('%Y%m%d') for e in due})
    urls=[BASE+'scoreboard?dates='+d for d in days];fetch=prefetch(urls,getter,timeout=6,workers=4);mapping={}
    for url in urls:
        try:mapping.update(event_mapping(json.loads(fetch(url,6)),due))
        except (OSError,ValueError,TypeError,KeyError,AttributeError):pass
    summary_urls={e['id']:BASE+'summary?event='+mapping[e['id']] for e in due if e['id'] in mapping}
    summaries=prefetch(summary_urls.values(),getter,timeout=6,workers=4)
    for event in due:
        key=event['id'];row=result[key]
        if key not in mapping:row['reason']='source_event_mapping_unavailable';continue
        row.update(source_event_id=mapping[key],source_url=summary_urls[key])
        try:
            payload=json.loads(summaries(summary_urls[key],6));stamp=datetime.now(timezone.utc).isoformat()
            result[key]=parse_summary(payload,event,mapping[key],stamp)
        except (OSError,ValueError,TypeError,KeyError,IndexError,AttributeError) as exc:
            row.update(reason='summary_unavailable_or_rejected',error_type=type(exc).__name__,
                       observed_at=datetime.now(timezone.utc).isoformat())
    if root and due:archive(root,[result[e['id']] for e in due])
    return result
