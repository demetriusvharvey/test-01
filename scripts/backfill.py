#!/usr/bin/env python3
"""Download licensed source snapshots to the separate research-data checkout."""
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.line_lab.backfill import fetch_and_archive

if __name__=='__main__':
    target=os.environ.get('PICKS_DATA_ROOT')
    if not target:
        print('Set PICKS_DATA_ROOT to a separate research-data checkout.',file=sys.stderr)
        raise SystemExit(2)
    results,failures=fetch_and_archive(target)
    print(json.dumps({'completed':results,'failed':failures},indent=2))
    if failures: raise SystemExit(1)
