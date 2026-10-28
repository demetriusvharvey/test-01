# Phase 12: tracking and monitoring

Forward forecasts, selected and skipped paper candidates, trial outcomes and scorecard results are written before games or after confirmed finals with immutable records. The update pipeline has a scheduler-gap heartbeat and rejects stale, incomplete and conflicting quotes. Its generated board now carries quote freshness, source-warning count and feature-distribution monitoring. Alerts are displayed within the site; there is no unsolicited external messaging.

Drift monitoring uses each game's first eligible pregame forecast, compares a prior 28-day reference with the most recent seven days, and reports sample counts. Fixed-bin population stability is descriptive and requires at least 100 reference and 50 current games; an illustrative review flag is not evidence of calibration decay, causation or lost profitability. Small windows remain `insufficient_data`. The live dashboard must continue to assess age against the visitor's current clock because a scheduled job may stop running.

Calibration decay, truly independent source reconciliation, actual sharp CLV and a comparison with an unbiased backtest are still unavailable until the required prospective data and rights-compatible feeds exist. No gaps are filled with invented observations.

Confirmed results now retain separate, append-only source observations. If an ESPN final arrives first and nflverse confirms it later, research uses the later corroboration time without rewriting the original final. Conflicting recorded scores are excluded from NFL challenger training and evaluation instead of being resolved by guessing. This improves future eligibility but does not certify independent odds or provide additional past outcomes.
