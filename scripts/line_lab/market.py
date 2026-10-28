"""Market components for the picks pipeline."""
from datetime import datetime, timedelta
from statistics import median
from .constants import *
from .model import project_home


def implied(odds): return -odds/(-odds+100) if odds<0 else 100/(odds+100)

def decimal_odds(odds):
    return 1+100/(-odds) if odds<0 else 1+odds/100

def build_market(events,now):
    merged={}
    for x in events:
        asof=datetime.fromisoformat(x['as_of']); start=datetime.fromisoformat(x['starts_at'])
        if now-asof>timedelta(minutes=95) or start<=now+timedelta(minutes=20): continue
        rec=merged.setdefault(x['id'],{k:x[k] for k in ('id','league','home','away','home_name','away_name','starts_at')})
        rec.setdefault('books',{})[x['book']]={'home':x['home_odds'],'away':x['away_odds'],'as_of':x['as_of']}
    return merged

def choose_candidates(markets,models,now,ledger):
    existing={p['id'] for p in ledger}; today=now.astimezone(ET).date().isoformat()
    already=sum(p.get('pick_day')==today for p in ledger)
    results=[]
    for event in markets.values():
        start=datetime.fromisoformat(event['starts_at'])
        if start.astimezone(ET).date().isoformat()!=today or start<=now+timedelta(minutes=20) or event['id'] in existing or len(event['books'])<3: continue
        elo=project_home(models[event['league']],event['home'],event['away'],start,event.get('neutral',False))
        if elo is None: continue
        # Team probability uses completed-game ratings only. Odds do not affect
        # the forecast; they are used below solely to price a paper selection.
        for side,p in [('home',elo),('away',1-elo)]:
            best=max(v[side] for v in event['books'].values())
            edge=p-implied(best)
            if edge>=.01:
                initial_books=[{'name':name,'odds':event['books'][name][side] if name in event['books'] else None,'as_of':event['books'][name]['as_of'] if name in event['books'] else None} for _,name in BOOKS]
                ev=p*decimal_odds(best)-1
                results.append({'id':event['id'],'league':event['league'],'team_code':event[side], 'team':event[side+'_name'],'opponent':event[('away' if side=='home' else 'home')+'_name'],'starts_at':event['starts_at'],'probability':round(p,5),'predicted_at':now.isoformat(),'pick_day':today,'initial_best_odds':best,'initial_books':initial_books,'edge':edge,'estimated_ev':round(ev,5),'outcome':'pending','model':'pure-elo-v1','mode':'paper','staking_allowed':False,'guard_reason':'sharp validation and point-in-time availability checks missing'})
    results.sort(key=lambda x:x['estimated_ev'],reverse=True)
    chosen=[]; used=set()
    for x in results:
        if x['id'] in used: continue
        chosen.append(x); used.add(x['id'])
        if len(chosen)>=max(0,3-already): break
    return chosen if already<3 else []
