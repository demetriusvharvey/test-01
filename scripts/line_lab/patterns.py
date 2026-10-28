"""Preregistered H010 batch. Inputs are matched-time and results stay shadow."""
import hashlib
import json
import math
import sqlite3
from collections import defaultdict
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from .constants import ET
from .history import aware
from .statistics import bh_adjust, paired_block_test
from .experiment import _block_interval

DEFINITIONS=[('H010a','NBA','home at least two fewer rest days','negative'),
             ('H010a','NFL','home at least two fewer rest days','negative'),
             ('H010b','NBA','one team on back-to-back','negative'),
             ('H010c','NBA','Pacific road team, early Eastern start','negative'),
             ('H010d','NBA','verified high-altitude Denver/Utah home game','positive'),
             ('H010e','NFL','divisional underdog','positive'),
             ('H010f','NFL','outdoor sustained wind at least 15 mph, underdog','positive'),
             ('H010g','NFL','one confirmed starting-quarterback change','negative'),
             ('H010h','NBA','home team after overtime','negative'),
             ('H010h','NFL','home team after overtime','negative')]
SCHEMA='''
CREATE TABLE IF NOT EXISTS pattern_runs (
 run_key TEXT PRIMARY KEY, completed_at TEXT NOT NULL, input_hash TEXT NOT NULL,
 hypothesis TEXT NOT NULL, league TEXT NOT NULL, result_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS pattern_no_update BEFORE UPDATE ON pattern_runs BEGIN SELECT RAISE(ABORT,'pattern runs are append-only'); END;
CREATE TRIGGER IF NOT EXISTS pattern_no_delete BEFORE DELETE ON pattern_runs BEGIN SELECT RAISE(ABORT,'pattern runs are append-only'); END;
'''


def _eligible(row,cutoff):
    try:
        forecast,start,final,feature,source,fetched=(aware(row[k]) for k in ('forecast_at','starts_at','final_observed_at','features_observed_at','market_source_as_of','market_fetched_at'))
        p=row['market_home_probability'];y=row['home_win']
        return (row.get('rights_verified') is True and feature<=forecast and source<=fetched<=forecast<start<=final<cutoff and forecast-source<=timedelta(minutes=95)
                and isinstance(p,(int,float)) and not isinstance(p,bool) and 0<p<1 and y in (0,1) and bool(row.get('game_id')))
    except (KeyError,TypeError,ValueError):return False


def _side(row,identifier):
    """Return the specified side; unknown/missing/conflicting inputs return None."""
    f=row.get('features') or {};p=row['market_home_probability']
    if identifier=='H010a':
        h,a=f.get('home_rest'),f.get('away_rest')
        return 'home' if isinstance(h,int) and isinstance(a,int) and h-a<=-2 else None
    if identifier=='H010b':
        h,a=f.get('home_b2b'),f.get('away_b2b')
        if not isinstance(h,bool) or not isinstance(a,bool) or h==a:return None
        return 'home' if h else 'away'
    if identifier=='H010c':
        return 'away' if f.get('away_pacific') is True and f.get('venue_eastern') is True and aware(row['starts_at']).astimezone(ET).hour<15 else None
    if identifier=='H010d':
        return 'home' if f.get('home_team') in ('DEN','UTA') and f.get('altitude_verified') is True and f.get('neutral') is False else None
    if identifier=='H010e':
        return ('home' if p<.5 else 'away') if f.get('division_game') is True and p!=.5 else None
    if identifier=='H010f':
        try:
            wind=float(f['wind_mph'])
            if not math.isfinite(wind) or f.get('roof')!='outdoors' or f.get('wind_type')!='sustained' or wind<15 or aware(f['weather_observed_at'])>aware(row['forecast_at']):return None
            return ('home' if p<.5 else 'away') if p!=.5 else None
        except (KeyError,TypeError,ValueError):return None
    if identifier=='H010g':
        try:
            if f.get('qb_status')!='confirmed' or aware(f['qb_observed_at'])>aware(row['forecast_at']):return None
            h,a=f.get('home_qb_changed'),f.get('away_qb_changed')
            if not isinstance(h,bool) or not isinstance(a,bool) or h==a:return None
            return 'home' if h else 'away'
        except (KeyError,TypeError,ValueError):return None
    if identifier=='H010h':return 'home' if f.get('home_last_game_overtime') is True else None
    return None


def analyze(rows,cutoff):
    """First forecast per game is chosen before outcomes; all tests are logged."""
    current=aware(cutoff);eligible=sorted([r for r in rows if _eligible(r,current)],key=lambda r:(aware(r['forecast_at']),r['game_id']))
    first={}
    for row in eligible:first.setdefault(row['game_id'],row)
    results=[]
    for ident,league,description,direction in DEFINITIONS:
        groups=defaultdict(list);seasons=defaultdict(list);error=None
        try:
            for row in first.values():
                if row.get('league')!=league:continue
                side=_side(row,ident)
                if not side:continue
                residual=(row['home_win']-row['market_home_probability'])*(1 if side=='home' else -1)
                day=aware(row['starts_at']).astimezone(ET).date().isoformat()
                groups[day].append(residual);seasons[str(row.get('season','unknown'))].append(residual)
            test=paired_block_test(groups);interval=_block_interval(groups)
        except Exception as exc:test=None;interval=None;error=type(exc).__name__
        samples=sum(len(v) for v in groups.values())
        results.append({'id':ident,'league':league,'description':description,'direction':direction,'games':samples,'days':len(groups),
                        'effect':sum(sum(v) for v in groups.values())/samples if samples else None,'interval':interval,
                        'raw_p':test['p_value'] if test else None,'adjusted_p':None,
                        'seasons':{k:{'games':len(v),'mean_residual':sum(v)/len(v)} for k,v in seasons.items()},
                        'status':'failed' if error else 'candidate_unvalidated' if test else 'not_testable',
                        'error':error,'holdout':'not_tested','promoted':False})
    adjusted=bh_adjust([r['raw_p'] for r in results])
    for r,q in zip(results,adjusted):
        r['adjusted_p']=q
        if q is not None:
            direction_matches=(r['effect']<0) if r['direction']=='negative' else (r['effect']>0)
            r['status']='candidate_unvalidated' if q<=.05 and direction_matches else 'no_detected_effect'
    return results


def append_run(root,rows,results,completed_at):
    if not root:raise ValueError('research storage is required')
    now=aware(completed_at);path=Path(root)/'observations'/'pattern_tests'/(now.date().isoformat()+'.sqlite');path.parent.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest();added=0
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript(SCHEMA)
        for result in results:
            key=hashlib.sha256((now.isoformat()+'|'+digest+'|'+result['id']+'|'+result['league']).encode()).hexdigest()
            added+=db.execute('INSERT OR IGNORE INTO pattern_runs VALUES (?,?,?,?,?,?)',
                (key,now.isoformat(),digest,result['id'],result['league'],json.dumps(result,sort_keys=True))).rowcount
    return added
