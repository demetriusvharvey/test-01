"""H024: chronological ensemble evaluation; preserve failures, never promote."""
import argparse
import json
import math
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from scripts.line_lab.nba_ensemble import walk_forward
from scripts.line_lab.statistics import paired_block_test,bh_adjust


def run(root,output):
    root=Path(root);source=root/'observations/nba_player_box/component_predictions.json'
    data=json.loads(source.read_text());results=walk_forward(data['rows'])
    prior=json.loads((source.parent/data['input_hash']/'evaluation.json').read_text())
    family=[r['raw_p'] for r in prior['results']]
    for r in results:
        byday=defaultdict(list)
        loss=lambda p,y:-(y*math.log(p)+(1-y)*math.log1p(-p))
        for p in r['predictions']:byday[p['date']].append(loss(p['probability'],p['home_win'])-loss(p['probabilities']['elo'],p['home_win']))
        test=paired_block_test(byday);r['day_block_test']=test;r['raw_p']=test['p_value'] if test else None
        family.append(r['raw_p'])
    adjusted=bh_adjust(family)[len(prior['results']):]
    for r,q in zip(results,adjusted):r['adjusted_p_h023_h024']=q
    folder=root/'observations/nba_ensemble'/data['input_hash'];folder.mkdir(parents=True,exist_ok=True)
    now=datetime.now(timezone.utc).isoformat()
    report={'hypothesis':'H024','evaluated_at':now,'input_hash':data['input_hash'],'results':results,
            'correction_family':'H023 and H024 reported season tests','promoted':False,
            'limitations':['previously inspected archive','correlated components','no market or simulation input',
                          'no independent future confirmation','conditional ranges are not weighted availability probabilities']}
    (folder/'evaluation.json').write_text(json.dumps(report,indent=2))
    if results:
        model={**results[-1]['model'],'exported_at':now,'evaluated_season':results[-1]['season']}
        (folder.parent/'current_candidate.json').write_text(json.dumps(model,sort_keys=True))
    lines=['# NBA chronological statistical ensemble','',f'Run: {now}. H024 was registered after inspecting H023.',
           'Weights are learned from earlier held-out component predictions only. All test comparisons use identical games. The previously inspected archive is exploratory, not independent confirmation.','',
           '| Season | Games | Ensemble Brier | Elo Brier | Ensemble log loss | Elo log loss | Earlier-selected component | Raw p | Joint BH p |',
           '|---|---:|---:|---:|---:|---:|---|---:|---:|']
    fmt=lambda x:'unavailable' if x is None else f'{x:.5f}'
    for r in results:
        a,b=r['ensemble'],r['components']['elo']
        lines.append(f"| {r['season']} | {a['games']} | {a['brier']:.5f} | {b['brier']:.5f} | {a['log_loss']:.5f} | {b['log_loss']:.5f} | {r['selected_component_from_training']} | {fmt(r['raw_p'])} | {fmt(r['adjusted_p_h023_h024'])} |")
    lines+=['','## Learned weights','']
    for r in results:lines.append(f"- Test {r['season']}: trained on {r['model']['training_games']} earlier component forecasts from {', '.join(r['model']['training_seasons'])}; weights {json.dumps(r['model']['weights'],sort_keys=True)}.")
    lines+=['','Weights are nonnegative and sum to one. A ten-percentage-point grid is fixed before testing; no test-season outcomes choose the weights. Individual component metrics, matched predictions, failure/null tests and training hashes are retained in the data artifact. BH adjustment includes both related H023 and H024 season-test families.',
            '', 'This is a statistical ensemble, not the full market/simulation ensemble from the master prompt. Market and simulator inputs have not earned inclusion. Current injury scenarios are combined only when required components have matching scenarios and timestamps. A team-only result is explicitly labeled and is not claimed injury-adjusted. No public pick changes.',
            '',f'Artifact: observations/nba_ensemble/{data["input_hash"]}/evaluation.json.','']
    Path(output).write_text('\n'.join(lines));print(json.dumps({'hypothesis':'H024','test_seasons':len(results),'promoted':False}))
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();run(args.data_root,args.output)
