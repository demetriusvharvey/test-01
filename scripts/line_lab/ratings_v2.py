"""Market-independent rating challengers; disabled pending forward validation."""
import heapq
import math
from datetime import timedelta
from zoneinfo import ZoneInfo
from .history import aware


def _probability(difference):
    return 1/(1+10**(-max(-1500,min(1500,difference))/400))


class ShadowElo:
    """Margin-adjusted Elo with shrunk home residual and descriptive uncertainty."""
    def __init__(self,league,carryover=.75,k=20,home_advantage=50,prior_home_games=50):
        if league not in ('NBA','NFL') or not 0<=carryover<=1 or k<=0 or prior_home_games<=0:raise ValueError('invalid settings')
        self.league=league;self.carryover=carryover;self.k=k;self.hfa=home_advantage;self.prior_home_games=prior_home_games
        self.ratings={};self.seasons={};self.games={};self.home_count={};self.home_residual={}
    def _prepare(self,team,season):
        if team not in self.ratings:self.ratings[team]=1500;self.seasons[team]=season;self.games[team]=0
        elif self.seasons[team]!=season:
            self.ratings[team]=1500+self.carryover*(self.ratings[team]-1500)
            self.seasons[team]=season;self.games[team]=0
    def predict(self,home,away,season,neutral=False):
        if home==away:raise ValueError('same team')
        self._prepare(home,season);self._prepare(away,season)
        home_effect=0 if neutral else self.hfa+120*self.home_residual.get(home,0)/(self.prior_home_games+self.home_count.get(home,0))
        probability=_probability(self.ratings[home]-self.ratings[away]+home_effect)
        # This rating-scale quantity is not a calibrated probability interval.
        sigma_home=250/math.sqrt(1+self.games[home]/10)
        sigma_away=250/math.sqrt(1+self.games[away]/10)
        return {'home_probability':probability,'rating_uncertainty':math.hypot(sigma_home,sigma_away),
                'status':'shadow_unvalidated','promoted':False}
    def update(self,game):
        home,away,season=game['home'],game['away'],str(game['season'])
        # A late correction from a past season must not roll state backwards.
        if any(team in self.seasons and int(str(self.seasons[team])[:4])>int(season[:4]) for team in (home,away)):return
        pred=self.predict(home,away,season,game.get('neutral',False))['home_probability']
        margin=game['home_score']-game['away_score']; outcome=1 if margin>0 else 0 if margin<0 else .5
        scale=15 if self.league=='NBA' else 10
        multiplier=max(.5,min(2.0,math.log1p(abs(margin))/math.log1p(scale)))
        delta=self.k*multiplier*(outcome-pred)
        self.ratings[home]+=delta;self.ratings[away]-=delta
        self.games[home]+=1;self.games[away]+=1
        if not game.get('neutral',False):
            self.home_count[home]=self.home_count.get(home,0)+1
            self.home_residual[home]=self.home_residual.get(home,0)+outcome-pred


def _eligible_games(rows,league,cutoff):
    result=[];now=aware(cutoff)
    for row in rows:
        try:
            forecast,start,final=(aware(row[k]) for k in ('forecast_at','starts_at','final_observed_at'))
            if row.get('league')!=league or row.get('rights_verified') is not True:continue
            if not forecast<start<=final<now:continue
            if not row.get('home') or not row.get('away') or row['home']==row['away']:continue
            int(str(row['season'])[:4])
            scores=[row[k] for k in ('home_score','away_score')]
            if any(not isinstance(x,int) or isinstance(x,bool) or x<0 for x in scores):continue
            if league=='NBA' and scores[0]==scores[1]:continue
            result.append(row)
        except (KeyError,TypeError,ValueError):continue
    ordered=sorted(result,key=lambda x:(aware(x['forecast_at']),x['game_id']))
    seen=set();first=[]
    for row in ordered:
        if row['game_id'] not in seen:seen.add(row['game_id']);first.append(row)
    return first


def walk_forward_carryover(rows,league,cutoff,min_games=500,min_seasons=4):
    """Fit a prior-only candidate grid; evaluation and promotion remain separate."""
    games=_eligible_games(rows,league,cutoff)
    seasons=sorted({str(row['season']) for row in games})
    if len(games)<min_games or len(seasons)<min_seasons:return None
    scores={};n={}
    for carryover in (0.0,.25,.5,.75,1.0):
        state=ShadowElo(league,carryover=carryover,k=20 if league=='NBA' else 24,
                        home_advantage=55 if league=='NBA' else 42)
        pending=[];losses=[]
        for i,game in enumerate(games):
            forecast=aware(game['forecast_at'])
            while pending and pending[0][0]<forecast:
                _,_,done=heapq.heappop(pending);state.update(done)
            p=state.predict(game['home'],game['away'],str(game['season']),game.get('neutral',False))['home_probability']
            y=1 if game['home_score']>game['away_score'] else 0 if game['home_score']<game['away_score'] else .5
            if str(game['season'])!=seasons[0]:losses.append(-(y*math.log(p)+(1-y)*math.log(1-p)))
            heapq.heappush(pending,(aware(game['final_observed_at']),i,game))
        if not losses:return None
        scores[str(carryover)]=sum(losses)/len(losses);n[str(carryover)]=len(losses)
    best=min(scores,key=scores.get)
    return {'trained_before':aware(cutoff).isoformat(),'candidate_carryover':float(best),
            'train_log_loss':scores,'counts':n,'seasons':seasons,'status':'shadow_unvalidated','promoted':False}


def observed_schedule_context(records,team,forecast_at,upcoming,lookback=7):
    """Rest and venue-to-venue travel from timestamped, finalized prior games."""
    try:
        now=aware(forecast_at);start=aware(upcoming['starts_at']);venue=upcoming['venue']
        if now>=start or aware(venue['observed_at'])>now or venue.get('rights_verified') is not True:return None
        upcoming_zone=ZoneInfo(venue['timezone']);upcoming_day=start.astimezone(upcoming_zone).date()
    except (KeyError,ValueError,TypeError):return None
    valid=[]
    for row in records:
        try:
            previous=aware(row['starts_at']);final=aware(row['final_observed_at'])
            if row.get('rights_verified') is not True or team not in (row['home'],row['away']) or not previous<=final<now or previous>=start:continue
            if aware(row['venue']['observed_at'])>now:continue
            ZoneInfo(row['venue']['timezone'])
            valid.append(row)
        except (KeyError,ValueError,TypeError):continue
    if not valid:return None
    valid.sort(key=lambda r:aware(r['starts_at']));last=valid[-1];old_zone=ZoneInfo(last['venue']['timezone'])
    old_start=aware(last['starts_at']);last_day=old_start.astimezone(old_zone).date()
    rest=max(0,(upcoming_day-last_day).days-1)
    count=sum(0<(upcoming_day-aware(row['starts_at']).astimezone(ZoneInfo(row['venue']['timezone'])).date()).days<=3 for row in valid)
    try:
        a,b=last['venue'],venue
        lat1,lon1,lat2,lon2=[float(x) for x in (a['lat'],a['lon'],b['lat'],b['lon'])]
        if not (-90<=lat1<=90 and -90<=lat2<=90 and -180<=lon1<=180 and -180<=lon2<=180):raise ValueError('coordinates')
        r1,r2=math.radians(lat1),math.radians(lat2)
        dlat,dlon=math.radians(lat2-lat1),math.radians(lon2-lon1)
        h=math.sin(dlat/2)**2+math.cos(r1)*math.cos(r2)*math.sin(dlon/2)**2
        distance=3958.8*2*math.asin(math.sqrt(min(1,max(0,h))))
    except (KeyError,ValueError,TypeError):distance=None
    offset=(start.astimezone(upcoming_zone).utcoffset()-old_start.astimezone(old_zone).utcoffset()).total_seconds()/3600
    return {'rest_days':rest,'back_to_back':rest==0,'games_in_four_days_including_upcoming':1+count,
            'venue_distance_miles':round(distance,1) if distance is not None else None,
            'utc_offset_change_hours':offset,'travel_itinerary':'unknown','status':'shadow_unvalidated'}
