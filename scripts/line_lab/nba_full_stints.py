"""Uniquely deduced period lineups, verified against whole-game box minutes."""
import csv
import io
import math
from collections import defaultdict,Counter
from .nba_stints import ident,reconstruct


def box_minutes(text):
    output=defaultdict(dict)
    for row in csv.DictReader(io.StringIO(text)):
        try:
            game,player=ident(row['game_id']),ident(row['athlete_id'])
            value=row.get('minutes')
            if value in ('',None) and str(row.get('did_not_play')).lower() in ('true','1'):value=0
            value=float(value)
            if not math.isfinite(value) or value<0:continue
            output[game][player]=value
        except (KeyError,ValueError,TypeError):continue
    return dict(output)


def period_starters(rows,teams):
    membership={p:t for t,entry in teams.items() for p in entry['roster']}
    state={};initial={t:set() for t in teams}
    def active(player):
        if player not in membership:raise ValueError('unknown_action_player')
        if player not in state:initial[membership[player]].add(player);state[player]=True
        if not state[player]:raise ValueError('action_off_court')
    for row in sorted(rows,key=lambda r:int(float(r['sequence_number']))):
        kind=row['type_text']
        if kind=='Substitution':
            incoming,outgoing=ident(row['athlete_id_1']),ident(row['athlete_id_2']);active(outgoing)
            if incoming not in membership or membership[incoming]!=membership[outgoing] or state.get(incoming) is True:raise ValueError('ambiguous_substitution')
            if incoming not in state:state[incoming]=False
            state[outgoing]=False;state[incoming]=True
        elif (any(k in kind.lower() for k in ('shot','layup','dunk','rebound','free throw','turnover'))
              and not any(k in kind.lower() for k in ('technical','team','shot clock'))
              or kind in ('Personal Foul','Shooting Foul','Offensive Foul','Loose Ball Foul','Personal Take Foul','Offensive Charge')):
            for field in ('athlete_id_1','athlete_id_2'):
                if row.get(field) not in ('',None):active(ident(row[field]))
    if any(len(values)!=5 for values in initial.values()):raise ValueError('nonunique_period_starters')
    return initial


def reconstruct_full(events,rosters,minutes):
    games=defaultdict(list)
    for row in events:
        try:games[ident(row['game_id'])].append(row)
        except (KeyError,ValueError):continue
    output=[];reasons=Counter();accepted=0
    for game,rows in games.items():
        try:
            rows=sorted(rows,key=lambda r:int(float(r['sequence_number'])))
            if game not in rosters or game not in minutes:raise ValueError('missing_box_context')
            final=next(r for r in reversed(rows) if r['type_text']=='End Game')
            if int(float(final['period_number']))!=4:raise ValueError('overtime_or_incomplete')
            periods={q:[r for r in rows if int(float(r['period_number']))==q and r['type_text']!='End Game'] for q in range(1,5)}
            end={q:next(r for r in reversed(part) if r['type_text']=='End Period') for q,part in periods.items()}
            stints=[]
            for q,part in periods.items():
                initial=period_starters(part,rosters[game])
                if q==1 and any(initial[t]!=entry['starters'] for t,entry in rosters[game].items()):raise ValueError('initial_starter_disagreement')
                teams={t:{**entry,'starters':initial[t]} for t,entry in rosters[game].items()}
                base=(int(float(end[q-1]['home_score'])),int(float(end[q-1]['away_score']))) if q>1 else (0,0)
                transformed=[{**r,'period_number':1,'home_score':int(float(r['home_score']))-base[0],
                              'away_score':int(float(r['away_score']))-base[1]} for r in part]
                transformed.append({**final,'period_number':4,'home_score':int(float(final['home_score']))-base[0],
                                    'away_score':int(float(final['away_score']))-base[1]})
                reconstructed,quality=reconstruct(transformed,{game:teams})
                if quality['accepted_games']!=1:raise ValueError('period_replay_failure')
                stints.extend({**s,'period':q} for s in reconstructed)
            measured=defaultdict(float)
            for stint in stints:
                for player in stint['home_players']+stint['away_players']:measured[player]+=stint['seconds']/60
            if any(p not in minutes[game] or abs(value-minutes[game][p])>1.1 for p,value in measured.items()):raise ValueError('player_minute_disagreement')
            if any(value>1.1 and p not in measured for p,value in minutes[game].items()):raise ValueError('missing_player_minutes')
            if abs(sum(s['seconds'] for s in stints)-2880)>1e-6:raise ValueError('incomplete_game_time')
            output.extend(stints);accepted+=1
        except (KeyError,ValueError,TypeError,IndexError,StopIteration) as exc:
            name=str(exc);reasons[name if name.replace('_','').isalpha() else 'malformed_or_incomplete']+=1
    return output,{'games_seen':len(games),'accepted_games':accepted,'rejected_games':len(games)-accepted,
                   'rejections':dict(reasons),'stints':len(output),'scope':'unique regulation lineups; per-player box-minute validation; overtime excluded'}
