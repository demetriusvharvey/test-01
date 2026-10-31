#!/usr/bin/env python3
"""Controlled offline walk-forward training; never run on a page refresh."""
import argparse,json,sys,hashlib,math
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.line_lab.forecast_data import load_archives
from scripts.line_lab.league_forecast import examples,BASE_FEATURES,NBA_FEATURES,NFL_FEATURES,logistic
from scripts.line_lab.ledger_v2 import snapshot_hash
from scripts.line_lab.statistics import paired_block_test
from scripts.line_lab.production import metrics
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def fit(rows,extended,c):
    x=[r['extended_vector'] if extended else r['vector'] for r in rows];y=[r['home_win'] for r in rows]
    scaler=StandardScaler().fit(x);clf=LogisticRegression(C=c,max_iter=1000,random_state=17).fit(scaler.transform(x),y)
    portable={'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),'weights':clf.coef_[0].tolist(),
            'intercept':float(clf.intercept_[0]),'extended':extended,'C':c}
    reference=clf.predict_proba(scaler.transform(x))[:,1]
    if max(abs(logistic(portable,v)-p) for v,p in zip(x,reference))>1e-12:raise ValueError('portable inference mismatch')
    return portable


def loss(ps,rs):return metrics([{'probability':p,'outcome':'win' if r['home_win'] else 'loss'} for p,r in zip(ps,rs)])


def evaluate(rows,league,season):
    past=sorted([r for r in rows if r['season']<season],key=lambda r:(r['date'],r['game_id']))
    test=[r for r in rows if r['season']==season]
    # Separate final earlier season into tuning and calibration dates. Training
    # excludes that entire season. Test outcomes never select a feature or weight.
    seasons=sorted({r['season'] for r in past})
    if len(seasons)<2 or not test:return None
    train=[r for r in past if r['season']<seasons[-1]]
    held=[r for r in past if r['season']==seasons[-1]]
    days=sorted({r['date'] for r in held});boundary=days[int(len(days)*.6)]
    tune=[r for r in held if r['date']<boundary];cal=[r for r in held if r['date']>=boundary]
    minimum=100 if league=='NFL' else 300
    if len(train)<minimum or len(tune)<50 or len(cal)<50:return None
    candidates={};diagnostics={}
    for extended in (False,True):
        if extended and any(r['extended_vector'] is None for r in tune+cal):continue
        candidate_train=[r for r in train if not extended or r['extended_vector'] is not None]
        if len(candidate_train)<minimum:continue
        for c in (.01,.1,1.):
            name=('efficiency' if extended else 'score')+'-'+str(c)
            model=fit(candidate_train,extended,c);candidates[name]=model
            ps=[logistic(model,r['extended_vector'] if extended else r['vector']) for r in tune]
            diagnostics[name]=loss(ps,tune)
    if not candidates:return None
    name=min(candidates,key=lambda n:diagnostics[n]['log_loss']);model=candidates[name]
    predict=lambda rs:[r['elo'] if model['extended'] and r['extended_vector'] is None else logistic(model,r['extended_vector'] if model['extended'] else r['vector']) for r in rs]
    tp=predict(tune)
    weights=[i/10 for i in range(11)]
    weight=min(weights,key=lambda w:loss([w*p+(1-w)*r['elo'] for p,r in zip(tp,tune)],tune)['log_loss'])
    blend=lambda rs:[weight*p+(1-weight)*r['elo'] for p,r in zip(predict(rs),rs)]
    # Choose identity versus Platt using a later disjoint calibration check,
    # never the final season. This prevents automatic calibration regressions.
    caldays=sorted({r['date'] for r in cal});calboundary=caldays[int(len(caldays)*.6)]
    calfit=[r for r in cal if r['date']<calboundary];calcheck=[r for r in cal if r['date']>=calboundary]
    cp=blend(calfit);cx=[[math.log(p/(1-p))] for p in cp]
    calibrator=LogisticRegression(C=1.,max_iter=1000,random_state=17).fit(cx,[r['home_win'] for r in calfit])
    intercept=float(calibrator.intercept_[0]);slope=float(calibrator.coef_[0,0])
    calibrate=lambda ps:[1/(1+math.exp(-max(-35,min(35,intercept+slope*math.log(p/(1-p)))))) for p in ps]
    checkp=blend(calcheck)
    if slope<=0 or loss(calibrate(checkp),calcheck)['log_loss']>=loss(checkp,calcheck)['log_loss']:
        intercept,slope=0.,1.
    raw=blend(test);ps=[r['elo'] if model['extended'] and r['extended_vector'] is None else p for p,r in zip(calibrate(raw),test)]
    residual={}
    for p,r in zip(ps,test):
        y=r['home_win'];b=r['elo']
        residual.setdefault(r['date'],[]).append(-(y*math.log(p)+(1-y)*math.log1p(-p))+(y*math.log(b)+(1-y)*math.log1p(-b)))
    evaluation={'season':season,'training_games':len(train),'tuning_games':len(tune),'calibration_games':len(cal),
                'training_end':max(r['date'] for r in train),'tuning_end':max(r['date'] for r in tune),
                'calibration_end':max(r['date'] for r in cal),'test_start':min(r['date'] for r in test),
                'calibration_method':'identity' if slope==1. and intercept==0. else 'platt',
                'calibration_fit_games':len(calfit),'calibration_check_games':len(calcheck),
                'test_end':max(r['date'] for r in test),'candidate':name,'logistic_weight':weight,
                'tuning_candidates':diagnostics,'ensemble':loss(ps,test),'uncalibrated_ensemble':loss(raw,test),
                'elo':loss([r['elo'] for r in test],test),'paired_log_loss_test':paired_block_test(residual),
                'missing_metric_fallbacks':sum(model['extended'] and r['extended_vector'] is None for r in test),
                'predictions':[{'id':r['game_id'],'date':r['date'],'home_win':r['home_win'],'probability':p,'elo':r['elo'],
                                'feature_cutoff':r['feature_cutoff'],'mode':'historical_backtest',
                                'odds_observed_at':None,'prediction_timestamp':None} for p,r in zip(ps,test)]}
    # This exact fitted artifact is evaluated on the following season. It is
    # not refitted on test outcomes, even for the latest partial season.
    artifact={'league':league,'model_version':league.lower()+'-chronological-ensemble-v1',
              'components':{name:model},'weights':{'elo':1-weight,name:weight},
              'calibration':{'intercept':intercept,'weight':slope},
              'training_cutoff':max(r['date'] for r in cal),'feature_names':BASE_FEATURES+(NBA_FEATURES if league=='NBA' else NFL_FEATURES) if model['extended'] else BASE_FEATURES,
              'calibration_status':'retrospective_only','validation':{'prediction_approved':False,'betting_approved':False,'reason':'prospective calibration and priced edge evidence pending'},
              'limitations':['retrospective source revisions possible','player news not a trained input','no verified contemporaneous historical odds']}
    return evaluation,artifact


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',required=True);parser.add_argument('--output',default='data/models');args=parser.parse_args()
    now=datetime.now(timezone.utc).isoformat();games,stats,hashes,observed=load_archives(args.data_root,now)
    today=datetime.now(timezone.utc).date();games=[g for g in games if g['date']<today]
    dest=Path(args.output);dest.mkdir(parents=True,exist_ok=True)
    (dest/'team_metrics.json').write_text(json.dumps({league:[[day.isoformat(),team,vector] for (day,team),vector in values.items()] for league,values in stats.items()},separators=(',',':'))+'\n')
    report={'created_at':now,'source_hashes':hashes,'source_observed_at':observed,
            'protocol':'rolling season holdouts; earlier season split by date for tune/calibration; inspected archive is exploratory',
            'historical_odds_qualified':False,'leagues':{}}
    for league in ('NBA','NFL'):
        rows=examples(games,league,stats[league]);folds=[];artifact=None
        for season in sorted({r['season'] for r in rows}):
            result=evaluate(rows,league,season)
            if result:
                ev,artifact=result;folds.append(ev)
                print(league,season,'N',ev['ensemble']['sample_size'],'candidate',ev['ensemble']['brier'],ev['ensemble']['log_loss'],'Elo',ev['elo']['brier'],flush=True)
        if artifact:
            artifact.update({'exported_at':now,'input_data_hash':snapshot_hash(hashes),'source_observed_at':observed,
                             'evaluation_season':folds[-1]['season'],'random_seed':17,'sklearn_version':sklearn.__version__,
                             'trainer_source_hash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                             'feature_source_hash':hashlib.sha256((Path(__file__).parent/'line_lab/league_forecast.py').read_bytes()).hexdigest()})
            artifact['model_identity_hash']=snapshot_hash({k:artifact[k] for k in ('league','model_version','components','weights','calibration','training_cutoff','feature_names','feature_source_hash')})
            artifact['artifact_hash']=snapshot_hash(artifact)
            payload=json.dumps(artifact,indent=2)+'\n'
            archive=dest/'artifacts';archive.mkdir(exist_ok=True)
            versioned=archive/(artifact['artifact_hash']+'.json')
            if versioned.exists() and versioned.read_text()!=payload:raise ValueError('immutable artifact collision')
            if not versioned.exists():versioned.write_text(payload)
            (dest/(league.lower()+'.json')).write_text(payload)
        report['leagues'][league]={'folds':folds,'ties_excluded':sum(g['league']==league and g['home_score']==g['away_score'] for g in games),
                                  'promoted_for_betting':False}
    (dest/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
