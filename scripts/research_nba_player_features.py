"""H023: evaluate lagged multi-stat NBA rotation features on matched later games."""
import argparse
import gzip
import hashlib
import json
import math
import sqlite3
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from scripts.research_simulator import load_games
from scripts.research_nba_boosting import evaluate
from scripts.line_lab.nba_statistical import examples,FEATURES as TEAM_FEATURES
from scripts.line_lab.nba_efficiency import enrich_examples,parse_team_stats,METRICS
from scripts.line_lab.nba_rotation import parse_players,rotation_features
from scripts.line_lab.nba_player_features import historical_features,FEATURES as PLAYER_FEATURES
from scripts.line_lab.nba_inference import probability
from scripts.line_lab.statistics import paired_block_test,bh_adjust


def run(root,output):
    root=Path(root);base=root/'observations/backfill';players=[];stats={};sources=[]
    for dataset in ('nba_player_boxscores','nba_team_game_boxscores'):
        for file in sorted((base/dataset).glob('*.sqlite')):
            with sqlite3.connect(file) as db:
                row=db.execute('SELECT content_gzip,source_url,sha256,retrieved_at FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            if not row:continue
            text=gzip.decompress(row[0]).decode('utf-8-sig')
            if dataset=='nba_player_boxscores':players.extend(parse_players(text))
            else:stats.update(parse_team_stats(text))
            sources.append({'url':row[1],'sha256':row[2],'observed_at':row[3]})
    games,_=load_games(root);old=rotation_features(games,players);new=historical_features(games,players)
    rows=[r for r in enrich_examples(examples(games),games,stats) if r['game_id'] in old and r['game_id'] in new]
    rotation=[{**r,'vector':r['vector']+old[r['game_id']]['vector']} for r in rows]
    extended=[{**r,'vector':r['vector']+new[r['game_id']]['vector']} for r in rows]
    names=list(TEAM_FEATURES)+list(METRICS)+list(PLAYER_FEATURES)
    digest=hashlib.sha256(json.dumps(extended,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    folder=root/'observations/nba_player_box'/digest;folder.mkdir(parents=True,exist_ok=True)
    results=[]
    for season in sorted({r['season'] for r in rows})[2:]:
        team=evaluate(rows,season)
        old_result=evaluate(rotation,season,folder/'rotation',list(TEAM_FEATURES)+list(METRICS)+list(PLAYER_FEATURES[:3]))
        candidate=evaluate(extended,season,folder/'multistat',names,model_version='nba-player-box-logistic-v1')
        if not (team and old_result and candidate):continue
        old_model=json.loads((folder/'rotation'/season/'logistic.json').read_text())
        new_model=json.loads((folder/'multistat'/season/'logistic.json').read_text())
        byday=defaultdict(list)
        old_rows={r['game_id']:r for r in rotation if r['season']==season}
        loss=lambda p,y:-(y*math.log(max(1e-6,min(1-1e-6,p)))+(1-y)*math.log(max(1e-6,min(1-1e-6,1-p))))
        for r in extended:
            if r['season']!=season:continue
            byday[r['date']].append(loss(probability(new_model,r['vector']),r['home_win'])-
                                    loss(probability(old_model,old_rows[r['game_id']]['vector']),r['home_win']))
        test=paired_block_test(byday)
        results.append({'season':season,'team':team,'rotation':old_result,'multistat':candidate,
                        'log_loss_day_block_test':test,'raw_p':test['p_value'] if test else None})
    for r,q in zip(results,bh_adjust([r['raw_p'] for r in results])):r['adjusted_p']=q
    checked=datetime.now(timezone.utc).isoformat()
    report={'hypothesis':'H023','evaluated_at':checked,'input_hash':digest,'features':names,
            'parsed_players':len(players),'matched_games':len(rows),'sources':sources,'results':results,
            'promoted':False,'missing':['verified historical pregame rosters/injuries','complete defensive impact',
                                        'validated replacement effects','untouched forward confirmation','qualified wagering use']}
    (folder/'evaluation.json').write_text(json.dumps(report,indent=2))
    if results:
        latest=results[-1]['season'];model=json.loads((folder/'multistat'/latest/'logistic.json').read_text())
        model['input_hash']=digest
        (folder.parent/'current_candidate.json').write_text(json.dumps(model,sort_keys=True))
    lines=['# NBA multi-stat player rotation comparison','',f'Run: {checked}. Hypothesis H023.',
           f'Parsed played-player rows: {len(players)}. Identical matched modeling games: {len(rows)}.',
           'Separate older training, prior-season calibration and later-season testing. Archive previously inspected; exploratory only. All metrics use identical games. No public pick is changed.','',
           '| Season | Games | Team Brier | Rotation Brier | Multi-stat Brier | Elo Brier | Multi-stat accuracy | Log loss delta vs rotation | Raw p | BH p |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    fmt=lambda value:'unavailable' if value is None else f'{value:.5f}'
    for r in results:
        a,b,c=[r[k]['logistic']['calibrated'] for k in ('team','rotation','multistat')]
        lines.append(f"| {r['season']} | {c['games']} | {a['brier']:.5f} | {b['brier']:.5f} | {c['brier']:.5f} | {r['multistat']['elo']['brier']:.5f} | {c['accuracy']:.5f} | {c['log_loss']-b['log_loss']:.5f} | {fmt(r['raw_p'])} | {fmt(r['adjusted_p'])} |")
    lines+=['','A negative log-loss delta favors the candidate. BH adjustment covers every season reported for H023; prior archived hypotheses are not independent confirmation. Boosting metrics and all failures are retained in the machine-readable evaluation.',
            '', 'The learner estimates coefficients for projected box statistics; it does not estimate causal player values. Prior per-minute rates feed projected rotations with minutes conserved. Missing player statistics withhold the multi-stat projection instead of becoming zero. Current injury scenarios use the same summary definitions and enumerate listed uncertain players without fabricated weights.',
            '', 'Steals, blocks and rebounds do not capture all defense. Historical rosters and availability are inferred/unknown. Current source timestamps do not establish historical pregame publication. No ROI or source-use approval is established.',
            '', f'Detailed artifact: observations/nba_player_box/{digest}/evaluation.json. Trained artifacts remain separate and disabled for public picks.','']
    Path(output).write_text('\n'.join(lines))
    print(json.dumps({'hypothesis':'H023','player_rows':len(players),'matched_games':len(rows),'evaluated_seasons':len(results),'promoted':False}))
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();run(args.data_root,args.output)
