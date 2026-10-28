"""Optional current injury context. No player-level feed data is archived.

This is descriptive context only, not a validated model input. The provider's
terms require the user to obtain a key and agree to them before enabling calls.
"""
import json
import re
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from .constants import NBA_TEAMS, NFL_TEAMS, normalize_code
from .history import aware

URL = 'https://api.prop-line.com/v1/sports/basketball_nba/injuries'
STATUSES = {'out', 'out_first_half', 'doubtful', 'questionable', 'probable',
            'game_time_decision', 'day_to_day', 'injured_list', 'suspended', 'other'}
PROVIDER_TEAM_ALIASES = {
    'NBA': {'GS':'GSW','NY':'NYK','NO':'NOP','SA':'SAS','UTAH':'UTA','WSH':'WAS'},
    'NFL': {'WSH':'WAS'},
}


def provider_team_code(value,league):
    """Map ESPN-style abbreviations without confusing teams across leagues."""
    code=str(value or '').strip().upper()
    return normalize_code(PROVIDER_TEAM_ALIASES.get(league,{}).get(code,code))


def _bucket(status):
    return status if status in ('out', 'doubtful') else 'questionable' if status in ('questionable', 'game_time_decision') else 'other'


def _fetch_injuries(key, enabled, url, opener):
    """Fetch once per run, never with a key in the URL or in an error message."""
    if not key or str(enabled).strip().lower() != 'true':
        return None
    request = Request(url, headers={'X-API-Key': key, 'Accept': 'application/json'})
    with opener(request, timeout=15) as response:
        body = response.read(5_000_001)
    if len(body) > 5_000_000:
        raise ValueError('injury response too large')
    return json.loads(body), datetime.now(timezone.utc).isoformat()


def fetch_nba_injuries(key, enabled, opener=urlopen):
    return _fetch_injuries(key, enabled, URL, opener)


def fetch_nfl_injuries(key, enabled, opener=urlopen):
    return _fetch_injuries(key, enabled, 'https://api.prop-line.com/v1/sports/football_nfl/injuries', opener)


def summarize_by_team(payload, observed_at, league='NBA'):
    """Count eligible rows by team, keeping names and raw response out of Git.

    An empty or partial report is not evidence that anyone is healthy. Reject
    future timestamps and conflicting records, and never use the counts as a
    player-impact estimate.
    """
    observed = aware(observed_at)
    sport={'NBA':'basketball_nba','NFL':'football_nfl'}.get(league)
    if not sport or not isinstance(payload, dict) or payload.get('sport') != sport:
        raise ValueError('unexpected injury sport')
    rows = payload.get('players')
    if not isinstance(rows, list) or isinstance(payload.get('count'), bool) or payload.get('count') != len(rows):
        raise ValueError('incomplete injury response')
    teams = set((NBA_TEAMS if league=='NBA' else NFL_TEAMS).values())
    candidates = {}
    incomplete = False
    for row in rows:
        if not isinstance(row, dict):
            incomplete = True
            continue
        code = provider_team_code(row.get('team_abbr'),league)
        player = row.get('player_id')
        status = row.get('status_code')
        stamps = [row.get('source_updated_at'), row.get('status_since')]
        try:
            times = [aware(s) for s in stamps if s]
            if (code not in teams or not isinstance(player, str) or not player.strip()
                    or status not in STATUSES or not times or any(t > observed for t in times)):
                raise ValueError('invalid status')
        except (TypeError, ValueError):
            incomplete = True
            continue
        ident = (code, player)
        candidates.setdefault(ident, set()).add(status)
    summaries = {code: {'out': 0, 'questionable': 0, 'doubtful': 0, 'other': 0} for code in teams}
    for (code, _), statuses in candidates.items():
        if len(statuses) != 1:
            incomplete = True
            continue
        status = next(iter(statuses))
        bucket = _bucket(status)
        summaries[code][bucket] += 1
    return summaries, incomplete


def summarize_positions_by_team(payload, observed_at, league):
    """Count listed statuses by reported position without publishing players.

    Unspecified or conflicting positions remain UNKNOWN. The complete team
    status parser is still responsible for rejecting incomplete reports.
    """
    observed=aware(observed_at)
    sport={'NBA':'basketball_nba','NFL':'football_nfl'}.get(league)
    if not sport or not isinstance(payload,dict) or payload.get('sport')!=sport:
        raise ValueError('unexpected injury sport')
    rows=payload.get('players')
    if not isinstance(rows,list) or isinstance(payload.get('count'),bool) or payload.get('count')!=len(rows):
        raise ValueError('incomplete injury response')
    teams=set((NBA_TEAMS if league=='NBA' else NFL_TEAMS).values());candidates={}
    for row in rows:
        if not isinstance(row,dict):continue
        code=provider_team_code(row.get('team_abbr'),league)
        player=row.get('player_id');status=row.get('status_code')
        try:
            times=[aware(value) for value in (row.get('source_updated_at'),row.get('status_since')) if value]
            if (code not in teams or not isinstance(player,str) or not player.strip()
                    or status not in STATUSES or not times or any(t>observed for t in times)):continue
        except (TypeError,ValueError):continue
        position=str(row.get('position') or '').strip().upper()
        if not re.fullmatch(r'[A-Z]{1,5}(?:[-/][A-Z]{1,5})?',position):position='UNKNOWN'
        candidates.setdefault((code,player),set()).add((status,position))
    result={code:{} for code in teams}
    for (code,_),values in candidates.items():
        statuses={status for status,_ in values}
        if len(statuses)!=1:continue
        status=next(iter(statuses));positions={position for _,position in values}
        position=next(iter(positions)) if len(positions)==1 else 'UNKNOWN'
        counts=result[code].setdefault(position,{'out':0,'doubtful':0,'questionable':0,'other':0})
        counts[_bucket(status)]+=1
    return result


def injury_quality_counts(payload,observed_at,league):
    """Return only aggregate diagnostics, never player identifiers or names."""
    observed=aware(observed_at)
    sport={'NBA':'basketball_nba','NFL':'football_nfl'}.get(league)
    rows=payload.get('players') if isinstance(payload,dict) and payload.get('sport')==sport else None
    if not isinstance(rows,list):raise ValueError('unexpected injury response')
    teams=set((NBA_TEAMS if league=='NBA' else NFL_TEAMS).values())
    result={'rows':len(rows),'invalid_row':0,'unknown_team':0,'missing_player_id':0,
            'unknown_status':0,'missing_timestamp':0,'invalid_or_future_timestamp':0,'missing_position':0}
    for row in rows:
        if not isinstance(row,dict):result['invalid_row']+=1;continue
        if provider_team_code(row.get('team_abbr'),league) not in teams:result['unknown_team']+=1
        if not isinstance(row.get('player_id'),str) or not row['player_id'].strip():result['missing_player_id']+=1
        if row.get('status_code') not in STATUSES:result['unknown_status']+=1
        position=str(row.get('position') or '').strip().upper()
        if not re.fullmatch(r'[A-Z]{1,5}(?:[-/][A-Z]{1,5})?',position):result['missing_position']+=1
        stamps=[s for s in (row.get('source_updated_at'),row.get('status_since')) if s]
        if not stamps:result['missing_timestamp']+=1;continue
        try:
            if any(aware(s)>observed for s in stamps):result['invalid_or_future_timestamp']+=1
        except (TypeError,ValueError):result['invalid_or_future_timestamp']+=1
    return result


def attach_nba_summaries(board, markets, payload, observed_at):
    summaries, incomplete = summarize_by_team(payload, observed_at)
    positions = summarize_positions_by_team(payload, observed_at, 'NBA')
    observed = aware(observed_at)
    for pick in list(board.get('picks', [])) + list(board.get('watchlist', [])):
        event = markets.get(pick.get('id'))
        if not event or event.get('league') != 'NBA':
            continue
        try:
            if observed >= aware(event['starts_at']):
                continue
            sides = {}
            for side in ('away', 'home'):
                code = event[side]
                if code not in summaries:
                    raise ValueError('unknown team')
                sides[side] = {'team': event[side + '_name'], 'counts': summaries[code], 'positions': positions[code]}
            pick['nba_availability_context'] = {
                'teams': sides, 'source': 'PropLine, ESPN-sourced',
                'observed_at': observed.isoformat(), 'incomplete': incomplete,
                'used_in_prediction': False,
            }
        except (KeyError, TypeError, ValueError):
            continue


def attach_nfl_summaries(board, markets, payload, observed_at):
    """Attach current aggregate NFL status counts, not starter assumptions."""
    summaries, incomplete = summarize_by_team(payload, observed_at, league='NFL')
    positions = summarize_positions_by_team(payload, observed_at, 'NFL')
    observed = aware(observed_at)
    for pick in list(board.get('picks', [])) + list(board.get('watchlist', [])):
        event = markets.get(pick.get('id'))
        if not event or event.get('league') != 'NFL':continue
        try:
            if observed >= aware(event['starts_at']):continue
            sides = {}
            for side in ('away','home'):
                code=event[side]
                if code not in summaries:raise ValueError('unknown team')
                sides[side]={'team':event[side+'_name'],'counts':summaries[code],'positions':positions[code]}
            pick['nfl_provider_availability_context']={
                'teams':sides,'source':'PropLine, ESPN-sourced',
                'observed_at':observed.isoformat(),'incomplete':incomplete,
                'used_in_prediction':False,
            }
        except (KeyError,TypeError,ValueError):continue
