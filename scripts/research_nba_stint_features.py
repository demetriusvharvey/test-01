"""H027: season-frozen learned lineup values in chronological NBA forecasts."""
import argparse
import gzip
import hashlib
import json
import math
import sqlite3
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from scripts.research_nba_lineups import load_stints,training_cohort,fit
from scripts.research_simulator import load_games
from scripts.research_nba_boosting import evaluate
from scripts.line_lab.nba_rotation import parse_players
from scripts.line_lab.nba_player_features import historical_features,FEATURES
from scripts.line_lab.nba_statistical import examples,FEATURES as TEAM_FEATURES
from scripts.line_lab.nba_efficiency import enrich_examples,parse_team_stats,METRICS
from scripts.line_lab.nba_inference import probability
from scripts.line_lab.statistics import paired_block_test,bh_adjust


def run(root,output,partial=False):
    root=Path(root);stints,sources,coverage,failures=load_stints(root,full=True,include_warmup=True)
    games,_=load_games(root);players=[];stats={};now=datetime.now(timezone.utc).isoformat()
    study='H028' if partial else 'H027';dataset='nba_partial_stint_features' if partial else 'nba_stint_features'
    base=root/'observations/backfill';folder=root/'observations'/dataset;folder.mkdir(parents=True,exist_ok=True)
    ratings={};rating_folder=folder/'season_ratings';rating_folder.mkdir(exist_ok=True)
    for season in sorted({g['season'] for g in games if g['league']=='NBA'}):
        past,names,minutes=training_cohort([r for r in stints if r['season']<season])
        if len(past)<1000:continue
        model=fit(past,names,1000,'player');supported=[p for p in names if minutes[p]>=120]
        cutoff=min(g['date'] for g in games if g['league']=='NBA' and g['season']==season).isoformat()
        artifact={'model_version':'nba-full-stint-ridge-v1','features':supported,
                  'weights':[float(w) for p,w in zip(names,model.coef_) if p in set(supported)],
                  'player_training_minutes':{p:minutes[p] for p in supported},'alpha':1000,'promoted':False,
                  'trained_before_season':season,'trained_before_date':cutoff,'training_seasons':sorted({r['season'] for r in past}),
                  'exported_at':now,'input_hash':hashlib.sha256(json.dumps(past,sort_keys=True).encode()).hexdigest()}
        ratings[season]=artifact;(rating_folder/(season+'.json')).write_text(json.dumps(artifact,sort_keys=True))
    for source_dataset in ('nba_player_boxscores','nba_team_game_boxscores'):
        for file in sorted((base/source_dataset).glob('*.sqlite')):
            with sqlite3.connect(file) as db:row=db.execute('SELECT content_gzip FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            if not row:continue
            text=gzip.decompress(row[0]).decode('utf-8-sig')
            if source_dataset=='nba_player_boxscores':players.extend(parse_players(text))
            else:stats.update(parse_team_stats(text))
    rated=historical_features(games,players,ratings,partial_coverage=partial);plain=historical_features(games,players)
    rows=[r for r in enrich_examples(examples(games),games,stats) if r['game_id'] in rated and r['game_id'] in plain]
    control=[{**r,'vector':r['vector']+plain[r['game_id']]['vector']} for r in rows]
    extended=[{**r,'vector':r['vector']+rated[r['game_id']]['vector']} for r in rows]
    base_names=list(TEAM_FEATURES)+list(METRICS)+list(FEATURES)
    names=base_names+(['known_stint_component_difference','home_stint_coverage','away_stint_coverage'] if partial else ['lineup_stint_strength_difference'])
    digest=hashlib.sha256(json.dumps(extended,sort_keys=True).encode()).hexdigest();version=folder/digest;version.mkdir(exist_ok=True)
    results=[]
    for season in sorted({g['season'] for g in games if g['league']=='NBA'})[2:]:
        a=evaluate(control,season,version/'control',base_names,model_version='nba-player-box-logistic-v1')
        b=evaluate(extended,season,version/'candidate',names,model_version='nba-partial-stint-logistic-v1' if partial else 'nba-stint-feature-logistic-v1')
        if not a or not b:
            results.append({'season':season,'status':'insufficient_matched_training_calibration_or_test'});continue
        prior=json.loads((version/'control'/season/'logistic.json').read_text());model=json.loads((version/'candidate'/season/'logistic.json').read_text())
        comparison=defaultdict(list);lookup={r['game_id']:r for r in control}
        loss=lambda p,y:-(y*math.log(p)+(1-y)*math.log1p(-p))
        for row in extended:
            if row['season']==season:
                comparison[row['date']].append(loss(probability(model,row['vector']),row['home_win'])-
                                               loss(probability(prior,lookup[row['game_id']]['vector']),row['home_win']))
        test=paired_block_test(comparison)
        results.append({'season':season,'status':'evaluated','control':a,'candidate':b,'day_block_test':test,'raw_p':test['p_value'] if test else None})
    related=[];pointer=root/'observations/nba_player_box/component_predictions.json'
    if pointer.exists():
        h=json.loads(pointer.read_text())['input_hash']
        for path in (root/f'observations/nba_player_box/{h}/evaluation.json',root/f'observations/nba_ensemble/{h}/evaluation.json'):
            if path.exists():related.extend(r.get('raw_p') for r in json.loads(path.read_text())['results'])
    if partial and (root/'observations/nba_stint_features/current_evaluation.json').exists():
        related.extend(r.get('raw_p') for r in json.loads((root/'observations/nba_stint_features/current_evaluation.json').read_text())['results'])
    valid=[r for r in results if r['status']=='evaluated']
    for r,q in zip(valid,bh_adjust(related+[r['raw_p'] for r in valid])[len(related):]):r['adjusted_p_related_outcome_tests']=q
    if valid:
        latest=valid[-1]['season'];model=json.loads((version/'candidate'/latest/'logistic.json').read_text());model['input_hash']=digest
        (folder/'current_candidate.json').write_text(json.dumps(model,sort_keys=True))
    report={'hypothesis':study,'partial_coverage':partial,'evaluated_at':datetime.now(timezone.utc).isoformat(),'matched_games':len(rows),
            'season_counts':{s:sum(r['season']==s for r in rows) for s in sorted({r['season'] for r in rows})},
            'rating_seasons':list(ratings),'sources':sources,'coverage':coverage,'failures':failures,'results':results,'promoted':False}
    if partial and extended:
        report['coverage_summary']={'mean_home_supported_fraction':sum(r['vector'][-2] for r in extended)/len(extended),
                                    'mean_away_supported_fraction':sum(r['vector'][-1] for r in extended)/len(extended),
                                    'fully_supported_games':sum(math.isclose(r['vector'][-1],1) and math.isclose(r['vector'][-2],1) for r in extended)}
    (version/'evaluation.json').write_text(json.dumps(report,indent=2));(folder/'current_evaluation.json').write_text(json.dumps(report,indent=2))
    lines=['# NBA season-frozen lineup values in outcome prediction','',f'Run: {report["evaluated_at"]}. {study}.',
           f'Matched game features: {len(rows)}. Counts: {json.dumps(report["season_counts"],sort_keys=True)}.',
           'Player ratings use strictly earlier seasons; actual same-game participation never becomes a pregame feature. No sample thresholds are lowered to force training. '+('The measured supported subset and two coverage indicators supplement the existing features; unknown individual effects remain unavailable. This partial component is not total lineup value.' if partial else 'Low-support/unseen projected players withhold this model.'),'',
           f'| Season | Status | Games | 27-feature Brier | {len(names)}-feature Brier | Elo Brier | Joint BH p |','|---|---|---:|---:|---:|---:|---:|']
    for r in results:
        if r['status']!='evaluated':lines.append(f"| {r['season']} | {r['status']} | — | — | — | — | — |");continue
        a,b=r['control']['logistic']['calibrated'],r['candidate']['logistic']['calibrated'];p=r['adjusted_p_related_outcome_tests']
        lines.append(f"| {r['season']} | evaluated | {b['games']} | {a['brier']:.5f} | {b['brier']:.5f} | {r['candidate']['elo']['brier']:.5f} | {'unavailable' if p is None else f'{p:.5f}'} |")
    lines+=['','The archive was previously inspected; this is exploratory development, not independent confirmation. Full-game lineup coverage is selective and excludes ambiguous/overtime games. The 2021-22 warm-up source is imported only if available. Missing effects remain missing; no zero replacement value or probability is fabricated. Retrospective source retrieval does not establish historical injury/lineup publication times.','',
            f'Detailed data and any candidate artifact: observations/{dataset}/{digest}/evaluation.json. No public model promotion.','']
    Path(output).write_text('\n'.join(lines));print(json.dumps({'hypothesis':study,'matched_games':len(rows),'evaluated_folds':len(valid),'failures':failures}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True);ap.add_argument('--partial-coverage',action='store_true')
    args=ap.parse_args();run(args.data_root,args.output,args.partial_coverage)
