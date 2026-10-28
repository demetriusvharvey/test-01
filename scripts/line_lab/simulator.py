"""Point-in-time score bootstrap challenger. Never used as a live betting edge.

Offense and defense are estimated from *earlier* completed games. Historical
paired score deviations preserve league-level scoring covariance; drawing a
score pair is materially different from repeatedly sampling a win flag.
"""
from collections import defaultdict
from datetime import date
from hashlib import sha256
import math
import random
from statistics import median


class ScoreHistory:
    def __init__(self, league):
        if league not in ('NBA', 'NFL'): raise ValueError('unsupported league')
        self.league=league
        self.team=defaultdict(lambda: [0, 0, 0])  # points for, points allowed, games
        self.scores=[]

    def add(self, game):
        if game['league']!=self.league: return
        h,a=game['home_score'],game['away_score']
        if not all(isinstance(s,int) and not isinstance(s,bool) and 0<=s<=250 for s in (h,a)):
            raise ValueError('invalid final score')
        self.scores.append((h,a))
        for code,scored,allowed in ((game['home'],h,a),(game['away'],a,h)):
            row=self.team[code]; row[0]+=scored; row[1]+=allowed; row[2]+=1

    def project(self, home, away, neutral=False):
        minimum=200 if self.league=='NBA' else 80
        team_minimum=5 if self.league=='NBA' else 3
        if home==away or len(self.scores)<minimum or any(self.team[t][2]<team_minimum for t in (home,away)):
            return None
        league_mean=sum(h+a for h,a in self.scores)/(2*len(self.scores))
        home_mean=sum(h for h,_ in self.scores)/len(self.scores)
        away_mean=sum(a for _,a in self.scores)/len(self.scores)
        # The two score means share the observed league-wide home advantage.
        # Shrink team rates toward the earlier league mean, never future scores.
        prior=10 if self.league=='NBA' else 4
        def rate(team,index):
            row=self.team[team]
            return (row[index]+prior*league_mean)/(row[2]+prior)
        h=rate(home,0)+rate(away,1)-league_mean
        a=rate(away,0)+rate(home,1)-league_mean
        if not neutral:
            h+=(home_mean-away_mean)/2
            a-=(home_mean-away_mean)/2
        return {'expected_home':max(0,h),'expected_away':max(0,a),
                'reference_home':home_mean,'reference_away':away_mean,
                'reference_league':league_mean,'reference_games':len(self.scores),
                'team_games':{home:self.team[home][2],away:self.team[away][2]}}

    def simulate(self, home, away, neutral=False, draws=10000, seed=20261028):
        if not isinstance(draws,int) or not 5000<=draws<=20000:raise ValueError('draws must be between 5000 and 20000')
        p=self.project(home,away,neutral)
        if p is None:return None
        rng=random.Random(seed);scores=[];home_wins=0;ties=0
        for _ in range(draws):
            sample_home,sample_away=self.scores[rng.randrange(len(self.scores))]
            h=max(0,round(p['expected_home']+sample_home-p['reference_home']))
            a=max(0,round(p['expected_away']+sample_away-p['reference_away']))
            if h==a:
                if self.league=='NBA':
                    # NBA games cannot end tied. Overtime detail is not in this
                    # feed, so this approximation is explicit and testable.
                    h+=1 if rng.random()<.5 else 0
                    a+=int(h==a)
                else: ties+=1
            home_wins+=h>a
            scores.append((h,a))
        return {**p,'league':self.league,'model_version':'score-bootstrap-v1',
                'draws':draws,'seed':seed,'home_wins':home_wins,'away_wins':draws-home_wins-ties,
                'ties':ties,'home_probability':(home_wins+ties/2)/draws,
                'median_home_score':median(h for h,_ in scores),
                'median_away_score':median(a for _,a in scores),
                'home_score_interval':[sorted(h for h,_ in scores)[int(.05*draws)],sorted(h for h,_ in scores)[int(.95*draws)-1]],
                'away_score_interval':[sorted(a for _,a in scores)[int(.05*draws)],sorted(a for _,a in scores)[int(.95*draws)-1]],
                'limitations':'Team score rates and historical paired score variance only; player injuries, lineups, weather, drives and possessions are not modeled'}


def as_of_histories(games, cutoff):
    """Use completed historical games strictly before cutoff's ET date."""
    result={league:ScoreHistory(league) for league in ('NBA','NFL')}
    for game in sorted(games,key=lambda g:(g['date'],g['id'])):
        if game['date']<cutoff and game['league'] in result:result[game['league']].add(game)
    return result


def backtest_scores(games,league,first_test_season=None,draws=5000):
    """Walk-forward by calendar day, with no same-day results used as features."""
    history=ScoreHistory(league);rows=[];bucket=[];current=None
    for g in sorted((x for x in games if x['league']==league),key=lambda x:(x['date'],x['id'])):
        if g['date']!=current:
            for old in bucket:history.add(old)
            bucket=[];current=g['date']
        bucket.append(g)
        if first_test_season and str(g['season'])<str(first_test_season):continue
        if g['home_score']==g['away_score']:continue
        # Stable seed per game; the historical game result has no influence.
        seed=int(sha256(g['id'].encode()).hexdigest()[:8],16)
        result=history.simulate(g['home'],g['away'],g.get('neutral',False),draws,seed)
        if result:
            p=result['home_probability'];y=int(g['home_score']>g['away_score'])
            rows.append({'game_id':g['id'],'season':g['season'],'league':league,
                         'probability':p,'outcome':y,'reference_games':result['reference_games']})
    return rows


def score_metrics(rows):
    if not rows:return {'games':0,'accuracy':None,'brier':None,'log_loss':None}
    return {'games':len(rows),'accuracy':sum((r['probability']>=.5)==r['outcome'] for r in rows)/len(rows),
            'brier':sum((r['probability']-r['outcome'])**2 for r in rows)/len(rows),
            'log_loss':sum(-(r['outcome']*math.log(max(1e-6,min(1-1e-6,r['probability'])))+
                              (1-r['outcome'])*math.log(max(1e-6,min(1-1e-6,1-r['probability'])))) for r in rows)/len(rows)}
