"""Bounded public schedule corroboration; never extend a pregame deadline."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from .history import aware
from .constants import ET
from .ingest import parse_espn_starts
from .public_fetch import prefetch


def reconcile(starts, reference, observed_at):
    result = dict(starts)
    changes, conflicts = {}, []
    current = aware(observed_at)
    for key, value in reference.items():
        if key not in starts or aware(starts[key]) <= current:
            continue
        original, corroborated = aware(starts[key]), aware(value)
        if corroborated <= current or abs(original - corroborated) > timedelta(minutes=20):
            result.pop(key, None)
            conflicts.append(key)
        elif corroborated < original:
            result[key] = corroborated.isoformat()
            changes[key] = {'provider_start': starts[key], 'corroborated_start': value,
                            'effective_start': result[key]}
    return result, changes, conflicts


def collect(starts, now, getter):
    day = aware(now).astimezone(ET).date()
    sources = [(league, f'https://site.api.espn.com/apis/site/v2/sports/{sport}/{league.lower()}/scoreboard?dates={(day+timedelta(days=lead)).strftime("%Y%m%d")}')
               for league, sport in [('NBA', 'basketball'), ('NFL', 'football')] for lead in (0, 1)]
    fetch = prefetch([url for _, url in sources], getter, timeout=8, workers=4)
    result, reports = dict(starts), []
    for league, url in sources:
        report = {'league': league, 'source_url': url, 'status': 'unavailable'}
        try:
            text = fetch(url, 8)
            observed = datetime.now(timezone.utc).isoformat()
            payload = json.loads(text)
            if not isinstance(payload, dict) or not isinstance(payload.get('events'), list):
                raise ValueError('scoreboard schema')
            reference = parse_espn_starts(payload, league)
            result, changes, conflicts = reconcile(result, reference, observed)
            report.update(status='checked', observed_at=observed,
                          source_sha256=hashlib.sha256(text.encode()).hexdigest(),
                          reference_games=len(reference), timing_corrections=changes,
                          quarantined_games=conflicts)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            report['error_type'] = type(exc).__name__
        reports.append(report)
    return result, reports
