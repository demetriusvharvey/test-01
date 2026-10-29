"""H029: daily winner ranking with complete-slate coverage and honest denominators."""
import math
import random
from collections import defaultdict
from .simulator import score_metrics
from .statistics import paired_block_test

MODELS=('elo','team14','player27','lineup30')


def rank_winners(rows,threshold=.5,limit=3):
    if not .5<=threshold<1 or type(limit) is not int or limit<0:raise ValueError('invalid ranking policy')
    picks=[];seen=set()
    for r in rows:
        p=r['home_probability'];game=r['game_id']
        if game in seen:raise ValueError('duplicate ranking game')
        seen.add(game)
        if type(p) not in (int,float) or not math.isfinite(p) or not 0<p<1:raise ValueError('invalid probability')
        if p==.5:continue
        home=p>.5;chosen=p if home else 1-p
        if chosen<threshold:continue
        pick={'game_id':game,'team':r['home'] if home else r['away'],'score':chosen}
        if 'home_win' in r:
            if r['home_win'] not in (0,1):raise ValueError('invalid outcome')
            pick['correct']=int(home==bool(r['home_win']))
        picks.append(pick)
    return sorted(picks,key=lambda p:(-p['score'],p['game_id']))[:limit]


def selection_metrics(picks):
    return score_metrics([{'probability':p['score'],'outcome':p['correct']} for p in picks])


def accuracy_interval(byday,draws=2000,seed=20261029):
    groups=[[p['correct'] for p in byday[d]] for d in sorted(byday) if byday[d]]
    if len(groups)<10 or sum(map(len,groups))<30:return None
    rng=random.Random(seed);samples=[]
    for _ in range(draws):
        selected=[groups[rng.randrange(len(groups))] for _ in groups]
        samples.append(sum(map(sum,selected))/sum(map(len,selected)))
    samples.sort()
    return {'lower':samples[int(.025*(draws-1))],'upper':samples[int(.975*(draws-1))],
            'draws':draws,'seed':seed,'unit':'calendar day','days':len(groups)}


def calibration(picks):
    bins=[]
    for lower,upper in ((.5,.6),(.6,.7),(.7,.8),(.8,.9),(.9,1.0000001)):
        values=[p for p in picks if lower<=p['score']<upper]
        bins.append({'range':[lower,min(upper,1)],'picks':len(values),
                     'mean_estimate':sum(p['score'] for p in values)/len(values) if values else None,
                     'win_fraction':sum(p['correct'] for p in values)/len(values) if values else None})
    return bins


def compare_historical(records,games):
    lookup={};expected=defaultdict(list)
    for g in games:
        if g['league']!='NBA':continue
        if g['id'] in lookup:raise ValueError('duplicate archived game')
        lookup[g['id']]=g;expected[g['date'].isoformat()].append(g)
    forecasts={}
    for row in records:
        game=row['game_id']
        if game in forecasts:raise ValueError('duplicate held-out forecast')
        g=lookup[game]
        if row['date']!=g['date'].isoformat() or row['season']!=g['season']:raise ValueError('forecast identity')
        if g['home_score']!=g['away_score'] and row['home_win']!=int(g['home_score']>g['away_score']):raise ValueError('outcome mismatch')
        if set(row['probabilities'])!=set(MODELS):raise ValueError('component schema')
        for p in row['probabilities'].values():
            if type(p) not in (int,float) or not math.isfinite(p) or not 0<p<1:raise ValueError('invalid probability')
        forecasts[game]=row
    results=[]
    for season in sorted({r['season'] for r in records}):
        days={d:slate for d,slate in expected.items() if slate[0]['season']==season}
        complete={d:slate for d,slate in days.items() if all(g['id'] in forecasts and g['home_score']!=g['away_score'] for g in slate)}
        selections={};season_results={}
        for name in MODELS:
            byday={};curves=[]
            for threshold in (.5,.6,.7,.8):
                selected={}
                for day,slate in sorted(complete.items()):
                    rows=[{'game_id':g['id'],'home':g['home'],'away':g['away'],
                           'home_probability':forecasts[g['id']]['probabilities'][name],
                           'home_win':forecasts[g['id']]['home_win']} for g in slate]
                    selected[day]=rank_winners(rows,threshold)
                picks=[p for values in selected.values() for p in values]
                curves.append({'threshold':threshold,'selected_days':sum(bool(x) for x in selected.values()),**selection_metrics(picks)})
                if threshold==.5:byday=selected
            picks=[p for values in byday.values() for p in values];selections[name]=byday
            season_results[name]={'primary':selection_metrics(picks),'accuracy_interval':accuracy_interval(byday),
                                  'calibration':calibration(picks),'coverage_curve':curves}
        for name in MODELS:
            differences={}
            for day in complete:
                chosen,baseline=selections[name][day],selections['elo'][day]
                if chosen and len(chosen)==len(baseline):
                    differences[day]=[a['correct']-b['correct'] for a,b in zip(chosen,baseline)]
            test=paired_block_test(differences,seed=20261029)
            season_results[name]['paired_accuracy_test_vs_elo']=test if name!='elo' else None
            season_results[name]['raw_p']=test['p_value'] if test and name!='elo' else None
        results.append({'season':season,'archived_days':len(days),'complete_days':len(complete),
                        'excluded_incomplete_days':len(days)-len(complete),'complete_games':sum(map(len,complete.values())),
                        'models':season_results})
    return results
