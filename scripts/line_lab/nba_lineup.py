"""Current roster-aware rotation scenarios; no invented availability weights."""
import math
import csv
import io
from collections import defaultdict
from datetime import timedelta
from .history import aware
from .nba_injury_feed import provider_team_code,STATUSES
from .constants import NBA_TEAMS,ET


def parse_current_rosters(text,observed_at,source):
    """Capture explicit ESPN IDs and source teams; never fuzzy-match names."""
    aware(observed_at);teams=defaultdict(set);membership={};conflicts=set()
    reader=csv.DictReader(io.StringIO(text))
    if not {'athlete_id','team_abbreviation'}<=set(reader.fieldnames or []):raise ValueError('roster schema')
    for row in reader:
        p=str(row['athlete_id']).strip();team=provider_team_code(row['team_abbreviation'],'NBA')
        if not p.isdigit() or team not in NBA_TEAMS.values():continue
        if p in membership and membership[p]!=team:conflicts.add(p)
        membership[p]=team;teams[team].add(p)
    return {team:{'team':team,'player_ids':sorted(ids),'observed_at':observed_at,
                  'source':source,'verified':not bool(ids&conflicts)}
            for team,ids in teams.items()}


def map_injury_statuses(payload,roster,observed_at):
    """Explicit espn: ID mapping; missing listings remain unknown."""
    now=aware(observed_at);ids=set(roster['player_ids']);statuses={};unmatched=0;invalid=0
    diagnostics={'unknown_namespace':0,'missing_from_roster':0,'explicit_id_conflict':0}
    if payload.get('sport')!='basketball_nba' or payload.get('count')!=len(payload.get('players',[])):return None
    for row in payload['players']:
        try:
            if provider_team_code(row.get('team_abbr'),'NBA')!=roster['team']:continue
            raw=str(row.get('player_id') or '')
            explicit=str(row.get('espn_athlete_id') or '').strip()
            prefixed=raw[5:] if raw.startswith('espn:') and raw[5:].isdigit() else ''
            if explicit and not explicit.isdigit():
                diagnostics['explicit_id_conflict']+=1;invalid+=1;continue
            if explicit and prefixed and explicit!=prefixed:
                diagnostics['explicit_id_conflict']+=1;invalid+=1;continue
            p=explicit or prefixed
            if not p:
                diagnostics['unknown_namespace']+=1;unmatched+=1;continue
            if p not in ids:
                diagnostics['missing_from_roster']+=1;unmatched+=1;continue
            status=row['status_code']
            stamps=[aware(v) for v in (row.get('source_updated_at'),row.get('status_since')) if v]
            if status not in STATUSES or not stamps or any(v>now for v in stamps):invalid+=1;continue
            if p in statuses and statuses[p]!=status:invalid+=1;continue
            statuses[p]=status
        except (KeyError,TypeError,ValueError):invalid+=1
    return {'observed_at':observed_at,'players':statuses,'unmatched':unmatched,'invalid':invalid,
            'diagnostics':diagnostics,'matched_players':len(statuses),'roster_players':len(ids),
            'complete':False,'identity_mapping_valid':not (unmatched or invalid),
            'missing_listing_means_healthy':False,
            'note':'matching succeeded only for explicit source IDs; full availability coverage unverified'}


def project_rotation(players,roster,statuses,as_of,starts_at,unavailable=(),conditional=False):
    """Use explicit IDs from a captured roster and explicitly mapped statuses.

    The caller must resolve source IDs before calling. Questionable players
    require explicit separate scenarios rather than assumed play likelihoods.
    """
    try:
        now,start=aware(as_of),aware(starts_at)
        observed=aware(roster['observed_at'])
        if not observed<=now<start or now-observed>timedelta(hours=30):return None
        if roster.get('verified') is not True or not roster.get('source'):return None
        ids=roster['player_ids'];team=roster['team']
        if not isinstance(ids,list) or len(set(ids))!=len(ids) or not 8<=len(ids)<=25:return None
        if any(not isinstance(p,str) or not p for p in ids):return None
        excluded=set(unavailable)
        if not excluded<=set(ids):return None
        report_time=aware(statuses['observed_at'])
        if not report_time<=now or now-report_time>timedelta(minutes=95):return None
        if statuses.get('complete') is not True and not (conditional and statuses.get('identity_mapping_valid') is True):return None
        reports=statuses['players']
        if any(p not in ids for p in reports):return None
        unresolved=[]
        for p,status in reports.items():
            if status in ('out','suspended','injured_list'):excluded.add(p)
            elif status in ('questionable','doubtful','game_time_decision','day_to_day'):
                if p not in excluded:unresolved.append(p)
            elif status not in ('available','probable','active'):return None
        histories=defaultdict(list)
        for row in players:
            if row['player_id'] not in ids or row['team']!=team or row['date']>=now.astimezone(ET).date():continue
            histories[row['player_id']].append(row)
        # A listed player assumed available cannot silently disappear because
        # their role/history is missing. Unlisted fringe roster players remain
        # explicitly unmodeled rather than being declared healthy or zero-value.
        if any(p not in excluded and not histories.get(p) for p in reports):return None
        unmodeled=sum(p not in excluded and not histories.get(p) for p in ids)
        estimates=[]
        for p in ids:
            if p in excluded:continue
            records=sorted(histories[p],key=lambda r:r['date'])[-10:]
            if not records:continue
            minutes=sum(r['minutes'] for r in records)/len(records)
            if not math.isfinite(minutes) or minutes<=0:continue
            estimates.append({'player_id':p,'weight':minutes,'minutes':0.,'prior_games':len(records)})
        from .nba_player_features import allocate_minutes
        estimates=allocate_minutes(estimates)
        if estimates is None:return None
        return {'team':team,'observed_at':now.isoformat(),'roster_observed_at':observed.isoformat(),
                'injury_observed_at':report_time.isoformat(),'players':estimates,
                'unavailable_players':sorted(excluded),'unresolved_players':sorted(unresolved),
                'unmodeled_roster_count':unmodeled,
                'availability_scenario':'unresolved' if unresolved else 'specified',
                'conditional_assumption':conditional,
                'used_in_prediction':False,'limitations':'minutes redistribution proxy; no verified replacement impact or availability probabilities'}
    except (KeyError,TypeError,ValueError,OverflowError,ZeroDivisionError):return None
