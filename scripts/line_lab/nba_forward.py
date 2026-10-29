"""Grade immutable pregame NBA ML forecasts against explicitly confirmed finals.

This measures the saved prediction pipeline; it does not grant promotion or
infer an unconditional probability from unweighted availability scenarios.
"""
import json
import math
import sqlite3
from pathlib import Path
from .history import aware
from .simulator import score_metrics


def _valid(row,now):
    try:
        predicted,start=aware(row['predicted_at']),aware(row['starts_at'])
        if not aware(row['model_exported_at'])<=predicted<start or predicted>now:return False
        if not row.get('model_input_hash') or not row.get('features'):return False
        if aware(row['input_data_observed_at'])>predicted:return False
        for key in ('home_probability','baseline_elo_probability'):
            p=row[key]
            if isinstance(p,bool) or not isinstance(p,(int,float)) or not math.isfinite(p) or not 0<p<1:return False
        return math.isclose(row['home_probability']+row['away_probability'],1,abs_tol=1e-12)
    except (KeyError,ValueError,TypeError):return False


def evaluate_saved(root,confirmed_finals,now):
    """Caller supplies only finals already qualified by ingest.qualify_final_results."""
    current=aware(now);folder=Path(root)/'observations/nba_ml_predictions'
    folder.mkdir(parents=True,exist_ok=True);first={};excluded=0
    for file in sorted(folder.glob('????-??-??.sqlite')):
        with sqlite3.connect(file) as db:
            rows=db.execute('SELECT payload FROM predictions').fetchall()
        for (payload,) in rows:
            row=json.loads(payload)
            if not _valid(row,current):excluded+=1;continue
            key=(row['game_id'],row['model_version'])
            # Fixed earliest eligible forecast, never most accurate revision.
            if key not in first or (aware(row['predicted_at']),payload)<(aware(first[key]['predicted_at']),json.dumps(first[key],sort_keys=True)):
                first[key]=row
    with sqlite3.connect(folder/'confirmed_outcomes.sqlite') as db:
        db.executescript("""CREATE TABLE IF NOT EXISTS outcomes(game_id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS nfo_no_update BEFORE UPDATE ON outcomes BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS nfo_no_delete BEFORE DELETE ON outcomes BEGIN SELECT RAISE(ABORT,'immutable'); END;""")
        for g in confirmed_finals:
            try:
                if not g['id'].startswith('nba:') or not g.get('source'):continue
                start=aware(g['starts_at'].isoformat() if hasattr(g['starts_at'],'isoformat') else g['starts_at'])
                scores=[g['home_score'],g['away_score']]
                if start>current or g['home']==g['away'] or any(type(v) is not int or v<0 for v in scores):continue
                value={'game_id':g['id'],'home':g['home'],'away':g['away'],'starts_at':start.isoformat(),
                       'home_score':scores[0],'away_score':scores[1],'source':g['source'],'confirmed_at':now}
                previous=db.execute('SELECT payload FROM outcomes WHERE game_id=?',(g['id'],)).fetchone()
                if previous:
                    old=json.loads(previous[0])
                    if any(old[k]!=value[k] for k in ('home','away','starts_at','home_score','away_score')):
                        raise ValueError('conflicting confirmed NBA outcome')
                else:db.execute('INSERT INTO outcomes VALUES (?,?)',(g['id'],json.dumps(value,sort_keys=True)))
            except (KeyError,TypeError):continue
        outcomes={game:json.loads(payload) for game,payload in db.execute('SELECT game_id,payload FROM outcomes')}
    grouped={}
    for (game,version),row in sorted(first.items()):
        group=grouped.setdefault(version,{'model':[],'elo':[],'pending':0,'void':0,'excluded':0,'scenario_agreement':0,'scenario_disagreement':0})
        final=outcomes.get(game)
        if not final:group['pending']+=1;continue
        if (row['home'],row['away'],aware(row['starts_at']))!=(final['home'],final['away'],aware(final['starts_at'])):
            group['excluded']+=1;continue
        if final['home_score']==final['away_score']:group['void']+=1;continue
        y=int(final['home_score']>final['away_score'])
        group['model'].append({'probability':row['home_probability'],'outcome':y})
        group['elo'].append({'probability':row['baseline_elo_probability'],'outcome':y})
        context=row.get('availability_scenarios') or {}
        if context.get('exhaustive_listed_uncertainty'):
            group['scenario_agreement' if context.get('consistent_winner') else 'scenario_disagreement']+=1
    result={'evaluated_at':now,'invalid_forecasts':excluded,'models':{},'promoted':False,
            'policy':'earliest eligible immutable forecast per game/version; identical paired Elo sample; confirmed finals only',
            'limitations':['pipeline versions may contain retrained artifacts; not a fixed-artifact trial',
                          'conditional scenarios are not an unconditional calibrated prediction',
                          'no causal player-effect validation, market comparison or profitability claim']}
    for version,g in grouped.items():
        model,elo=score_metrics(g.pop('model')),score_metrics(g.pop('elo'))
        result['models'][version]={**g,'model':model,'elo':elo,
                                  'brier_difference':model['brier']-elo['brier'] if model['games'] else None,
                                  'log_loss_difference':model['log_loss']-elo['log_loss'] if model['games'] else None,
                                  'status':'forward_results_available' if model['games'] else 'awaiting_confirmed_finals'}
    (folder/'forward_evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
