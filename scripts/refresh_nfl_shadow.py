#!/usr/bin/env python3
"""Capture daily descriptive QB metrics from observed nflverse source data."""
import gzip
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.line_lab.nfl_shadow import qb_summaries, save_qb_snapshot
from scripts.line_lab.availability import capture_nfl_injuries


def fetch(url):
    request=Request(url,headers={'User-Agent':'MoneylineResearch/1.0','Accept':'application/octet-stream,text/csv'})
    with urlopen(request,timeout=90) as response:
        payload=response.read(35_000_001)
        if len(payload)>35_000_000:raise ValueError('source exceeds 35 MB cap')
        return payload,datetime.now(timezone.utc).isoformat()

if __name__=='__main__':
    target=os.environ.get('PICKS_DATA_ROOT')
    if not target:raise SystemExit('PICKS_DATA_ROOT is required')
    day=datetime.now(ZoneInfo('America/New_York'))
    season=day.year if day.month>=8 else day.year-1
    try:
        pbp,pbp_time=fetch(f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz')
        schedule,schedule_time=fetch('https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv')
        now=datetime.now(timezone.utc).isoformat()
        stats=qb_summaries(gzip.decompress(pbp).decode('utf-8-sig'),schedule.decode('utf-8-sig'),pbp_time,schedule_time,now)
        added=save_qb_snapshot(target,season,stats,pbp_time,schedule_time,hashlib.sha256(pbp).hexdigest(),hashlib.sha256(schedule).hexdigest())
        print('NFL QB shadow snapshot:',len(stats),'team/quarterback summaries;',added,'new snapshots. No model inputs promoted.')
    except Exception as exc:
        # URLs may be operationally sensitive in other adapters; log only type.
        print('NFL shadow refresh unavailable:',type(exc).__name__,file=sys.stderr)
        raise SystemExit(1)
    try:
        injury,injury_time=fetch(f'https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_{season}.csv.gz')
        added=capture_nfl_injuries(target,gzip.decompress(injury).decode('utf-8-sig'),season,injury_time,hashlib.sha256(injury).hexdigest())
        print('NFL injury reports:',added,'first-observed rows archived; not used in predictions.')
    except Exception as exc:
        print('NFL injury source unavailable:',type(exc).__name__,file=sys.stderr)
