"""Point-in-time availability snapshots and unpromoted scenario research."""
import csv
import hashlib
import io
import json
import math
import sqlite3
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from .history import aware

SCHEMA='''
CREATE TABLE IF NOT EXISTS injury_observations (
 observation_key TEXT PRIMARY KEY, season INTEGER NOT NULL, week INTEGER NOT NULL,
 team TEXT NOT NULL, player_id TEXT NOT NULL, position TEXT, name TEXT,
 report_status TEXT, practice_status TEXT, source_modified_raw TEXT,
 observed_at TEXT NOT NULL, source_sha256 TEXT NOT NULL, source TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS injury_lookup ON injury_observations(season,week,team,player_id,observed_at);
CREATE TRIGGER IF NOT EXISTS injury_no_update BEFORE UPDATE ON injury_observations BEGIN SELECT RAISE(ABORT,'injury observations are append-only'); END;
CREATE TRIGGER IF NOT EXISTS injury_no_delete BEFORE DELETE ON injury_observations BEGIN SELECT RAISE(ABORT,'injury observations are append-only'); END;
'''


def capture_nfl_injuries(root,text,season,observed_at,source_sha256):
    """Store first-hand observations, never equate capture time with publication."""
    observed=aware(observed_at)
    rows=list(csv.DictReader(io.StringIO(text)))
    eligible=[]
    for r in rows:
        try:
            if int(r['season'])!=season or not 1<=int(r['week'])<=25:continue
            if not r.get('team') or not r.get('gsis_id') or r['gsis_id'] in ('NA','null'):continue
            eligible.append(r)
        except (KeyError,TypeError,ValueError):continue
    if not eligible:return 0
    latest=max(int(r['week']) for r in eligible)
    eligible=[r for r in eligible if int(r['week'])>=latest-1]
    path=Path(root)/'observations'/'nfl_availability'/(observed.date().isoformat()+'.sqlite')
    path.parent.mkdir(parents=True,exist_ok=True);added=0
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript(SCHEMA)
        for r in eligible:
            values=[season,int(r['week']),r['team'],r['gsis_id'],r.get('position',''),r.get('full_name',''),
                    r.get('report_status',''),r.get('practice_status',''),r.get('date_modified',''),
                    observed.isoformat(),source_sha256,'nflverse injuries; CC BY 4.0; upstream rights review']
            key=hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()
            added+=db.execute('INSERT OR IGNORE INTO injury_observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',[key]+values).rowcount
    return added


def nfl_statuses_as_of(root,season,week,team,prediction_at,starts_at,lookback_days=14,max_age=timedelta(hours=30)):
    """Return observed statuses only; absent players do not imply good health."""
    prediction,start=aware(prediction_at),aware(starts_at)
    if prediction>=start:return {}
    latest={};base=Path(root)/'observations'/'nfl_availability'
    for delta in range(lookback_days+1):
        path=base/((prediction.date()-timedelta(days=delta)).isoformat()+'.sqlite')
        if not path.exists():continue
        with closing(sqlite3.connect(path)) as db:
            db.row_factory=sqlite3.Row
            for row in db.execute('SELECT * FROM injury_observations WHERE season=? AND week=? AND team=?',(season,week,team)):
                value=dict(row); stamp=aware(value['observed_at']); key=value['player_id']
                if stamp>prediction or prediction-stamp>max_age:continue
                if key not in latest or stamp>aware(latest[key][0]['observed_at']):latest[key]=[value]
                elif stamp==aware(latest[key][0]['observed_at']):latest[key].append(value)
    resolved={}
    for key,rows in latest.items():
        statuses={(r.get('report_status') or '').strip().lower() for r in rows if (r.get('report_status') or '').strip()}
        # Conflicting values from the same file are not resolved by guessing.
        result=dict(rows[0]);result['report_status']=next(iter(statuses)) if len(statuses)==1 else None
        result['status_conflict']=len(statuses)>1
        resolved[key]=result
    return resolved


def estimate_play_rate(records,status,cutoff,prior_strength=20,min_records=200):
    """Empirical-Bayes rate using only pregame reports and earlier participation."""
    now=aware(cutoff);eligible=[];seen=set()
    if not isinstance(prior_strength,(int,float)) or not math.isfinite(prior_strength) or prior_strength<=0:return None
    for r in records:
        try:
            report,start,final=(aware(r[k]) for k in ('report_observed_at','starts_at','participation_observed_at'))
            key=(r['game_id'],r['player_id'])
            if key in seen or not report<start<=final<now or r.get('played') not in (0,1):continue
            if r.get('rights_verified') is not True:continue
            seen.add(key);eligible.append(r)
        except (KeyError,TypeError,ValueError):continue
    if len(eligible)<min_records:return None
    bucket=[r for r in eligible if str(r.get('status','')).lower()==str(status).lower()]
    if not bucket:return None
    prior=sum(r['played'] for r in eligible)/len(eligible)
    return {'probability':(sum(r['played'] for r in bucket)+prior_strength*prior)/(len(bucket)+prior_strength),
            'bucket_n':len(bucket),'prior_n':len(eligible),'trained_before':now.isoformat(),
            'status':'shadow_unvalidated','promoted':False}


def scenario_mixture(base_probability,scenarios,player_effects,observed_at,prediction_at,max_scenarios=32):
    """Mix explicit joint scenarios; never invent player impacts or correlation."""
    try:
        if aware(observed_at)>aware(prediction_at):return None
        if not isinstance(base_probability,(int,float)) or not 0<base_probability<1:return None
        if not scenarios or len(scenarios)>max_scenarios:return None
        weights=[float(s['weight']) for s in scenarios]
        if any(not math.isfinite(x) or x<0 for x in weights) or abs(sum(weights)-1)>1e-8:return None
        logit=math.log(base_probability/(1-base_probability));values=[]
        for scenario in scenarios:
            players=scenario['unavailable_players']
            if len(players)!=len(set(players)) or any(p not in player_effects for p in players):return None
            impacts=[float(player_effects[p]) for p in players]
            if any(not math.isfinite(x) for x in impacts):return None
            z=max(-35,min(35,logit+sum(impacts)))
            values.append(1/(1+math.exp(-z)))
        mean=sum(w*p for w,p in zip(weights,values))
        variance=sum(w*(p-mean)**2 for w,p in zip(weights,values))
        return {'expected_probability':mean,'scenario_variance':variance,'scenarios':len(scenarios),
                'status':'shadow_unvalidated','staking_allowed':False}
    except (KeyError,TypeError,ValueError,OverflowError):return None


def news_freshness(latest_news_at,latest_quote_at,prediction_at):
    try:
        news,quote,prediction=(aware(x) for x in (latest_news_at,latest_quote_at,prediction_at))
        if news>prediction or quote>prediction:return 'unknown'
        return 'news_newer_than_quote' if news>quote else 'quote_after_news'
    except (ValueError,TypeError):return 'unknown'
