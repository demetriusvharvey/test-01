"""Lagged NBA rotation estimates: final minutes only update later dates."""
import csv
import io
import math
from collections import defaultdict,deque
from datetime import date
from .constants import NBA_TEAMS,normalize_code,team_code


def parse_players(text):
    reader=csv.DictReader(io.StringIO(text));rows=[];seen=set()
    if not {'game_date','athlete_id','minutes','points'}<=set(reader.fieldnames or []):
        raise ValueError('player box schema missing required columns')
    for row in reader:
        try:
            day=date.fromisoformat(row['game_date'][:10]);player=row['athlete_id'].strip()
            team=normalize_code(row.get('team_abbreviation') or row.get('team_abbrev') or '')
            if team not in NBA_TEAMS.values():
                team=team_code(row.get('team_display_name') or row.get('team_name') or '', 'NBA')
            minutes=float(row['minutes']);points=float(row['points'])
            if not team or not player or not math.isfinite(minutes+points) or not 0<minutes<=70 or points<0:continue
            key=(day,team,player)
            if key in seen:continue
            seen.add(key)
            rows.append({'date':day,'team':team,'player_id':player,'minutes':minutes,'points':points})
        except (KeyError,TypeError,ValueError):continue
    return rows


def rotation_features(games,players):
    """Project from prior appearances; inferred membership is not a verified roster."""
    daily=defaultdict(list)
    for row in players:daily[row['date']].append(row)
    games_byday=defaultdict(list)
    for g in games:
        if g['league']=='NBA':games_byday[g['date']].append(g)
    history=defaultdict(lambda:deque(maxlen=10));last={};last_team={};output={}
    for day in sorted(set(daily)|set(games_byday)):
        team_projections={}
        for team in {t for g in games_byday[day] for t in (g['home'],g['away'])}:
            eligible=[p for p in history if last_team[p]==team and 0<(day-last[p]).days<=21]
            values=[]
            for player in eligible:
                records=history[player]
                minutes=sum(r['minutes'] for r in records)/len(records)
                ppm=sum(r['points'] for r in records)/sum(r['minutes'] for r in records)
                values.append((player,minutes,ppm,len(records)))
            values.sort(key=lambda v:(-v[1],v[0]));values=values[:12]
            if len(values)<8:continue
            total=sum(v[1] for v in values)
            team_projections[team]={'projected_points':sum(240*v[1]/total*v[2] for v in values),
                                    'top_five_share':sum(v[1] for v in values[:5])/total,
                                    'experienced_share':sum(v[1] for v in values if v[3]>=5)/total,
                                    'players':len(values)}
        for game in games_byday[day]:
            h,a=team_projections.get(game['home']),team_projections.get(game['away'])
            if h and a:
                output[game['id']]={'vector':[(h['projected_points']-a['projected_points'])/20,
                                             h['top_five_share']-a['top_five_share'],
                                             h['experienced_share']-a['experienced_share']],
                                    'roster_status':'inferred from prior appearances, not confirmed',
                                    'injury_status':'historical pregame availability unknown'}
        # No same-date player statistic can enter the day's predictions.
        for row in daily[day]:
            p=row['player_id'];history[p].append(row);last[p]=day;last_team[p]=row['team']
    return output
