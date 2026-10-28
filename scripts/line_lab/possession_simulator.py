"""Independent, retrospective scoring-process challenger; never a live pick source.

NBA possessions are estimated from box-score events, not reconstructed play-by-play.
NFL offensive drive outcomes are observed from nflverse play-by-play score deltas.
Only earlier completed games can contribute to any forecast. Neither model uses
future injuries, lineup reports, RotoBot content, bookmaker odds, or game scores.
"""
import csv
import io
import math
import random
from collections import defaultdict
from datetime import date
from hashlib import sha256
from statistics import median

from .constants import normalize_code, game_id

NBA_EVENTS = (0, 1, 2, 3)
NFL_EVENTS = (0, 2, 3, 6, 7, 8)


def nba_observations(text):
    """Pair verified home/away rows and derive estimated possessions and events."""
    groups = defaultdict(dict)
    required = {'game_date','season','team','opponent','home','points',
                'field_goals_made','field_goal_attempts','three_point_makes',
                'free_throws_made','free_throw_attempts','offensive_rebounds','turnovers'}
    reader = csv.DictReader(io.StringIO(text))
    if not required <= set(reader.fieldnames or []):
        raise ValueError('NBA source lacks required box-score columns')
    for row in reader:
        try:
            day = date.fromisoformat(row['game_date'])
            team, opponent = normalize_code(row['team']), normalize_code(row['opponent'])
            home = row['home'].lower() == 'true'
            if row['home'].lower() not in ('true','false') or team == opponent: continue
            fg, fga, threes, ft, fta, orb, tov, pts = (
                int(row[k]) for k in ('field_goals_made','field_goal_attempts',
                'three_point_makes','free_throws_made','free_throw_attempts',
                'offensive_rebounds','turnovers','points'))
            possessions = fga - orb + tov + .44 * fta
            if not (0 <= threes <= fg <= fga and 0 <= ft <= fta and
                    all(x >= 0 for x in (orb,tov,pts)) and 60 <= possessions <= 140 and
                    pts == 2 * fg + threes + ft): continue
            # One-point events are a box-score abstraction, not literal NBA possessions.
            events = {1:ft,2:fg-threes,3:threes}
            events[0] = round(possessions) - sum(events.values())
            if events[0] < 0: continue
            key = (row['season'],day,frozenset((team,opponent)))
            if team in groups[key]: raise ValueError('duplicate NBA team game')
            groups[key][team] = {'team':team,'opponent':opponent,'home':home,
                                  'possessions':possessions,'events':events,'points':pts}
        except (KeyError,TypeError,ValueError): continue
    results=[]
    for (season,day,_),sides in groups.items():
        if len(sides)!=2: continue
        hs=[r for r in sides.values() if r['home']]
        if len(hs)!=1: continue
        h=hs[0]; a=sides[h['opponent']]
        if a['home'] or a['opponent']!=h['team'] or h['points']==a['points']: continue
        results.append({'id':game_id('NBA',day,a['team'],h['team']), 'league':'NBA',
                        'season':season,'date':day,'home':h['team'],'away':a['team'],
                        'home_score':h['points'],'away_score':a['points'],
                        'counts':(round(h['possessions']),round(a['possessions'])),
                        'events':(h['events'],a['events']),'neutral':False})
    return results


def nfl_drive_observations(text):
    """Extract offensive points on fixed drives; reject unverified/malformed rows."""
    reader=csv.DictReader(io.StringIO(text))
    fields={'game_id','game_date','home_team','away_team','fixed_drive','posteam',
            'posteam_score','posteam_score_post','play_id','season','play_deleted'}
    if not fields <= set(reader.fieldnames or []):
        raise ValueError('NFL source lacks drive and score columns')
    drives={}; games={}
    for row in reader:
        try:
            if row['play_deleted']=='1': continue
            home,away=normalize_code(row['home_team']),normalize_code(row['away_team'])
            team=normalize_code(row['posteam'])
            if team not in (home,away) or not row['fixed_drive']: continue
            start,end=float(row['posteam_score']),float(row['posteam_score_post'])
            order=float(row['play_id'])
            if not all(map(math.isfinite,(start,end,order))) or start<0 or end<start: continue
            key=(row['game_id'],row['fixed_drive'],team)
            if key not in drives:drives[key]=[order,start,order,end]
            else:
                d=drives[key]
                if order<d[0]:d[0],d[1]=order,start
                if order>d[2]:d[2],d[3]=order,end
            games[row['game_id']] = (date.fromisoformat(row['game_date']),home,away,row['season'])
        except (ValueError,KeyError,TypeError): continue
    by_game=defaultdict(lambda:defaultdict(list)); invalid=set()
    for (gid,_,team),(_,start,__,end) in drives.items():
        points=end-start
        if not points.is_integer() or int(points) not in NFL_EVENTS:
            invalid.add(gid);continue
        by_game[gid][team].append(int(points))
    results=[]
    for gid,sides in by_game.items():
        if gid in invalid or gid not in games:continue
        day,home,away,season=games[gid]
        if len(sides[home])<5 or len(sides[away])<5:continue
        results.append({'id':game_id('NFL',day,away,home),'source_game_id':gid,
                        'league':'NFL','season':season,'date':day,'home':home,'away':away,
                        'counts':(len(sides[home]),len(sides[away])),
                        'events':({v:sides[home].count(v) for v in NFL_EVENTS},
                                  {v:sides[away].count(v) for v in NFL_EVENTS})})
    return results


def _tilted(events,base,mean):
    """Exponential tilt of prior event frequencies to the target scoring rate."""
    if not 0 < mean < max(events):return None
    def distribution(lam):
        weights=[max(1e-7,base.get(v,0))*math.exp(max(-50,min(50,lam*v))) for v in events]
        total=sum(weights)
        return [x/total for x in weights]
    low,high=-10.,10.
    for _ in range(50):
        mid=(low+high)/2
        p=distribution(mid)
        if sum(v*w for v,w in zip(events,p))<mean:low=mid
        else:high=mid
    p=distribution((low+high)/2); cdf=[];running=0
    for x in p:running+=x;cdf.append(running)
    cdf[-1]=1.
    return cdf


class ProcessHistory:
    """Chronological observations with opponent-adjusted scoring and observed pace."""
    def __init__(self,league):
        if league not in ('NBA','NFL'):raise ValueError('unsupported league')
        self.league=league;self.games=[];self.off=defaultdict(lambda:[0.,0.,0]);self.defense=defaultdict(lambda:[0.,0.,0])
        self.events=defaultdict(int);self.count_pairs=[];self.home_points=0;self.away_points=0;self.units=0

    def add(self,game):
        if game['league']!=self.league:raise ValueError('wrong league')
        if self.games and game['date']<self.games[-1]['date']:raise ValueError('games must be chronological')
        for index,(team,other) in enumerate(((game['home'],game['away']),(game['away'],game['home']))):
            n=game['counts'][index]; events=game['events'][index]
            if not isinstance(n,int) or n<5 or sum(events.values())!=n:raise ValueError('invalid count')
            pts=sum(k*v for k,v in events.items())
            for store,key in ((self.off,team),(self.defense,other)):
                store[key][0]+=pts;store[key][1]+=n;store[key][2]+=1
            for k,v in events.items():self.events[k]+=v
            if index==0:self.home_points+=pts
            else:self.away_points+=pts
            self.units+=n
        self.games.append(game);self.count_pairs.append(game['counts'])

    def simulate(self,home,away,draws=5000,seed=20261028,neutral=False):
        if not isinstance(draws,int) or not 5000<=draws<=20000:raise ValueError('draws must be 5000..20000')
        minimum=200 if self.league=='NBA' else 80
        if home==away or len(self.games)<minimum or min(self.off[home][2],self.off[away][2])<3:return None
        avg=(self.home_points+self.away_points)/self.units
        events=NBA_EVENTS if self.league=='NBA' else NFL_EVENTS
        prior=10 if self.league=='NBA' else 5
        def shrink(store,team):
            points,units,games=store[team]
            typical=self.units/(2*len(self.games))
            return (points+prior*typical*avg)/(units+prior*typical)
        targets=[]
        home_adv=(self.home_points-self.away_points)/self.units
        for team,opp,sign in ((home,away,1),(away,home,-1)):
            target=shrink(self.off,team)*shrink(self.defense,opp)/avg
            if not neutral:target+=sign*home_adv/2
            targets.append(target)
        cdfs=[_tilted(events,self.events,target) for target in targets]
        if None in cdfs:return None
        rng=random.Random(seed);scores=[];wins=ties=0
        for _ in range(draws):
            nh,na=self.count_pairs[rng.randrange(len(self.count_pairs))]
            score=[]
            for n,cdf in ((nh,cdfs[0]),(na,cdfs[1])):
                s=0
                for _ in range(n):
                    v=rng.random()
                    for j,limit in enumerate(cdf):
                        if v<=limit:s+=events[j];break
                score.append(s)
            h,a=score
            if h==a:
                if self.league=='NBA':
                    # A tied regulation is resolved as an explicitly unmodeled overtime coin flip.
                    if rng.random()<.5:h+=1
                    else:a+=1
                else:ties+=1
            wins+=h>a;scores.append((h,a))
        return {'model_version':'scoring-process-v1','league':self.league,
                'draws':draws,'seed':seed,'reference_games':len(self.games),
                'home_wins':wins,'away_wins':draws-wins-ties,'ties':ties,
                'home_probability':(wins+ties/2)/draws,
                'mean_home_score':round(sum(x for x,_ in scores)/draws,2),
                'mean_away_score':round(sum(y for _,y in scores)/draws,2),
                'median_home_score':median(x for x,_ in scores),
                'median_away_score':median(y for _,y in scores),
                'scoring_unit':'estimated box-score possession' if self.league=='NBA' else 'observed offensive drive',
                'limitations':'Retrospective team scoring; no verified pregame injuries, player rotation, special-teams/defensive scores or market calibration'}


def walk_forward(observations,games,first_season,draws=5000):
    """Use strictly previous days, matching official finals for evaluation only."""
    completed={g['id']:g for g in games}
    history=ProcessHistory(observations[0]['league']) if observations else None
    if history is None:return []
    observations=sorted(observations,key=lambda x:(x['date'],x['id']))
    output=[];pending=[];day=None
    for g in observations:
        if g['date']!=day:
            for old in pending:history.add(old)
            pending=[];day=g['date']
        pending.append(g)
        actual=completed.get(g['id'])
        if not actual or str(g['season'])<str(first_season) or actual['home_score']==actual['away_score']:continue
        # Incomplete drive accounting is okay only when validated against finals.
        if g['league']=='NFL':
            off=(sum(k*v for k,v in g['events'][0].items()),sum(k*v for k,v in g['events'][1].items()))
            if off[0]>actual['home_score'] or off[1]>actual['away_score']:continue
        seed=int(sha256(g['id'].encode()).hexdigest()[:8],16)
        result=history.simulate(g['home'],g['away'],draws,seed,actual.get('neutral',False))
        if result:output.append({'game_id':g['id'],'season':g['season'],'probability':result['home_probability'],
                                 'outcome':int(actual['home_score']>actual['away_score'])})
    return output
