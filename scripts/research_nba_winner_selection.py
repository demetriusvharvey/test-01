"""H029: compare daily top-three winners; no public model promotion."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from scripts.research_simulator import load_games
from scripts.line_lab.nba_winner_selection import compare_historical,MODELS
from scripts.line_lab.statistics import bh_adjust


def run(root,output):
    root=Path(root);source=json.loads((root/'observations/nba_partial_stint_features/winner_components.json').read_text())
    games,_=load_games(root);results=compare_historical(source['rows'],games);related=[]
    pointer=root/'observations/nba_player_box/component_predictions.json'
    if pointer.exists():
        h=json.loads(pointer.read_text())['input_hash']
        for path in (root/f'observations/nba_player_box/{h}/evaluation.json',root/f'observations/nba_ensemble/{h}/evaluation.json'):
            if path.exists():related.extend(r.get('raw_p') for r in json.loads(path.read_text())['results'])
    for dataset in ('nba_stint_features','nba_partial_stint_features'):
        path=root/f'observations/{dataset}/current_evaluation.json'
        if path.exists():related.extend(r.get('raw_p') for r in json.loads(path.read_text())['results'])
    tests=[r['models'][name] for r in results for name in MODELS if name!='elo']
    for test,q in zip(tests,bh_adjust(related+[t['raw_p'] for t in tests])[len(related):]):test['adjusted_p_related_tests']=q
    now=datetime.now(timezone.utc).isoformat();report={'hypothesis':'H029','evaluated_at':now,'source_input_hash':source['input_hash'],
        'policy':'up to three highest model winner probabilities, threshold 0.50; 50/50 abstains',
        'results':results,'promoted':False,'limitations':['complete dates relative to archive, not independently verified historical schedules',
        'previously inspected archives, not untouched confirmation','historical availability unverified; not an injury-policy backtest','no odds or ROI']}
    folder=root/'observations/nba_winner_selection'/source['input_hash'];folder.mkdir(parents=True,exist_ok=True)
    (folder/'evaluation.json').write_text(json.dumps(report,indent=2));(folder.parent/'current_evaluation.json').write_text(json.dumps(report,indent=2))
    lines=['# NBA daily winner ranking comparison','',f'Run {now}. H029.',
        'Fixed top-three winner ranking, no sportsbook input. All four models use the same complete archived dates. This evaluates the daily selection objective, not betting profitability.','',
        '| Season | Model | Complete / archive days | Selected | Accuracy | Day-block 95% interval | Selected Brier | Joint BH p |',
        '|---|---|---:|---:|---:|---|---:|---:|']
    fmt=lambda v:'unavailable' if v is None else f'{v:.5f}'
    for r in results:
        for name in MODELS:
            m=r['models'][name];p=m['primary'];ci=m['accuracy_interval'];interval=f"{ci['lower']:.3f}–{ci['upper']:.3f}" if ci else 'insufficient sample'
            lines.append(f"| {r['season']} | {name} | {r['complete_days']} / {r['archived_days']} | {p['games']} | {fmt(p['accuracy'])} | {interval} | {fmt(p['brier'])} | {fmt(m.get('adjusted_p_related_tests'))} |")
    lines+=['','Intervals resample entire calendar days using a fixed seed; small samples receive no interval. Paired tests compare selected outcomes on matched dates; models may choose different games. Multiple-test adjustment includes the related earlier outcome studies. Calibration bins and fixed-threshold coverage tables are retained in the artifact; thresholds are not optimized on these test results.',
        '', 'Archive coverage is not a verified historical schedule. A missing model/game excludes the entire date from the primary comparison, and exclusion counts are retained. The historical model features inferred membership and unknown historical availability; current conditional injury ranking is a separate forward policy. Previously inspected seasons are exploratory. No public record changes, model promotion, odds-based edge or ROI claim.',
        '',f'Artifact: observations/nba_winner_selection/{source["input_hash"]}/evaluation.json.','']
    Path(output).write_text('\n'.join(lines));print(json.dumps({'hypothesis':'H029','seasons':len(results),'promoted':False}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();run(args.data_root,args.output)
