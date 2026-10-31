"""Read hashed cached public archives; never synthesize missing news or prices."""
import csv,gzip,io,sqlite3,hashlib
from collections import defaultdict
from pathlib import Path
from datetime import date
from .ingest import parse_nba_csv,parse_nfl_csv
from .nba_efficiency import parse_team_stats
from .constants import normalize_code
from .history import aware


def assets(root,dataset,now=None):
    for file in sorted((Path(root)/'observations/backfill'/dataset).glob('*.sqlite')):
        with sqlite3.connect(file) as db:
            rows=db.execute('SELECT content_gzip,retrieved_at,sha256 FROM assets ORDER BY retrieved_at DESC').fetchall()
        row=next((r for r in rows if now is None or aware(r[1])<=aware(now)),None)
        if row:
            content=gzip.decompress(row[0])
            if row[2] not in (hashlib.sha256(content).hexdigest(),hashlib.sha256(row[0]).hexdigest()):raise ValueError('archive hash mismatch')
            if content.startswith(b'\x1f\x8b'):content=gzip.decompress(content)
            yield content.decode('utf-8-sig'),row[1],row[2]


def nfl_team_stats(text):
    totals=defaultdict(lambda:[0.,0.,0.,0.,0.,0.,0.,0.])
    for r in csv.DictReader(io.StringIO(text)):
        if r.get('season_type') not in ('REG','POST') or r.get('play_type') not in ('run','pass'):continue
        if r.get('qb_kneel')=='1' or r.get('qb_spike')=='1':continue
        try:
            day=date.fromisoformat(r['game_date']);off=normalize_code(r['posteam']);defense=normalize_code(r['defteam'])
            epa=float(r['epa']);success=float(r.get('success') or (epa>0))
            import math
            if not off or not defense or not math.isfinite(epa) or success not in (0,1):continue
            a=totals[(day,off)];b=totals[(day,defense)]
            a[0]+=epa;a[1]+=1;a[4]+=success;b[2]+=epa;b[3]+=1;b[5]+=success
            if r['play_type']=='pass':a[6]+=epa
            else:a[7]+=epa
        except (KeyError,ValueError,TypeError):continue
    # Passing/rushing EPA per all offensive plays preserves pace mix and avoids
    # filling a no-pass game with an unsupported conditional average.
    return {key:[v[0]/v[1],v[2]/v[3],v[4]/v[1],v[5]/v[3],v[6]/v[1],v[7]/v[1]]
            for key,v in totals.items() if v[1]>=10 and v[3]>=10}


def load_archives(root,now=None,include_pbp=True):
    games=[];stats={'NBA':{},'NFL':{}};hashes={};observed=[]
    for dataset,parser,league in [('nba_team_game_boxscores',parse_nba_csv,'NBA'),('nfl_schedules',parse_nfl_csv,'NFL')]:
        for text,stamp,sha in assets(root,dataset,now):
            games.extend(parser(text));hashes[dataset+':'+sha]=sha;observed.append(stamp)
            if league=='NBA':stats['NBA'].update(parse_team_stats(text))
    if include_pbp:
        for text,stamp,sha in assets(root,'nfl_pbp',now):
            stats['NFL'].update(nfl_team_stats(text));hashes['nfl_pbp:'+sha]=sha;observed.append(stamp)
    unique={}
    for g in games:
        if g['id'] in unique and unique[g['id']]!=g:raise ValueError('conflicting archive game')
        unique[g['id']]=g
    return list(unique.values()),stats,hashes,max(observed) if observed else None
