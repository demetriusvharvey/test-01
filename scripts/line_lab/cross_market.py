"""Licensed spread/total observations and a disabled cross-market challenger."""
import hashlib
import json
import math
import sqlite3
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from .anchors import devig, implied_american
from .constants import ET, game_id, team_code
from .history import aware

SCHEMA='''
CREATE TABLE IF NOT EXISTS market_quotes (
 quote_key TEXT PRIMARY KEY, game_id TEXT NOT NULL, provider TEXT NOT NULL, book TEXT NOT NULL,
 market TEXT NOT NULL, home TEXT NOT NULL, away TEXT NOT NULL, point REAL NOT NULL,
 first_price INTEGER NOT NULL, second_price INTEGER NOT NULL, source_as_of TEXT NOT NULL,
 fetched_at TEXT NOT NULL, starts_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS market_no_update BEFORE UPDATE ON market_quotes BEGIN SELECT RAISE(ABORT,'market quotes are append-only'); END;
CREATE TRIGGER IF NOT EXISTS market_no_delete BEFORE DELETE ON market_quotes BEGIN SELECT RAISE(ABORT,'market quotes are append-only'); END;
'''


def parse_featured_markets(payload, league, fetched_at, allowed_books):
    """Parse only complete, point-matched US spreads/totals from The Odds API."""
    fetched=aware(fetched_at);rows=[]
    if not isinstance(payload,list): raise ValueError('response must be a list')
    for event in payload:
        try:
            home,away=team_code(event['home_team'],league),team_code(event['away_team'],league)
            start=aware(event['commence_time'])
            if not home or not away or home==away or fetched>=start:continue
            for book in event.get('bookmakers',[]):
                name=allowed_books.get(book.get('key'))
                if not name:continue
                for market in book.get('markets',[]):
                    try:
                        kind=market.get('key')
                        if kind not in ('spreads','totals'):continue
                        timestamp=aware(market.get('last_update') or book.get('last_update'))
                        if timestamp>fetched or fetched-timestamp>timedelta(minutes=95):continue
                        outcomes=market.get('outcomes',[])
                        if len(outcomes)!=2:continue
                        sides={row.get('name'):row for row in outcomes}
                        if len(sides)!=2:continue
                        names=(event['home_team'],event['away_team']) if kind=='spreads' else ('Over','Under')
                        first,second=sides[names[0]],sides[names[1]]
                        p1,p2=first['price'],second['price']
                        if not all(isinstance(v,int) and not isinstance(v,bool) and abs(v)>=100 for v in (p1,p2)):continue
                        x,y=float(first['point']),float(second['point'])
                        if not math.isfinite(x) or not math.isfinite(y):continue
                        if (kind=='spreads' and abs(x+y)>1e-7) or (kind=='totals' and (abs(x-y)>1e-7 or x<=0)):continue
                        rows.append({'game_id':game_id(league,start.astimezone(ET).date(),away,home),
                                     'provider':'the_odds_api','book':name,'market':kind,'home':home,'away':away,
                                     'point':x,'first_price':p1,'second_price':p2,'as_of':timestamp.isoformat(),
                                     'fetched_at':fetched.isoformat(),'starts_at':start.isoformat()})
                    except (KeyError,TypeError,ValueError,OverflowError):continue
        except (KeyError,TypeError,ValueError,OverflowError):continue
    return rows


def archive_market_snapshots(root,rows):
    if not root:return 0
    by_day={}
    for row in rows:
        try:
            if not aware(row['as_of'])<=aware(row['fetched_at'])<aware(row['starts_at']):continue
            day=aware(row['fetched_at']).date().isoformat();by_day.setdefault(day,[]).append(row)
        except (KeyError,TypeError,ValueError):continue
    added=0
    for day,items in by_day.items():
        path=Path(root)/'observations'/'cross_market'/(day+'.sqlite');path.parent.mkdir(parents=True,exist_ok=True)
        with closing(sqlite3.connect(path)) as db, db:
            db.executescript(SCHEMA)
            for row in items:
                values=[row[k] for k in ('game_id','provider','book','market','home','away','point','first_price','second_price','as_of','fetched_at','starts_at')]
                key=hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()
                added+=db.execute('INSERT OR IGNORE INTO market_quotes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',[key]+values).rowcount
    return added


def fit_margin_distribution(rows,cutoff,league,min_games=500,min_seasons=2):
    """Build an unpromoted empirical residual distribution from past-only rows.

    Each row must carry a captured pregame spread/total and a separately observed
    final. Retrospective untimestamped rows are ineligible. NFL ties are retained.
    """
    now=aware(cutoff);eligible=[];seen=set()
    for row in rows:
        try:
            captured,start,settled=(aware(row[k]) for k in ('captured_at','starts_at','settled_at'))
            if row.get('league')!=league or not aware(row['source_as_of'])<=captured<start<=settled<now:continue
            if row.get('game_id') in seen or row.get('rights_verified') is not True:continue
            values=[float(row[k]) for k in ('home_spread','total','home_score','away_score')]
            if any(not math.isfinite(v) for v in values) or values[1]<=0:continue
            spread,total,hs,away=values
            if league=='NBA' and hs==away:continue
            seen.add(row['game_id']);eligible.append({'residual':hs-away+spread,'total':total,'season':str(row['season'])})
        except (KeyError,TypeError,ValueError):continue
    if len(eligible)<min_games or len({x['season'] for x in eligible})<min_seasons:return None
    return {'league':league,'trained_before':now.isoformat(),'games':len(eligible),'seasons':sorted({x['season'] for x in eligible}),
            'residuals':eligible,'status':'shadow_unvalidated','promoted':False}


def spread_to_win_prob(fit,spread,total,as_of,bandwidth=12):
    """Conditional home-win probability from weighted, discrete margins.

    Retaining discrete margins preserves NFL scoring key numbers without an
    assumed normal distribution. Fixed bandwidth is a shadow-only placeholder.
    """
    if not fit or fit.get('promoted') is not False:return None
    try:
        if aware(fit['trained_before'])>=aware(as_of):return None
        spread,total,bandwidth=float(spread),float(total),float(bandwidth)
        if any(not math.isfinite(x) for x in (spread,total,bandwidth)) or total<=0 or bandwidth<=0:return None
        weights=[math.exp(-.5*((r['total']-total)/bandwidth)**2) for r in fit['residuals']]
        denom=sum(w for r,w in zip(fit['residuals'],weights) if abs(r['residual']-spread)>1e-9)
        if denom<=0:return None
        win=sum(w for r,w in zip(fit['residuals'],weights) if r['residual']>spread)
        return {'home_probability':win/denom,'training_games':fit['games'],
                'status':'shadow_unvalidated','bandwidth':bandwidth}
    except (KeyError,TypeError,ValueError,OverflowError):return None


def cross_market_gap(moneyline_quote,spread_quote,estimate,now,start,threshold=None):
    """Compare aligned same-book snapshots, never create a wager signal."""
    try:
        current,starts=aware(now),aware(start)
        if not estimate or estimate.get('status')!='shadow_unvalidated':return None
        if (moneyline_quote['game_id'],moneyline_quote['book'])!=(spread_quote['game_id'],spread_quote['book']):return None
        for quote in (moneyline_quote,spread_quote):
            source,observed=aware(quote['as_of']),aware(quote['fetched_at'])
            if not source<=observed<=current<starts or current-source>timedelta(minutes=95):return None
        fair=devig([implied_american(moneyline_quote['home_odds']),implied_american(moneyline_quote['away_odds'])])[0]
        gap=estimate['home_probability']-fair
        # A threshold is only a user-supplied research parameter, not a vetted rule.
        flag=abs(gap)>threshold if isinstance(threshold,(int,float)) and threshold>=0 else None
        return {'difference':gap,'threshold_exceeded':flag,'status':'shadow_unvalidated','betting_signal':False}
    except (KeyError,TypeError,ValueError):return None
