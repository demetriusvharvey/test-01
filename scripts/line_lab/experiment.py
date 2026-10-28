"""Prospective paper forecasts and transparent model-versus-market reporting."""
import hashlib
import json
import math
import random
import sqlite3
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from .history import aware
from .market import decimal_odds, implied
from .model import project_home
from .guard import assess_disagreement
from .statistics import paired_block_test, bh_adjust
from .constants import ET

FORECAST_SCHEMA='''
CREATE TABLE IF NOT EXISTS forecasts (
 forecast_key TEXT PRIMARY KEY, game_id TEXT NOT NULL, league TEXT NOT NULL,
 home TEXT NOT NULL, away TEXT NOT NULL, starts_at TEXT NOT NULL, captured_at TEXT NOT NULL, model_version TEXT NOT NULL,
 pure_probability REAL NOT NULL, retail_probability REAL NOT NULL,
 legacy_blend_probability REAL NOT NULL, sharp_probability REAL, fitted_sharp_blend REAL,
 latest_source_at TEXT NOT NULL, feature_snapshot TEXT NOT NULL, market_snapshot TEXT NOT NULL, guard_snapshot TEXT NOT NULL,
 validation_status TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS forecasts_no_update BEFORE UPDATE ON forecasts BEGIN SELECT RAISE(ABORT,'forecasts are append-only'); END;
CREATE TRIGGER IF NOT EXISTS forecasts_no_delete BEFORE DELETE ON forecasts BEGIN SELECT RAISE(ABORT,'forecasts are append-only'); END;
'''
OUTCOME_SCHEMA='''
CREATE TABLE IF NOT EXISTS outcomes (
 game_id TEXT PRIMARY KEY, home TEXT NOT NULL, away TEXT NOT NULL,
 home_score INTEGER NOT NULL, away_score INTEGER NOT NULL, observed_at TEXT NOT NULL,
 source TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS outcomes_no_update BEFORE UPDATE ON outcomes BEGIN SELECT RAISE(ABORT,'outcomes are append-only'); END;
CREATE TRIGGER IF NOT EXISTS outcomes_no_delete BEFORE DELETE ON outcomes BEGIN SELECT RAISE(ABORT,'outcomes are append-only'); END;
'''
TEST_SCHEMA='''
CREATE TABLE IF NOT EXISTS test_runs (
 run_key TEXT PRIMARY KEY, hypothesis TEXT NOT NULL, league TEXT NOT NULL,
 completed_at TEXT NOT NULL, input_hash TEXT NOT NULL, status TEXT NOT NULL,
 games INTEGER NOT NULL, raw_p REAL, adjusted_p REAL, result_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS tests_no_update BEFORE UPDATE ON test_runs BEGIN SELECT RAISE(ABORT,'tests are append-only'); END;
CREATE TRIGGER IF NOT EXISTS tests_no_delete BEFORE DELETE ON test_runs BEGIN SELECT RAISE(ABORT,'tests are append-only'); END;
'''

def _db(path,schema):
    path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(path);db.executescript(schema);return db

def record_forecasts(root,markets,models,now,shadow_context=None):
    captured=aware(now); path=Path(root)/'observations'/'forecasts'/(captured.date().isoformat()+'.sqlite');added=0
    with closing(_db(path,FORECAST_SCHEMA)) as db, db:
        for event in markets.values():
            if len(event['books'])<3 or aware(event['starts_at'])<=captured+timedelta(minutes=20): continue
            model=models.get(event['league'])
            if not model: continue
            p=project_home(model,event['home'],event['away'],aware(event['starts_at']),event.get('neutral',False))
            if p is None: continue
            times=[aware(book['as_of']) for book in event['books'].values()]
            if any(t>captured for t in times): continue
            prices=[implied(b['home'])/(implied(b['home'])+implied(b['away'])) for b in event['books'].values()]
            retail=median(prices)
            inputs={'home_rating':model['ratings'][event['home']],'away_rating':model['ratings'][event['away']],
                    'model_version':'pure-elo-v1','k':model.get('k'),'last_season':model.get('last_season'),
                    'source_text_sha256':model.get('source_hashes',{}),
                    'home_advantage':model['home_advantage'],'rest_weight':model['rest_weight'],
                    'form_weight':model.get('form_weight',0),'neutral':event.get('neutral',False),
                    'home_last':str(model['last'].get(event['home'])),'away_last':str(model['last'].get(event['away'])),
                    'home_games':model.get('games_played',{}).get(event['home']),
                    'away_games':model.get('games_played',{}).get(event['away']),
                    'home_margins':model.get('margins',{}).get(event['home'],[]),
                    'away_margins':model.get('margins',{}).get(event['away'],[]),
                    'shadow_context':(shadow_context or {}).get(event['id'])}
            feature_json=json.dumps(inputs,sort_keys=True,separators=(',',':'))
            key=hashlib.sha256((event['id']+'|'+captured.isoformat()+'|'+feature_json).encode()).hexdigest()
            market_json=json.dumps(event['books'],sort_keys=True,separators=(',',':'))
            guard_json=json.dumps(assess_disagreement(p,retail,event['league']),sort_keys=True,separators=(',',':'))
            cursor=db.execute('INSERT OR IGNORE INTO forecasts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
              (key,event['id'],event['league'],event['home'],event['away'],aware(event['starts_at']).isoformat(),captured.isoformat(),'pure-elo-v1',
               p,retail,.75*retail+.25*p,None,None,max(times).isoformat(),feature_json,market_json,guard_json,'paper_unvalidated'))
            added+=cursor.rowcount
    return added

def read_forecasts(root):
    rows=[];base=Path(root)/'observations'/'forecasts'
    if not base.exists(): return rows
    for file in sorted(base.glob('*.sqlite')):
        with closing(sqlite3.connect(file)) as db:
            db.row_factory=sqlite3.Row
            rows.extend(dict(row) for row in db.execute('SELECT * FROM forecasts'))
    return rows

def record_outcomes(root,finals,now):
    observed=aware(now); recorded={r['game_id']:r for r in read_forecasts(root)};added=0
    if not recorded:return 0
    path=Path(root)/'observations'/'forecast_outcomes.sqlite'
    with closing(_db(path,OUTCOME_SCHEMA)) as db, db:
        for final in finals:
            row=recorded.get(final['id'])
            if not row or (final['home'],final['away'])!=(row['home'],row['away']) or aware(row['starts_at'])>observed: continue
            h,a=final['home_score'],final['away_score']
            if not isinstance(h,int) or not isinstance(a,int): continue
            cursor=db.execute('INSERT OR IGNORE INTO outcomes VALUES (?,?,?,?,?,?,?)',
                (final['id'],final['home'],final['away'],h,a,observed.isoformat(),final.get('source','confirmed final')))
            added+=cursor.rowcount
    return added

def _logloss(p,y):
    p=max(1e-6,min(1-1e-6,p));return -(y*math.log(p)+(1-y)*math.log(1-p))

def _block_interval(day_values,seed=20261028,iterations=2000):
    """Game-day-block bootstrap of the mean; require a minimum useful sample."""
    if len(day_values)<10 or sum(len(v) for v in day_values.values())<30:return None
    groups=list(day_values.values());rng=random.Random(seed);draws=[]
    for _ in range(iterations):
        sample=[groups[rng.randrange(len(groups))] for _ in groups]
        values=[value for group in sample for value in group]
        draws.append(sum(values)/len(values))
    draws.sort();return [round(draws[int(.025*(iterations-1))],4),round(draws[int(.975*(iterations-1))],4)]

def _retail_brier_summary(items):
    n=len(items)
    if not n:return {'games':0,'pure_brier':None,'retail_brier':None,'retail_brier_skill':None}
    a=sum((row['pure_probability']-y)**2 for row,y in items)/n
    b=sum((row['retail_probability']-y)**2 for row,y in items)/n
    return {'games':n,'pure_brier':round(a,5),'retail_brier':round(b,5),
            'retail_brier_skill':round(1-a/b,5) if b>0 else None}

def build_scoreboard(root,ledger,now=None):
    forecasts=read_forecasts(root);outcome_file=Path(root)/'observations'/'forecast_outcomes.sqlite';outcomes={}
    if outcome_file.exists():
        with closing(sqlite3.connect(outcome_file)) as db:
            db.row_factory=sqlite3.Row;outcomes={row['game_id']:dict(row) for row in db.execute('SELECT * FROM outcomes')}
    # The first forecast per event is chosen before outcomes are inspected.
    first={}
    for row in sorted(forecasts,key=lambda x:x['captured_at']):
        first.setdefault(row['game_id'],row)
    byleague={league:[] for league in ('NBA','NFL')}
    for game,row in first.items():
        out=outcomes.get(game)
        if not out or (out['home'],out['away'])!=(row['home'],row['away']) or out['home_score']==out['away_score']:continue
        y=1 if out['home_score']>out['away_score'] else 0
        byleague[row['league']].append((row,y))
    report={};test_inputs={}
    for league,items in byleague.items():
        n=len(items);a=sum(_logloss(r['pure_probability'],y) for r,y in items)/n if n else None
        retail=sum(_logloss(r['retail_probability'],y) for r,y in items)/n if n else None
        paper=[p for p in ledger if p.get('model')=='pure-elo-v1' and p.get('league')==league and p.get('outcome') in ('win','loss') and isinstance(p.get('initial_best_odds'),int)]
        returns=[decimal_odds(p['initial_best_odds'])-1 if p['outcome']=='win' else -1.0 for p in paper]
        groups=defaultdict(list)
        for p,value in zip(paper,returns):groups[p.get('pick_day','unknown')].append(value)
        months=defaultdict(list);buckets=defaultdict(list)
        sharp_items=[(row,y) for row,y in items if isinstance(row.get('sharp_probability'),(int,float)) and 0<row['sharp_probability']<1]
        test_inputs[league]=[(row['forecast_key'],row['pure_probability'],row['sharp_probability'],y) for row,y in sharp_items]
        sharp_differences=defaultdict(list)
        for row,y in sharp_items:
            day=aware(row['starts_at']).astimezone(ET).date().isoformat()
            sharp_differences[day].append(_logloss(row['pure_probability'],y)-_logloss(row['sharp_probability'],y))
        sharp_error=None
        try:
            sharp_test=paired_block_test(sharp_differences)
            if sharp_test: sharp_test['difference_interval']=_block_interval(sharp_differences)
        except Exception as exc:
            sharp_test=None;sharp_error=type(exc).__name__
        for row,y in items:
            months[aware(row['starts_at']).astimezone(ET).strftime('%Y-%m')].append((row,y))
            inputs=json.loads(row['feature_snapshot']);h=inputs.get('home_games');a_games=inputs.get('away_games')
            played=min(h,a_games) if isinstance(h,int) and isinstance(a_games,int) else None
            bucket='unknown' if played is None else '0-9' if played<10 else '10-29' if played<30 else '30+'
            buckets[bucket].append((row,y))
        report[league]={'forecast_games':n,'pure_log_loss':round(a,4) if a is not None else None,
                        'retail_log_loss':round(retail,4) if retail is not None else None,
                        'benchmark':'retail median; not a sharp anchor',
                        'sharp_games':len(sharp_items),
                        'sharp_log_loss':round(sum(_logloss(r['sharp_probability'],y) for r,y in sharp_items)/len(sharp_items),4) if sharp_items else None,
                        'sharp_paired_test':sharp_test,'sharp_test_error':sharp_error,
                        'sharp_clv':None,'paper_picks':len(paper),'paper_roi':round(sum(returns)/len(returns),4) if returns else None,
                        'paper_roi_interval':_block_interval(groups),'verdict':'inconclusive',
                        'retail_brier':_retail_brier_summary(items),
                        'retail_brier_by_month':{key:_retail_brier_summary(value) for key,value in months.items()},
                        'retail_brier_by_games_played':{key:_retail_brier_summary(value) for key,value in buckets.items()},
                        'stake_status':'paper','staking_allowed':False}
    adjusted=bh_adjust([report[league]['sharp_paired_test']['p_value'] if report[league]['sharp_paired_test'] else None for league in ('NBA','NFL')])
    for league,q in zip(('NBA','NFL'),adjusted):report[league]['sharp_p_adjusted']=q
    completed=aware(now) if now else datetime.now(timezone.utc)
    path=Path(root)/'observations'/'study_tests'/(completed.date().isoformat()+'.sqlite')
    with closing(_db(path,TEST_SCHEMA)) as db, db:
        for league in ('NBA','NFL'):
            raw=json.dumps(test_inputs[league],sort_keys=True,separators=(',',':'))
            digest=hashlib.sha256(raw.encode()).hexdigest()
            test=report[league]['sharp_paired_test'];error=report[league]['sharp_test_error']
            status='failed' if error else 'completed' if test else 'insufficient_data'
            key=hashlib.sha256(('H004|'+league+'|'+completed.isoformat()+'|'+digest).encode()).hexdigest()
            db.execute('INSERT OR IGNORE INTO test_runs VALUES (?,?,?,?,?,?,?,?,?,?)',
                       (key,'H004',league,completed.isoformat(),digest,status,len(test_inputs[league]),
                        test['p_value'] if test else None,report[league]['sharp_p_adjusted'],json.dumps(test or ({'error':error} if error else {}),sort_keys=True)))
    return report
