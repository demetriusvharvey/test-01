# Work summary

## What is built

- Step 0 and Phase 1: audit, source and hypothesis registries, modular Python pipeline, point-in-time quote checks, and an append-only SQLite data branch. Historical NFL and NBA source snapshots are attributed and labeled retrospective, not pregame knowledge. The optional Odds API adapter remains disabled when the free key is absent.
- Phase 2: immutable v2 paper ledger with distinct observed price, book, feature snapshot, future grading fields and clearly labeled retail close proxies. Actual wager fields remain empty unless the user supplies them.
- Phases 3–4: shadow anchor and three de-vig methods, qualified-source and fee guards, optional quota-capped spread/total collection, and empirical cross-market research tools. No independent sharp source or licensed historical NBA close is configured; retail is never called sharp.
- Phase 5: timestamped NFL injury/practice capture, shadow scenario helpers and a preregistered status-count challenger. NBA status capture happens before forecasts when a user-provided free PropLine key is enabled; only per-team aggregates are stored. NFL status capture no longer fails just because the QB data source fails. The challenger currently has no qualified training sample, does not estimate individual player impact, and does not change live predictions. Historical NBA status and lineup access/rights are unresolved.
- Phase 6: shadow margin Elo, season carryover and shrunk home-advantage tools, plus point-in-time schedule/rest/travel calculations. They do not automatically promote to production.
- Phase 7: descriptive, shrunken NFL referee report using 1,328 retrospective games. Source/assignment timestamps and odds do not support causal or prospective claims. NBA officials are archived when available, without invented effects.
- Phase 8: preregistered schedule-pattern batch, day-block tests, multiple-testing correction and append-only trial logs. The initial forward run had 96 forecast snapshots and no matched settled outcomes; all ten tested definitions were `not_testable`.
- Phase 9: prior-only, market-independent elastic-net and monotonic boosted-stump challengers, plus a regularized status-count challenger with an unchanged team forecast as offset. The append-only registry and weekly workflow log insufficient data and compare later challenger forecasts against frozen baselines from the same timestamp. None is promoted. The stump model is not XGBoost, LightGBM or CatBoost.
- Phase 10: user-requested ordering takes the model-favored side, applies existing freshness, source and price guards, then ranks qualified candidates by predicted win probability instead of EV. Previous selections stay immutable. This ordering is uncalibrated and has not been shown to improve returns. Append-only logs include skipped sides; trust, timing and execution-aware replay helpers remain research-only. A missing candidate audit suppresses new picks.
- Phases 11–12: prospective validation calculations, strict evidence gates and counts; feature drift/freshness monitoring and missed-update warnings. Grading requires explicit final status and holds conflicting supplemental scores for review; a score alone is not treated as a final. No wagering is automated.
- Phase 13: the user-facing site shows picks, sportsbook prices, record and accuracy, date history, variables, a daily rotating quote and explicitly unavailable injury context. A separate temporary watchlist follows Philadelphia without adding it to the model's accuracy record. The user-requested simplified interface omits research dashboards and model percentages.
- Phase 14: source-isolated bounded retries, versioned feature snapshots, structured run summaries, Python 3.12 configuration and CI. Unit and fixture tests accompany each implementation stage.

## Lakers review and honest numbers

On October 27, 2026 Portland beat the Lakers 136–129. The frozen legacy pick was Lakers moneyline: a FanDuel quote of -126 was recorded separately from a best quote of -125 at other books. No actual bet is recorded. One loss does not identify a faulty feature or justify changing a model weight. The review and source details are in [reports/lakers_2026-10-27.md](reports/lakers_2026-10-27.md).

At the initial prospective research checkpoint, no independently verified sharp-closing sample or settled pure-model paper picks were available. Consequently, sharp CLV, its confidence interval, an unbiased sharp-market comparison, and a defensible ROI interval are **not available**. The all-model historical win counter includes older legacy picks and is not proof of profit. No gains, improved accuracy, or profitable edge are claimed.

## What is not finished

The full master prompt is **not complete**. Certified sharp prices and closes, pregame NBA injury/lineup rights, complete point-in-time player and referee history, XGBoost/LightGBM/CatBoost and Bayesian/lineup models, validated trust and timing models, an eligible execution-aware walk-forward backtest, and the required future replication/holdout results are missing. Several research helpers are implemented, but cannot substitute for licensed historical data or results that have not happened. Per-league qualification requires 300 settled prospective picks and additional preregistered evidence; none is guaranteed. The site places no bets.

The underlying odds pages and scheduled update are roughly hourly, and scheduled jobs can be delayed; the browser's once-a-minute check does not create a minute-by-minute source. No purchase, subscription, paid feed, or additional account was created.

## Next five priorities

1. Establish a permitted, independently sourced sharp pregame and certified closing-price feed with reliable timestamps and retention rights.
2. Obtain rights-compatible NBA injury, lineup and player data, along with verified NFL starting-QB and inactive statuses, without backdating knowledge.
3. Accumulate prospective paper forecasts, all skipped candidates, actual confirmed outcomes and sufficiently frequent price observations.
4. Evaluate the preregistered challengers and availability/schedule factors using walk-forward splits, multiple-testing correction, two independent season replications and a later untouched holdout.
5. Validate calibration, execution assumptions and sharp CLV, improve feed latency only with an appropriate authorized source, and promote changes only if the evidence supports them.
