"""Point-in-time, aggregate player-status features for a shadow challenger."""
from datetime import timedelta
from .history import aware


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
            observed=aware(context['latest_observed_at'])
            if context.get('source')!='nflverse injury and practice reports' or context.get('incomplete') is not False:return None
            if observed>now or now-observed>timedelta(hours=30):return None
            home,away=(_counts_nfl(context,side,now) for side in ('home','away'))
            source='nflverse injury and practice reports'
        else:return None
        if any(context['teams'][side].get('team')!=event[side+'_name'] for side in ('home','away')):return None
        return {'schema':'availability-counts-v1','source':source,'observed_at':observed.isoformat(),
                'features':{name+'_difference':home[name]-away[name] for name in ('out','doubtful','questionable')},
                'used_in_prediction':False,'limitations':'listed players only; team report and player impact may be incomplete'}
    except (KeyError,TypeError,ValueError,OverflowError):return None
