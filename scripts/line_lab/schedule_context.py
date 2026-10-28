"""Informational rest context from the current, pregame team-result snapshot."""
from datetime import date
from .constants import ET
from .history import aware


def observed_rest_context(event,model,now):
    """Report known previous-game dates; do not infer a travel itinerary."""
    try:
        current=aware(now);start=aware(event['starts_at'])
        if current>=start:return None
        day=start.astimezone(ET).date();today=current.astimezone(ET).date();result={}
        for side in ('home','away'):
            team=event[side];last=model.get('last',{}).get(team)
            if not isinstance(last,date) or last>today or last>=day:
                result[side]=None;continue
            days=(day-last).days-1
            result[side]={'team':event[side+'_name'],'last_game':last.isoformat(),
                          'rest_days':days,'back_to_back':days==0}
        return {'teams':result,'source':'completed game data available to current pipeline',
                'observed_at':current.isoformat(),'travel':'unknown','time_zone_change':'unknown',
                'note':'previous-game dates may be incomplete; market may already reflect the schedule',
                'used_in_prediction':False}
    except (KeyError,TypeError,ValueError):return None


def attach_rest_context(board,markets,models,now):
    for pick in board.get('picks',[]):
        event=markets.get(pick.get('id'))
        if event and event.get('league') in models:
            pick['schedule_context']=observed_rest_context(event,models[event['league']],now)
