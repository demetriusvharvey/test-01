# Pregame collection continuation — November 1, 2026

Starting production snapshot: `19c88bf` (implementation `9b65e2f`), Vercel
`dpl_23BxerKHjkLgLjX46wBSfPaEsDPs`, READY. Both CI and the refresh workflow
were successful. The legacy record was 8–4 and remains preserved.

## Changes

The production runner now attempts NBA per-game starter-list collection within
two hours of start. It matches exact team/date/start identities to a unique
ESPN event ID, verifies a scheduled pregame summary, and reduces explicit player
starter flags to attributed evidence. Five flags on each side are **listed,
unconfirmed**, not an official confirmed lineup. Unknowns, incomplete lists,
conflicts, outdated/future metadata and post-start/live/final summaries never
approve a recommendation. Snapshots are append-only and frozen again with
production forecasts. No historical availability is fabricated.

NFL QB joins now accept explicit ESPN namespace declarations, quarantine
conflicting IDs/statuses, validate statuses, and expose match/failure counts.
Older cached depth schemas are refreshed to populate projected names.

The board's generated timestamp is now the final inference timestamp, rather
than the earlier rendering-stage time. This prevents a newly published forecast
from appearing later than its containing board snapshot. Lineup-collection and
QB-report-match diagnostics are published alongside existing eligibility reasons.

## Source observations and limitations

The NBA CDN schedule and live scoreboard probes returned 403. They were not
bypassed. The current ESPN NBA pregame summary for `401909903` (BOS at ORL)
was fetched and parsed successfully, but contained no starter list. It remained
unknown. A completed-game summary verified the actual boolean `starter` schema;
completed-game data are rejected by the pregame parser, not reused as a forecast.

Most games are outside the collection window at this verification time. The
scheduled production workflow will attempt collection as they approach start.
Provider-listed flags have no independently verified confirmation contract, and
unknown publication timestamps remain null. Confirmed NBA lineups and confirmed
NFL game starters/inactives therefore remain blockers for betting approval.

## Validation and evaluation

283 tests passed, including new tests for exact mapping, ambiguous IDs,
wrong-team/start data, incomplete lists, source failures/malformed responses,
postgame leakage, stale/future timestamps, append-only evidence, bounded
collection windows, explicit QB joins and conflicting QB reports. JavaScript
syntax, Python compilation and whitespace checks passed.

The saved chronological evaluation was reproduced without refitting, tuning
thresholds, modifying artifacts or promoting a model. Historical calibration,
Brier and log-loss findings are unchanged from
`reports/forecast_evaluation_audit.json`. No improvement in predictive accuracy
or profitability is claimed for this data-collection change. Matched historical
availability and price evidence remain inadequate for credible injury-aware
ROI, drawdown or market-favorite performance estimates.

Elo remains the incumbent; trained challengers and player adjustments remain in
shadow mode. UI layout, manual FanDuel calculator and historical prediction
records are preserved. Next: obtain verifiable game-specific confirmations and
accumulate prospective, timestamped outcome/market comparisons.
