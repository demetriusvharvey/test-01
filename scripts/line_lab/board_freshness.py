"""Keep a labeled recent successful snapshot through a total schedule outage."""
import copy
from datetime import timedelta
from .history import aware


def protect_last_success(current,previous,now):
    current=copy.deepcopy(current);stamp=aware(now)
    errors=current.get('errors',[])
    failures=[any(str(e).startswith(league+' score source unavailable') for e in errors) for league in ('NBA','NFL')]
    failed=all(failures)
    if current.get('games') or not failed:
        current['refresh_status']={'status':'partial' if any(failures) else 'ok','attempted_at':now,
                                   'last_successful_at':current.get('generated_at')}
        return current
    current['refresh_status']={'status':'unavailable','attempted_at':now,'last_successful_at':None}
    try:
        old=aware(previous['generated_at'])
        if not previous.get('games') or not old<=stamp<=old+timedelta(minutes=95):return current
        saved=copy.deepcopy(previous)
        saved['refresh_status']={'status':'stale','attempted_at':now,'last_successful_at':previous['generated_at']}
        saved['errors']=list(errors)+['Current schedule refresh unavailable; showing the last successful slate.']
        saved['source_status']={**saved.get('source_status',{}),'scoreboard_status':'unavailable','serving_last_success':True}
        saved['picks']=[{**p,'data_stale':True} for p in saved.get('picks',[]) if aware(p['starts_at'])>stamp]
        for game in saved.get('games',[]):game['data_stale']=True
        return saved
    except (TypeError,KeyError,ValueError):return current
