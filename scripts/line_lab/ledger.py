"""Ledger components for the picks pipeline."""
from scripts.refresh_feed import NBA_REFS


def append_referee_assignments(history, report, now):
    # Archive each reported crew and later changes; do not infer a causal effect.
    if report.get('status')!='ok': return 0
    changed=0
    for g in report.get('games',[]):
        matchup=g.get('matchup','')
        if not matchup: continue
        crew=[g.get('crew_chief',''),g.get('referee',''),g.get('umpire',''),g.get('alternate','')]
        if not all(crew[:3]): continue
        key=report['date_expected']+':'+matchup
        previous=next((x for x in reversed(history) if x.get('key')==key),None)
        if previous and previous.get('crew')==crew: continue
        history.append({'key':key,'game_date':report['date_expected'],'matchup':matchup,'crew':crew,'observed_at':now.isoformat(),'source':NBA_REFS})
        changed+=1
    return changed

def grade_ledger(ledger,finals,now):
    byid={x['id']:x for x in finals}; changed=0
    for p in ledger:
        if p.get('outcome') in ('win','loss','void'): continue
        g=byid.get(p['id'])
        if not g: continue
        hs,as_=g['home_score'],g['away_score']
        if hs==as_: result='void'
        else: result='win' if p['team_code']==(g['home'] if hs>as_ else g['away']) else 'loss'
        p['outcome']=result; p['graded_at']=now.isoformat(); p['final_score']={'home':hs,'away':as_}; changed+=1
    return changed

def backfill_initial_books(ledger, snapshots):
    # A legacy pick can only gain quotes from its exact original board snapshot.
    bykey={(p.get('id'),p.get('predicted_at')):p for p in snapshots}
    changed=0
    for pick in ledger:
        snapshot=bykey.get((pick.get('id'),pick.get('predicted_at')))
        if pick.get('initial_books') or not snapshot: continue
        books=snapshot.get('initial_books',[])
        prices=[b.get('odds') for b in books if isinstance(b.get('odds'),int)]
        if not prices or max(prices)!=pick.get('initial_best_odds'): continue
        pick['initial_books']=books; changed+=1
    return changed
