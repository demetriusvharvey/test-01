"""Report components for the picks pipeline."""
from datetime import datetime
from statistics import median
from .constants import *
from .market import decimal_odds, implied


def render_board(markets,ledger,now,errors,models=None,training_counts=None,added_finals=None,scheduled=None):
    today=now.astimezone(ET).date().isoformat()
    active=[]
    for pick in ledger:
        if pick.get('pick_day')!=today or pick.get('outcome')!='pending': continue
        event=markets.get(pick['id'])
        if not event or datetime.fromisoformat(event['starts_at'])<=now: continue
        side='home' if pick['team_code']==event['home'] else 'away'
        books=[{'name':name,'odds':event['books'][name][side] if name in event['books'] else None,'as_of':event['books'][name]['as_of'] if name in event['books'] else None} for _,name in BOOKS]
        available=[b['odds'] for b in books if b['odds'] is not None]
        if not available: continue
        best=max(available)
        fair=[]
        for quote in event['books'].values():
            try:
                h,a=implied(quote['home']),implied(quote['away'])
                fair.append((h if side=='home' else a)/(h+a))
            except (KeyError,TypeError,ValueError,ZeroDivisionError):continue
        reference=median(fair) if fair else None
        model_p=pick.get('probability') if pick.get('model')=='pure-elo-v1' else None
        active.append({'id':pick['id'],'team':pick['team'],'opponent':pick['opponent'],'league':pick['league'],'starts_at':pick['starts_at'],'books':books,'best':best,'predicted_at':pick['predicted_at'],
                       'model':pick.get('model'),'mode':pick.get('mode','legacy'),
                       'model_probability':model_p,
                       'estimated_ev':round(model_p*decimal_odds(best)-1,5) if isinstance(model_p,(int,float)) else None,
                       'retail_reference_probability':reference,
                       'retail_price_edge':reference-implied(best) if reference is not None else None,
                       'model_edge_vs_retail':model_p-reference if reference is not None and isinstance(model_p,(int,float)) else None})
    history=[]
    for pick in ledger:
        item={key:pick.get(key) for key in ('id','team','opponent','league','starts_at','pick_day','predicted_at','graded_at','outcome','initial_best_odds','initial_books','model','mode','estimated_ev')}
        item['model_probability']=pick.get('probability') if pick.get('model')=='pure-elo-v1' else None
        history.append(item)
    wins=sum(p.get('outcome')=='win' for p in ledger); losses=sum(p.get('outcome')=='loss' for p in ledger); voids=sum(p.get('outcome')=='void' for p in ledger); pending=sum(p.get('outcome')=='pending' for p in ledger)
    details={}
    for league,model in (models or {}).items():
        unavailable=any(x.startswith(league+' historical') for x in errors)
        details[league]={'available':not unavailable,'training_games':(training_counts or {}).get(league,0),
                         'same_day_finals':(added_finals or {}).get(league,0),'home_advantage':model['home_advantage'],
                         'rest_weight':model['rest_weight'],'form_weight':model.get('form_weight',0),
                         'selection_season':model.get('validation_season'),'holdout_season':model.get('holdout_season'),
                         'selection_count':model.get('selection_count'),'holdout_count':model.get('holdout_count'),
                         'candidate_name':model.get('candidate_name'),'candidate_passed':model.get('candidate_passed',False),
                         'candidate_testing':model.get('candidate_testing','disabled')}
    upcoming=[{'id':e['id'],'league':e['league'],'home':e['home_name'],'away':e['away_name'],
               'starts_at':e['starts_at'],'books':e['books']}
              for e in markets.values() if datetime.fromisoformat(e['starts_at'])>now]
    listed={e['id'] for e in upcoming}
    for e in scheduled or []:
        if e['id'] not in listed and datetime.fromisoformat(e['starts_at'])>now:
            upcoming.append({**e,'books':{}});listed.add(e['id'])
    upcoming.sort(key=lambda e:(e['starts_at'],e['id']))
    return {'generated_at':now.isoformat(),'model':'Pure team Elo — not validated as profitable','source':'AgentBets odds snapshots; BoxScore Lab NBA results; nflverse NFL schedules and results; ESPN final scores','accuracy':{'wins':wins,'losses':losses,'voids':voids,'pending':pending,'percent':round(100*wins/(wins+losses),1) if wins+losses else None},'picks':active,'history':history,'games':upcoming,'model_details':details,'errors':errors}
