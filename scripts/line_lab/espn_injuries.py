"""Keyless public ESPN injury snapshots, without scraping commentary or guessing IDs.

This endpoint is best-effort, not a contracted real-time/complete inactive feed.
A missing listing is never a confirmation that a player is available.
"""
import hashlib,json,re
from .ingest import get
from .constants import team_code
from .nba_injury_feed import provider_team_code
from .history import aware
from datetime import datetime,timezone,timedelta

URLS={'NBA':'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries',
      'NFL':'https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries'}
STATUS={'out':'out','doubtful':'doubtful','questionable':'questionable','probable':'probable',
        'day-to-day':'day_to_day','day to day':'day_to_day','available':'available','active':'available',
        'injured reserve':'injured_list','suspension':'suspended','suspended':'suspended'}


def parse(payload,league,observed_at):
    observed=aware(observed_at)
    if league not in URLS or not isinstance(payload,dict):raise ValueError('injury schema')
    if payload.get('status')!='success' or not isinstance(payload.get('injuries'),list):raise ValueError('injury schema')
    source=aware(payload['timestamp'])
    if not observed-timedelta(minutes=20)<=source<=observed:raise ValueError('stale or future injury snapshot')
    rows=[];unknown=0;seen={};conflicts=set()
    for group in payload['injuries']:
        if not isinstance(group,dict):unknown+=1;continue
        team=team_code(group.get('displayName'),league)
        if not team or not isinstance(group.get('injuries'),list):unknown+=1;continue
        for injury in group['injuries']:
            try:
                a=injury['athlete'];actual=provider_team_code(a['team']['abbreviation'],league)
                if actual!=team:raise ValueError('team mismatch')
                ids=set()
                if str(a.get('id','')).isdigit():ids.add(str(a['id']))
                for link in a.get('links',[]):
                    # Accept only explicit player-card identity URLs in this
                    # league. Never infer an athlete ID from a name or row ID.
                    match=re.match(r'^https://www\.espn\.com/'+league.lower()+r'/player/(?:[^?#]*?/)?_/id/(\d+)(?:/|$)',link.get('href',''))
                    if match:ids.add(match.group(1))
                if len(ids)!=1:raise ValueError('missing/conflicting athlete identity')
                identity=next(iter(ids));status=STATUS.get(str(injury.get('status','')).lower())
                stamp=aware(injury['date'])
                if stamp>observed or not status:raise ValueError('unknown status or future report')
                key=(team,identity)
                if key in seen:
                    if seen[key]!=status:
                        conflicts.add(key)
                        raise ValueError('conflicting player statuses')
                    continue
                seen[key]=status
                rows.append({'player_id':'espn:'+identity,'espn_athlete_id':identity,'team_abbr':team,
                             'status_code':status,'source_updated_at':stamp.isoformat(),'status_since':stamp.isoformat(),
                             'position':a.get('position',{}).get('abbreviation','UNKNOWN')})
            except (KeyError,TypeError,ValueError,AttributeError):unknown+=1
    # Quarantine every version of a conflicting identity, including the first
    # row; row order must never choose the reported status.
    membership={}
    for r in rows:membership.setdefault(r['espn_athlete_id'],set()).add(r['team_abbr'])
    for identity,teams in membership.items():
        if len(teams)>1:
            conflicts.update((team,identity) for team in teams);unknown+=1
    rows=[r for r in rows if (r['team_abbr'],r['espn_athlete_id']) not in conflicts]
    return {'sport':'basketball_nba' if league=='NBA' else 'football_nfl','players':rows,'count':len(rows),
            'source':'ESPN public injury endpoint','source_url':URLS[league],'source_timestamp':source.isoformat(),
            'observation_timestamp':observed_at,'parse_errors':unknown,'conflicting_players':len(conflicts),
            'source_sha256':hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'complete_availability':False}


def fetch(league,getter=get):
    payload=json.loads(getter(URLS[league],10));observed=datetime.now(timezone.utc).isoformat()
    return parse(payload,league,observed),observed
