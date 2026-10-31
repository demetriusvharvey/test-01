#!/usr/bin/env python3
"""Replay portable inference on a captured slate and hashed historical archives.

This does not claim a new source fetch. --write preserves the slate's original
refresh timestamp and all historical outcomes. Useful for deployment smoke QA.
"""
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.line_lab.constants import ET
from scripts.line_lab.forecast_data import load_archives,assets
from scripts.line_lab.history import aware
from scripts.line_lab.ingest import parse_nfl_locations
from scripts.line_lab.model import train_model
from scripts.line_lab.production import apply_pipeline
from scripts.line_lab.reproducibility import reproduce_pure_elo_v1


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',required=True);parser.add_argument('--board',default='dist/board.json');parser.add_argument('--write',action='store_true');args=parser.parse_args()
    now=datetime.now(timezone.utc).isoformat();board=json.loads(Path(args.board).read_text());old_accuracy=board['accuracy'].copy()
    if not aware(board['generated_at'])<=aware(now):raise ValueError('future captured slate')
    games,stats,hashes,observed=load_archives(args.data_root,now,False)
    models={league:train_model(games,aware(now).astimezone(ET).date(),league) for league in ('NBA','NFL')}
    for league,model in models.items():model['source_hashes']={k:v for k,v in hashes.items() if k.startswith('nba_' if league=='NBA' else 'nfl_')}
    locations={}
    for text,stamp,sha in assets(args.data_root,'nfl_schedules',now):locations.update(parse_nfl_locations(text))
    for game in board['games']:
        if game['league']=='NFL' and game['id'] in locations:game['neutral']=locations[game['id']]
    nba=[{'game_id':r['id'],'predicted_at':r['predicted_at'],'ensemble_scenarios':r['availability_scenarios']}
         for r in board.get('research_forecasts',[]) if r['league']=='NBA' and r.get('availability_scenarios')]
    apply_pipeline(board,models,games,now,args.data_root,nba)
    assert board['accuracy']==old_accuracy
    assert not board['picks'] # Current unpromoted artifacts must never pass.
    for forecast in board['research_forecasts']:
        assert aware(forecast['predicted_at'])<aware(forecast['starts_at'])
        assert abs(reproduce_pure_elo_v1(forecast['incumbent_snapshot'],'home')-forecast['home_probability'])<1e-12
    board['verification']={'verified_at':now,'mode':'captured_slate_replay','source_refresh_timestamp_preserved':True,
                           'forecasts':len(board['research_forecasts']),'legacy_accuracy_preserved':True}
    if args.write:Path(args.board).write_text(json.dumps(board,indent=2)+'\n')
    print(json.dumps(board['verification'],sort_keys=True))

if __name__=='__main__':main()
