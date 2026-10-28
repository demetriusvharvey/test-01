"""Read the latest existing research results without inventing statistics."""
import json
import sqlite3
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from .history import aware


def research_dashboard(root,now,lookback_days=90):
    current=aware(now);base=Path(root)/'observations';latest={};replay={}
    for delta in range(lookback_days+1):
        path=base/'pattern_tests'/((current.date()-timedelta(days=delta)).isoformat()+'.sqlite')
        if not path.exists():continue
        with closing(sqlite3.connect(path)) as db:
            for completed,identifier,league,payload in db.execute('SELECT completed_at,hypothesis,league,result_json FROM pattern_runs'):
                try:
                    timestamp=aware(completed);key=(identifier,league);result=json.loads(payload)
                    if timestamp>current or not isinstance(result,dict):continue
                    if key not in latest or timestamp>latest[key][0]:latest[key]=(timestamp,result)
                except (TypeError,ValueError):continue
    path=base/'paper_replay.sqlite'
    if path.exists():
        with closing(sqlite3.connect(path)) as db:
            for completed,league,payload in db.execute('SELECT completed_at,league,result_json FROM replay_runs'):
                try:
                    timestamp=aware(completed);result=json.loads(payload)
                    if timestamp>current or league not in ('NBA','NFL') or not isinstance(result,dict):continue
                    if league not in replay or timestamp>replay[league][0]:replay[league]=(timestamp,result)
                except (TypeError,ValueError):continue
    return {'patterns':[value[1] for key,value in sorted(latest.items())],
            'paper_replay':{key:{'completed_at':value[0].isoformat(),**value[1]} for key,value in replay.items()},
            'status':'descriptive_research_only'}
