"""Frozen daily winner-policy trials, separate from public picks and wager records."""
import hashlib
import json
import math
import sqlite3
from pathlib import Path
from datetime import timedelta
from .constants import ET
from .history import aware
from .nba_forward import _valid
from .nba_winner_selection import rank_winners

POLICY='nba-top3-scenario-v1'
MODELS={'nba-efficiency-logistic-v1':None,'nba-rotation-logistic-v1':'availability_scenarios',
        'nba-player-box-logistic-v1':'player_box_scenarios','nba-convex-ensemble-v1':'ensemble_scenarios',
        'nba-partial-stint-logistic-v1':'partial_stint_scenarios'}


def candidate(row,version,now):
    """None means unsupported inputs; a valid disagreement means an abstention."""
    if not _valid(row,now) or aware(row['predicted_at'])!=now:return None
    parts=row['game_id'].split(':')
    if len(parts)!=4 or (parts[2],parts[3])!=(row['away'],row['home']) or parts[1]!=aware(row['starts_at']).astimezone(ET).date().isoformat():return None
    field=MODELS[version]
    if field is None:
        if row['model_version']!=version:return None
        p=row['home_probability'];home=p>.5;score=p if home else 1-p
        result={'game_id':row['game_id'],'team':row['home'] if home else row['away'],'score':score,
                'score_type':'team_model_probability','abstain':p==.5}
    else:
        context=row.get(field) or {};scenarios=context.get('scenarios') or []
        try:
            n=context['uncertain_players'];stamp=aware(context['injury_observed_at'])
            if (context.get('status')!='conditional_research_only' or context.get('model_version')!=version
                    or context.get('exhaustive_listed_uncertainty') is not True or not context.get('model_hash')
                    or type(n) is not int or not 0<=n<=6 or len(scenarios)!=2**n
                    or not now-timedelta(minutes=95)<=stamp<=now):return None
            if len({s['scenario'] for s in scenarios})!=len(scenarios):return None
            values=[s['home_probability'] for s in scenarios]
            if any(type(p) not in (int,float) or not math.isfinite(p) or not 0<p<1 for p in values):return None
            if any(not math.isclose(s['home_probability']+s['away_probability'],1,abs_tol=1e-12) for s in scenarios):return None
            team=row['home'] if min(values)>.5 else row['away'] if max(values)<.5 else None
            if context.get('consistent_winner')!=team:return None
            result={'game_id':row['game_id'],'team':team,'score':min(values) if team==row['home'] else min(1-p for p in values) if team else None,
                    'score_type':'minimum_listed_scenario_probability','abstain':team is None,
                    'component_model_hash':context['model_hash'],'scenario_count':len(scenarios),
                    'injury_observed_at':context['injury_observed_at']}
        except (KeyError,ValueError,TypeError,OverflowError):return None
    result.update({'starts_at':row['starts_at'],'home':row['home'],'away':row['away'],
                   'source_prediction_hash':hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()})
    return result


def record_ranked(root,predictions,scheduled,now):
    current=aware(now);day=current.astimezone(ET).date().isoformat();eligible={}
    for game in scheduled:
        if game['league']=='NBA' and aware(game['starts_at']).astimezone(ET).date().isoformat()==day and aware(game['starts_at'])>current+timedelta(minutes=5):
            eligible[game['id']]=game
    if not eligible:return {'status':'no_eligible_games','added':0,'unavailable':{}}
    rows={}
    for row in predictions:
        if row['game_id'] not in eligible:continue
        if row['game_id'] in rows:raise ValueError('mixed prediction revisions')
        if aware(row['starts_at'])!=aware(eligible[row['game_id']]['starts_at']):continue
        rows[row['game_id']]=row
    folder=Path(root)/'observations/nba_ranked_forecasts';folder.mkdir(parents=True,exist_ok=True)
    added=0;unavailable={}
    with sqlite3.connect(folder/(day+'.sqlite')) as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS decisions(key TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS nrd_no_update BEFORE UPDATE ON decisions BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS nrd_no_delete BEFORE DELETE ON decisions BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TABLE IF NOT EXISTS attempts(key TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS nra_no_update BEFORE UPDATE ON attempts BEGIN SELECT RAISE(ABORT,'immutable'); END;
        CREATE TRIGGER IF NOT EXISTS nra_no_delete BEFORE DELETE ON attempts BEGIN SELECT RAISE(ABORT,'immutable'); END;''')
        def audit(version,status,supported):
            payload=json.dumps({'day':day,'model_version':version,'observed_at':now,'status':status,
                                'eligible_games':len(eligible),'supported_games':supported},sort_keys=True)
            db.execute('INSERT OR IGNORE INTO attempts VALUES (?,?)',(hashlib.sha256(payload.encode()).hexdigest(),payload))
        for version in MODELS:
            key=f'{day}:{version}:{POLICY}'
            if db.execute('SELECT 1 FROM decisions WHERE key=?',(key,)).fetchone():
                audit(version,'existing_frozen_decision',None);continue
            candidates=[]
            for game in sorted(eligible):
                value=candidate(rows[game],version,current) if game in rows else None
                if value is not None:candidates.append(value)
            if len(candidates)!=len(eligible):
                unavailable[version]='incomplete_model_or_schedule_coverage'
                audit(version,'source_unavailable',len(candidates));continue
            baseline=rank_winners([{'game_id':g,'home':rows[g]['home'],'away':rows[g]['away'],
                                   'home_probability':rows[g]['baseline_elo_probability']} for g in sorted(eligible)])
            baseline=[{**p,'starts_at':rows[p['game_id']]['starts_at'],'home':rows[p['game_id']]['home'],'away':rows[p['game_id']]['away']} for p in baseline]
            picks=sorted((p for p in candidates if not p['abstain']),key=lambda p:(-p['score'],p['game_id']))[:3]
            record={'day':day,'model_version':version,'policy_version':POLICY,'frozen_at':now,'eligible_games':sorted(eligible),
                    'picks':picks,'matched_elo_picks':baseline,'scenario_abstentions':sum(p['abstain'] for p in candidates),
                    'used_in_public_picks':False,'limitation':'scenario minimum is not a confidence bound; no availability weights or betting edge'}
            db.execute('INSERT INTO decisions VALUES (?,?)',(key,json.dumps(record,sort_keys=True)));added+=1
            audit(version,'frozen',len(candidates))
    return {'status':'recorded' if added else 'unchanged_or_unavailable','added':added,'unavailable':unavailable}


def evaluate_ranked(root,now):
    current=aware(now);folder=Path(root)/'observations/nba_ranked_forecasts';folder.mkdir(parents=True,exist_ok=True)
    source=Path(root)/'observations/nba_ml_predictions/confirmed_outcomes.sqlite';outcomes={}
    if source.exists():
        with sqlite3.connect(source) as db:outcomes={g:json.loads(p) for g,p in db.execute('SELECT game_id,payload FROM outcomes')}
    records=[];attempts=[]
    for path in sorted(folder.glob('????-??-??.sqlite')):
        with sqlite3.connect(path) as db:
            records.extend(json.loads(r[0]) for r in db.execute('SELECT payload FROM decisions ORDER BY key'))
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='attempts'").fetchone():
                attempts.extend(json.loads(r[0]) for r in db.execute('SELECT payload FROM attempts ORDER BY key'))
    models={}
    def grade(picks):
        counts={'wins':0,'losses':0,'pending':0,'voids':0,'excluded':0}
        for pick in picks:
            final=outcomes.get(pick['game_id'])
            if not final:counts['pending']+=1;continue
            if (aware(final['confirmed_at'])>current or aware(pick['starts_at'])>current
                    or (pick['home'],pick['away'],aware(pick['starts_at']))!=(final['home'],final['away'],aware(final['starts_at']))):
                counts['excluded']+=1;continue
            if final['home_score']==final['away_score']:counts['voids']+=1;continue
            winner=final['home'] if final['home_score']>final['away_score'] else final['away']
            counts['wins' if pick['team']==winner else 'losses']+=1
        settled=counts['wins']+counts['losses'];counts['accuracy']=counts['wins']/settled if settled else None
        return counts
    for record in records:
        if aware(record['frozen_at'])>current:continue
        group=models.setdefault(record['model_version'],{'decisions':0,'scenario_abstentions':0,'picks':[],'elo':[]})
        group['decisions']+=1;group['scenario_abstentions']+=record['scenario_abstentions']
        group['picks'].extend(record['picks']);group['elo'].extend(record['matched_elo_picks'])
    for group in models.values():group['winner_record']=grade(group.pop('picks'));group['matched_elo_record']=grade(group.pop('elo'))
    coverage={}
    for version in MODELS:
        observed=[a for a in attempts if a['model_version']==version and aware(a['observed_at'])<=current]
        days={a['day'] for a in observed};decided={r['day'] for r in records if r['model_version']==version and aware(r['frozen_at'])<=current}
        coverage[version]={'audited_attempts':len(observed),'audited_days':len(days),'decision_days':len(decided),
                           'audited_days_without_decision':len(days-decided),
                           'unavailable_attempts':sum(a['status']=='source_unavailable' for a in observed)}
    report={'evaluated_at':now,'data_coverage':coverage,'policy_version':POLICY,'models':models,'public_record_changed':False,
            'limitation':'first usable daily model snapshot; matched Elo at the same time; no wager or ROI record'}
    (folder/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
