# Availability evidence and FanDuel eligibility verification

Verification date: November 1, 2026 (America/New_York).

## Observed starting state

The production alias served commit `0d1bcd9`, deployment
`dpl_EFvWheJXUyb9peQQS8CnE5TprWGj`, READY. The latest CI and daily-picks
workflow runs were successful. The previously cited `88e8d36` was an ancestor,
not the latest production snapshot. Baseline local verification: 259 tests passed.
The public legacy winner record was already 8 wins, 4 losses, 0 pending (66.7%).
This small selected-game record is separate from all-game research evaluation.

## Implemented behavior

- ESPN duplicate status conflicts quarantine every version of that identity,
  independent of input order. Conflicting team membership is also quarantined.
- Nonzero injury listings on both teams no longer imply complete coverage.
  Full coverage requires an explicit source completeness assertion, while the
  production verification and model-validation gates remain independent.
- Production forecasts freeze game-specific aggregate availability evidence,
  source URLs/hashes, retrieval and supplied source timestamps, and market snapshots.
- A bounded free ESPN NFL depth-chart adapter preserves explicit IDs, source
  provenance and provider-order projections, cached for at most one hour.
  Rams/Commanders use ESPN's `lar`/`wsh` slugs. No projection confirms a starter.
  An omitted or stale (>30h) QB injury designation remains unknown. Older
  reported statuses retain their timestamp and are not treated as current health.
- Malformed or empty primary injury responses can fall back to the existing
  keyless public ESPN injury adapter. A failed depth source cannot abort the board.
- Ingested quotes must match canonical game/date/league/team identity and h2h.
  Market snapshots preserve provider, bookmaker, game, teams and source URL.
- Eligibility uses only FanDuel paired moneyline prices with matching identity,
  source/retrieval timestamps and a maximum source age of 20 minutes. Another
  book cannot substitute for FanDuel. No-vig uses the paired quote; EV uses the
  actual offered payout. Manual FanDuel calculator behavior is retained.
- Independent failure reasons remain visible when availability is missing;
  missing injury timestamps no longer short-circuit odds and lineup diagnostics.
- Per-book/league source diagnostics distinguish unavailable, empty, fresh and
  stale-for-eligibility responses. No paid odds subscription was introduced.
- Existing UI layout is retained; NFL game details add projected QB coverage.

## Validation

271 tests passed, browser JavaScript syntax passed, Python compilation passed,
and `git diff --check` passed. This is a static Python-generated site, with no
package.json, TypeScript check or application bundler build. The Vercel static
build and fresh hosted pipeline are checked separately at release.

A real keyless source refresh completed at 2026-11-01T04:27:13Z. It archived
159 price observations and 85 research forecasts: 58 NBA and 27 NFL. Every
forecast had captured injury-source context, but none had verified complete
availability. Zero bets qualified. The legacy 8–4 record was unchanged.

End-to-end trace examples:

- NBA `nba:2026-11-01:BOS:ORL`: ESPN injury source -> aggregate evidence and
  hash -> incumbent Elo with shadow challenger -> explicit lineup/availability,
  calibration, uncertainty and price failure reasons -> immutable production ledger.
- NFL `nfl:2026-11-01:ARI:DAL`: ESPN injury source and explicit-ID QB depth
  projections -> captured game evidence -> incumbent Elo with shadow challenger
  -> unconfirmed-QB and other eligibility failures -> immutable production ledger.

The local refresh first revealed LA/WAS depth slug errors, subsequently fixed
and both corrected URLs fetched/parsed successfully. It also revealed old
"available" QB reports; a regression test now requires those to remain unknown.
A hosted refresh verifies the final code and new board before release completion.

A byte-for-byte payload comparison against the preceding observations commit
verified preservation of all 685 original production forecasts, 4 original
outcomes and 4 confirmations; the local run appended 85 forecasts, 2 outcomes
and 6 confirmations. Contradictory research results remain preserved/flagged.
No original prediction, loss or timestamp was replaced.

## Reproduced chronological evaluation

`python -m scripts.audit_forecast_evaluation` reproduced all 3 saved NBA folds
and 15 NFL folds without fitting or tuning. These are previously inspected,
exploratory historical folds, not a new untouched injury-aware holdout. The
latest available fold is shown here; it predates this reliability change.

| League/fold | Games | Challenger accuracy | Fixed-Elo accuracy | Home winner accuracy | Challenger Brier | Fixed-Elo Brier | Challenger log loss | Fixed-Elo log loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NBA 2026–27 | 71 | 63.38% | 60.56% | 49.30% | 0.21777 | 0.21712 | 0.62401 | 0.62053 |
| NFL 2026 | 106 | 59.43% | 58.49% | 49.06% | 0.23257 | 0.23444 | 0.65558 | 0.66069 |

NBA paired day-block 95% Brier-difference interval: [-0.01420, 0.01862].
NFL: [-0.01659, 0.01149]. Both include zero. Full per-fold calibration bands,
accuracy intervals, chronological cutoffs and denominator checks are in
`reports/forecast_evaluation_audit.json`. The fixed-Elo historical feature is
not mislabeled as the actual production incumbent benchmark; prospective
incumbent forecasts remain separately frozen and scored.

Historical matched-time prices and availability reports are insufficient for
credible market comparisons or injury-adjusted betting ROI. Market favorite
results, betting ROI, drawdown and confidence intervals remain unavailable;
they are not fabricated from retrospective/current prices. No betting threshold
or model was tuned against these evaluation folds.

## Remaining limitations

Elo remains live; trained league challengers and player-impact scenarios remain
shadow-only. This change improves reliability and auditability, not demonstrated
winner accuracy or validated profitability. Complete NBA starting lineups and
confirmed game-specific NFL starters/inactives remain unverified. The public
injury endpoint and depth chart do not provide those confirmations. Player
adjustments need prospective point-in-time outcomes and independent validation.

Actions is scheduled every 15 minutes, subject to delays. AgentBets prices update
about hourly, so many valid display quotes exceed the stricter 20-minute betting
limit. FanDuel/Fanatics NBA pages recovered during local inspection; intermittent
source failures are diagnosed rather than patched with invented prices. No free
continuous FanDuel fallback with reliable timestamps was established. The manual
calculator cannot turn an unvalidated model into an eligible recommendation.

The next highest-value task is prospective, game-specific confirmed lineup and
starter coverage with measured latency, followed by frozen-model forward
calibration and paired market evaluation. Current reports must not be backfilled
into historical games.
