"""Optional current injury context. No player-level feed data is archived.

This is descriptive context only, not a validated model input. The provider's
terms require the user to obtain a key and agree to them before enabling calls.
"""
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from .constants import NBA_TEAMS, normalize_code
from .history import aware

URL = 'https://api.prop-line.com/v1/sports/basketball_nba/injuries'
STATUSES = {'out', 'out_first_half', 'doubtful', 'questionable', 'probable',
            'game_time_decision', 'day_to_day', 'injured_list', 'suspended', 'other'}


def fetch_nba_injuries(key, enabled, opener=urlopen):
    """Fetch once per run, never with a key in the URL or in an error message."""
    if not key or str(enabled).strip().lower() != 'true':
        return None
    request = Request(URL, headers={'X-API-Key': key, 'Accept': 'application/json'})
    with opener(request, timeout=15) as response:
        payload = json.load(response)
    return payload, datetime.now(timezone.utc).isoformat()


def summarize_by_team(payload, observed_at):
    """Count eligible rows by team, keeping names and raw response out of Git.

    An empty or partial report is not evidence that anyone is healthy. Reject
    future timestamps and conflicting records, and never use the counts as a
    player-impact estimate.
    """
    observed = aware(observed_at)
    if not isinstance(payload, dict) or payload.get('sport') != 'basketball_nba':
        raise ValueError('unexpected injury sport')
    rows = payload.get('players')
    if not isinstance(rows, list) or isinstance(payload.get('count'), bool) or payload.get('count') != len(rows):
        raise ValueError('incomplete injury response')
    teams = set(NBA_TEAMS.values())
    candidates = {}
    incomplete = False
    for row in rows:
        if not isinstance(row, dict):
            incomplete = True
            continue
        code = normalize_code(str(row.get('team_abbr') or '').strip().upper())
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
        bucket = status if status in ('out', 'doubtful') else 'questionable' if status in ('questionable', 'game_time_decision') else 'other'
        summaries[code][bucket] += 1
    return summaries, incomplete


def attach_nba_summaries(board, markets, payload, observed_at):
    summaries, incomplete = summarize_by_team(payload, observed_at)
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
                sides[side] = {'team': event[side + '_name'], 'counts': summaries[code]}
            pick['nba_availability_context'] = {
                'teams': sides, 'source': 'PropLine, ESPN-sourced',
                'observed_at': observed.isoformat(), 'incomplete': incomplete,
                'used_in_prediction': False,
            }
        except (KeyError, TypeError, ValueError):
            continue
