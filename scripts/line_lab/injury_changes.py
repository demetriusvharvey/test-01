"""Compare consecutive public aggregate injury snapshots; no player identities stored."""
from datetime import timedelta
from .history import aware

CONTEXT_KEYS=('nba_availability_context','nfl_provider_availability_context')


def annotate_injury_changes(board, previous):
    """Annotate observed count changes without modifying historical forecasts.

    Comparisons are only valid for matching game IDs, same provider and
    chronological observations. Gaps, incomplete reports and missing teams
    are explicitly not evidence that injuries improved.
    """
    if not isinstance(previous,dict):return 0
    earlier={x.get('id'):x for x in previous.get('games',[]) if isinstance(x,dict)}
    changes=0
    for game in board.get('games',[]):
        prior=earlier.get(game.get('id'))
        if not prior:continue
        for key in CONTEXT_KEYS:
            curr,old=game.get(key),prior.get(key)
            if not isinstance(curr,dict) or not isinstance(old,dict):continue
            try:
                if curr.get('source')!=old.get('source'):continue
                now,then=aware(curr['observed_at']),aware(old['observed_at'])
                if now<=then:continue
                if now-then>timedelta(hours=30):
                    game['injury_change']={'status':'comparison_unavailable',
                        'reason':'previous injury report too old to compare'}
                    continue
                if curr.get('incomplete') is not False or old.get('incomplete') is not False:
                    game['injury_change']={'status':'comparison_unavailable',
                        'reason':'missing or incomplete injury report','observed_at':curr['observed_at']}
                    continue
                diff={}
                for side in ('home','away'):
                    new_team,old_team=curr['teams'][side],old['teams'][side]
                    if new_team['team']!=old_team['team'] or not new_team.get('report_present') or not old_team.get('report_present'):
                        raise ValueError('missing team coverage')
                    for counts in (new_team['counts'],old_team['counts']):
                        if any(type(counts[status]) is not int or not 0<=counts[status]<=80
                               for status in ('out','doubtful','questionable')):
                            raise ValueError('invalid aggregate injury count')
                    diff[side]={status:new_team['counts'][status]-old_team['counts'][status]
                                for status in ('out','doubtful','questionable')}
                changed=any(amount for side in diff.values() for amount in side.values())
                game['injury_change']={'status':'changed' if changed else 'unchanged',
                    'observed_at':curr['observed_at'],'previous_observed_at':old['observed_at'],
                    'count_differences':diff,'limitations':'aggregate listing changes do not establish who will play'}
                if changed:changes+=1
            except (KeyError,ValueError,TypeError,OverflowError):
                game['injury_change']={'status':'comparison_unavailable','reason':'invalid snapshot alignment'}
    return changes
