"""Report archived source schemas without printing protected rows or secrets."""
import argparse
import json
import sqlite3
from pathlib import Path

DATASETS = ('nba_team_game_boxscores', 'nfl_pbp', 'nfl_schedules')

def inspect(root):
    base = Path(root) / 'observations' / 'backfill'
    lines = ['# Archived simulator input schemas', '', 'Column names describe retrospective assets only. No live injury, lineup or odds data are implied.', '']
    for dataset in DATASETS:
        lines.append(f'## {dataset}')
        files = sorted((base / dataset).glob('*.sqlite'))
        if not files:
            lines.extend(['', 'Unavailable.', ''])
            continue
        for file in files:
            with sqlite3.connect(file) as db:
                row = db.execute('SELECT columns_json, row_count, source_url, retrieved_at FROM assets ORDER BY retrieved_at DESC LIMIT 1').fetchone()
            if row:
                cols, count, url, timestamp = row
                lines.extend(['', f'- Season: {file.stem}; rows: {count}; archived: {timestamp}; source: {url}', f'- Columns: {", ".join(json.loads(cols))}'])
        lines.append('')
    return '\n'.join(lines)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-root', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    Path(args.output).write_text(inspect(args.data_root))
