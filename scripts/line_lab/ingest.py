"""Ingest components for the picks pipeline."""
import csv, io, json, re, time
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from .constants import *


def get(url, timeout=25):
    request=Request(url,headers={'User-Agent':'LineLab/1.0 (+sports research)','Accept':'application/json,text/csv,text/html'})
    # Only retry this public-data adapter. The metered Odds API uses a separate
    # client and is never retried here, preserving its request budget.
    for attempt in range(3):
        try:
            with urlopen(request,timeout=timeout) as r:return r.read().decode('utf-8','replace')
        except HTTPError as exc:
            if attempt==2 or not (exc.code==429 or 500<=exc.code<600):raise
        except (URLError,TimeoutError):
            if attempt==2:raise
        time.sleep(.2*(2**attempt))

class Tables(HTMLParser):
    def __init__(self):
        super().__init__(); self.tables=[]; self.table=None; self.row=None; self.cell=None; self.text=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'table' and self.table is None: self.table=[]
        elif tag == 'tr' and self.table is not None: self.row=[]
        elif tag in ('th','td') and self.row is not None: self.cell=[]
    def handle_data(self, data):
        self.text.append(data)
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag):
        if tag in ('th','td') and self.cell is not None and self.row is not None:
            self.row.append(' '.join(''.join(self.cell).split())); self.cell=None
        elif tag == 'tr' and self.row is not None and self.table is not None:
            if self.row: self.table.append(self.row)
            self.row=None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table); self.table=None

def parse_american(s):
    m=re.match(r'^\s*([+-]\d+)',str(s))
    return int(m.group(1)) if m and abs(int(m.group(1)))>=100 else None

def parse_book_html(html, book, league, now):
    p=Tables(); p.feed(html); text=' '.join(' '.join(p.text).split())
    m=re.search(r'Last updated:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4}\s+at\s+\d{1,2}:\d{2}\s*[AP]M\s+UTC)',text,re.I)
    if not m: raise ValueError('No source timestamp')
    asof=datetime.strptime(m.group(1),'%B %d, %Y at %I:%M %p UTC').replace(tzinfo=timezone.utc)
    if asof > now+timedelta(minutes=5): raise ValueError('Source timestamp is in the future')
    matching=[t for t in p.tables if t and len(t[0])>=4 and 'Matchup' in t[0][0] and t[0][2]=='Away ML' and t[0][3]=='Home ML']
    if not matching: raise ValueError('No odds table')
    events=[]
    for row in matching[0][1:]:
        if len(row)<4 or ' @ ' not in row[0]: continue
        away_name,home_name=row[0].split(' @ ',1)
        away=team_code(away_name,league); home=team_code(home_name,league)
        away_price=parse_american(row[2]); home_price=parse_american(row[3])
        if not all([away,home,away_price,home_price]): continue
        clean=re.sub(r'\s+(EDT|EST)$','',row[1])
        try: starts=datetime.strptime(f'{clean} {now.astimezone(ET).year}','%b %d, %I:%M %p %Y').replace(tzinfo=ET)
        except ValueError: continue
        # Avoid year boundary errors when December pages contain early January games.
        if starts < now.astimezone(ET)-timedelta(days=180): starts=starts.replace(year=starts.year+1)
        events.append({'id':game_id(league,starts.date(),away,home),'league':league,'home':home,'away':away,'home_name':home_name,'away_name':away_name,'starts_at':starts.astimezone(timezone.utc).isoformat(),'book':book,'home_odds':home_price,'away_odds':away_price,'as_of':asof.isoformat()})
    return events,asof

def parse_nba_csv(text):
    games=[]
    for row in csv.DictReader(io.StringIO(text)):
        if row.get('home','').lower()!='true': continue
        try:
            day=date.fromisoformat(row['game_date']); home=normalize_code(row['team']); away=normalize_code(row['opponent'])
            hs=int(row['points']); away_score=int(row['opponent_points'])
            if home==away or hs==away_score: continue
            games.append({'id':game_id('NBA',day,away,home),'date':day,'home':home,'away':away,'home_score':hs,'away_score':away_score,'season':row['season'],'league':'NBA','neutral':False})
        except (KeyError,TypeError,ValueError): continue
    return games

def parse_nfl_csv(text):
    games=[]
    for row in csv.DictReader(io.StringIO(text)):
        try:
            if int(row['season'])<2010 or row['game_type'] not in ('REG','WC','DIV','CON','SB'): continue
            day=date.fromisoformat(row['gameday']); home=normalize_code(row['home_team']); away=normalize_code(row['away_team'])
            hs=int(row['home_score']); away_score=int(row['away_score'])
            games.append({'id':game_id('NFL',day,away,home),'date':day,'home':home,'away':away,'home_score':hs,'away_score':away_score,'season':row['season'],'league':'NFL','neutral':row.get('location','').lower()=='neutral'})
        except (KeyError,TypeError,ValueError): continue
    return games

def parse_nfl_locations(text):
    locations={}
    for row in csv.DictReader(io.StringIO(text)):
        try:
            day=date.fromisoformat(row['gameday']); h=normalize_code(row['home_team']); a=normalize_code(row['away_team'])
            venue=row.get('location','').strip().lower()
            if venue in ('home','neutral'): locations[game_id('NFL',day,a,h)] = venue=='neutral'
        except (KeyError,TypeError,ValueError): continue
    return locations

def parse_espn_results(payload,league):
    finals=[]
    for e in payload.get('events',[]):
        try:
            comp=e['competitions'][0]; status=comp.get('status',{}).get('type',{})
            if not status.get('completed',False) or status.get('name') != 'STATUS_FINAL': continue
            sides={x['homeAway']:x for x in comp['competitors']}
            h,a=sides['home'],sides['away']; hc=team_code(h['team']['displayName'],league); ac=team_code(a['team']['displayName'],league)
            if not hc or not ac: continue
            # Provider UTC dates may cross midnight: prefer its local game date when available.
            start=datetime.fromisoformat(e['date'].replace('Z','+00:00'))
            day=start.astimezone(ET).date()
            season=e.get('season',{})
            finals.append({'id':game_id(league,day,ac,hc),'league':league,'date':day,'starts_at':start,
                           'season_year':season.get('year'),'season_type':season.get('type'),
                           'home':hc,'away':ac,'home_score':int(h['score']),'away_score':int(a['score']),'source':'ESPN final'})
        except (KeyError,IndexError,TypeError,ValueError): continue
    return finals


def qualify_final_results(supplemental,explicit_finals,now):
    """Require explicit final status; quarantine contradictory source scores.

    Score-bearing historical tables may be updated while a game is in progress.
    They cannot establish that a game has ended. Matching supplemental scores
    are retained as source confirmations, never as independent proof of finality.
    """
    grouped={};other={};conflicts=set()
    def identity(row):
        home,away=row['home'],row['away'];scores=(row['home_score'],row['away_score'])
        if not home or not away or home==away or any(not isinstance(v,int) or isinstance(v,bool) or v<0 for v in scores):
            raise ValueError('invalid game score')
        return (home,away,*scores)
    for row in supplemental:
        try:other.setdefault(row['id'],[]).append((identity(row),row))
        except (KeyError,TypeError,ValueError):continue
    for row in explicit_finals:
        try:
            start=row['starts_at']
            if not isinstance(start,datetime) or start.tzinfo is None or start.utcoffset() is None or start>now:continue
            grouped.setdefault(row['id'],[]).append((identity(row),row))
        except (KeyError,TypeError,ValueError):continue
    verified=[];corroborating=[]
    for game,values in grouped.items():
        identities={value for value,_ in values}
        if len(identities)!=1 or any(value not in identities for value,_ in other.get(game,[])):
            conflicts.add(game);continue
        verified.append(values[0][1])
        seen=set()
        for _,row in other.get(game,[]):
            source=row.get('source')
            if source not in seen:corroborating.append(row);seen.add(source)
    return verified+corroborating,verified,sorted(conflicts)

def parse_espn_starts(payload,league):
    starts={}
    for e in payload.get('events',[]):
        try:
            comp=e['competitions'][0]; sides={x['homeAway']:x for x in comp['competitors']}
            status=comp.get('status',e.get('status',{})).get('type',{}).get('name','')
            if status in ('STATUS_POSTPONED','STATUS_CANCELED','STATUS_CANCELLED','STATUS_ABANDONED','STATUS_DELAYED'): continue
            h=team_code(sides['home']['team']['displayName'],league); a=team_code(sides['away']['team']['displayName'],league)
            start=datetime.fromisoformat(e['date'].replace('Z','+00:00'))
            if h and a: starts[game_id(league,start.astimezone(ET).date(),a,h)]=start.astimezone(timezone.utc).isoformat()
        except (KeyError,IndexError,TypeError,ValueError): continue
    return starts
