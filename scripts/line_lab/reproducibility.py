"""Reproduce frozen pure-elo-v1 predictions from their immutable input snapshot."""
import math
from datetime import date
from .constants import ET
from .history import aware
from .ledger_v2 import snapshot_hash


def reproduce_pure_elo_v1(snapshot,side):
    """Frozen v1 scoring formula; this does not rebuild external source data."""
    try:
        if snapshot['model']!='pure-elo-v1' or side not in ('home','away'):return None
        day=aware(snapshot['starts_at']).astimezone(ET).date()
        def rest(value):
            if value in (None,'None',''):return 3
            return min(7,max(0,(day-date.fromisoformat(value)).days-1))
        def mean(values):
            return sum(float(v) for v in values)/len(values) if values else 0.0
        hr,ar=float(snapshot['home_rating']),float(snapshot['away_rating'])
        hfa=0 if snapshot['neutral'] else float(snapshot['home_advantage'])
        rd=rest(snapshot['home_last'])-rest(snapshot['away_last'])
        form=mean(snapshot['home_margins'])-mean(snapshot['away_margins'])
        difference=hr-ar+hfa+float(snapshot['rest_weight'])*rd+float(snapshot['form_weight'])*form
        if not math.isfinite(difference):return None
        p=1/(1+10**(-max(-1200,min(1200,difference))/400))
        return p if side=='home' else 1-p
    except (KeyError,TypeError,ValueError,OverflowError,ZeroDivisionError):return None


def verify_paper_pick(pick):
    """Verify a stored v2 prediction without modifying the ledger."""
    if pick.get('ledger_version')!=2 or pick.get('model')!='pure-elo-v1':return 'not_available'
    try:
        snapshot=pick['feature_snapshot']
        if snapshot_hash(snapshot)!=pick['feature_snapshot_hash']:return 'hash_mismatch'
        if pick['team_code']==snapshot['home']:side='home'
        elif pick['team_code']==snapshot['away']:side='away'
        else:return 'team_mismatch'
        value=reproduce_pure_elo_v1(snapshot,side);original=float(pick['model_only_probability'])
        if value is None or not math.isfinite(original):return 'not_reproducible'
        return 'verified' if abs(value-original)<1e-10 else 'prediction_mismatch'
    except (KeyError,TypeError,ValueError,OverflowError):return 'not_reproducible'


def attach_prediction_checks(board,ledger):
    frozen={p.get('id'):p for p in ledger};active=[]
    for item in board.get('picks',[]):
        original=frozen.get(item.get('id'),{});status=verify_paper_pick(original)
        item['prediction_integrity']=status
        if original.get('model')=='pure-elo-v1' and status!='verified':
            board['errors'].append('A paper pick was hidden because its frozen prediction could not be verified')
            continue
        active.append(item)
    board['picks']=active
