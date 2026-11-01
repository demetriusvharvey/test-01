"""Explain why today's forecasts cannot become bets without changing eligibility."""
from collections import Counter
from .constants import ET
from .history import aware


VALIDATION = {'validation_insufficient', 'availability_model_unvalidated',
              'validated_uncertainty_unavailable'}
DATA = {'injury_information_unverified', 'starting_lineups_unconfirmed',
        'starting_quarterbacks_unconfirmed', 'odds_missing_stale_or_unverified',
        'odds_identity_mismatch', 'forecast_not_fresh_pregame',
        'forecast_game_mismatch', 'invalid_or_missing_input'}


def summarize(games, now):
    current = aware(now)
    today = current.astimezone(ET).date()
    due = []
    for game in games:
        try:
            start = aware(game['starts_at'])
            if current < start and start.astimezone(ET).date() == today:
                due.append(game)
        except (KeyError, ValueError, TypeError):
            continue
    reasons = Counter(reason for game in due
                      for reason in (game.get('forecast') or {}).get('decision', {}).get('reasons', []))
    decisions = [(g.get('forecast') or {}).get('decision', {}) for g in due]
    qualified = sum(d.get('eligible') is True for d in decisions)
    missing = sum(not g.get('forecast') for g in due)
    # A price rejection is not evidence of no value when prerequisite evidence
    # is missing. The distinction is central to the public empty-state message.
    status = ('no_upcoming_games' if not due else 'qualified' if qualified else
              'validation_pending' if VALIDATION.intersection(reasons) else
              'data_unavailable' if missing or DATA.intersection(reasons) else
              'no_qualified_edge')
    return {'schema': 'recommendation-readiness-v1', 'as_of': now,
            'day': today.isoformat(), 'status': status, 'scheduled_games': len(due),
            'forecasts': len(due) - missing, 'recommendations': qualified,
            'missing_forecasts': missing, 'blockers': dict(sorted(reasons.items())),
            'validation_pending': bool(VALIDATION.intersection(reasons)),
            'data_pending': bool(missing or DATA.intersection(reasons))}
