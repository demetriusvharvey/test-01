"""Attribution-aware officiating research; no causal claims or live features."""
import math
from collections import defaultdict
from statistics import stdev
from .anchors import devig, implied_american
from .history import aware
from .constants import ET, team_code

# Exact published team-name variants only. Never guess between the LA teams.
OFFICIAL_NBA_NAMES={
    'atlanta':'ATL','boston':'BOS','brooklyn':'BKN','charlotte':'CHA',
    'chicago':'CHI','cleveland':'CLE','dallas':'DAL','denver':'DEN',
    'detroit':'DET','golden state':'GSW','houston':'HOU','indiana':'IND',
    'l.a. clippers':'LAC','la clippers':'LAC','l.a. lakers':'LAL','la lakers':'LAL',
    'memphis':'MEM','miami':'MIA','milwaukee':'MIL','minnesota':'MIN',
    'new orleans':'NOP','new york':'NYK','oklahoma city':'OKC','orlando':'ORL',
    'philadelphia':'PHI','phoenix':'PHX','portland':'POR','sacramento':'SAC',
    'san antonio':'SAS','toronto':'TOR','utah':'UTA','washington':'WAS',
}


def current_official_crew(report,event,observed_at,now):
    """Expose only an exact current official-page matchup, not a ref effect."""
    try:
        observed,current,start=aware(observed_at),aware(now),aware(event['starts_at'])
        if event.get('league')!='NBA' or not observed<=current<start:return None
        if report.get('status')!='ok' or report.get('date_expected')!=start.astimezone(ET).date().isoformat():return None
        matches=[]
        for game in report.get('games',[]):
            parts=game.get('matchup','').split(' @ ')
            if len(parts)!=2:continue
            codes=[]
            for name in parts:
                normalized=' '.join(name.strip().lower().split())
                codes.append(team_code(normalized,'NBA') or OFFICIAL_NBA_NAMES.get(normalized))
            if codes!=[event['away'],event['home']]:continue
            crew=[game.get('crew_chief','').strip(),game.get('referee','').strip(),game.get('umpire','').strip()]
            if not all(crew) or len(set(crew))!=3:continue
            matches.append(crew)
        if len(matches)!=1:return None
        return {'crew_chief':matches[0][0],'referee':matches[0][1],'umpire':matches[0][2],
                'observed_at':observed.isoformat(),'source':'https://official.nba.com/referee-assignments/',
                'assignment_can_change':True,'used_in_prediction':False}
    except (AttributeError,KeyError,TypeError,ValueError):return None


def attach_current_officials(board,markets,report,observed_at,now):
    for pick in board.get('picks',[]):
        event=markets.get(pick.get('id'))
        if event and report and observed_at:
            pick['referee_assignment']=current_official_crew(report,event,observed_at,now)


def assignment_as_of(history,game_date,matchup,predicted_at,starts_at):
    """Use only the latest matching crew actually observed before the pick."""
    now,start=aware(predicted_at),aware(starts_at)
    if now>=start:return None
    matches=[]
    for item in history:
        try:
            if item.get('game_date')!=game_date or item.get('matchup')!=matchup:continue
            if aware(item['observed_at'])>now:continue
            crew=item.get('crew',[])
            if len(crew)<3 or not all(crew[:3]):continue
            matches.append(item)
        except (KeyError,TypeError,ValueError):continue
    return max(matches,key=lambda x:aware(x['observed_at'])) if matches else None


def retrospective_nfl_summary(rows,start_year=2021,end_year=2025,prior_strength=20):
    """Summarize known final results, with unverified historical price timing.

    These are descriptive counts only. The source data were retrieved after the
    games, and neither official assignment publication nor close is verified.
    """
    groups=defaultdict(list);excluded_ties=0
    for r in rows:
        try:
            year=int(r['season']);h=int(float(r['home_score']));a=int(float(r['away_score']))
            if not start_year<=year<=end_year or r['game_type']!='REG' or not r.get('referee'):continue
            if r.get('location','').lower()=='neutral':continue
            if h==a:excluded_ties+=1;continue
            y=int(h>a);p=None
            try:
                p=devig([implied_american(int(float(r['home_moneyline']))),implied_american(int(float(r['away_moneyline'])))])[0]
            except (KeyError,TypeError,ValueError):pass
            groups[r['referee']].append({'win':y,'market':p,'season':year})
        except (KeyError,TypeError,ValueError,OverflowError):continue
    all_games=[g for values in groups.values() for g in values]
    if not all_games:return {'games':0,'officials':[],'excluded_ties':excluded_ties,'status':'no_data'}
    league_rate=sum(g['win'] for g in all_games)/len(all_games)
    result=[]
    for name,games in groups.items():
        n=len(games);wins=sum(g['win'] for g in games)
        alpha=prior_strength*league_rate+wins;beta=prior_strength*(1-league_rate)+n-wins
        mean=alpha/(alpha+beta);variance=alpha*beta/((alpha+beta)**2*(alpha+beta+1));radius=1.9599639845*math.sqrt(variance)
        market=[g['win']-g['market'] for g in games if g['market'] is not None]
        market_mean=sum(market)/len(market) if market else None
        market_radius=1.96*stdev(market)/math.sqrt(len(market)) if len(market)>1 else None
        result.append({'referee':name,'games':n,'home_wins':wins,'observed_home_win_rate':wins/n,
                       'shrunken_home_win_rate':mean,'interval':[max(0,mean-radius),min(1,mean+radius)],
                       'market_games':len(market),'retrospective_market_residual':market_mean,
                       'market_interval':[market_mean-market_radius,market_mean+market_radius] if market_radius is not None else None,
                       'raw_p':None,'adjusted_p':None,'holdout':'not_tested','verdict':'descriptive_only'})
    result.sort(key=lambda x:(-x['games'],x['referee']))
    return {'games':len(all_games),'league_home_win_rate':league_rate,'officials':result,'excluded_ties':excluded_ties,
            'prior_strength':prior_strength,'status':'retrospective_descriptive_not_predictive'}


def prospective_effect(rows,referee,predicted_at,prior_strength=30):
    """Shrunk market residual using only a prior, pregame-observed referee."""
    cutoff=aware(predicted_at);values=[];seen=set()
    for row in rows:
        try:
            assignment,forecast,start,final=(aware(row[k]) for k in ('assignment_observed_at','forecast_at','starts_at','final_observed_at'))
            market_source,market_fetch=(aware(row[k]) for k in ('market_source_as_of','market_fetched_at'))
            p=row['market_home_probability'];y=row['home_win']
            if row.get('referee')!=referee or row.get('rights_verified') is not True:continue
            if row['game_id'] in seen or not market_source<=market_fetch<=forecast:continue
            if not assignment<=forecast<start<=final<cutoff or not isinstance(p,(int,float)) or not 0<p<1 or y not in (0,1):continue
            seen.add(row['game_id']);values.append((y,p))
        except (KeyError,TypeError,ValueError):continue
    if not values:return None
    n=len(values);effect=sum(y-p for y,p in values)/(n+prior_strength)
    radius=1.96*math.sqrt(sum(p*(1-p) for _,p in values))/(n+prior_strength)
    return {'n':n,'effect':effect,'interval':[effect-radius,effect+radius],
            'status':'shadow_unvalidated','adjusted_p':None,'promoted':False}
