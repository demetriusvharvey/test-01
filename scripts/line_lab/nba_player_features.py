"""Shared, past-only NBA box-stat rotation features for training and inference."""
import math
from collections import defaultdict,deque
from .constants import ET
from .history import aware

BOX_STATS=('assists','turnovers','offensive_rebounds','defensive_rebounds','steals','blocks',
           'field_goals_attempted','three_point_field_goals_attempted','free_throws_attempted','fouls')
FEATURES=('rotation_scoring_difference','top_five_share_difference','experienced_share_difference')+tuple(
    'projected_'+name+'_difference' for name in BOX_STATS)


def allocate_minutes(estimates):
    """Project a maximum twelve-player, 240-minute rotation, with a 48-minute cap."""
    if len(estimates)<8:return None
    values=[dict(p,minutes=0.) for p in sorted(estimates,key=lambda p:(-p['weight'],p['player_id']))[:12]]
    if any(not math.isfinite(p['weight']) or p['weight']<=0 for p in values):return None
    remaining=240.;active=list(values)
    while active and remaining>1e-8:
        total=sum(p['weight'] for p in active)
        capped=[p for p in active if remaining*p['weight']/total>=48]
        if not capped:
            for p in active:p['minutes']=remaining*p['weight']/total
            remaining=0.;break
        for p in capped:p['minutes']=48.
        remaining-=48*len(capped);active=[p for p in active if p not in capped]
    return values if remaining<=1e-8 else None


def summarize(rotation,histories,team):
    """Aggregate prior per-minute rates at projected minutes; missing stays missing."""
    output={'scoring':0.,'experienced_share':0.,**{k:0. for k in BOX_STATS}}
    for player in rotation:
        records=list(histories.get((team,player['player_id']),[]))[-10:]
        total=sum(r['minutes'] for r in records)
        if not total:return None
        for metric in ('points',)+BOX_STATS:
            values=[r.get(metric) for r in records]
            if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values):return None
            name='scoring' if metric=='points' else metric
            output[name]+=player['minutes']*sum(values)/total
        if len(records)>=5:output['experienced_share']+=player['minutes']/240
    output['top_five_share']=sum(sorted((p['minutes'] for p in rotation),reverse=True)[:5])/240
    return output


def difference(home,away):
    return [(home['scoring']-away['scoring'])/20,
            home['top_five_share']-away['top_five_share'],home['experienced_share']-away['experienced_share']]+[
                home[k]-away[k] for k in BOX_STATS]


def current_summary(players,rotation,as_of):
    cutoff=aware(as_of).astimezone(ET).date();history=defaultdict(list)
    ids={p['player_id'] for p in rotation['players']};team=rotation['team']
    for row in players:
        if row['team']==team and row['player_id'] in ids and row['date']<cutoff:
            history[(team,row['player_id'])].append(row)
    for key,rows in history.items():history[key]=sorted(rows,key=lambda r:r['date'])[-10:]
    return summarize(rotation['players'],history,team)


def historical_features(games,players,ratings_by_season=None):
    """Prior appearances infer membership; historical pregame availability is unknown."""
    daily=defaultdict(list);slates=defaultdict(list)
    for row in players:daily[row['date']].append(row)
    for g in games:
        if g['league']=='NBA':slates[g['date']].append(g)
    history=defaultdict(lambda:deque(maxlen=10));last={};membership={};output={}
    for day in sorted(set(daily)|set(slates)):
        summaries={}
        rating=(ratings_by_season.get(slates[day][0]['season']) if slates[day] else None) if ratings_by_season is not None else None
        if rating and (rating.get('trained_before_season')!=slates[day][0]['season'] or not rating.get('training_seasons')
                       or any(s>=slates[day][0]['season'] for s in rating['training_seasons'])):rating=None
        for team in {t for g in slates[day] for t in (g['home'],g['away'])}:
            estimates=[]
            for player,assigned in membership.items():
                if assigned!=team or not 0<(day-last[player]).days<=21:continue
                rows=history[(team,player)]
                estimates.append({'player_id':player,'weight':sum(r['minutes'] for r in rows)/len(rows)})
            rotation=allocate_minutes(estimates)
            if rotation:
                summary=summarize(rotation,history,team)
                if summary and ratings_by_season is not None:
                    from .nba_lineup_value import rotation_value
                    value=rotation_value(rating,{'players':rotation}) if rating else None
                    if value is None:continue
                    summary['stint_value']=value
                if summary:summaries[team]=summary
        for game in slates[day]:
            h,a=summaries.get(game['home']),summaries.get(game['away'])
            if h and a:output[game['id']]={'vector':difference(h,a)+([(h['stint_value']-a['stint_value'])/20] if ratings_by_season is not None else []),
                                          'availability':'historical pregame injuries and lineups unknown'}
        # Freeze every feature on a date before observing ANY game on that date.
        for row in daily[day]:
            player=row['player_id'];history[(row['team'],player)].append(row)
            last[player]=day;membership[player]=row['team']
    return output
