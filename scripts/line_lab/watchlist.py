"""Price a user-requested game to follow without recording a model pick."""
from .constants import BOOKS
from .history import aware


def render_watchlist(markets,requests,now):
    current=aware(now);result=[];seen=set()
    for requested in requests:
        try:
            event=markets[requested['id']];code=requested['team_code']
            if event['id'] in seen or aware(event['starts_at'])<=current:continue
            side='home' if code==event['home'] else 'away' if code==event['away'] else None
            if not side:continue
            books=[{'name':name,'odds':event['books'][name][side] if name in event['books'] else None,
                    'as_of':event['books'][name]['as_of'] if name in event['books'] else None} for _,name in BOOKS]
            prices=[b['odds'] for b in books if isinstance(b['odds'],int) and not isinstance(b['odds'],bool)]
            if not prices:continue
            other='away' if side=='home' else 'home'
            result.append({'id':event['id'],'team_code':code,'team':event[side+'_name'],
                           'opponent':event[other+'_name'],'league':event['league'],'starts_at':event['starts_at'],
                           'books':books,'best':max(prices),'watching':True})
            seen.add(event['id'])
        except (KeyError,TypeError,ValueError):continue
    return result
