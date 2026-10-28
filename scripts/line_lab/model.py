"""Model components for the picks pipeline."""
from datetime import date, datetime, timedelta, timezone
from .constants import *
from .features import recent_margin, record_margin


def elo_probability(diff): return 1/(1+10**(-max(-1200,min(1200,diff))/400))

def build_ratings(games, cutoff, league, params=None, validation_season=None):
    # Training ends before today's ET date. This avoids training on later same-day results.
    ratings={}; last={}; margins={}; last_season=None; validation_errors=[]
    values=params or ((20,55,0,0) if league=='NBA' else (24,42,0,0))
    k,home_advantage,rest_weight=values[:3]
    form_weight=values[3] if len(values)>3 else 0
    for g in sorted((x for x in games if x['league']==league and x['date']<cutoff),key=lambda x:(x['date'],x['id'])):
        if last_season is not None and g['season']!=last_season:
            ratings={team:1500+(value-1500)*0.75 for team,value in ratings.items()}
            margins={}
        last_season=g['season']
        h,a=g['home'],g['away']; hr=ratings.get(h,1500); ar=ratings.get(a,1500)
        rh=min(7,max(0,(g['date']-last[h]).days-1)) if h in last else 3
        ra=min(7,max(0,(g['date']-last[a]).days-1)) if a in last else 3
        form=recent_margin(margins,h)-recent_margin(margins,a)
        p=elo_probability(hr-ar+(0 if g['neutral'] else home_advantage)+rest_weight*(rh-ra)+form_weight*form)
        outcome=1 if g['home_score']>g['away_score'] else 0 if g['home_score']<g['away_score'] else 0.5
        if g['season']==validation_season and outcome!=0.5: validation_errors.append((p-outcome)**2)
        ratings[h]=hr+k*(outcome-p); ratings[a]=ar-k*(outcome-p)
        record_margin(margins,h,a,g['home_score']-g['away_score'])
        last[h]=g['date']; last[a]=g['date']
    return {'ratings':ratings,'last':last,'margins':margins,'last_season':last_season,'home_advantage':home_advantage,'rest_weight':rest_weight,'form_weight':form_weight,'k':k,'validation_count':len(validation_errors),'validation_brier':sum(validation_errors)/len(validation_errors) if validation_errors else None}

def feature_passes(baseline_validation, candidate_validation, baseline_holdout, candidate_holdout, minimum):
    metrics=[baseline_validation,candidate_validation,baseline_holdout,candidate_holdout]
    if any(x['validation_count']<minimum or x['validation_brier'] is None for x in metrics): return False
    return (baseline_validation['validation_brier']-candidate_validation['validation_brier']>=0.0005 and
            baseline_holdout['validation_brier']-candidate_holdout['validation_brier']>=0.0005)

def train_model(games,cutoff,league):
    # Preserve legacy baseline parameter selection. Exploratory feature promotion
    # is disabled pending the preregistered protocol and untouched confirmation.
    count={}
    for g in games:
        if g['league']==league and g['date']<cutoff and g['home_score']!=g['away_score']:
            count[g['season']]=count.get(g['season'],0)+1
    minimum=1000 if league=='NBA' else 200
    completed=sorted(s for s,n in count.items() if n>=minimum)
    if league=='NBA': base_configs=[(20,55,0,0),(20,40,0,0),(20,70,0,0),(15,55,0,0),(25,55,0,0)]
    else: base_configs=[(24,42,0,0),(24,25,0,0),(24,55,0,0),(18,42,0,0),(30,42,0,0)]
    if len(completed)<2:
        result=build_ratings(games,cutoff,league,base_configs[0])
        result.update({'validation_season':None,'holdout_season':None,'candidate_passed':False,'candidate_name':None,'candidate_testing':'disabled'})
        return result
    val,holdout=completed[-2],completed[-1]
    fitted=[build_ratings(games,cutoff,league,c,val) for c in base_configs]
    best_index=min(range(len(fitted)),key=lambda i:fitted[i]['validation_brier'] if fitted[i]['validation_brier'] is not None else float('inf'))
    baseline_val=fitted[best_index]
    baseline_hold=build_ratings(games,cutoff,league,base_configs[best_index])
    # Legacy rest/form findings were exploratory and lack pre-registration,
    # independent replication, multiple-testing adjustment and full-blend
    # evidence. Suspend both features and stop re-testing them on every run.
    baseline_hold.update({'validation_season':val,'holdout_season':None,'legacy_review_season':holdout,
                          'candidate_passed':False,'candidate_name':None,'candidate_testing':'disabled',
                          'selection_count':baseline_val['validation_count']})
    return baseline_hold

def project_home(model, home, away, when, neutral=False):
    ratings=model['ratings']; last=model['last']
    if home not in ratings or away not in ratings: return None
    day=when.astimezone(ET).date()
    rh=min(7,max(0,(day-last[home]).days-1)) if home in last else 3
    ra=min(7,max(0,(day-last[away]).days-1)) if away in last else 3
    form=recent_margin(model.get('margins',{}),home)-recent_margin(model.get('margins',{}),away)
    return elo_probability(ratings[home]-ratings[away]+(0 if neutral else model['home_advantage'])+model['rest_weight']*(rh-ra)+model.get('form_weight',0)*form)

def apply_same_day_finals(models, finals, today, nfl_locations, now):
    # Yesterday's historical results are already in the model. Add only ESPN
    # regular/postseason games that have actually finished today, once each.
    seen=set(); added={'NBA':0,'NFL':0}
    for game in sorted(finals,key=lambda x:x.get('starts_at',now)):
        if game.get('date')!=today or game.get('season_type') not in (2,3): continue
        if game.get('starts_at',now)>now or game['id'] in seen: continue
        league=game['league']; model=models.get(league)
        if not model or (league=='NFL' and game['id'] not in nfl_locations): continue
        # ESPN and historical providers can label NBA seasons by different years.
        # The game date determines the regular/postseason's starting year.
        start_year=today.year if today.month>=8 else today.year-1
        season=f'{start_year}-{str(start_year+1)[-2:]}' if league=='NBA' else str(start_year)
        if model.get('last_season') and season!=model['last_season']:
            model['ratings']={team:1500+(value-1500)*0.75 for team,value in model['ratings'].items()}
            model['margins']={}; model['last_season']=season
        home,away=game['home'],game['away']
        hr=model['ratings'].get(home,1500); ar=model['ratings'].get(away,1500)
        rh=min(7,max(0,(today-model['last'][home]).days-1)) if home in model['last'] else 3
        ra=min(7,max(0,(today-model['last'][away]).days-1)) if away in model['last'] else 3
        neutral=nfl_locations.get(game['id'],False) if league=='NFL' else False
        form=recent_margin(model['margins'],home)-recent_margin(model['margins'],away)
        p=elo_probability(hr-ar+(0 if neutral else model['home_advantage'])+model['rest_weight']*(rh-ra)+model.get('form_weight',0)*form)
        outcome=1 if game['home_score']>game['away_score'] else 0 if game['home_score']<game['away_score'] else 0.5
        model['ratings'][home]=hr+model['k']*(outcome-p); model['ratings'][away]=ar-model['k']*(outcome-p)
        record_margin(model['margins'],home,away,game['home_score']-game['away_score'])
        model['last'][home]=today; model['last'][away]=today; seen.add(game['id']); added[league]+=1
    return added
