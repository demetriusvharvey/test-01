"""Observed same-source moneyline history; descriptive, never a trading signal."""
import sqlite3
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from .anchors import implied_american
from .history import aware


def same_book_history(root,event,team_code,book,now,lookback_days=7):
    """Return observed, pregame snapshots for one exact team, book and provider.

    An earliest observed quote is not an opener, a latest observed quote is not
    a close, and a shared source is not independent confirmation. Reject
    conflicting snapshots at the same source time rather than choosing one.
    """
    try:
        current=aware(now);start=aware(event['starts_at']);live=event['books'][book]
        side='home' if team_code==event['home'] else 'away' if team_code==event['away'] else None
        source=live.get('provider');live_at=aware(live['as_of']);live_fetched=aware(live['fetched_at'])
        if not side or not source or not live_at<=live_fetched<=current<start:return None
        if current-live_at>timedelta(minutes=95):return None
        live_price=live[side];implied_american(live_price)
    except (KeyError,TypeError,ValueError):return None
    base=Path(root)/'observations'/'odds';rows=[]
    for delta in range(lookback_days+1):
        path=base/((current.date()-timedelta(days=delta)).isoformat()+'.sqlite')
        if not path.exists():continue
        with closing(sqlite3.connect(path)) as db:
            rows.extend(db.execute('SELECT home,away,home_odds,away_odds,source_as_of,fetched_at,starts_at FROM snapshots WHERE game_id=? AND book=? AND provider=? AND market=?',
                                   (event['id'],book,source,'h2h')).fetchall())
    by_time={};found_current=False
    for home,away,h,a,stamp,fetched,scheduled in rows:
        try:
            source_time,seen,game_start=aware(stamp),aware(fetched),aware(scheduled)
            if (home,away)!=(event['home'],event['away']) or abs((game_start-start).total_seconds())>1200:continue
            if not source_time<=seen<=current<min(start,game_start) or seen-source_time>timedelta(minutes=95):continue
            price=h if side=='home' else a;implied_american(price)
            key=source_time.isoformat()
            if key in by_time and by_time[key]['odds']!=price:return None
            by_time.setdefault(key,{'as_of':key,'odds':price,'implied':implied_american(price)})
            if source_time==live_at and seen==live_fetched and price==live_price:found_current=True
        except (TypeError,ValueError):continue
    if not found_current:return None
    points=sorted(by_time.values(),key=lambda x:x['as_of'])
    # Current prices may not have the latest reported source timestamp when
    # multiple upstream feeds disagree; do not mix a different latest point.
    if not points or points[-1]['as_of']!=live_at.isoformat() or points[-1]['odds']!=live_price:return None
    if len(points)>24:
        # Preserve both ends with deterministic evenly spaced samples.
        indices=sorted({round(i*(len(points)-1)/23) for i in range(24)})
        points=[points[i] for i in indices]
    return {'book':book,'provider':source,'points':points,'history_type':'observed_not_opener_or_close',
            'price_movement_is_evidence_of_edge':False}


def attach_histories(root,board,markets,ledger,now):
    by_id={p.get('id'):p for p in ledger}
    for pick in board.get('picks',[]):
        event=markets.get(pick.get('id'));original=by_id.get(pick.get('id'),{})
        if not event:continue
        books=[b for b in pick.get('books',[]) if b.get('odds')==pick.get('best') and b.get('name') in event.get('books',{})]
        if not books:continue
        pick['line_history']=same_book_history(root,event,original.get('team_code'),books[0]['name'],now)
