"""Prospective matched-time challenger evaluation; no automatic model promotion."""
import hashlib
import json
import math
import sqlite3
from collections import defaultdict
from contextlib import closing
from pathlib import Path

from .constants import ET
from .experiment import _block_interval, _logloss, read_forecasts, corroborated_nfl_outcomes
from .history import aware
from .model_stack import FORBIDDEN
from .statistics import bh_adjust, paired_block_test

SCHEMA='''
CREATE TABLE IF NOT EXISTS challenger_tests (
 run_key TEXT PRIMARY KEY, completed_at TEXT NOT NULL, league TEXT NOT NULL,
 model_version TEXT NOT NULL, input_hash TEXT NOT NULL, status TEXT NOT NULL,
 games INTEGER NOT NULL, raw_p REAL, adjusted_p REAL, result_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS challenger_tests_no_update BEFORE UPDATE ON challenger_tests BEGIN SELECT RAISE(ABORT,'tests are append-only'); END;
CREATE TRIGGER IF NOT EXISTS challenger_tests_no_delete BEFORE DELETE ON challenger_tests BEGIN SELECT RAISE(ABORT,'tests are append-only'); END;
'''


def read_inputs(root,as_of=None):
    root=Path(root);baselines=read_forecasts(root);candidates=[];trials={};outcomes={}
    for path in sorted((root/'observations/challenger_forecasts').glob('*.sqlite')):
        with closing(sqlite3.connect(path)) as db:
            db.row_factory=sqlite3.Row;candidates.extend(dict(x) for x in db.execute('SELECT * FROM challenger_forecasts'))
    path=root/'observations/model_registry.sqlite'
    if path.exists():
        with closing(sqlite3.connect(path)) as db:
            db.row_factory=sqlite3.Row
            for row in db.execute("SELECT * FROM trials WHERE status='candidate'"):
                try:
                    trial=dict(row);trial['artifact']=json.loads(trial['artifact_json']);trials[trial['trial_id']]=trial
                except (ValueError,TypeError):continue
    path=root/'observations/forecast_outcomes.sqlite'
    if path.exists():
        with closing(sqlite3.connect(path)) as db:
            db.row_factory=sqlite3.Row;outcomes={r['game_id']:dict(r) for r in db.execute('SELECT * FROM outcomes')}
    if as_of is not None:
        # NBA remains ineligible; NFL research needs a later nflverse source
        # corroboration without rewriting its first reported final.
        confirmed=corroborated_nfl_outcomes(root,as_of)
        nba_ids={row['game_id'] for row in baselines if row.get('league')=='NBA'}
        outcomes={key:value for key,value in outcomes.items() if key in nba_ids}
        outcomes.update(confirmed)
    return baselines,candidates,trials,outcomes


def evaluate(baselines,candidates,trials,outcomes,now):
    """Fix first candidate per game/version before inspecting finals or fit."""
    cutoff=aware(now);same_time={(b['game_id'],b['league'],b['captured_at']):b for b in baselines}
    first={};versions=set()
    for row in sorted(candidates,key=lambda x:x.get('captured_at','')):
        trial=trials.get(row.get('model_id'));model=(trial or {}).get('artifact',{})
        version=model.get('model_version');league=row.get('league')
        if not version or league not in ('NBA','NFL') or not row.get('game_id'):continue
        versions.add((league,version));first.setdefault((league,version,row['game_id']),row)
    # Both league hypotheses exist even when no candidate has qualified yet.
    versions.update((league,version) for league in ('NBA','NFL') for version in ('pure-elasticnet-v1','pure-stumpboost-v1','availability-logistic-v1'))
    versions.add(('NFL','nfl-position-status-logistic-v1'))
    matched=defaultdict(list);excluded=defaultdict(int)
    for (league,version,game_id),row in first.items():
        key=(league,version);trial=trials.get(row.get('model_id'),{});model=trial.get('artifact',{})
        base=same_time.get((game_id,league,row.get('captured_at')));out=outcomes.get(game_id)
        try:
            captured=aware(row['captured_at']);start=aware(row['starts_at'])
            if not captured<start<=cutoff or not base or not out:raise ValueError('not settled or unmatched')
            if aware(trial['completed_at'])>captured or aware(model['trained_before'])>=captured:raise ValueError('training after prediction')
            if model.get('promoted') is not False or any(any(word in f.lower() for word in FORBIDDEN) for f in model['features']):raise ValueError('not pure shadow model')
            if aware(out['observed_at'])<start or aware(out['observed_at'])>cutoff:raise ValueError('invalid outcome time')
            if (base['home'],base['away'])!=(out['home'],out['away']) or aware(base['starts_at'])!=start:raise ValueError('game mismatch')
            if out['home_score']==out['away_score']:raise ValueError('tie')
            # Only rights-screened NFL outcomes currently qualify; NBA is blocked.
            features=json.loads(base['feature_snapshot'])
            if league!='NFL' or out.get('source')!='nflverse' or not features.get('source_text_sha256',{}).get('games.csv'):
                raise ValueError('source rights/timing not established')
            if version in ('availability-logistic-v1','nfl-position-status-logistic-v1'):
                if version=='availability-logistic-v1':
                    from .availability_model import FEATURES
                    source_key='availability';schema='availability-counts-v1'
                else:
                    from .position_status_model import FEATURES
                    source_key='nfl_position_status';schema='nfl-position-status-v1'
                observed=(features.get('shadow_context') or {}).get(source_key) or {}
                candidate_features=json.loads(row['feature_json'])
                if observed.get('schema')!=schema or observed.get('used_in_prediction') is not False:
                    raise ValueError('availability snapshot missing')
                if observed.get('source')!='nflverse injury and practice reports' or aware(observed['observed_at'])>captured:
                    raise ValueError('availability source or timestamp invalid')
                if candidate_features.get('availability_source')!=observed['source'] or candidate_features.get('availability_observed_at')!=observed['observed_at']:
                    raise ValueError('availability provenance mismatch')
                if any(candidate_features.get(name)!=observed['features'].get(name) for name in FEATURES):
                    raise ValueError('availability feature mismatch')
                if not math.isclose(float(candidate_features['baseline_probability']),float(base['pure_probability']),rel_tol=1e-12,abs_tol=1e-12):
                    raise ValueError('baseline mismatch')
            p=float(row['probability']);reference=float(base['pure_probability'])
            if not 0<p<1 or not 0<reference<1 or not math.isfinite(p+reference):raise ValueError('invalid probability')
            y=int(out['home_score']>out['away_score'])
            matched[key].append({'game_id':game_id,'captured_at':row['captured_at'],'starts_at':row['starts_at'],
                                 'model_id':row['model_id'],'candidate':p,'baseline':reference,'outcome':y})
        except (KeyError,TypeError,ValueError,json.JSONDecodeError):
            excluded[key]+=1
    result=[]
    for league,version in sorted(versions):
        key=(league,version);rows=matched[key];groups=defaultdict(list)
        for row in rows:
            day=aware(row['starts_at']).astimezone(ET).date().isoformat()
            groups[day].append(_logloss(row['candidate'],row['outcome'])-_logloss(row['baseline'],row['outcome']))
        n=len(rows);test=paired_block_test(groups)
        result.append({'league':league,'model_version':version,'games':n,'excluded':excluded[key],
                       'days':len(groups),'logloss_difference':sum(sum(x) for x in groups.values())/n if n else None,
                       'difference_interval':_block_interval(groups),'raw_p':test['p_value'] if test else None,
                       'brier_difference':sum((r['candidate']-r['outcome'])**2-(r['baseline']-r['outcome'])**2 for r in rows)/n if n else None,
                       'status':'descriptive_only' if test else 'insufficient_data',
                       'promoted':False,'input_hash':hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()})
    # H016's two league tests form a family distinct from H011's model family.
    for family in ('H011','H016'):
        group=[item for item in result if ('H016' if item['model_version'] in ('availability-logistic-v1','nfl-position-status-logistic-v1') else 'H011')==family]
        for item,q in zip(group,bh_adjust([r['raw_p'] for r in group])):item['adjusted_p']=q
    return result


def append_results(root,results,now):
    path=Path(root)/'observations/challenger_tests.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path)) as db,db:
        db.executescript(SCHEMA)
        for result in results:
            key=hashlib.sha256((now+'|'+result['league']+'|'+result['model_version']+'|'+result['input_hash']).encode()).hexdigest()
            db.execute('INSERT OR IGNORE INTO challenger_tests VALUES (?,?,?,?,?,?,?,?,?,?)',
                       (key,now,result['league'],result['model_version'],result['input_hash'],result['status'],
                        result['games'],result['raw_p'],result['adjusted_p'],json.dumps(result,sort_keys=True)))
