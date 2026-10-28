"""Normalize only safe, timestamped market observations; isolate conflicts."""
from collections import defaultdict
from datetime import datetime, timezone
from .history import valid_observation, aware
from .market import implied


def validate_and_deduplicate(events, observed_at):
    groups=defaultdict(list); warnings=[]
    for e in events:
        stamp=e.get('fetched_at',observed_at)
        if not valid_observation(e,stamp):
            warnings.append('invalid, stale, future, incomplete or post-start quote')
            continue
        groups[(e['provider'],e['id'],e['book'])].append(e)
    result=[]
    for (provider,event,book),rows in groups.items():
        signatures={(r['home'],r['away'],r['home_odds'],r['away_odds'],r['as_of'],r['starts_at']) for r in rows}
        if len(signatures)>1:
            warnings.append(f'conflicting duplicate: {provider} {event} {book}')
        else:
            result.append(rows[0])
    return result,warnings


def reconcile_quotes(events, disagreement=0.05, start_tolerance_seconds=20*60):
    """Quarantine materially conflicting book/event quotes; otherwise prefer latest.

    AgentBets reports that its pages are powered by The Odds API. A comparison
    here is therefore not evidence of statistically independent confirmation.
    """
    groups=defaultdict(list); warnings=[]
    for e in events: groups[(e['id'],e['book'])].append(e)
    selected=[]
    for (event,book),rows in groups.items():
        if len(rows)>1:
            diff=max(max(implied(r['home_odds']) for r in rows)-min(implied(r['home_odds']) for r in rows),
                     max(implied(r['away_odds']) for r in rows)-min(implied(r['away_odds']) for r in rows))
            starts=[aware(r['starts_at']) for r in rows]
            teams={(r['home'],r['away']) for r in rows}
            if diff>disagreement or len(teams)!=1 or (max(starts)-min(starts)).total_seconds()>start_tolerance_seconds:
                warnings.append(f'provider disagreement: {event} {book}')
                continue
        # The page-level AgentBets timestamp may be less precise than market updates.
        selected.append(max(rows,key=lambda r:(aware(r['as_of']),r['provider']=='the_odds_api')))
    return selected,warnings
