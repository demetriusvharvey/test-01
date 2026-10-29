"""Current roster-aware rotation scenarios; no invented availability weights."""
import math
from collections import defaultdict
from datetime import timedelta
from .history import aware


def project_rotation(players,roster,statuses,as_of,starts_at,unavailable=()):
    """Use explicit IDs from a captured roster and explicitly mapped statuses.

    The caller must resolve source IDs before calling. Questionable players
    require explicit separate scenarios rather than assumed play likelihoods.
    """
    try:
        now,start=aware(as_of),aware(starts_at)
        observed=aware(roster['observed_at'])
        if not observed<=now<start or now-observed>timedelta(hours=30):return None
        if roster.get('verified') is not True or not roster.get('source'):return None
        ids=roster['player_ids'];team=roster['team']
        if not isinstance(ids,list) or len(set(ids))!=len(ids) or not 8<=len(ids)<=25:return None
        if any(not isinstance(p,str) or not p for p in ids):return None
        excluded=set(unavailable)
        if not excluded<=set(ids):return None
        report_time=aware(statuses['observed_at'])
        if not report_time<=now or now-report_time>timedelta(minutes=95) or statuses.get('complete') is not True:return None
        reports=statuses['players']
        if any(p not in ids for p in reports):return None
        unresolved=[]
        for p,status in reports.items():
            if status in ('out','suspended','injured_list'):excluded.add(p)
            elif status in ('questionable','doubtful','game_time_decision','day_to_day'):
                if p not in excluded:unresolved.append(p)
            elif status not in ('available','probable','active'):return None
        histories=defaultdict(list)
        for row in players:
            if row['player_id'] not in ids or row['team']!=team or row['date']>=now.date():continue
            histories[row['player_id']].append(row)
        estimates=[]
        for p in ids:
            if p in excluded:continue
            records=sorted(histories[p],key=lambda r:r['date'])[-10:]
            if not records:continue
            minutes=sum(r['minutes'] for r in records)/len(records)
            if not math.isfinite(minutes) or minutes<=0:continue
            estimates.append({'player_id':p,'weight':minutes,'minutes':0.,'prior_games':len(records)})
        if len(estimates)<8:return None
        # Redistribute to observed rotation players, capped at regulation 48.
        remaining=240.;active=list(estimates)
        while active and remaining>1e-8:
            total=sum(p['weight'] for p in active);capped=[]
            for p in active:
                allocation=remaining*p['weight']/total
                if allocation>=48:
                    p['minutes']=48.;capped.append(p)
            if not capped:
                for p in active:p['minutes']=remaining*p['weight']/total
                remaining=0.;break
            remaining-=48*len(capped);active=[p for p in active if p not in capped]
        if remaining>1e-8:return None
        return {'team':team,'observed_at':now.isoformat(),'roster_observed_at':observed.isoformat(),
                'injury_observed_at':report_time.isoformat(),'players':estimates,
                'unavailable_players':sorted(excluded),'unresolved_players':sorted(unresolved),
                'availability_scenario':'unresolved' if unresolved else 'specified',
                'used_in_prediction':False,'limitations':'minutes redistribution proxy; no verified replacement impact or availability probabilities'}
    except (KeyError,TypeError,ValueError,OverflowError,ZeroDivisionError):return None
