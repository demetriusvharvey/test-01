"""H025: free archived NBA first-quarter lineup association research."""
import argparse
import gzip
import hashlib
import io
import json
import math
import sqlite3
import time
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from scripts.line_lab.backfill import SCHEMA
from scripts.line_lab.nba_stints import reconstruct,starter_rosters
from scripts.line_lab.statistics import paired_block_test,bh_adjust

COLUMNS=('game_id','game_date','season','season_type','sequence_number','type_text','period_number',
         'clock_display_value','home_team_id','away_team_id','home_score','away_score','team_id','athlete_id_1','athlete_id_2')


def archive_parquet(root,year):
    import pyarrow as pa
    import pyarrow.parquet as pq
    path=Path(root)/f'observations/backfill/nba_pbp_parquet/{year}.sqlite';path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        with sqlite3.connect(path) as db:row=db.execute('SELECT content_gzip,source_url,sha256,retrieved_at FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
        if row and (year<2027 or (datetime.now(timezone.utc)-datetime.fromisoformat(row[3])).total_seconds()<43200):
            return gzip.decompress(row[0]),{'url':row[1],'sha256':row[2],'observed_at':row[3],'cached':True}
    url=f'https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_pbp/play_by_play_{year}.parquet'
    for attempt in range(2):
        try:
            with urlopen(Request(url,headers={'User-Agent':'MoneylineResearch/1.0','Accept':'application/octet-stream'}),timeout=60) as response:
                payload=response.read(35_000_001);modified=response.headers.get('Last-Modified');etag=response.headers.get('ETag')
            if len(payload)>35_000_000:raise ValueError('parquet exceeds 35MB cap')
            table=pq.ParquetFile(pa.BufferReader(payload));columns=table.schema_arrow.names
            if not set(COLUMNS)<=set(columns) or not table.metadata.num_rows:raise ValueError('parquet schema mismatch')
            break
        except Exception:
            if attempt:raise
            time.sleep(1)
    digest=hashlib.sha256(payload).hexdigest();observed=datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(path) as db:
        db.executescript(SCHEMA)
        db.execute('INSERT OR IGNORE INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                   (digest,'nba_pbp_parquet',str(year),url,observed,modified,etag,
                    'CC-BY-4.0; upstream use review required','SportsDataverse, ESPN source; research only',
                    'retrospective_only','parquet.gz',json.dumps(columns),table.metadata.num_rows,gzip.compress(payload,mtime=0)))
    return payload,{'url':url,'sha256':digest,'observed_at':observed,'cached':False}


def load_stints(root,full=False):
    import pyarrow as pa
    import pyarrow.parquet as pq
    all_stints=[];sources=[];coverage=[];failures=[]
    for year in range(2023,2028):
        try:
            box=Path(root)/f'observations/backfill/nba_player_boxscores/{year}.sqlite'
            if not box.exists():raise ValueError('player starter archive unavailable')
            with sqlite3.connect(box) as db:
                row=db.execute('SELECT content_gzip,source_url,sha256,retrieved_at FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            box_text=gzip.decompress(row[0]).decode('utf-8-sig')
            starters=starter_rosters(box_text)
            payload,source=archive_parquet(root,year);source['starter_source']={'url':row[1],'sha256':row[2],'observed_at':row[3]}
            parquet=pq.ParquetFile(pa.BufferReader(payload))
            events=(r for batch in parquet.iter_batches(batch_size=8192,columns=list(COLUMNS)) for r in batch.to_pylist())
            if full:
                from scripts.line_lab.nba_full_stints import reconstruct_full,box_minutes
                stints,quality=reconstruct_full(events,starters,box_minutes(box_text))
            else:stints,quality=reconstruct(events,starters)
            all_stints.extend(stints)
            sources.append(source);coverage.append({'season_file':year,**quality})
        except Exception as exc:failures.append({'season_file':year,'error':type(exc).__name__})
    return all_stints,sources,coverage,failures


def vocabulary(rows):
    minutes=defaultdict(float)
    for r in rows:
        for p in r['home_players']+r['away_players']:minutes[p]+=r['seconds']/60
    names=sorted(p for p,n in minutes.items() if n>=120)
    return names,dict(minutes)


def known(rows,names):
    names=set(names)
    return [r for r in rows if r['seconds']>=10 and set(r['home_players']+r['away_players'])<=names]


def training_cohort(rows):
    # Retain low-sample players as nuisance controls during fitting. Publishing
    # and evaluation still require 120 actual training minutes per player.
    rows=[r for r in rows if r['seconds']>=10]
    _,minutes=vocabulary(rows)
    return rows,sorted(minutes),minutes


def matrix(rows,names,kind):
    from scipy.sparse import csr_matrix
    index={p:i for i,p in enumerate(names)};data=[];cols=[];offset=[0]
    for r in rows:
        home=r['home_players'] if kind=='player' else [r['home']]
        away=r['away_players'] if kind=='player' else [r['away']]
        for sign,side in ((1,home),(-1,away)):
            for p in side:data.append(sign);cols.append(index[p])
        offset.append(len(data))
    return csr_matrix((data,cols,offset),shape=(len(rows),len(names)),dtype=float)


def target(rows):return [(r['home_points']-r['away_points'])*2880/r['seconds'] for r in rows]
def weights(rows):return [r['seconds']/60 for r in rows]
def mse(rows,predictions):return sum(w*(y-p)**2 for w,y,p in zip(weights(rows),target(rows),predictions))/sum(weights(rows))


def fit(rows,names,alpha,kind):
    from sklearn.linear_model import Ridge
    model=Ridge(alpha=alpha,solver='lsqr',tol=1e-7)
    model.fit(matrix(rows,names,kind),target(rows),sample_weight=weights(rows))
    return model


def run(root,output,full=False):
    root=Path(root);stints,sources,coverage,failures=load_stints(root,full)
    study='H026' if full else 'H025';dataset='nba_full_lineups' if full else 'nba_lineups'
    model_version='nba-full-stint-ridge-v1' if full else 'nba-stint-ridge-v1'
    scope='uniquely reconstructed regulation-game' if full else 'verified first-quarter'
    folder=root/'observations'/dataset;folder.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(json.dumps(stints,sort_keys=True).encode()).hexdigest();version=folder/digest;version.mkdir(exist_ok=True)
    results=[];seasons=sorted({r['season'] for r in stints})
    for season in seasons[2:]:
        earlier=sorted(s for s in seasons if s<season);calibration=earlier[-1]
        train=[r for r in stints if r['season']<calibration]
        train,names,minutes=training_cohort(train)
        supported=[p for p in names if minutes[p]>=120]
        validation=known([r for r in stints if r['season']==calibration],supported)
        test=known([r for r in stints if r['season']==season],supported)
        if len(train)<1000 or len(validation)<500 or not test:
            results.append({'season':season,'status':'insufficient_matched_stints','train':len(train),'validation':len(validation),'test':len(test)});continue
        team_names=sorted({t for r in train for t in (r['home'],r['away'])})
        validation=[r for r in validation if r['home'] in team_names and r['away'] in team_names]
        test=[r for r in test if r['home'] in team_names and r['away'] in team_names]
        if not validation or not test:continue
        models={};scores={};selected={}
        for kind,features in (('player',names),('team',team_names)):
            trials=[]
            for alpha in (100,1000,10000):
                model=fit(train,features,alpha,kind)
                trials.append((mse(validation,model.predict(matrix(validation,features,kind))),alpha,model))
            validation_mse,alpha,model=min(trials,key=lambda x:(x[0],x[1]));selected[kind]=alpha;models[kind]=model
            scores[kind]=model.predict(matrix(test,features,kind)).tolist()
        mean=sum(w*y for w,y in zip(weights(train),target(train)))/sum(weights(train))
        byday=defaultdict(list)
        for r,y,p,t in zip(test,target(test),scores['player'],scores['team']):byday[r['date']].append(r['seconds']/60*((y-p)**2-(y-t)**2))
        comparison=paired_block_test(byday)
        artifact={'model_version':model_version,'features':supported,'weights':[float(v) for p,v in zip(names,models['player'].coef_) if p in set(supported)],
                  'intercept':float(models['player'].intercept_),'alpha':selected['player'],'player_training_minutes':{p:minutes[p] for p in supported},
                  'training_seasons':earlier[:-1],'calibration_season':calibration,'evaluated_season':season,'promoted':False,
                  'units':'net points per 48 minutes; observational '+scope+' association'}
        (version/f'{season}.json').write_text(json.dumps(artifact,sort_keys=True))
        results.append({'season':season,'status':'evaluated','training_stints':len(train),'validation_stints':len(validation),
                        'test_stints':len(test),'test_games':len({r['game_id'] for r in test}),'test_minutes':sum(weights(test)),
                        'players':len(supported),'nuisance_players':len(names)-len(supported),'alpha':selected,'player_mse':mse(test,scores['player']),'team_mse':mse(test,scores['team']),
                        'league_mse':mse(test,[mean]*len(test)),'paired_day_test':comparison,'raw_p':comparison['p_value'] if comparison else None})
    valid=[r for r in results if r['status']=='evaluated']
    prior=[]
    if full and (root/'observations/nba_lineups/current_evaluation.json').exists():
        prior=[r.get('raw_p') for r in json.loads((root/'observations/nba_lineups/current_evaluation.json').read_text())['results']]
    adjusted=bh_adjust(prior+[r['raw_p'] for r in valid])[len(prior):]
    for r,q in zip(valid,adjusted):r['adjusted_p']=q
    # Refitted candidate is explicitly separate from the evaluated fold artifacts.
    # Its effects may be inspected prospectively; no probabilities or promotion.
    now=datetime.now(timezone.utc);from scripts.line_lab.constants import ET
    cutoff=now.astimezone(ET).date().isoformat();past=[r for r in stints if r['date']<cutoff]
    past,names,minutes=training_cohort(past)
    if valid and len(past)>=1000:
        alpha=valid[-1]['alpha']['player'];model=fit(past,names,alpha,'player')
        supported=[p for p in names if minutes[p]>=120]
        artifact={'model_version':model_version,'features':supported,'weights':[float(v) for p,v in zip(names,model.coef_) if p in set(supported)],
                  'intercept':float(model.intercept_),'alpha':alpha,'player_training_minutes':{p:minutes[p] for p in supported},'nuisance_players':len(names)-len(supported),
                  'trained_before_date':cutoff,'exported_at':now.isoformat(),'input_hash':digest,'promoted':False,
                  'units':'net points per 48 minutes; observational '+scope+' association',
                  'limitations':'refitted candidate, selective lineup coverage, unvalidated injury/replacement causality'}
        (version/'refitted_candidate.json').write_text(json.dumps(artifact,sort_keys=True))
        (folder/'current_candidate.json').write_text(json.dumps(artifact,sort_keys=True))
    report={'hypothesis':study,'evaluated_at':now.isoformat(),'input_hash':digest,'sources':sources,'coverage':coverage,
            'failures':failures,'stints':len(stints),'results':results,'promoted':False}
    (version/'evaluation.json').write_text(json.dumps(report,indent=2));(folder/'current_evaluation.json').write_text(json.dumps(report,indent=2))
    lines=['# NBA '+scope+' lineup associations','',f'Run {now.isoformat()}. {study}. Source failures: {len(failures)}.',
           'Source IDs, unique period constraints and explicit substitutions reconstruct stints. Ambiguous games are rejected. Scope: '+scope+'. Full-game mode also validates each player against box minutes and excludes overtime. This is postgame training data, not historical pregame availability. No public pick changes.','',
           '| Source season | Games seen | Accepted | Rejected | Stints |','|---|---:|---:|---:|---:|']
    for r in coverage:lines.append(f"| {r['season_file']} | {r['games_seen']} | {r['accepted_games']} | {r['rejected_games']} | {r['stints']} |")
    lines+=['','| Test season | Status | Matched games | Stints | Player MSE | Team MSE | League MSE | BH p |','|---|---|---:|---:|---:|---:|---:|---:|']
    for r in results:
        if r['status']!='evaluated':lines.append(f"| {r['season']} | {r['status']} | — | {r['test']} | — | — | — | — |");continue
        p='unavailable' if r['adjusted_p'] is None else f"{r['adjusted_p']:.5f}"
        lines.append(f"| {r['season']} | evaluated | {r['test_games']} | {r['test_stints']} | {r['player_mse']:.3f} | {r['team_mse']:.3f} | {r['league_mse']:.3f} | {p} |")
    lines+=['','MSE is minute-weighted squared error in net points per 48 minutes; lower is better. These are stint-rate errors, not game-winner accuracy. Ridge penalties are selected on a distinct prior season. Low-sample players are nuisance controls in training; only effects backed by 120 actual training minutes are published or admitted to validation/test rows. Unknown-player test rows are excluded. This selective coverage must not be described as all-game validation.',
            '', 'Ratings control observed teammates/opponents but remain observational associations. H026 tests are jointly corrected with H025. They are not possession RAPM, complete defensive ratings or causal injury effects. Full-game replacement and probability conversion require separate evaluation. All rejected-game reasons, source hashes, thresholds and fold artifacts are retained. No wagering-source approval or profit is established.',
            '',f'Artifact: observations/{dataset}/{digest}/evaluation.json.','']
    Path(output).write_text('\n'.join(lines));print(json.dumps({'stints':len(stints),'source_failures':failures,'evaluated_folds':len(valid)}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True);ap.add_argument('--full-game',action='store_true')
    args=ap.parse_args();run(args.data_root,args.output,args.full_game)
