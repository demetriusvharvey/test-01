"""Exploratory day-start replay of the actual top-three Elo winner rule."""
import argparse
import json
import random
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

from scripts.line_lab.model import build_ratings,project_home
from scripts.line_lab.simulator import score_metrics
from scripts.research_simulator import load_games

START='2024-01-01'
BINS=((.5,.6),(.6,.7),(.7,.8),(.8,1.000001))


def replay(games,start=START,bootstrap_draws=2000):
    by_day=defaultdict(list)
    for game in games:
        if game['date'].isoformat()>=start and game['home_score']!=game['away_score']:
            by_day[game['date']].append(game)
    selected=[];all_favorites=[]
    # Freeze each day's ratings before any games on that day are observed.
    for day,slate in sorted(by_day.items()):
        models={league:build_ratings(games,day,league) for league in ('NBA','NFL')}
        ranked=[]
        for g in slate:
            home_p=project_home(models[g['league']],g['home'],g['away'],
                                datetime.combine(day,datetime.min.time(),timezone.utc),g.get('neutral',False))
            if home_p is None or home_p==.5:continue
            side='home' if home_p>.5 else 'away'
            p=home_p if side=='home' else 1-home_p
            outcome=int((g['home_score']>g['away_score']) if side=='home' else (g['away_score']>g['home_score']))
            ranked.append({'game_id':g['id'],'day':day.isoformat(),'league':g['league'],
                           'season':str(g['season']),'probability':p,'outcome':outcome})
        ranked.sort(key=lambda r:(-r['probability'],r['game_id']))
        all_favorites.extend(ranked);selected.extend(ranked[:3])
    bins=[]
    for low,high in BINS:
        values=[r for r in selected if low<=r['probability']<high]
        bins.append({'range':f'{low:.2f}–{min(1,high):.2f}','games':len(values),
                     'mean_forecast':sum(r['probability'] for r in values)/len(values) if values else None,
                     'actual_win_rate':sum(r['outcome'] for r in values)/len(values) if values else None})
    groups=defaultdict(list)
    for row in selected:groups[row['day']].append(row['outcome'])
    interval=None
    if len(selected)>=30 and len(groups)>=10:
        days=sorted(groups);rng=random.Random(20261028);draws=[]
        for _ in range(bootstrap_draws):
            sample=[outcome for _ in days for outcome in groups[days[rng.randrange(len(days))]]]
            draws.append(sum(sample)/len(sample))
        draws.sort();interval=[draws[int(.025*len(draws))],draws[int(.975*len(draws))-1]]
    by_league={league:score_metrics([r for r in selected if r['league']==league]) for league in ('NBA','NFL')}
    by_year={year:score_metrics([r for r in selected if r['day'].startswith(year)]) for year in sorted({r['day'][:4] for r in selected})}
    return {'selected':score_metrics(selected),'all_model_favorites':score_metrics(all_favorites),
            'uninformative_50_percent':score_metrics([{'probability':.5,'outcome':r['outcome']} for r in selected]),
            'accuracy_day_block_interval':interval,'selected_days':len(groups),'by_league':by_league,
            'by_calendar_year':by_year,'reliability':bins,'first_test_date':start,
            'source_games':len(games),'sample_game_ids':[r['game_id'] for r in selected[:5]]}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();games,sources=load_games(args.data_root);result=replay(games)
    f=lambda x:'—' if x is None else f'{x:.4f}'
    lines=['# Retrospective top-three winner ranking','',
           'A chronological day-start replay of fixed NBA/NFL Elo on archived final scores. The archive was retrieved after these games: this is not the live published forecast record, an untouched holdout, a verified pregame injury test, or proof of wagering profit. The model does not use injuries or sportsbook prices.','',
           '| Selection | Games | Accuracy | Brier | Log loss |', '|---|---:|---:|---:|---:|']
    for label,key in (('Three highest-ranked per day','selected'),('Every model favorite','all_model_favorites'),('50% baseline on selected games','uninformative_50_percent')):
        metric=result[key];lines.append(f"| {label} | {metric['games']} | {f(metric['accuracy'])} | {f(metric['brier'])} | {f(metric['log_loss'])} |")
    lines.extend(['',f"Selected days: {result['selected_days']}. Day-block accuracy interval: {result['accuracy_day_block_interval'] or 'unavailable (sample too small)'}.",'',
                  '| Winner forecast range | Games | Mean forecast | Observed win rate |','|---|---:|---:|---:|'])
    for b in result['reliability']:lines.append(f"| {b['range']} | {b['games']} | {f(b['mean_forecast'])} | {f(b['actual_win_rate'])} |")
    lines.extend(['','Selection favors strong favorites and accuracy alone does not establish a pricing advantage. Sources lack original pregame publication timestamps; NBA upstream gambling-use rights remain unresolved. No old outcome is added to the site’s forward winner record.','',
                  '## Archived sources',''])
    lines.extend(f"- {s['url']} — {s['parsed_games']} games, SHA-256 `{s['sha256']}`, archived {s['retrieved_at']}" for s in sources)
    lines.extend(['','## Machine-readable results','','```json',json.dumps(result,indent=2,sort_keys=True),'```',''])
    Path(args.output).write_text('\n'.join(lines));print(json.dumps({k:result[k] for k in ('selected','selected_days','by_league')},sort_keys=True))

if __name__=='__main__':main()
