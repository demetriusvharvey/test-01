"""Point-in-time, aggregate player-status features for a shadow challenger."""
from datetime import timedelta
import re
from .history import aware


def position_availability_snapshot(event,context,prediction_at):
    """Capture all reported positions as research data, never as player effects."""
    try:
        now,start=aware(prediction_at),aware(event['starts_at'])
        observed=aware(context['observed_at'])
        if (event.get('league') not in ('NBA','NFL') or context.get('source')!='PropLine, ESPN-sourced'
                or context.get('used_in_prediction') is not False or observed>now or now>=start
                or now-observed>timedelta(minutes=95)):return None
        statuses=('out','doubtful','questionable','other');teams={};unknown=0
        for side in ('away','home'):
            value=context['teams'][side]
            if (value.get('team')!=event[side+'_name'] or value.get('report_present') is False
                    or not isinstance(value.get('positions'),dict)):return None
            positions={}
            for position,counts in value['positions'].items():
                if not isinstance(position,str) or not re.fullmatch(r'[A-Z]{1,7}(?:[-/][A-Z]{1,5})?',position):return None
                if not isinstance(counts,dict):return None
                values={name:counts[name] for name in statuses}
                if any(not isinstance(n,int) or isinstance(n,bool) or n<0 or n>80 for n in values.values()):return None
                positions[position]=values
                if position=='UNKNOWN':unknown+=sum(values.values())
            totals={name:sum(counts[name] for counts in positions.values()) for name in statuses}
            if totals!=value['counts'] or sum(totals.values())>80:return None
            teams[side]={'team':value['team'],'positions':positions,'counts':totals}
        fields_complete=(context.get('incomplete') is False and unknown==0
                         and all(sum(teams[side]['counts'].values())>0 for side in ('home','away')))
        differences=None
        if fields_complete:
            positions=set(teams['home']['positions'])|set(teams['away']['positions'])
            differences={position:{status:teams['home']['positions'].get(position,{}).get(status,0)-
                                     teams['away']['positions'].get(position,{}).get(status,0)
                                   for status in statuses} for position in sorted(positions)}
        return {'schema':'position-status-v1','source':context['source'],'observed_at':observed.isoformat(),
                'teams':teams,'incomplete':context.get('incomplete') is not False,
                'unknown_position_count':unknown,'position_fields_complete':fields_complete,
                'training_eligible':False,'rights_review_required':True,
                'features':differences,'used_in_prediction':False}
    except (KeyError,TypeError,ValueError,OverflowError):return None


def _counts_nba(context, side):
    counts=context['teams'][side]['counts']
    values={name:counts[name] for name in ('out','doubtful','questionable','other')}
    if any(not isinstance(v,int) or isinstance(v,bool) or not 0<=v<=40 for v in values.values()):
        raise ValueError('invalid count')
    # No listing is not evidence that a team has a complete healthy roster.
    if not sum(values.values()):raise ValueError('team report absent')
    return values


def _counts_nfl(context, side, now):
    team=context['teams'][side];entries=team['entries']
    if not isinstance(entries,list) or not entries or team.get('total_entries')!=len(entries):
        raise ValueError('missing or truncated team report')
    values={'out':0,'doubtful':0,'questionable':0,'other':0};reported=0
    for player in entries:
        status=str(player.get('report_status') or '').strip().lower()
        stamp=aware(player.get('observed_at'))
        if stamp>now or now-stamp>timedelta(hours=30):raise ValueError('stale report')
        if status in ('out','doubtful','questionable'):
            values[status]+=1;reported+=1
        elif status in ('probable','available','active'):
            values['other']+=1;reported+=1
        # A practice-only row is not a confirmed game designation.
    if not reported:raise ValueError('no game designations observed')
    if any(v>80 for v in values.values()):raise ValueError('invalid count')
    return values


def availability_features(event,context,prediction_at):
    """Produce only observed, game-specific status differences or None.

    Counts are coarse, non-causal signals. In particular, every player does not
    have the same value. A model may learn from them only in shadow mode until
    properly validated. No unlisted player is assumed available.
    """
    try:
        now,start=aware(prediction_at),aware(event['starts_at'])
        if now>=start or not context or context.get('used_in_prediction') is not False:return None
        league=event['league']
        if league=='NBA':
            observed=aware(context['observed_at'])
            if context.get('incomplete') is not False or context.get('source')!='PropLine, ESPN-sourced':return None
            if observed>now or now-observed>timedelta(minutes=95):return None
            home,away=(_counts_nba(context,side) for side in ('home','away'))
            source='PropLine, ESPN-sourced'
        elif league=='NFL':
            report_observed=aware(context['latest_observed_at']);schedule_observed=aware(context['schedule_observed_at'])
            observed=max(report_observed,schedule_observed)
            if context.get('source')!='nflverse injury and practice reports' or context.get('incomplete') is not False:return None
            if observed>now or now-report_observed>timedelta(hours=30):return None
            home,away=(_counts_nfl(context,side,now) for side in ('home','away'))
            source='nflverse injury and practice reports'
        else:return None
        if any(context['teams'][side].get('team')!=event[side+'_name'] for side in ('home','away')):return None
        return {'schema':'availability-counts-v1','source':source,'observed_at':observed.isoformat(),
                'features':{name+'_difference':home[name]-away[name] for name in ('out','doubtful','questionable')},
                'used_in_prediction':False,'limitations':'listed players only; team report and player impact may be incomplete'}
    except (KeyError,TypeError,ValueError,OverflowError):return None


NFL_POSITION_GROUPS={
    'QB':'QB','RB':'BACK','FB':'BACK','WR':'RECEIVER','TE':'RECEIVER',
    'C':'LINE','G':'LINE','OG':'LINE','T':'LINE','OT':'LINE','OL':'LINE',
    'DT':'FRONT','DE':'FRONT','DL':'FRONT','NT':'FRONT','EDGE':'FRONT',
    'LB':'LINEBACKER','ILB':'LINEBACKER','OLB':'LINEBACKER',
    'CB':'SECONDARY','DB':'SECONDARY','S':'SECONDARY','FS':'SECONDARY','SS':'SECONDARY',
    'K':'SPECIAL','P':'SPECIAL','LS':'SPECIAL',
}
NFL_GROUPS=('QB','BACK','RECEIVER','LINE','FRONT','LINEBACKER','SECONDARY','SPECIAL','OTHER')
NFL_STATUSES=('out','doubtful','questionable')


def nfl_position_features(event,context,prediction_at):
    """Frozen NFL injury counts by position group, without assumed player value.

    An absent player or practice-only status is never counted as available.
    Unrecognized positions remain OTHER. Both teams require untruncated, fresh
    observed reports. The report's capture time is not its publication time.
    """
    try:
        now,start=aware(prediction_at),aware(event['starts_at'])
        observed=aware(context['latest_observed_at'])
        if (event['league']!='NFL' or not observed<=now<start or now-observed>timedelta(hours=30)
                or context.get('source')!='nflverse injury and practice reports'
                or context.get('used_in_prediction') is not False or context.get('incomplete') is not False):return None
        teams={}
        for side in ('home','away'):
            team=context['teams'][side];entries=team['entries']
            if (team['team']!=event[side+'_name'] or not isinstance(entries,list)
                    or not entries or team['total_entries']!=len(entries)):return None
            counts={(group,status):0 for group in NFL_GROUPS for status in NFL_STATUSES}
            seen=set();reported=0
            for player in entries:
                name=player['name'];stamp=aware(player['observed_at'])
                if not isinstance(name,str) or not name or name in seen or stamp>now or now-stamp>timedelta(hours=30):return None
                seen.add(name)
                status=str(player.get('report_status') or '').strip().lower()
                if status in NFL_STATUSES:
                    code=str(player.get('position') or '').strip().upper()
                    group=NFL_POSITION_GROUPS.get(code,'OTHER')
                    counts[group,status]+=1;reported+=1
            if not reported:return None
            teams[side]=counts
        features={f'{group.lower()}_{status}_difference':teams['home'][group,status]-teams['away'][group,status]
                  for group in NFL_GROUPS for status in NFL_STATUSES}
        return {'schema':'nfl-position-status-v1','source':context['source'],
                'observed_at':observed.isoformat(),'features':features,'used_in_prediction':False,
                'limitations':'listed, game-designated players only; role and replacement impact unverified'}
    except (KeyError,TypeError,ValueError,OverflowError):return None
