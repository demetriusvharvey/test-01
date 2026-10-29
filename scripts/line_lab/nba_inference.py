"""Timestamped NBA ML inference, separate from production winner selection."""
import gzip
import hashlib
import json
import math
import sqlite3
from pathlib import Path
from datetime import date,timedelta
from .constants import ET
from .history import aware
from .nba_statistical import examples
from .nba_efficiency import parse_team_stats,enrich_examples


def probability(model,vector):
    n=len(vector)
    if any(len(model[k])!=n for k in ('features','mean','scale','weights')):raise ValueError('feature dimensions')
    numbers=list(vector)+list(model['mean'])+list(model['scale'])+list(model['weights'])+[model[k] for k in ('intercept','calibration_intercept','calibration_weight')]
    if not n or any(type(x) not in (int,float) or not math.isfinite(x) for x in numbers) or any(x<=0 for x in model['scale']):raise ValueError('invalid input or artifact')
    z=float(model['intercept'])+sum(w*(x-m)/s for w,x,m,s in zip(model['weights'],vector,model['mean'],model['scale']))
    # Match sklearn clipping before the calibration logit.
    p=1/(1+math.exp(-max(-35,min(35,z))));p=max(1e-6,min(1-1e-6,p))
    calibrated=model['calibration_intercept']+model['calibration_weight']*math.log(p/(1-p))
    return 1/(1+math.exp(-max(-35,min(35,calibrated))))


def record_nba_predictions(root,games,scheduled,now,injury_payload=None,injury_observed_at=None):
    path=Path(root)/'observations/nba_statistical/current_candidate.json'
    if not path.exists():return {'status':'model_unavailable','predictions':[]}
    model=json.loads(path.read_text());current=aware(now);cutoff=current.astimezone(ET).date()
    if model.get('model_version')!='nba-efficiency-logistic-v1' or model.get('promoted') is not False or aware(model['exported_at'])>current:
        raise ValueError('unusable research artifact')
    past=[g for g in games if g['league']=='NBA' and g['date']<cutoff]
    events={}
    for game in scheduled:
        if game['league']!='NBA' or not current<aware(game['starts_at'])<=current+timedelta(days=8):continue
        _,_,away,home=game['id'].split(':')
        events[game['id']]={**game,'home':home,'away':away,'date':aware(game['starts_at']).astimezone(ET).date(),
                            'season':str(cutoff.year if cutoff.month>=8 else cutoff.year-1)+'-'+str((cutoff.year+1) if cutoff.month>=8 else cutoff.year)[-2:],
                            'upcoming':True,'neutral':game.get('neutral',False)}
    stats={};source_times=[]
    for file in sorted((Path(root)/'observations/backfill/nba_team_game_boxscores').glob('*.sqlite')):
        with sqlite3.connect(file) as db:
            row=db.execute('SELECT content_gzip,retrieved_at FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
        if row and aware(row[1])<=current:
            stats.update(parse_team_stats(gzip.decompress(row[0]).decode('utf-8-sig')));source_times.append(row[1])
    combined=past+list(events.values())
    rows=enrich_examples(examples(combined),combined,stats);predictions=[]
    rotation_model_path=Path(root)/'observations/nba_rotation/current_candidate.json'
    rotation_model=json.loads(rotation_model_path.read_text()) if rotation_model_path.exists() else None
    player_model_path=Path(root)/'observations/nba_player_box/current_candidate.json'
    player_model=json.loads(player_model_path.read_text()) if player_model_path.exists() else None
    ensemble_path=Path(root)/'observations/nba_ensemble/current_candidate.json'
    ensemble_model=json.loads(ensemble_path.read_text()) if ensemble_path.exists() else None
    players=[];rosters={}
    if (rotation_model or player_model) and injury_payload:
        from .nba_rotation import parse_players
        from .nba_lineup import parse_current_rosters
        for file in sorted((Path(root)/'observations/backfill/nba_player_boxscores').glob('*.sqlite')):
            with sqlite3.connect(file) as db:
                r=db.execute('SELECT content_gzip,retrieved_at FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            if r and aware(r[1])<=current:players.extend(parse_players(gzip.decompress(r[0]).decode('utf-8-sig')))
        roster_year=cutoff.year+int(cutoff.month>=8)
        file=Path(root)/f'observations/backfill/nba_roster_snapshots/{roster_year}.sqlite'
        if file.exists():
            with sqlite3.connect(file) as db:
                r=db.execute('SELECT content_gzip,retrieved_at,source_url,sha256 FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            if r and aware(r[1])<=current:
                from .nba_refresh import roster_observed_at
                observed=roster_observed_at(root,r[2],r[3],r[1])
                if aware(observed)<=current:rosters=parse_current_rosters(gzip.decompress(r[0]).decode('utf-8-sig'),observed,r[2])
    for row in rows:
        if row['game_id'] not in events:continue
        p=probability(model,row['vector']);event=events[row['game_id']]
        predictions.append({'game_id':row['game_id'],'predicted_at':now,'starts_at':event['starts_at'],
            'model_version':model['model_version'],'model_input_hash':model['input_hash'],
            'model_exported_at':model['exported_at'],'input_data_observed_at':max(source_times) if source_times else None,
            'home_probability':p,'away_probability':1-p,'baseline_elo_probability':row['elo'],'home':event['home'],'away':event['away'],
            'features':dict(zip(model['features'],row['vector'])),'used_in_public_picks':False,
            'missing_inputs':['injury-adjusted lineup','replacement impact','travel'],
            'uncertainty':'retrospective calibration; predictive intervals and forward accuracy unestablished'})
        if rotation_model:
            from .nba_scenarios import conditional_forecasts
            predictions[-1]['availability_scenarios']=conditional_forecasts(
                rotation_model,row['vector'],event,players,rosters,injury_payload,injury_observed_at,now,probability)
        if player_model:
            from .nba_scenarios import conditional_forecasts
            predictions[-1]['player_box_scenarios']=conditional_forecasts(
                player_model,row['vector'],event,players,rosters,injury_payload,injury_observed_at,now,probability)
        if ensemble_model:
            from .nba_ensemble import conditional_ensemble
            predictions[-1]['ensemble_scenarios']=conditional_ensemble(ensemble_model,p,row['elo'],
                predictions[-1].get('availability_scenarios'),predictions[-1].get('player_box_scenarios'),event,now)
    folder=Path(root)/'observations/nba_ml_predictions';folder.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(folder/(current.date().isoformat()+'.sqlite')) as db:
        db.executescript("""CREATE TABLE IF NOT EXISTS predictions (key TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS np_no_update BEFORE UPDATE ON predictions BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS np_no_delete BEFORE DELETE ON predictions BEGIN SELECT RAISE(ABORT,'immutable'); END;""")
        for row in predictions:
            content=json.dumps(row,sort_keys=True);key=hashlib.sha256(content.encode()).hexdigest()
            db.execute('INSERT OR IGNORE INTO predictions VALUES (?,?)',(key,content))
    return {'status':'research_forecasts_recorded','predictions':predictions}
