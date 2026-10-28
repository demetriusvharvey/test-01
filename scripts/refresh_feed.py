#!/usr/bin/env python3
"""Produce an attributed feed snapshot. Does not place bets or publish a Site."""
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

NBA_REFS = 'https://official.nba.com/referee-assignments/'
ODDS_API = 'https://api.the-odds-api.com/v4/sports/{sport}/odds/'
ROOT = Path(__file__).resolve().parents[1]

class RefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.text, self.row, self.cell = [], [], None, None
        self.table = None
    def handle_starttag(self, tag, attrs):
        if tag == 'table' and self.table is None:
            self.table = []
        elif self.table is not None and tag == 'tr':
            self.row = []
        elif self.row is not None and tag in ('th', 'td'):
            self.cell = []
    def handle_data(self, data):
        self.text.append(data)
        if self.cell is not None:
            self.cell.append(data)
    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None and self.row is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None and self.table is not None:
            if self.row:
                self.table.append(self.row)
            self.row = None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table)
            self.table = None

def parse_referees(html, expected_date):
    parser = RefParser()
    parser.feed(html)
    all_text = ' '.join(' '.join(parser.text).split())
    date_text = expected_date.strftime('%B ') + str(expected_date.day) + expected_date.strftime(', %Y')
    if date_text not in all_text:
        return {'status': 'stale_or_date_unverified', 'date_expected': expected_date.isoformat(), 'games': []}
    for table in parser.tables:
        if table and len(table[0]) >= 3 and table[0][0].strip().lower() == 'game' and 'crew' in table[0][1].lower():
            games = []
            for row in table[1:]:
                if len(row) >= 4 and '@' in row[0]:
                    games.append({'matchup': row[0], 'crew_chief': row[1], 'referee': row[2], 'umpire': row[3], 'alternate': row[4] if len(row) > 4 else ''})
            return {'status': 'ok' if games else 'no_assignments', 'date_expected': expected_date.isoformat(), 'games': games}
    return {'status': 'format_unrecognized', 'date_expected': expected_date.isoformat(), 'games': []}

def get_bytes(url):
    request = Request(url, headers={'User-Agent': 'LineLabResearch/1.0 (+research; contact repository owner)', 'Accept': 'application/json,text/html'})
    with urlopen(request, timeout=20) as response:
        return response.read()

def parse_odds(events, sport):
    result = []
    for event in events:
        for book in event.get('bookmakers', []):
            if book.get('key') != 'fanduel':
                continue
            for market in book.get('markets', []):
                if market.get('key') != 'h2h':
                    continue
                prices = {o['name']: o['price'] for o in market.get('outcomes', []) if 'name' in o and 'price' in o}
                if event.get('home_team') not in prices or event.get('away_team') not in prices:
                    continue
                result.append({'sport': sport, 'home': event['home_team'], 'away': event['away_team'], 'starts_at': event.get('commence_time'), 'price_home': prices[event['home_team']], 'price_away': prices[event['away_team']], 'book_updated_at': book.get('last_update'), 'market_updated_at': market.get('last_update')})
    return result

def collect():
    now = datetime.now(timezone.utc)
    data = {'generated_at': now.isoformat(), 'nba_referees': {'source': NBA_REFS}, 'fanduel_moneylines': {'source': 'The Odds API', 'events': []}}
    try:
        parsed = parse_referees(get_bytes(NBA_REFS).decode('utf-8', errors='replace'), now.astimezone(ZoneInfo('America/New_York')).date())
        data['nba_referees'].update(parsed)
    except Exception as exc:
        data['nba_referees'].update({'status': 'error', 'error_type': type(exc).__name__, 'games': []})
    api_key = os.environ.get('ODDS_API_KEY', '').strip()
    if not api_key:
        data['fanduel_moneylines']['status'] = 'missing_api_key'
    else:
        errors = []
        for sport in ('basketball_nba', 'americanfootball_nfl'):
            params = urlencode({'apiKey': api_key, 'regions': 'us', 'markets': 'h2h', 'oddsFormat': 'american', 'bookmakers': 'fanduel'})
            try:
                events = json.loads(get_bytes(ODDS_API.format(sport=sport) + '?' + params))
                data['fanduel_moneylines']['events'].extend(parse_odds(events, sport))
            except Exception as exc:
                # Do not print URLs or exceptions: URLs can contain the API key.
                errors.append({'sport': sport, 'error_type': type(exc).__name__})
        data['fanduel_moneylines']['status'] = 'partial_error' if errors else 'ok'
        data['fanduel_moneylines']['errors'] = errors
    return data

def main():
    payload = collect()
    output = ROOT / 'dist' / 'feed.json'
    output.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print('Wrote', output.relative_to(ROOT), '| NBA refs:', payload['nba_referees']['status'], '| odds:', payload['fanduel_moneylines']['status'])

if __name__ == '__main__':
    main()
