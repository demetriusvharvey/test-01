"""Immutable daily winner forecasts, independent of sportsbook price and EV.

This is a ranking of Elo outcomes, not a calibrated confidence or betting edge.
"""
from datetime import datetime, timedelta
from .constants import ET, BOOKS
from .ledger import grade_ledger
from .ledger_v2 import feature_snapshot, snapshot_hash, validate_transition
from .model import project_home
from .reproducibility import verify_paper_pick


def make_daily_winners(scheduled, models, now, prior, limit=3):
    """Save up to three most favored teams on today's unstarted slate, once.

    Only a missing/unusable schedule or model can produce no daily winners;
    prices and expected value never enter this selection. Immutable existing
    forecasts are never revised in response to later odds or game news.
    """
    day = now.astimezone(ET).date().isoformat()
    existing_ids = {row['id'] for row in prior if row.get('pick_day') == day}
    if len(existing_ids) >= limit: return []
    candidates = []
    for game in scheduled:
        try:
            start = datetime.fromisoformat(game['starts_at'])
            if start.tzinfo is None or start <= now+timedelta(minutes=5) or start.astimezone(ET).date().isoformat() != day or game['id'] in existing_ids: continue
            league = game['league'];model = models[league]
            _, _, away, home = game['id'].split(':')
            if home == away or model.get('source_hashes') is None or home not in model['ratings'] or away not in model['ratings']: continue
            event = {'home':home,'away':away,'starts_at':game['starts_at'],'neutral':game.get('neutral',False)}
            p_home = project_home(model,home,away,start,event['neutral'])
            if p_home is None or not 0 < p_home < 1 or p_home == .5:continue
            side = 'home' if p_home > .5 else 'away'
            chosen = p_home if side == 'home' else 1-p_home
            snapshot = feature_snapshot(event, model)
            candidates.append({'id':game['id'],'league':league,'team_code':event[side],
                               'team':game[side],'opponent':game['away' if side=='home' else 'home'],
                               'starts_at':game['starts_at'],'pick_day':day,'predicted_at':now.isoformat(),
                               'probability':round(chosen,8),'outcome':'pending','model':'pure-elo-v1',
                               'winner_selection':True,'ledger_version':2,'selection_rule':'top-elo-winner-v1',
                               'feature_snapshot':snapshot,'feature_snapshot_hash':snapshot_hash(snapshot),
                               'model_only_probability':chosen,
                               'limitations':'Injuries, lineups, weather and player-specific effects are not model inputs; probability is not calibrated.'})
        except (KeyError,TypeError,ValueError,OverflowError):continue
    candidates.sort(key=lambda row:(-row['probability'],row['id']))
    return candidates[:max(0,limit-len(existing_ids))]


def render_winners(board, ledger, now, models):
    """Use the real game slate for optional prices and injury context."""
    day=now.astimezone(ET).date().isoformat();games={g['id']:g for g in board['games']}
    for game in board['games']:
        try:
            _,_,away,home=game['id'].split(':')
            model=models[game['league']]
            p=project_home(model,home,away,datetime.fromisoformat(game['starts_at']),game.get('neutral',False))
            if p is not None and p!=.5:
                game['predicted_winner']=game['home'] if p>.5 else game['away']
                game['prediction_uncertain']=.45<p<.55
        except (KeyError,ValueError,TypeError):pass
    active=[];history=[]
    for row in ledger:
        status=verify_paper_pick(row)
        if status!='verified':
            board['errors'].append('A winner forecast failed its frozen input check')
            continue
        item={key:row.get(key) for key in ('id','league','team','opponent','starts_at','pick_day','predicted_at','outcome','graded_at')}
        item['model']='pure-elo-v1';item['winner_selection']=True
        history.append(item)
        if row['pick_day']!=day or row['outcome']!='pending' or datetime.fromisoformat(row['starts_at'])<=now:continue
        game=games.get(row['id'])
        if game is None:continue
        side='home' if row['team_code']==row['feature_snapshot']['home'] else 'away'
        item={**item,'current':True,'books':[
            {'name':name,'odds':game.get('books',{}).get(name,{}).get(side),
             'as_of':game.get('books',{}).get(name,{}).get('as_of')}
            for _,name in BOOKS], 'prediction_integrity':status,'close_forecast':row['probability']<.55}
        for field in ('nba_availability_context','nfl_provider_availability_context','availability_context','schedule_context','referee_assignment','line_history'):
            if field in game:item[field]=game[field]
        active.append(item)
    active.sort(key=lambda x:(-next(r['probability'] for r in ledger if r['id']==x['id']),x['id']))
    for rank,item in enumerate(active,1):item['rank']=rank
    wins=sum(x['outcome']=='win' for x in history);losses=sum(x['outcome']=='loss' for x in history)
    pending=sum(x['outcome']=='pending' for x in history);voids=sum(x['outcome']=='void' for x in history)
    board['legacy_history']=board['history']
    board['picks']=active;board['history']=history
    board['accuracy']={'wins':wins,'losses':losses,'pending':pending,'voids':voids,
                       'percent':round(100*wins/(wins+losses),1) if wins+losses else None}
    board['model']='Pure team Elo winner ranking — probabilities not calibrated'
    return board
