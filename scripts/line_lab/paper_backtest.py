"""Chronological replay of frozen paper picks with explicit execution assumptions."""
import heapq
import math
from collections import Counter,defaultdict
from datetime import timedelta

from .anchors import devig,implied_american
from .constants import ET
from .experiment import _block_interval,_logloss
from .history import aware


def _candidate(row,cutoff):
    """Pre-selection checks use only information captured before the pick."""
    try:
        predicted,start,feature,source,fetched=(aware(row[k]) for k in
            ('predicted_at','starts_at','feature_observed_at','source_as_of','fetched_at'))
        if not feature<=predicted<start or not source<=fetched<=predicted or predicted-source>timedelta(minutes=95):return None
        if predicted>cutoff or row.get('rights_verified') is not True or row.get('selection')!='selected_paper':return None
        if row.get('league') not in ('NBA','NFL') or row.get('side') not in ('home','away') or not row.get('game_id') or not row.get('book'):return None
        model=float(row['model_probability'])
        if not math.isfinite(model) or not 0<model<1:return None
        home,away=(implied_american(row[k]) for k in ('home_odds','away_odds'))
        reference=devig([home,away])[0]
        probability=reference if row['side']=='home' else 1-reference
        price=row['home_odds'] if row['side']=='home' else row['away_odds']
        decimal=1/implied_american(price)
        return {'predicted':predicted,'start':start,'model':model,'market':probability,'decimal':decimal,'row':row}
    except (KeyError,TypeError,ValueError,OverflowError):return None


def _settlement(row,start,cutoff):
    """Ties and cancellations remain unresolved unless settlement is verified."""
    try:
        observed=aware(row['result_observed_at']);status=row['result_status']
        if not start<=observed<=cutoff or row.get('outcome_rights_verified') is not True:return None
        if status in ('win','loss'):return observed,status
        if status=='void' and row.get('settlement_rule_verified') is True:return observed,status
        return None
    except (KeyError,TypeError,ValueError):return None


def _certified_sharp(row,predicted,start):
    value=row.get('sharp_close')
    try:
        if not value or not all(value.get(k) is True for k in ('rights_verified','independent','certified_close')):return None
        if not value.get('source') or not aware(value['as_of'])<=aware(value['observed_at'])<start:return None
        if aware(value['observed_at'])<predicted:return None
        p=float(value['selected_probability'])
        return p if math.isfinite(p) and 0<p<1 else None
    except (KeyError,TypeError,ValueError):return None


def replay(rows,cutoff,initial_bankroll=100.0,flat_units=1.0,daily_cap=3.0,slippage_fraction=.02):
    """Replay first frozen pick per game; never place a wager or claim a fill.

    Bankroll and limits are hypothetical. Later results cannot affect earlier
    selection or position sizing; unknown settlements keep stake reserved.
    """
    now=aware(cutoff)
    if any(not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) or x<=0
           for x in (initial_bankroll,flat_units,daily_cap)) or not 0<=slippage_fraction<1:
        raise ValueError('invalid replay assumptions')
    # Freeze the first selected row per game before checking later outcomes.
    selected=[r for r in rows if r.get('selection')=='selected_paper']
    def order(row):
        try:return aware(row['predicted_at'])
        except (KeyError,TypeError,ValueError):return now+timedelta(days=1)
    selected.sort(key=lambda r:(order(r),str(r.get('game_id',''))))
    first={}
    for row in selected:
        key=(row.get('league'),row.get('game_id'))
        if key[1]:first.setdefault(key,row)
    candidates=[];excluded=Counter()
    for row in first.values():
        candidate=_candidate(row,now)
        if candidate:candidates.append(candidate)
        else:excluded['ineligible_source_time_or_inputs']+=1
    candidates.sort(key=lambda x:(x['predicted'],x['row']['game_id']))
    cash=float(initial_bankroll);reserved=0.0;daily=defaultdict(float);pending=[];unresolved=[];settled=[];sequence=0
    peak=float(initial_bankroll);max_drawdown=0.0;equity=[]
    def settle_until(when):
        nonlocal cash,reserved,peak,max_drawdown
        while pending and pending[0][0]<=when:
            observed,_,item=heapq.heappop(pending);reserved-=item['stake']
            status=item['status'];profit=item['stake']*(item['decimal']-1) if status=='win' else -item['stake'] if status=='loss' else 0.0
            cash+=item['stake']+profit;item['profit']=profit;settled.append(item)
            value=cash+reserved;peak=max(peak,value);max_drawdown=max(max_drawdown,peak-value)
            equity.append({'observed_at':observed.isoformat(),'units':round(value,6)})
    for candidate in candidates:
        settle_until(candidate['predicted']);row=candidate['row'];day=candidate['start'].astimezone(ET).date().isoformat()
        stake=min(flat_units,max(0.0,daily_cap-daily[day]),cash)
        if stake<=1e-12:excluded['daily_cap_or_cash']+=1;continue
        # A 2% haircut applies to the quoted net payout, not to the probability.
        execution_decimal=1+(candidate['decimal']-1)*(1-slippage_fraction)
        daily[day]+=stake;cash-=stake;reserved+=stake
        item={**candidate,'stake':stake,'decimal':execution_decimal,'day':day,
              'sharp_close_probability':_certified_sharp(row,candidate['predicted'],candidate['start'])}
        result=_settlement(row,candidate['start'],now)
        if result:
            item['status']=result[1];sequence+=1;heapq.heappush(pending,(result[0],sequence,item))
        else:unresolved.append(item)
    settle_until(now)
    graded=[r for r in settled if r['status'] in ('win','loss')]
    roi_groups=defaultdict(list);clv_groups=defaultdict(list);loss_groups=defaultdict(list)
    bins=[{'low':i/5,'high':(i+1)/5,'n':0,'mean_probability':None,'win_rate':None,'_p':0,'_y':0} for i in range(5)]
    for item in graded:
        y=1 if item['status']=='win' else 0;day=item['day'];p=item['model'];market=item['market']
        roi_groups[day].append(item['profit']/item['stake']);loss_groups[day].append(_logloss(p,y)-_logloss(market,y))
        if item['sharp_close_probability'] is not None:
            clv_groups[day].append(item['decimal']*item['sharp_close_probability']-1)
        bucket=bins[min(4,int(p*5))];bucket['n']+=1;bucket['_p']+=p;bucket['_y']+=y
    for b in bins:
        if b['n']:b['mean_probability']=b['_p']/b['n'];b['win_rate']=b['_y']/b['n']
        del b['_p'];del b['_y']
    n=len(graded);staked=sum(x['stake'] for x in graded);sharp_n=sum(len(v) for v in clv_groups.values())
    return {'forecast_candidates':len(first),'qualified_candidates':len(candidates),'settled':n,
            'wins':sum(x['status']=='win' for x in graded),'losses':sum(x['status']=='loss' for x in graded),
            'verified_voids':sum(x['status']=='void' for x in settled),'pending_or_unresolved':len(unresolved)+len(pending),
            'excluded':dict(excluded),'stake_units':staked,'paper_profit_units':sum(x['profit'] for x in graded),
            'paper_roi':sum(x['profit'] for x in graded)/staked if staked else None,
            'paper_roi_interval':_block_interval(roi_groups),'model_brier':sum((x['model']-(x['status']=='win'))**2 for x in graded)/n if n else None,
            'market_brier':sum((x['market']-(x['status']=='win'))**2 for x in graded)/n if n else None,
            'paired_logloss_difference':sum(sum(v) for v in loss_groups.values())/n if n else None,
            'paired_logloss_interval':_block_interval(loss_groups),'sharp_close_samples':sharp_n,
            'sharp_clv':sum(sum(v) for v in clv_groups.values())/sharp_n if sharp_n else None,
            'sharp_clv_interval':_block_interval(clv_groups),'max_drawdown_units':max_drawdown if settled else None,
            'cash_units':cash,'reserved_units':reserved,'equity_curve':equity,'calibration':bins,
            'assumptions':{'initial_bankroll_units':initial_bankroll,'flat_stake_units':flat_units,'daily_cap_units':daily_cap,
                           'net_payout_slippage_fraction':slippage_fraction,'limits_and_fills':'illustrative, not verified',
                           'no_actual_wagers':True},'validated_profitable':False}
