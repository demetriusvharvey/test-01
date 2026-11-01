"""Free, timestamped NFL depth-chart projections. Never starter confirmation.

The first listed QB is a provider-order projection, not a verified game starter.
An injury-list omission never upgrades a quarterback's availability to healthy.
"""
import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .constants import NFL_TEAMS
from .history import aware
from .nba_injury_feed import provider_team_code,STATUSES
from .public_fetch import prefetch

BASE='https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/'
TEAM_SLUGS={'LA':'lar','WAS':'wsh'}


def team_url(team):return BASE+TEAM_SLUGS.get(team,team.lower())+'/depthcharts'


def parse_depth(payload,team,observed_at):
    observed=aware(observed_at)
    if not isinstance(payload,dict) or payload.get('status')!='success':raise ValueError('depth schema')
    if provider_team_code(payload.get('team',{}).get('abbreviation'),'NFL')!=team:raise ValueError('depth team mismatch')
    source=aware(payload.get('timestamp'))
    if not observed-timedelta(minutes=20)<=source<=observed:raise ValueError('depth stale or future')
    candidates=[];names={}
    for chart in payload.get('depthchart',[]):
        for position in chart.get('positions',{}).values():
            if position.get('position',{}).get('abbreviation')!='QB':continue
            ids=[str(a.get('id','')) for a in position.get('athletes',[])]
            if not ids or any(not x.isdigit() for x in ids) or len(ids)!=len(set(ids)):raise ValueError('depth QB identity')
            candidates.append(ids)
            for athlete in position.get('athletes',[]):
                name=athlete.get('displayName')
                if isinstance(name,str):names[str(athlete['id'])]=name[:120]
    if not candidates or any(ids!=candidates[0] for ids in candidates):raise ValueError('missing or conflicting QB depth')
    return {'team':team,'source':'ESPN public depth chart','source_url':team_url(team),
            'source_timestamp':source.isoformat(),'observed_at':observed.isoformat(),
            'source_sha256':hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'listed_quarterbacks':['espn:'+x for x in candidates[0]],
            'projected_player_id':'espn:'+candidates[0][0],'projected_name':names.get(candidates[0][0]),'projection_basis':'provider_list_order',
            'starter_status':'projected','confirmed':False,'used_in_prediction':False,'training_eligible':False}


def _cache(root):
    path=Path(root)/'observations/nfl_depth/ledger.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    db.executescript('''CREATE TABLE IF NOT EXISTS snapshots(key TEXT PRIMARY KEY,team TEXT,observed_at TEXT,payload TEXT);
    CREATE TRIGGER IF NOT EXISTS depth_no_update BEFORE UPDATE ON snapshots BEGIN SELECT RAISE(ABORT,'immutable'); END;
    CREATE TRIGGER IF NOT EXISTS depth_no_delete BEFORE DELETE ON snapshots BEGIN SELECT RAISE(ABORT,'immutable'); END;''')
    return db


def collect_depth(events,now,getter,root=None):
    """Fetch at most one chart per team playing in the next 24h; cache for 1h."""
    current=aware(now);teams=set();result={};errors=[]
    for e in events:
        if e.get('league')=='NFL' and current<aware(e['starts_at'])<=current+timedelta(hours=24):
            teams.update((e['home'],e['away']))
    teams &= set(NFL_TEAMS.values())
    if root:
        db=_cache(root)
        try:
            for team in sorted(teams):
                rows=db.execute('SELECT observed_at,payload FROM snapshots WHERE team=?',(team,)).fetchall()
                rows=[r for r in rows if current-timedelta(hours=1)<=aware(r[0])<=current]
                if rows:
                    cached=json.loads(max(rows,key=lambda r:aware(r[0]))[1])
                    # Refresh old capture schemas rather than hide player names
                    # behind identifiers until the one-hour cache expires.
                    if 'projected_name' in cached and 'training_eligible' in cached:result[team]=cached
        finally:db.close()
    urls={team:team_url(team) for team in sorted(teams-result.keys())}
    fetch=prefetch(urls.values(),getter,timeout=6,workers=6)
    for team,url in urls.items():
        try:
            payload=json.loads(fetch(url,6));stamp=datetime.now(timezone.utc).isoformat()
            result[team]=parse_depth(payload,team,stamp)
            if root:
                text=json.dumps(result[team],sort_keys=True,allow_nan=False)
                db=_cache(root)
                try:
                    with db:db.execute('INSERT OR IGNORE INTO snapshots VALUES (?,?,?,?)',
                        (hashlib.sha256(text.encode()).hexdigest(),team,stamp,text))
                finally:db.close()
        except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
            errors.append('NFL QB depth unavailable: '+team+' ('+type(exc).__name__+')')
    return result,errors


def _recent(stamp,now,age):
    try:return now-age<=aware(stamp)<=now
    except (TypeError,ValueError):return False


def explicit_espn_id(row):
    """Accept only a declared ESPN namespace; never coerce a provider ID."""
    raw=str(row.get('player_id') or '')
    prefixed=raw[5:] if raw.startswith('espn:') and raw[5:].isdigit() else ''
    explicit=str(row.get('espn_athlete_id') or '').strip()
    if explicit and not explicit.isdigit():return None
    if explicit and prefixed and explicit!=prefixed:return None
    value=explicit or prefixed
    return 'espn:'+value if value else None


def game_context(event,depth,injuries,prediction_at):
    """Join explicit team/ESPN IDs; no fuzzy player-name or GSIS matching."""
    now,start=aware(prediction_at),aware(event['starts_at'])
    if event['league']!='NFL' or now>=start:return None
    sides={}
    if injuries and not (injuries.get('sport')=='football_nfl' and
            _recent(injuries.get('observation_timestamp'),now,timedelta(minutes=20))):injuries=None
    for side in ('away','home'):
        chart=depth.get(event[side]);status='unknown';updated=None;last_status=None;reason='not_listed_or_feed_unavailable'
        if chart and (chart.get('team')!=event[side] or not now-timedelta(hours=1)<=aware(chart['observed_at'])<=now):chart=None
        match_count=0;identity_conflicts=0
        if chart and injuries:
            rows=[]
            for r in injuries.get('players',[]):
                if not isinstance(r,dict) or provider_team_code(r.get('team_abbr'),'NFL')!=event[side]:continue
                identity=explicit_espn_id(r)
                if identity==chart['projected_player_id']:rows.append(r)
                elif (r.get('player_id')==chart['projected_player_id'] or
                      str(r.get('espn_athlete_id') or '')==chart['projected_player_id'][5:]):identity_conflicts+=1
            match_count=len(rows)
            values={r.get('status_code') for r in rows}
            if identity_conflicts:reason='player_identity_conflict'
            elif len(values)>1:reason='conflicting_reported_statuses'
            elif rows and (len(values)!=1 or not values<=STATUSES):reason='invalid_reported_status'
            elif rows:
                times=[r.get('source_updated_at') or r.get('status_since') for r in rows]
                if not all(_recent(t,now,timedelta(days=3650)) for t in times):reason='invalid_or_future_report_timestamp'
                else:
                    last_status=next(iter(values));updated=max(times,key=aware)
                    if all(_recent(t,now,timedelta(hours=30)) for t in times):
                        status=last_status;reason='recent_reported_status'
                    else:reason='report_stale'
        sides[side]={'team':event[side],'depth':chart,'availability_status':status,
                     'matched_report_rows':match_count,'identity_conflicts':identity_conflicts,
                     'status_updated_at':updated,'last_reported_status':last_status,'availability_reason':reason,'injury_observed_at':injuries.get('observation_timestamp') if injuries else None}
    return {'game_id':event['id'],'teams':sides,'observed_at':prediction_at,
            'starter_status':'projected' if all(v['depth'] for v in sides.values()) else 'unknown',
            'starting_quarterbacks_confirmed':False,'used_in_prediction':False,
            'note':'Depth-chart order is a projection; no listing means unknown availability.'}
