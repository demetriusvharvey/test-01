"""Strict first-quarter lineup reconstruction from explicit starter/substitution IDs."""
import csv
import io
from collections import defaultdict,Counter
from datetime import date


def ident(value):
    text=str(value or '').strip()
    if text.isdigit():return text
    if text.endswith('.0') and text[:-2].isdigit():return text[:-2]
    raise ValueError('invalid source identity')


def clock_seconds(value):
    parts=str(value).split(':')
    if len(parts)==1:
        seconds=float(parts[0])
        if not 0<=seconds<60:raise ValueError('invalid_clock')
        return seconds
    if len(parts)!=2:raise ValueError('invalid_clock')
    minutes=int(parts[0]);seconds=float(parts[1])
    if not 0<=seconds<60 or not 0<=minutes*60+seconds<=720:raise ValueError('invalid_clock')
    return minutes*60+seconds


def starter_rosters(text):
    reader=csv.DictReader(io.StringIO(text));groups=defaultdict(dict);bad=set()
    if not {'game_id','team_id','athlete_id','starter'}<=set(reader.fieldnames or []):raise ValueError('starter schema')
    for row in reader:
        try:
            game,team,player=(ident(row[k]) for k in ('game_id','team_id','athlete_id'))
            value=str(row['starter']).lower()
            if value not in ('true','false','1','0'):bad.add(game);continue
            entry=groups[game].setdefault(team,{'roster':set(),'starters':set()})
            if player in entry['roster']:bad.add(game)
            entry['roster'].add(player)
            if value in ('true','1'):entry['starters'].add(player)
        except (ValueError,KeyError):continue
    return {g:t for g,t in groups.items() if g not in bad and len(t)==2 and all(len(v['starters'])==5 for v in t.values())}


def reconstruct(events,rosters):
    """Unknown period-opening lineups remain unknown; only verified Q1 is used."""
    groups=defaultdict(list)
    for row in events:
        try:groups[ident(row['game_id'])].append(row)
        except (KeyError,ValueError):continue
    output=[];reasons=Counter();accepted=0
    for game,rows in sorted(groups.items()):
        try:
            if game not in rosters:raise ValueError('missing_verified_starters')
            rows=sorted(rows,key=lambda r:int(float(r['sequence_number'])))
            if not any(r['type_text']=='End Game' for r in rows):raise ValueError('no_final_marker')
            first=rows[0]
            if str(first['season_type']) not in ('2','2.0'):raise ValueError('non_regular_season')
            home,away=ident(first['home_team_id']),ident(first['away_team_id'])
            if home==away or set(rosters[game])!={home,away}:raise ValueError('team_identity')
            day=date.fromisoformat(str(first['game_date'])[:10]);year=int(float(first['season']))
            season=f'{year-1}-{str(year)[-2:]}'
            lineups={t:set(rosters[game][t]['starters']) for t in (home,away)}
            if lineups[home]&lineups[away]:raise ValueError('cross_team_player')
            clock=boundary=720.;score=(0,0);boundary_score=(0,0);stints=[];ended=False;seen=set()
            def emit(at,points):
                seconds=boundary-at;delta=tuple(points[i]-boundary_score[i] for i in range(2))
                if seconds==0 and any(delta):raise ValueError('zero_duration_scoring')
                if seconds>0:
                    stints.append({'game_id':game,'date':day.isoformat(),'season':season,'home':home,'away':away,
                                   'home_players':sorted(lineups[home]),'away_players':sorted(lineups[away]),
                                   'seconds':seconds,'home_points':delta[0],'away_points':delta[1]})
            for row in rows:
                if int(float(row['period_number']))!=1:continue
                sequence=int(float(row['sequence_number']))
                if sequence in seen:raise ValueError('duplicate_sequence')
                seen.add(sequence)
                if (ident(row['home_team_id']),ident(row['away_team_id']))!=(home,away):raise ValueError('changing_team_identity')
                at=clock_seconds(row['clock_display_value'])
                if not 0<=at<=clock:raise ValueError('clock_order')
                points=(int(float(row['home_score'])),int(float(row['away_score'])))
                if any(not 0<=points[i]-score[i]<=4 for i in range(2)):raise ValueError('score_order')
                if row['type_text']=='Substitution':
                    if points!=score:raise ValueError('substitution_score_change')
                    team=ident(row['team_id']);incoming,outgoing=ident(row['athlete_id_1']),ident(row['athlete_id_2'])
                    if team not in lineups or outgoing not in lineups[team] or incoming in lineups[team] or incoming not in rosters[game][team]['roster']:
                        raise ValueError('substitution_membership')
                    emit(at,points);lineups[team].remove(outgoing);lineups[team].add(incoming)
                    boundary=at;boundary_score=points
                elif row['type_text']=='End Period':
                    if at!=0:raise ValueError('period_end_clock')
                    emit(at,points);ended=True;score=points;break
                clock=at;score=points
            if not ended:raise ValueError('missing_quarter_end')
            final=next(r for r in reversed(rows) if r['type_text']=='End Game')
            if int(float(final['home_score']))<score[0] or int(float(final['away_score']))<score[1]:raise ValueError('final_score_conflict')
            if abs(sum(s['seconds'] for s in stints)-720)>1e-6:raise ValueError('incomplete_duration')
            if sum(s['home_points'] for s in stints)!=score[0] or sum(s['away_points'] for s in stints)!=score[1]:raise ValueError('incomplete_scores')
            output.extend(stints);accepted+=1
        except (ValueError,TypeError,KeyError,IndexError) as exc:
            message=str(exc);reasons[message if message.replace('_','').isalpha() else 'malformed_event']+=1
    return output,{'games_seen':len(groups),'accepted_games':accepted,'rejected_games':len(groups)-accepted,
                   'rejections':dict(reasons),'stints':len(output),'scope':'verified first quarter only; later period starters unknown'}
