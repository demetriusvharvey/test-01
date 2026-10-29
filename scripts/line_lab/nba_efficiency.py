"""Past-only NBA team box-score feature construction."""
import csv
import io
import math
from collections import defaultdict,deque
from datetime import date
from .constants import normalize_code

METRICS=('off_rating_est','def_rating_est','effective_fg_pct','pace_proxy',
         'turnover_rate','rebound_rate','free_throw_rate','three_point_pct')


def parse_team_stats(text):
    output={}
    for row in csv.DictReader(io.StringIO(text)):
        try:
            day=date.fromisoformat(row['game_date']);team=normalize_code(row['team'])
            fga,fta,orb,tov,reb=(float(row[k]) for k in
                ('field_goal_attempts','free_throw_attempts','offensive_rebounds','turnovers','rebounds'))
            pace=fga-orb+tov+.44*fta
            if not team or not 60<=pace<=160 or fga<=0:continue
            vector=[float(row['off_rating_est']),float(row['def_rating_est']),float(row['effective_fg_pct']),
                    pace,tov/pace,reb/pace,fta/fga,float(row['three_point_pct'])]
            if any(not math.isfinite(x) for x in vector):continue
            key=(day,team)
            if key in output and output[key]!=vector:raise ValueError('conflicting team game')
            output[key]=vector
        except (KeyError,TypeError,ValueError):continue
    return output


def enrich_examples(rows,games,stats):
    byday=defaultdict(list);lookup={g['id']:g for g in games};history=defaultdict(lambda:deque(maxlen=20))
    for row in rows:byday[row['date']].append(row)
    # Include warm-up games that precede the baseline feature eligibility date.
    games_byday=defaultdict(list)
    for g in games:
        if g['league']=='NBA':games_byday[g['date'].isoformat()].append(g)
    output=[]
    for day,slate in sorted(games_byday.items()):
        for row in byday.get(day,[]):
            game=lookup[row['game_id']];h,a=game['home'],game['away']
            if len(history[h])<10 or len(history[a])<10:continue
            means=lambda t:[sum(x[i] for x in history[t])/len(history[t]) for i in range(len(METRICS))]
            hv,av=means(h),means(a)
            output.append({**row,'vector':row['vector']+[x-y for x,y in zip(hv,av)]})
        for game in slate:
            for team in (game['home'],game['away']):
                value=stats.get((date.fromisoformat(day),team))
                if value is not None:history[team].append(value)
    return output
