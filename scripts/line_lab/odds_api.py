"""Optional, quota-limited The Odds API adapter; never log request URLs/keys."""
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .constants import BOOKS, ET, game_id, team_code
from .history import aware
from .cross_market import parse_featured_markets, archive_market_snapshots

SPORTS={'NBA':'basketball_nba','NFL':'americanfootball_nfl'}
BOOK_NAMES=dict(BOOKS)
BOOK_NAMES['williamhill_us']='Caesars'
QUOTA_SCHEMA='''
CREATE TABLE IF NOT EXISTS calls (
  id INTEGER PRIMARY KEY, league TEXT NOT NULL, attempted_at TEXT NOT NULL,
  status TEXT NOT NULL, remaining INTEGER, used INTEGER, cost INTEGER
);
'''

def parse_odds_api(payload, league, fetched_at):
    events=[]
    if not isinstance(payload,list): raise ValueError('odds response is not a list')
    for event in payload:
        try:
            home=team_code(event['home_team'],league); away=team_code(event['away_team'],league)
            start=aware(event['commence_time'])
            if not home or not away or home==away: continue
            for book in event.get('bookmakers',[]):
                name=BOOK_NAMES.get(book.get('key'))
                if not name: continue
                for market in book.get('markets',[]):
                    if market.get('key')!='h2h': continue
                    outcomes=market.get('outcomes',[])
                    if len(outcomes)!=2: continue
                    prices={o.get('name'):o.get('price') for o in outcomes}
                    if len(prices)!=2 or event['home_team'] not in prices or event['away_team'] not in prices: continue
                    source_time=market.get('last_update') or book.get('last_update')
                    if not source_time: continue
                    events.append({'id':game_id(league,start.astimezone(ET).date(),away,home),'provider':'the_odds_api',
                                   'provider_event_id':str(event['id']),'league':league,'home':home,'away':away,
                                   'home_name':event['home_team'],'away_name':event['away_team'],'starts_at':start.isoformat(),
                                   'book':name,'home_odds':prices[event['home_team']],'away_odds':prices[event['away_team']],
                                   'as_of':aware(source_time).isoformat(),'fetched_at':aware(fetched_at).isoformat()})
        except (KeyError,TypeError,ValueError,OverflowError): continue
    return events

def _db(root):
    path=Path(root)/'observations'/'api_quota.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path);db.executescript(QUOTA_SCHEMA);return db

def should_call(root,league,now,interval=timedelta(hours=6),monthly_limit=240,reserve=60,next_cost=1):
    now=aware(now);month=now.strftime('%Y-%m-01T00:00:00+00:00')
    with closing(_db(root)) as db:
        last=db.execute('SELECT attempted_at FROM calls WHERE league=? ORDER BY attempted_at DESC,id DESC LIMIT 1',(league,)).fetchone()
        count=db.execute('SELECT COALESCE(SUM(COALESCE(cost,1)),0) FROM calls WHERE attempted_at>=?',(month,)).fetchone()[0]
        remaining=db.execute('SELECT remaining FROM calls WHERE remaining IS NOT NULL ORDER BY attempted_at DESC,id DESC LIMIT 1').fetchone()
    if last and now-aware(last[0])<interval: return False
    if count+next_cost>monthly_limit: return False
    # A previous month's remaining count may be zero; permit a new month to
    # discover whether the provider reset it, but still observe the hard cap.
    if remaining and remaining[0]-next_cost<reserve:
        with closing(_db(root)) as db:
            in_month=db.execute('SELECT COUNT(*) FROM calls WHERE attempted_at>=? AND remaining IS NOT NULL',(month,)).fetchone()[0]
        if in_month: return False
    return True

def record_call(root,league,when,status,remaining=None,used=None,cost=None):
    with closing(_db(root)) as db, db:
        db.execute('INSERT INTO calls(league,attempted_at,status,remaining,used,cost) VALUES (?,?,?,?,?,?)',
                   (league,aware(when).isoformat(),status,remaining,used,cost))

def _int_header(headers,key):
    try: return int(headers.get(key))
    except (TypeError,ValueError): return None

def collect_odds_api(root,key,now,featured=False):
    if not key: return [],['The Odds API is disabled: missing API key']
    output=[]; warnings=[]
    for league,sport in SPORTS.items():
        cost=3 if featured else 1
        interval=timedelta(hours=12 if featured else 6)
        budget=360 if featured else 240
        if not should_call(root,league,now,interval=interval,monthly_limit=budget,next_cost=cost): continue
        params=urlencode({'apiKey':key,'regions':'us','markets':'h2h,spreads,totals' if featured else 'h2h','oddsFormat':'american'})
        url=f'https://api.the-odds-api.com/v4/sports/{sport}/odds/?{params}'
        try:
            request=Request(url,headers={'User-Agent':'MoneylineResearch/1.0','Accept':'application/json'})
            with urlopen(request,timeout=20) as response:
                payload=json.loads(response.read().decode('utf-8'))
                headers=response.headers
                fetched=datetime.now(timezone.utc).isoformat()
                reported_cost=_int_header(headers,'x-requests-last')
                record_call(root,league,fetched,'ok',_int_header(headers,'x-requests-remaining'),_int_header(headers,'x-requests-used'),cost if reported_cost is None else reported_cost)
                output.extend(parse_odds_api(payload,league,fetched))
                if featured:
                    try:
                        rows=parse_featured_markets(payload,league,fetched,BOOK_NAMES)
                        archive_market_snapshots(root,rows)
                    except Exception as exc:
                        warnings.append(f'{league} spread/total archive unavailable ({type(exc).__name__})')
        except Exception as exc:
            # Exception text can contain a URL with the key: never print it.
            fetched=datetime.now(timezone.utc).isoformat()
            record_call(root,league,fetched,'error',cost=cost)
            warnings.append(f'The Odds API {league} unavailable ({type(exc).__name__})')
    return output,warnings
