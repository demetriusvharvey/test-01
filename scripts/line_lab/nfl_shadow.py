"""Timestamped NFL QB context for shadow research; never an active model input."""
import csv
import gzip
import io
import math, json, hashlib
import sqlite3
from collections import defaultdict
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from .constants import ET, game_id, normalize_code
from .history import aware

SHADOW_SCHEMA='''
CREATE TABLE IF NOT EXISTS qb_snapshots (
 snapshot_key TEXT PRIMARY KEY, season INTEGER NOT NULL, source_retrieved_at TEXT NOT NULL,
 schedule_retrieved_at TEXT NOT NULL, source_sha256 TEXT NOT NULL,
 schedule_sha256 TEXT NOT NULL, summaries_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS qb_no_update BEFORE UPDATE ON qb_snapshots BEGIN SELECT RAISE(ABORT,'QB snapshots are append-only'); END;
CREATE TRIGGER IF NOT EXISTS qb_no_delete BEFORE DELETE ON qb_snapshots BEGIN SELECT RAISE(ABORT,'QB snapshots are append-only'); END;
'''

def _number(value):
    try:
        x=float(value)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError):return None

def _valid_id(value):
    return value if value and value not in ('NA','None','null','') else None

def qb_summaries(pbp_text,schedule_text,source_observed_at,schedule_observed_at,prediction_at):
    """Return only results of earlier completed games seen before prediction."""
    source_time=aware(source_observed_at);schedule_time=aware(schedule_observed_at);prediction=aware(prediction_at)
    if source_time>prediction or schedule_time>prediction or prediction-source_time>timedelta(hours=48):return {}
    prior_day=prediction.astimezone(ET).date().isoformat();completed=set()
    for row in csv.DictReader(io.StringIO(schedule_text)):
        if row.get('gameday','')>=prior_day or not row.get('game_id'):continue
        if _number(row.get('home_score')) is not None and _number(row.get('away_score')) is not None:completed.add(row['game_id'])
    stats=defaultdict(lambda:{'plays':0,'epa_sum':0.0,'cpoe_n':0,'cpoe_sum':0.0,'games':set()})
    for row in csv.DictReader(io.StringIO(pbp_text)):
        quarterback=_valid_id(row.get('passer_player_id'));game=row.get('game_id');team=normalize_code(row.get('posteam',''))
        if not quarterback or not team or game not in completed or str(row.get('pass_attempt')) not in ('1','1.0'):continue
        epa=_number(row.get('qb_epa'))
        if epa is None:epa=_number(row.get('epa'))
        if epa is None:continue
        stat=stats[(team,quarterback)];stat['plays']+=1;stat['epa_sum']+=epa;stat['games'].add(game)
        cpoe=_number(row.get('cpoe'))
        if cpoe is not None:stat['cpoe_n']+=1;stat['cpoe_sum']+=cpoe
    result={}
    for (team,qb),value in stats.items():
        result[(team,qb)]={'pass_plays':value['plays'],'games':len(value['games']),
                           'epa_per_pass':round(value['epa_sum']/value['plays'],5),
                           'epa_shrunk_to_zero':round(value['epa_sum']/(value['plays']+100),5),
                           'cpoe_count':value['cpoe_n'],
                           'cpoe_mean':round(value['cpoe_sum']/value['cpoe_n'],5) if value['cpoe_n'] else None}
    return result

def _latest_pbp(root,year,prediction):
    path=Path(root)/'observations'/'backfill'/'nfl_pbp'/(str(year)+'.sqlite')
    if not path.exists():return None
    with closing(sqlite3.connect(path)) as db:
        row=db.execute('SELECT retrieved_at,sha256,content_gzip FROM assets WHERE retrieved_at<=? ORDER BY retrieved_at DESC LIMIT 1',(aware(prediction).isoformat(),)).fetchone()
    if not row:return None
    return {'retrieved_at':row[0],'sha256':row[1],'text':gzip.decompress(row[2]).decode('utf-8-sig')}

def save_qb_snapshot(root,season,summaries,source_observed_at,schedule_observed_at,source_sha256,schedule_sha256):
    if not summaries:return 0
    source=aware(source_observed_at);schedule=aware(schedule_observed_at)
    payload=[{'team':team,'qb':qb,**value} for (team,qb),value in sorted(summaries.items())]
    serialized=json.dumps(payload,sort_keys=True,separators=(',',':'))
    key=hashlib.sha256((source.isoformat()+'|'+schedule.isoformat()+'|'+source_sha256+'|'+schedule_sha256).encode()).hexdigest()
    path=Path(root)/'observations'/'nfl_qb'/(source.date().isoformat()+'.sqlite');path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript(SHADOW_SCHEMA)
        cursor=db.execute('INSERT OR IGNORE INTO qb_snapshots VALUES (?,?,?,?,?,?,?)',
            (key,season,source.isoformat(),schedule.isoformat(),source_sha256,schedule_sha256,serialized))
        return cursor.rowcount

def _latest_qb_snapshot(root,season,prediction_at):
    prediction=aware(prediction_at);base=Path(root)/'observations'/'nfl_qb';found=[]
    for day in range(3):
        path=base/((prediction.date()-timedelta(days=day)).isoformat()+'.sqlite')
        if not path.exists():continue
        with closing(sqlite3.connect(path)) as db:
            rows=db.execute('SELECT source_retrieved_at,schedule_retrieved_at,source_sha256,summaries_json FROM qb_snapshots WHERE season=?',(season,)).fetchall()
        found.extend(row for row in rows if aware(row[0])<=prediction and aware(row[1])<=prediction and prediction-aware(row[0])<=timedelta(hours=48))
    if not found:return None
    source,schedule,digest,raw=max(found,key=lambda row:aware(row[0]))
    values=json.loads(raw);summary={(v['team'],v['qb']):{k:x for k,x in v.items() if k not in ('team','qb')} for v in values}
    return {'retrieved_at':source,'sha256':digest,'summaries':summary}

def build_nfl_shadow_context(root,schedule_text,schedule_observed_at,prediction_at):
    """Attach observed descriptive QB context; schedules do not confirm starters."""
    prediction=aware(prediction_at);local_day=prediction.astimezone(ET);season=local_day.year if local_day.month>=8 else local_day.year-1
    asset=_latest_qb_snapshot(root,season,prediction_at)
    if asset:summaries=asset['summaries']
    else:
        asset=_latest_pbp(root,season,prediction_at)
        if not asset:return {}
        summaries=qb_summaries(asset['text'],schedule_text,asset['retrieved_at'],schedule_observed_at,prediction_at)
    if not summaries:return {}
    contexts={}
    for row in csv.DictReader(io.StringIO(schedule_text)):
        try:
            game_day=row['gameday'];home=normalize_code(row['home_team']);away=normalize_code(row['away_team'])
            if game_day<prediction.astimezone(ET).date().isoformat():continue
            key=game_id('NFL',game_day,away,home)
            home_qb=_valid_id(row.get('home_qb_id'));away_qb=_valid_id(row.get('away_qb_id'))
            contexts[key]={'status':'shadow_only','source_observed_at':asset['retrieved_at'],'source_sha256':asset['sha256'],
                           'schedule_observed_at':schedule_observed_at,'starter_status':'unconfirmed',
                           'home_qb':summaries.get((home,home_qb)) if home_qb else None,
                           'away_qb':summaries.get((away,away_qb)) if away_qb else None,
                           'weather_status':'not_verified','used_in_prediction':False}
        except (KeyError,TypeError,ValueError):continue
    return contexts
