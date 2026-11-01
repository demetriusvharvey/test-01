#!/usr/bin/env python3
"""Audit saved walk-forward predictions without fitting/tuning on test data."""
import argparse
import hashlib
import json
from pathlib import Path
from scripts.line_lab.evaluation_audit import audit_fold


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',default='data/models/evaluation.json')
    parser.add_argument('--output',default='reports/forecast_evaluation_audit.json')
    args = parser.parse_args()
    raw = Path(args.input).read_bytes()
    source = json.loads(raw)
    report = {'source_sha256':hashlib.sha256(raw).hexdigest(),
              'protocol':'recompute frozen exploratory historical folds; no model selection or promotion',
              'leagues':{}}
    for league, data in source['leagues'].items():
        seen = set()
        folds = []
        for fold in data['folds']:
            ids = {r['id'] for r in fold['predictions']}
            if seen & ids:raise ValueError('game repeated across test folds')
            seen.update(ids)
            result = audit_fold(fold)
            folds.append(result)
            print(league, fold['season'], 'N', result['candidate']['sample_size'],
                  'Brier delta interval', result['paired_intervals_95']['brier_difference'])
        report['leagues'][league] = {'folds':folds, 'promoted':False}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':main()
