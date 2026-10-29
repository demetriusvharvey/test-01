"""Chronological NBA logistic baseline with separate-season calibration."""
import math
from collections import defaultdict,deque
from .model import elo_probability
from .availability_model import _fit,_predict
from .calibration import _fit as fit_calibration,predict_shadow
from .simulator import score_metrics

FEATURES=('elo_difference','scoring_difference','allowed_difference','win_rate_difference','rest_difference','home_court')


def examples(games):
    ratings={};recent=defaultdict(lambda:deque(maxlen=20));last={};byday=defaultdict(list)
    for g in games:
        if g['league']=='NBA':byday[g['date']].append(g)
    output=[];season=None
    for day,slate in sorted(byday.items()):
        for g in sorted(slate,key=lambda g:g['id']):
            if season!=g['season']:
                ratings={t:1500+.75*(r-1500) for t,r in ratings.items()};season=g['season']
            h,a=g['home'],g['away'];hr,ar=ratings.get(h,1500),ratings.get(a,1500)
            home_court=0 if g.get('neutral') else 55
            p=elo_probability(hr-ar+home_court)
            if len(recent[h])>=10 and len(recent[a])>=10 and (g.get('upcoming') or g['home_score']!=g['away_score']):
                def avg(team,index):return sum(r[index] for r in recent[team])/len(recent[team])
                rest=lambda t:min(7,max(0,(day-last[t]).days-1)) if t in last else 3
                vector=[(hr-ar)/400,(avg(h,0)-avg(a,0))/20,
                        (avg(h,1)-avg(a,1))/20,avg(h,2)-avg(a,2),
                        (rest(h)-rest(a))/7,home_court/55]
                output.append({'game_id':g['id'],'date':day.isoformat(),'season':g['season'],
                               'vector':vector,'baseline_probability':.5,'elo':p,
                               **({} if g.get('upcoming') else {'home_win':int(g['home_score']>g['away_score'])})})
        # All day-start features are frozen before observing any same-day result.
        for g in sorted(slate,key=lambda g:g['id']):
            if g.get('upcoming'):continue
            h,a=g['home'],g['away'];hr,ar=ratings.get(h,1500),ratings.get(a,1500)
            y=1 if g['home_score']>g['away_score'] else 0 if g['home_score']<g['away_score'] else .5
            p=elo_probability(hr-ar+(0 if g.get('neutral') else 55))
            ratings[h]=hr+20*(y-p);ratings[a]=ar-20*(y-p)
            recent[h].append((g['home_score'],g['away_score'],y))
            recent[a].append((g['away_score'],g['home_score'],1-y));last[h]=last[a]=day
    return output


def evaluate_season(rows,test_season,min_training=500,min_calibration=200):
    seasons=sorted({r['season'] for r in rows if r['season']<test_season})
    if len(seasons)<2:return None
    calibration_season=seasons[-1]
    train=[r for r in rows if r['season']<calibration_season]
    calibration=[r for r in rows if r['season']==calibration_season]
    test=[r for r in rows if r['season']==test_season]
    if len(train)<min_training or len(calibration)<min_calibration or not test:return None
    model=_fit(train,.1,epochs=200)
    calibration_rows=[{'pure_probability':_predict(model,.5,r['vector']),'outcome':r['home_win']} for r in calibration]
    weights=fit_calibration(calibration_rows,False,iterations=300)
    fit={'method':'platt_shadow','weights':weights}
    raw=[_predict(model,.5,r['vector']) for r in test]
    calibrated=[predict_shadow(fit,p) for p in raw]
    metrics=lambda values:score_metrics([{'probability':p,'outcome':r['home_win']} for p,r in zip(values,test)])
    bins=[]
    for lo,hi in ((0,.2),(.2,.4),(.4,.6),(.6,.8),(.8,1.00001)):
        selected=[(p,r['home_win']) for p,r in zip(calibrated,test) if lo<=p<hi]
        bins.append({'range':[lo,min(hi,1)],'games':len(selected),
                     'mean_probability':sum(p for p,y in selected)/len(selected) if selected else None,
                     'home_win_rate':sum(y for p,y in selected)/len(selected) if selected else None})
    return {'test_season':test_season,'training_games':len(train),'calibration_season':calibration_season,
            'calibration_games':len(calibration),'logistic':metrics(raw),'calibrated_logistic':metrics(calibrated),
            'elo':metrics([r['elo'] for r in test]),'home_baseline':metrics([1.0 for r in test]),
            'uninformative':metrics([.5 for r in test]),'reliability':bins,
            'artifact':{'model_version':'nba-logistic-score-v1','features':list(FEATURES),
                        'model':model,'calibration':fit,'trained_through_season':seasons[-2],
                        'calibrated_through_season':calibration_season,'promoted':False}}
