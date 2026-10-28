#!/usr/bin/env python3
"""Experimental, point-in-time moneyline predictions and an immutable pick ledger."""
from __future__ import annotations
import csv, io, json, math, re, sys
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from statistics import median
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.refresh_feed import parse_referees, NBA_REFS
ET = ZoneInfo('America/New_York')
BOOKS = [('fanduel','FanDuel'),('draftkings','DraftKings'),('betmgm','BetMGM'),('caesars','Caesars'),('fanatics','Fanatics'),('betrivers','BetRivers')]
NBA_SEASONS = ['2022-23','2023-24','2024-25','2025-26','2026-27']
NBA_TEAMS = {
 'atlanta hawks':'ATL','boston celtics':'BOS','brooklyn nets':'BKN','charlotte hornets':'CHA','chicago bulls':'CHI','cleveland cavaliers':'CLE','dallas mavericks':'DAL','denver nuggets':'DEN','detroit pistons':'DET','golden state warriors':'GSW','houston rockets':'HOU','indiana pacers':'IND','la clippers':'LAC','los angeles clippers':'LAC','los angeles lakers':'LAL','l.a. lakers':'LAL','memphis grizzlies':'MEM','miami heat':'MIA','milwaukee bucks':'MIL','minnesota timberwolves':'MIN','new orleans pelicans':'NOP','new york knicks':'NYK','oklahoma city thunder':'OKC','orlando magic':'ORL','philadelphia 76ers':'PHI','phoenix suns':'PHX','portland trail blazers':'POR','sacramento kings':'SAC','san antonio spurs':'SAS','toronto raptors':'TOR','utah jazz':'UTA','washington wizards':'WAS'}
NFL_TEAMS = {
 'arizona cardinals':'ARI','atlanta falcons':'ATL','baltimore ravens':'BAL','buffalo bills':'BUF','carolina panthers':'CAR','chicago bears':'CHI','cincinnati bengals':'CIN','cleveland browns':'CLE','dallas cowboys':'DAL','denver broncos':'DEN','detroit lions':'DET','green bay packers':'GB','houston texans':'HOU','indianapolis colts':'IND','jacksonville jaguars':'JAX','kansas city chiefs':'KC','las vegas raiders':'LV','los angeles chargers':'LAC','los angeles rams':'LA','miami dolphins':'MIA','minnesota vikings':'MIN','new england patriots':'NE','new orleans saints':'NO','new york giants':'NYG','new york jets':'NYJ','philadelphia eagles':'PHI','pittsburgh steelers':'PIT','san francisco 49ers':'SF','seattle seahawks':'SEA','tampa bay buccaneers':'TB','tennessee titans':'TEN','washington commanders':'WAS'}
ALIASES={'OAK':'LV','SD':'LAC','STL':'LA','LAR':'LA','JAC':'JAX','PHO':'PHX','NOH':'NOP','NJN':'BKN','CHO':'CHA'}

def team_code(name, league):
    name = ' '.join(str(name).strip().lower().split())
    return (NBA_TEAMS if league == 'NBA' else NFL_TEAMS).get(name)
def normalize_code(code): return ALIASES.get(code,code)
def game_id(league, game_date, away, home): return f'{league.lower()}:{game_date}:{normalize_code(away)}:{normalize_code(home)}'

def get(url, timeout=25):
    request=Request(url,headers={'User-Agent':'LineLab/1.0 (+sports research)','Accept':'application/json,text/csv,text/html'})
    with urlopen(request,timeout=timeout) as r: return r.read().decode('utf-8','replace')

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

def elo_probability(diff): return 1/(1+10**(-max(-1200,min(1200,diff))/400))

def build_ratings(games, cutoff, league, params=None, validation_season=None):
    # Training ends before today's ET date. This avoids training on later same-day results.
    ratings={}; last={}; last_season=None; validation_errors=[]
    k,home_advantage,rest_weight=params or ((20,55,0) if league=='NBA' else (24,42,0))
    for g in sorted((x for x in games if x['league']==league and x['date']<cutoff),key=lambda x:(x['date'],x['id'])):
        if last_season is not None and g['season']!=last_season:
            ratings={team:1500+(value-1500)*0.75 for team,value in ratings.items()}
        last_season=g['season']
        h,a=g['home'],g['away']; hr=ratings.get(h,1500); ar=ratings.get(a,1500)
        rh=min(7,max(0,(g['date']-last[h]).days-1)) if h in last else 3
        ra=min(7,max(0,(g['date']-last[a]).days-1)) if a in last else 3
        p=elo_probability(hr-ar+(0 if g['neutral'] else home_advantage)+rest_weight*(rh-ra))
        outcome=1 if g['home_score']>g['away_score'] else 0 if g['home_score']<g['away_score'] else 0.5
        if g['season']==validation_season and outcome!=0.5: validation_errors.append((p-outcome)**2)
        ratings[h]=hr+k*(outcome-p); ratings[a]=ar-k*(outcome-p)
        last[h]=g['date']; last[a]=g['date']
    return {'ratings':ratings,'last':last,'home_advantage':home_advantage,'rest_weight':rest_weight,'k':k,'validation_count':len(validation_errors),'validation_brier':sum(validation_errors)/len(validation_errors) if validation_errors else None}

def train_model(games,cutoff,league):
    # Select among small, fixed alternatives on the latest completed season using
    # chronological pre-game predictions. This is tuning, not an independent test
    # or evidence of profit. Prefer the baseline for marginal changes.
    count={}
    for g in games:
        if g['league']==league and g['date']<cutoff and g['home_score']!=g['away_score']:
            count[g['season']]=count.get(g['season'],0)+1
    minimum=1000 if league=='NBA' else 200
    completed=sorted(s for s,n in count.items() if n>=minimum)
    if league=='NBA': candidates=[(20,55,0),(20,55,8),(20,40,0),(20,70,0),(15,55,0),(25,55,0)]
    else: candidates=[(24,42,0),(24,42,4),(24,25,0),(24,55,0),(18,42,0),(30,42,0)]
    if not completed: return build_ratings(games,cutoff,league,candidates[0])
    val=completed[-1]
    fitted=[build_ratings(games,cutoff,league,c,val) for c in candidates]
    baseline=fitted[0]; best=min(fitted,key=lambda x:x['validation_brier'] if x['validation_brier'] is not None else float('inf'))
    winner=best if best['validation_count']>=minimum and baseline['validation_brier']-best['validation_brier']>=0.0005 else baseline
    winner['validation_season']=val
    return winner

def project_home(model, home, away, when, neutral=False):
    ratings=model['ratings']; last=model['last']
    if home not in ratings or away not in ratings: return None
    day=when.astimezone(ET).date()
    rh=min(7,max(0,(day-last[home]).days-1)) if home in last else 3
    ra=min(7,max(0,(day-last[away]).days-1)) if away in last else 3
    return elo_probability(ratings[home]-ratings[away]+(0 if neutral else model['home_advantage'])+model['rest_weight']*(rh-ra))

def implied(odds): return -odds/(-odds+100) if odds<0 else 100/(odds+100)

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
            start=datetime.fromisoformat(e['date'].replace('Z','+00:00')).astimezone(ET).date()
            finals.append({'id':game_id(league,start,ac,hc),'home':hc,'away':ac,'home_score':int(h['score']),'away_score':int(a['score'])})
        except (KeyError,IndexError,TypeError,ValueError): continue
    return finals

def parse_espn_starts(payload,league):
    starts={}
    for e in payload.get('events',[]):
        try:
            comp=e['competitions'][0]; sides={x['homeAway']:x for x in comp['competitors']}
            h=team_code(sides['home']['team']['displayName'],league); a=team_code(sides['away']['team']['displayName'],league)
            start=datetime.fromisoformat(e['date'].replace('Z','+00:00'))
            if h and a: starts[game_id(league,start.astimezone(ET).date(),a,h)]=start.astimezone(timezone.utc).isoformat()
        except (KeyError,IndexError,TypeError,ValueError): continue
    return starts

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

def build_market(events,now):
    merged={}
    for x in events:
        asof=datetime.fromisoformat(x['as_of']); start=datetime.fromisoformat(x['starts_at'])
        if now-asof>timedelta(minutes=95) or start<=now+timedelta(minutes=20): continue
        rec=merged.setdefault(x['id'],{k:x[k] for k in ('id','league','home','away','home_name','away_name','starts_at')})
        rec.setdefault('books',{})[x['book']]={'home':x['home_odds'],'away':x['away_odds'],'as_of':x['as_of']}
    return merged

def choose_candidates(markets,models,now,ledger):
    existing={p['id'] for p in ledger}; today=now.astimezone(ET).date().isoformat()
    already=sum(p.get('pick_day')==today for p in ledger)
    results=[]
    for event in markets.values():
        start=datetime.fromisoformat(event['starts_at'])
        if start.astimezone(ET).date().isoformat()!=today or start<=now+timedelta(minutes=20) or event['id'] in existing or len(event['books'])<3: continue
        elo=project_home(models[event['league']],event['home'],event['away'],start,event.get('neutral',False))
        if elo is None: continue
        fair=[implied(b['home'])/(implied(b['home'])+implied(b['away'])) for b in event['books'].values()]
        market=median(fair); p_home=.75*market+.25*elo
        for side,p in [('home',p_home),('away',1-p_home)]:
            best=max(v[side] for v in event['books'].values())
            edge=p-implied(best)
            if edge>=.01:
                results.append({'id':event['id'],'league':event['league'],'team_code':event[side], 'team':event[side+'_name'],'opponent':event[('away' if side=='home' else 'home')+'_name'],'starts_at':event['starts_at'],'probability':round(p,5),'predicted_at':now.isoformat(),'pick_day':today,'initial_best_odds':best,'edge':edge,'outcome':'pending','model':'elo-market-v1'})
    results.sort(key=lambda x:x['edge'],reverse=True)
    chosen=[]; used=set()
    for x in results:
        if x['id'] in used: continue
        chosen.append(x); used.add(x['id'])
        if len(chosen)>=max(0,3-already): break
    return chosen if already<3 else []

def render_board(markets,ledger,now,errors):
    today=now.astimezone(ET).date().isoformat()
    active=[]
    for pick in ledger:
        if pick.get('pick_day')!=today or pick.get('outcome')!='pending': continue
        event=markets.get(pick['id'])
        if not event or datetime.fromisoformat(event['starts_at'])<=now: continue
        side='home' if pick['team_code']==event['home'] else 'away'
        books=[{'name':name,'odds':event['books'][name][side] if name in event['books'] else None,'as_of':event['books'][name]['as_of'] if name in event['books'] else None} for _,name in BOOKS]
        available=[b['odds'] for b in books if b['odds'] is not None]
        if not available: continue
        best=max(available)
        active.append({'team':pick['team'],'opponent':pick['opponent'],'league':pick['league'],'starts_at':pick['starts_at'],'probability':pick['probability'],'books':books,'best':best,'predicted_at':pick['predicted_at']})
    wins=sum(p.get('outcome')=='win' for p in ledger); losses=sum(p.get('outcome')=='loss' for p in ledger); voids=sum(p.get('outcome')=='void' for p in ledger); pending=sum(p.get('outcome')=='pending' for p in ledger)
    return {'generated_at':now.isoformat(),'model':'Experimental Elo + market baseline','source':'AgentBets odds snapshots; BoxScore Lab NBA results; nflverse NFL schedules and results; ESPN final scores','accuracy':{'wins':wins,'losses':losses,'voids':voids,'pending':pending,'percent':round(100*wins/(wins+losses),1) if wins+losses else None},'picks':active,'errors':errors}

def main():
    now=datetime.now(timezone.utc); today=now.astimezone(ET).date(); errors=[]; games=[]; nfl_locations={}
    for season in NBA_SEASONS:
        try:
            result=parse_nba_csv(get(f'https://boxscorelab.com/downloads/{season}-team-game-results.csv'))
            if not result: raise ValueError('empty NBA season')
            games.extend(result)
        except Exception as e: errors.append('NBA historical data unavailable: '+season+' ('+type(e).__name__+')')
    try:
        nfl_csv=get('https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv')
        nfl=parse_nfl_csv(nfl_csv); nfl_locations=parse_nfl_locations(nfl_csv)
        if not nfl: raise ValueError('empty NFL data')
        games.extend(nfl)
    except Exception as e: errors.append('NFL historical data unavailable ('+type(e).__name__+')')
    models={league:train_model(games,today,league) for league in ('NBA','NFL')}
    raw=[]
    for slug,name in BOOKS:
        for league in ('NBA','NFL'):
            try:
                rows,asof=parse_book_html(get(f'https://agentbets.ai/odds/{slug}/{league.lower()}'),name,league,now)
                raw.extend(rows)
            except Exception as e: errors.append(f'{name} {league} odds unavailable ({type(e).__name__})')
    data_dir=ROOT/'data'; data_dir.mkdir(exist_ok=True)
    ledger_path=data_dir/'predictions.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    refs_path=data_dir/'referee_history.json'
    refs=json.loads(refs_path.read_text()) if refs_path.exists() else []
    try:
        ref_report=parse_referees(get(NBA_REFS),today)
        print('NBA referees:',ref_report['status'],'new/changed:',append_referee_assignments(refs,ref_report,now))
    except Exception as e:
        print('NBA referee source unavailable:',type(e).__name__)
    refs_path.write_text(json.dumps(refs,indent=2)+'\n')
    finals=[{'id':g['id'],'home':g['home'],'away':g['away'],'home_score':g['home_score'],'away_score':g['away_score']} for g in games if g['date']<=today]
    espn_starts={}
    for league,sport in [('NBA','basketball/nba'),('NFL','football/nfl')]:
        for days_ago in range(0,4):
            day=(today-timedelta(days=days_ago)).strftime('%Y%m%d')
            try:
                payload=json.loads(get(f'https://site.api.espn.com/apis/site/v2/sports/{sport}/scoreboard?dates={day}',10))
                finals.extend(parse_espn_results(payload,league)); espn_starts.update(parse_espn_starts(payload,league))
            except Exception as e: errors.append(f'{league} scores {day} unavailable ({type(e).__name__})')
    grade_ledger(ledger,finals,now)
    markets=build_market(raw,now)
    for event in markets.values():
        if event['league']=='NFL' and event['id'] in nfl_locations: event['neutral']=nfl_locations[event['id']]
        if event['id'] in espn_starts:
            event['starts_at']=min(event['starts_at'],espn_starts[event['id']])
    # If a league's training history is missing, do not produce predictions for it.
    blocked={('NBA' if x.startswith('NBA historical') else 'NFL') for x in errors if x.startswith(('NBA historical','NFL historical'))}
    permitted={k:v for k,v in markets.items() if v['league'] not in blocked and (v['league']!='NFL' or 'neutral' in v)}
    print('Training games:', len([x for x in games if x['league']=='NBA']), 'NBA;', len([x for x in games if x['league']=='NFL']), 'NFL. Fresh matchups:', len(markets))
    for league,model in models.items(): print('MODEL',league,'validation',model.get('validation_season'),'games',model.get('validation_count'),'brier',model.get('validation_brier'),'params',model['k'],model['home_advantage'],model['rest_weight'])
    for event in permitted.values():
        start=datetime.fromisoformat(event['starts_at'])
        if start.astimezone(ET).date()!=today or len(event['books'])<3: continue
        estimate=project_home(models[event['league']],event['home'],event['away'],start,event.get('neutral',False))
        if estimate is None: continue
        fair=median([implied(b['home'])/(implied(b['home'])+implied(b['away'])) for b in event['books'].values()])
        homep=.75*fair+.25*estimate
        print('TODAY', event['league'],event['away'],'at',event['home'],'model home',round(100*homep,1),'best home',max(v['home'] for v in event['books'].values()),'best away',max(v['away'] for v in event['books'].values()))
    ledger.extend(choose_candidates(permitted,models,now,ledger))
    ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
    board=render_board(markets,ledger,now,errors)
    (ROOT/'dist'/'board.json').write_text(json.dumps(board,indent=2)+'\n')
    print('Board:',len(board['picks']),'active picks;',board['accuracy']['wins'],'wins;',board['accuracy']['losses'],'losses;',len(errors),'source warnings')
    for e in errors: print('SOURCE:',e)
    if not raw: print('No odds sources reachable; board intentionally has no active picks.')

if __name__=='__main__': main()
