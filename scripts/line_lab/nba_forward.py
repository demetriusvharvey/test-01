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
        if not row.get('model_input_hash') or not row.get('features') or not row.get('model_version'):return False
        if not row['game_id'].startswith('nba:') or row['home']==row['away']:return False
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
    # Conditional models have no justified scenario weights, so grade only
    # their frozen, scenario-consistent winner; never invent a Brier probability.
    conditional={};first_conditional={}
    for file in sorted(folder.glob('????-??-??.sqlite')):
        with sqlite3.connect(file) as db:records=db.execute('SELECT payload FROM predictions').fetchall()
        for (payload,) in records:
            row=json.loads(payload)
            if not _valid(row,current):continue
            for field in ('availability_scenarios','player_box_scenarios','ensemble_scenarios','stint_prediction_scenarios'):
                context=row.get(field) or {};scenarios=context.get('scenarios') or []
                try:
                    if context.get('status')!='conditional_research_only' or not context.get('exhaustive_listed_uncertainty'):continue
                    if not context.get('model_hash') or aware(context['injury_observed_at'])>aware(row['predicted_at']):continue
                    if not 1<=len(scenarios)<=64 or len(scenarios)!=2**context['uncertain_players']:continue
                    values=[r['home_probability'] for r in scenarios]
                    if any(not math.isfinite(v) or not 0<v<1 for v in values):continue
                    if any(not math.isclose(s['home_probability']+s['away_probability'],1,abs_tol=1e-12) for s in scenarios):continue
                    winner=row['home'] if min(values)>.5 else row['away'] if max(values)<.5 else None
                    if context.get('consistent_winner')!=winner:continue
                    key=(row['game_id'],context['model_version'])
                    old=first_conditional.get(key)
                    if old is None or aware(row['predicted_at'])<aware(old[0]['predicted_at']):
                        first_conditional[key]=(row,winner)
                except (KeyError,ValueError,TypeError,OverflowError):continue
    for (game,version),(row,winner) in sorted(first_conditional.items()):
        group=conditional.setdefault(version,{'wins':0,'losses':0,'pending':0,'abstained':0,'void':0,'excluded':0})
        final=outcomes.get(game)
        if not final:group['pending']+=1;continue
        if (row['home'],row['away'],aware(row['starts_at']))!=(final['home'],final['away'],aware(final['starts_at'])):
            group['excluded']+=1;continue
        if final['home_score']==final['away_score']:group['void']+=1;continue
        if winner is None:group['abstained']+=1;continue
        actual=final['home'] if final['home_score']>final['away_score'] else final['away']
        group['wins' if winner==actual else 'losses']+=1
    for group in conditional.values():
        settled=group['wins']+group['losses']
        group['settled_predictions']=settled
        group['accuracy']=group['wins']/settled if settled else None
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
    result={'evaluated_at':now,'invalid_forecasts':excluded,'models':{},'conditional_winner_records':conditional,'promoted':False,
            'policy':'earliest eligible immutable forecast per game/version; identical paired Elo sample; confirmed finals only',
            'limitations':['pipeline versions may contain retrained artifacts; not a fixed-artifact trial',
                          'conditional scenarios are not an unconditional calibrated prediction; only scenario-consistent winner accuracy is graded',
                          'no causal player-effect validation, market comparison or profitability claim']}
    for version,g in grouped.items():
        model,elo=score_metrics(g.pop('model')),score_metrics(g.pop('elo'))
        result['models'][version]={**g,'model':model,'elo':elo,
                                  'brier_difference':model['brier']-elo['brier'] if model['games'] else None,
                                  'log_loss_difference':model['log_loss']-elo['log_loss'] if model['games'] else None,
                                  'status':'forward_results_available' if model['games'] else 'awaiting_confirmed_finals'}
    (folder/'forward_evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
