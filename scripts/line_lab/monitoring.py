"""Timestamp-respecting data freshness and descriptive feature drift monitoring."""
import json
import math
from datetime import timedelta

from .experiment import read_forecasts
from .history import aware

RATING_BINS=(-200,-100,-50,0,50,100,200)
PROBABILITY_BINS=(.35,.4,.45,.5,.55,.6,.65)


def population_stability(reference,current,bins):
    """Fixed-bin PSI, with smoothing; descriptive and not proof of model decay."""
    if not reference or not current:return None
    if any(not math.isfinite(x) for x in list(reference)+list(current)):
        raise ValueError('non-finite feature')
    def proportions(values):
        counts=[0]*(len(bins)+1)
        for value in values:
            index=sum(value>cut for cut in bins);counts[index]+=1
        eps=1e-6;denom=len(values)+eps*len(counts)
        return [(n+eps)/denom for n in counts]
    a=proportions(reference);b=proportions(current)
    return sum((y-x)*math.log(y/x) for x,y in zip(a,b))


def summarize_drift(rows,now,min_reference=100,min_current=50):
    """First forecast per game, older 28-day reference vs most recent 7 days."""
    end=aware(now);boundary=end-timedelta(days=7);begin=end-timedelta(days=35)
    first={}
    for row in sorted(rows,key=lambda r:r.get('captured_at','')):
        try:
            captured=aware(row['captured_at']);start=aware(row['starts_at'])
            if not begin<=captured<=end or captured>=start or not row.get('game_id'):continue
            first.setdefault(row['game_id'],row)
        except (KeyError,TypeError,ValueError):continue
    result={}
    for league in ('NBA','NFL'):
        groups={'reference':[],'current':[]}
        for row in first.values():
            if row.get('league')!=league:continue
            try:
                features=json.loads(row['feature_snapshot']);diff=float(features['home_rating'])-float(features['away_rating'])
                probability=float(row['pure_probability'])
                if not math.isfinite(diff) or not 0<probability<1:continue
                key='reference' if aware(row['captured_at'])<boundary else 'current'
                groups[key].append((diff,probability))
            except (KeyError,TypeError,ValueError,json.JSONDecodeError):continue
        ref,cur=groups['reference'],groups['current']
        enough=len(ref)>=min_reference and len(cur)>=min_current
        rating=population_stability([x[0] for x in ref],[x[0] for x in cur],RATING_BINS) if enough else None
        probability=population_stability([x[1] for x in ref],[x[1] for x in cur],PROBABILITY_BINS) if enough else None
        result[league]={'reference_games':len(ref),'current_games':len(cur),'rating_psi':rating,
                        'probability_psi':probability,'status':'review' if enough and max(rating,probability)>.25 else 'descriptive' if enough else 'insufficient_data'}
    return result


def build_monitoring(root,now,markets,errors):
    observed=aware(now);times=[]
    for event in markets.values():
        for quote in event.get('books',{}).values():
            try:
                asof=aware(quote['as_of'])
                if asof<=observed:times.append(asof)
            except (KeyError,TypeError,ValueError):continue
    return {'pipeline_generated_at':observed.isoformat(),'source_warning_count':len(errors),
            'latest_quote_at':max(times).isoformat() if times else None,
            'oldest_quote_at':min(times).isoformat() if times else None,
            'source_freshness':'no_quotes' if not times else 'stale' if observed-min(times)>timedelta(minutes=95) else 'within_window',
            'drift':summarize_drift(read_forecasts(root),now),
            'alerts':'display_only','limitations':'PSI is descriptive, not proof of calibration decay or profit'}
