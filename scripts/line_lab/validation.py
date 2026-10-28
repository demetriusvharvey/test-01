"""Prospective validation calculations; missing sharp data can never pass a gate."""
import math
from collections import defaultdict

from .constants import ET
from .history import aware
from .market import decimal_odds
from .statistics import bh_adjust, paired_block_test
from .experiment import _block_interval, _logloss


def _qualified(row):
    try:
        predicted=aware(row['predicted_at']); start=aware(row['starts_at']); final=aware(row['final_observed_at'])
        pre_source=aware(row['sharp_source_at']); pre_seen=aware(row['sharp_observed_at'])
        close_source=aware(row['close_source_at']); close_seen=aware(row['close_observed_at'])
        if not pre_source<=pre_seen<=predicted<=close_source<=close_seen<start<=final:
            return False
        if not all(row.get(k) is True for k in ('rights_verified','independent_sharp','closing_certified')):
            return False
        if not row.get('sharp_source') or not row.get('id') or row.get('result') not in (0,1):
            return False
        if any(not isinstance(row.get(k),(int,float)) or not math.isfinite(row[k]) or not 0<row[k]<1
               for k in ('model_probability','sharp_pregame_probability','sharp_close_probability')):
            return False
        if not isinstance(row.get('price'),int) or isinstance(row['price'],bool) or abs(row['price'])<100:
            return False
        return True
    except (KeyError,TypeError,ValueError):
        return False


def assess_forward(rows):
    """Evaluate first selected qualified forecast per game, never retail as sharp."""
    first={}
    for row in sorted(rows,key=lambda r:r.get('predicted_at','')):
        if row.get('id'):first.setdefault(row['id'],row)
    valid=[r for r in first.values() if _qualified(r)]
    losses=defaultdict(list);clvs=defaultdict(list);returns=defaultdict(list)
    brier_model=[];brier_sharp=[]
    for row in valid:
        y=row['result'];p=row['model_probability'];s=row['sharp_pregame_probability']
        day=aware(row['starts_at']).astimezone(ET).date().isoformat()
        losses[day].append(_logloss(p,y)-_logloss(s,y))
        clvs[day].append(decimal_odds(row['price'])*row['sharp_close_probability']-1)
        returns[day].append(decimal_odds(row['price'])-1 if y else -1.0)
        brier_model.append((p-y)**2);brier_sharp.append((s-y)**2)
    n=len(valid)
    def mean(groups):
        values=[v for group in groups.values() for v in group]
        return sum(values)/len(values) if values else None
    return {'eligible_games':n,'excluded_games':len(first)-n,'game_days':len(losses),
            'paired_log_loss_difference':mean(losses),'paired_log_loss_interval':_block_interval(losses),
            'paired_test':paired_block_test(losses),'sharp_clv':mean(clvs),
            'sharp_clv_interval':_block_interval(clvs),'paper_roi':mean(returns),
            'paper_roi_interval':_block_interval(returns),
            'model_brier':sum(brier_model)/n if n else None,
            'sharp_brier':sum(brier_sharp)/n if n else None}


def validation_gates(summaries,replication_confirmed=None,untouched_holdout_confirmed=None):
    """Report evidence thresholds; never authorize orders or silently promote."""
    leagues=('NBA','NFL')
    q=bh_adjust([summaries.get(l,{}).get('paired_test',{}).get('p_value')
                 if summaries.get(l,{}).get('paired_test') else None for l in leagues])
    results={}
    for league,adjusted in zip(leagues,q):
        s=summaries.get(league,{})
        clv=s.get('sharp_clv_interval');roi=s.get('paper_roi_interval')
        checks={'at_least_300':s.get('eligible_games',0)>=300,
                'paired_loss_favors_model':s.get('paired_log_loss_difference') is not None and s['paired_log_loss_difference']<0 and adjusted is not None and adjusted<=.05,
                'positive_sharp_clv_interval':bool(clv and clv[0]>0),
                'paper_roi_interval_not_negative':bool(roi and roi[0]>=0),
                'brier_no_worse':s.get('model_brier') is not None and s.get('sharp_brier') is not None and s['model_brier']<=s['sharp_brier'],
                'two_replication_seasons':(replication_confirmed or {}).get(league) is True,
                'untouched_later_holdout':(untouched_holdout_confirmed or {}).get(league) is True}
        results[league]={'checks':checks,'adjusted_p':adjusted,'evidence_bar_met':all(checks.values()),
                         'staking_allowed':False,'automatic_promotion':False}
    return results


def progress_from_ledger(ledger):
    """Current truthful counts; no provider-certified sharp-close feed is configured."""
    result={}
    for league in ('NBA','NFL'):
        rows=[p for p in ledger if p.get('league')==league and p.get('ledger_version')==2
              and p.get('mode')=='paper' and p.get('model')=='pure-elo-v1' and p.get('outcome') in ('win','loss')]
        result[league]={'settled_paper_picks':len(rows),'required_picks':300,
                        'verified_sharp_closes':0,'validated_profitable':False,
                        'staking_allowed':False,
                        'reason':'no configured independent verified sharp-close feed or untouched validation'}
    return result
