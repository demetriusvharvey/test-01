"""Point-in-time market-anchor research helpers; never a model input."""
import math
from collections import defaultdict
from datetime import timedelta
from statistics import median
from .history import aware


def implied_american(odds):
    if not isinstance(odds, (int, float)) or isinstance(odds, bool) or not math.isfinite(odds) or abs(odds) < 100:
        raise ValueError('invalid American odds')
    return -odds / (-odds + 100) if odds < 0 else 100 / (odds + 100)


def devig(prices, method='multiplicative'):
    """Remove overround from two implied probabilities; return probabilities.

    Shin assumes nonnegative insider fraction; it is undefined here for an
    underround. Choosing a method from a backtest requires separate validation.
    """
    q = [float(x) for x in prices]
    if len(q) != 2 or any(not math.isfinite(x) or not 0 < x < 1 for x in q):
        raise ValueError('two probabilities in (0,1) required')
    total = sum(q)
    if method == 'multiplicative':
        return tuple(x / total for x in q)
    if method == 'power':
        lo, hi = 0.0, 100.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if sum(x ** mid for x in q) > 1: lo = mid
            else: hi = mid
        return tuple(x ** ((lo + hi) / 2) for x in q)
    if method == 'shin':
        if total < 1 - 1e-12: raise ValueError('Shin does not handle underrounds')
        if abs(total - 1) < 1e-12: return tuple(q)
        def probabilities(z):
            return [2 * (x * x / total) / (math.sqrt(z*z + 4*(1-z)*x*x/total) + z) for x in q]
        lo, hi = 0.0, 1.0 - 1e-12
        for _ in range(100):
            mid = (lo + hi) / 2
            if sum(probabilities(mid)) > 1: lo = mid
            else: hi = mid
        return tuple(probabilities((lo + hi) / 2))
    raise ValueError('unknown devig method')


def _quote_valid(q, now, start, max_age):
    try:
        source, fetched = aware(q['as_of']), aware(q['fetched_at'])
        if not (source <= fetched <= now < start) or now-source > max_age: return False
        if not q.get('book') or q.get('kind') not in ('retail', 'sharp', 'exchange', 'prediction_market'): return False
        implied_american(q['home_odds']); implied_american(q['away_odds'])
        if q['kind'] != 'retail' and not (q.get('rights_verified') is True and q.get('source_type_verified') is True and q.get('upstream_group')): return False
        if q['kind'] in ('exchange', 'prediction_market'):
            fee = q.get('fee_fraction')
            if not (isinstance(fee,(int,float)) and not isinstance(fee,bool) and 0 <= fee < 1 and q.get('liquidity_verified') is True): return False
            if not (isinstance(q.get('available_units'),(int,float)) and q['available_units'] > 0): return False
        return True
    except (KeyError,TypeError,ValueError,OverflowError): return False


def _effective_probability(odds, fee):
    implied = implied_american(odds)
    decimal = 1 / implied
    return 1 / (1 + (decimal - 1) * (1 - fee))


def build_shadow_anchor(quotes, now, starts_at, method='multiplicative', weights=None, max_age=timedelta(minutes=95)):
    """Return a time-matched sharp/exchange reference or a labeled retail fallback.

    This output is descriptive shadow data and is never allowed into pure Elo.
    Per-source weights may only be supplied from an earlier eligible fit.
    Duplicate observations with the same upstream group are counted once.
    """
    current, start = aware(now), aware(starts_at)
    if method not in ('multiplicative','power','shin'): raise ValueError('unknown devig method')
    fitted_weights = {}
    if weights is not None:
        if not isinstance(weights,dict) or not weights.get('training_cutoff') or aware(weights['training_cutoff']) >= current:
            raise ValueError('weights must have an earlier training cutoff')
        fitted_weights = weights.get('weights',{})
    valid = [q for q in quotes if _quote_valid(q,current,start,max_age)]
    trusted = [q for q in valid if q['kind'] != 'retail']
    if trusted:
        latest = {}
        for q in trusted:
            group=q['upstream_group']
            if group not in latest or aware(q['fetched_at']) > aware(latest[group]['fetched_at']): latest[group]=q
        rows = list(latest.values()); values = []
        for q in rows:
            fee=q.get('fee_fraction',0) if q['kind'] in ('exchange','prediction_market') else 0
            try: fair=devig([_effective_probability(q['home_odds'],fee),_effective_probability(q['away_odds'],fee)],method)
            except ValueError: continue
            weight=fitted_weights.get(q['upstream_group'],1.0)
            if not isinstance(weight,(int,float)) or isinstance(weight,bool) or not math.isfinite(weight) or weight<=0: continue
            values.append((q,fair[0],float(weight)))
        if values:
            total=sum(x[2] for x in values)
            return {'source':'qualified_shadow_consensus','probability_home':sum(v*w for _,v,w in values)/total,
                    'books':[q['book'] for q,_,_ in values],'upstream_groups':[q['upstream_group'] for q,_,_ in values],
                    'method':method,'validated':False,'usable_for_staking':False}
    retail=[]
    for q in valid:
        if q['kind']=='retail':
            try:retail.append(devig([implied_american(q['home_odds']),implied_american(q['away_odds'])],method)[0])
            except ValueError:continue
    if not retail:return {'source':'unavailable','probability_home':None,'books':[],'validated':False,'usable_for_staking':False}
    return {'source':'retail_median_not_sharp','probability_home':median(retail),
            'books':[q['book'] for q in valid if q['kind']=='retail'],'method':method,'validated':False,'usable_for_staking':False}


def fit_shadow_weights(rows, cutoff, min_games=500):
    """Fit source-quality weights only from forecasts settled before cutoff."""
    cutoff=aware(cutoff); by_source=defaultdict(list); seen=set()
    for row in rows:
        try:
            captured, start, settled = (aware(row[k]) for k in ('captured_at','starts_at','settled_at'))
            if not captured < start <= settled < cutoff: continue
            if row.get('rights_verified') is not True or row.get('source_type_verified') is not True: continue
            if not aware(row['source_as_of']) <= aware(row['source_fetched_at']) <= captured: continue
            p=row['home_probability']; outcome=row['home_win']; group=row['upstream_group']; key=(row['game_id'],group)
            if key in seen or not isinstance(p,(int,float)) or not 0<p<1 or outcome not in (0,1): continue
            seen.add(key); by_source[group].append(-(outcome*math.log(p)+(1-outcome)*math.log(1-p)))
        except (KeyError,TypeError,ValueError):continue
    eligible={group:values for group,values in by_source.items() if len(values)>=min_games}
    if not eligible:return None
    # Conservative score-based weights; not promoted without validation.
    weights={group:math.exp(-sum(values)/len(values)) for group,values in eligible.items()}
    total=sum(weights.values())
    return {'training_cutoff':cutoff.isoformat(),'weights':{group:w/total for group,w in weights.items()},
            'counts':{group:len(values) for group,values in eligible.items()},'promoted':False}


def price_diagnostic(home_odds, away_odds):
    """Return a price gap only, not an instruction to place opposite bets."""
    h,a=implied_american(home_odds),implied_american(away_odds)
    return {'implied_sum':h+a,'underround':h+a<1,
            'status':'informational_only_prices_may_change_no_execution'}
