# Prediction engine engineering report — October 31, 2026

## Baseline preserved

Original source commit: `d35effb38a81623a1875f8d93e534f1600060221`.
Original daily policy: up to three highest Elo winner probabilities per Eastern calendar day, saved once; odds, injuries and lineups did not affect the chosen probability.

The public 55.6% is **5 wins / 9 settled predictions**, not a large backtest. NBA: **4–4 (50%)**. NFL: **1–0 (100%; one game)**. Three October 31 NBA forecasts are pending. All 12 original records remain; no losses were removed and no old predictions were replaced.

| Pick date (Eastern) | League | Saved team | Outcome | Original probability |
|---|---|---|---|---:|
| 2026-10-28 | NBA | San Antonio Spurs | win | 0.819039 |
| 2026-10-28 | NBA | Oklahoma City Thunder | loss | 0.805564 |
| 2026-10-28 | NBA | Minnesota Timberwolves | loss | 0.727953 |
| 2026-10-29 | NBA | Portland Trail Blazers | loss | 0.743297 |
| 2026-10-29 | NFL | Green Bay Packers | win | 0.665822 |
| 2026-10-29 | NBA | New Orleans Pelicans | win | 0.587629 |
| 2026-10-30 | NBA | Boston Celtics | win | 0.840329 |
| 2026-10-30 | NBA | Detroit Pistons | win | 0.830094 |
| 2026-10-30 | NBA | Charlotte Hornets | loss | 0.746717 |
| 2026-10-31 | NBA | Portland Trail Blazers | pending | 0.720389 |
| 2026-10-31 | NBA | Cleveland Cavaliers | pending | 0.693160 |
| 2026-10-31 | NBA | San Antonio Spurs | pending | 0.666955 |

Original settled-probability Brier: **0.295307**; log loss: **0.796746**. The probability sample is nine. This is descriptive, not sufficient calibration evidence.

Frozen winner ledger SHA-256: `b916ae0eb3775d3aa83189ff948bc9929816a423f3b5b0643e055ba0055dbdfd`.

## Pipeline audit and implementation

| Area | Finding and resulting behavior |
|---|---|
| Ingestion | BoxScore Lab score/efficiency CSVs, nflverse schedules/PBP, scoreboard schedules, and original odds adapters retained. Independent public requests now use six bounded workers. Cached archive bytes are hash-checked; conflicting duplicate games fail closed. |
| Team ratings | Existing incumbent Elo formula and parameter selection retained. New day-start feature builder uses strictly earlier dates, opponent-rating-adjusted margins, scoring/allowed rates, rest, back-to-backs and experience. Same-day results cannot alter those features. |
| NBA research | Existing statistical, rotation, player-box, stint, lineup, scenario and ensemble models remain research. Conditional scenarios are connected to public upcoming-game details and append-only forecasts. No unweighted scenario average is invented. |
| NFL research | Separate fitting, seasonal windows and coefficients; EPA/play, offensive/defensive success, passing/rushing contributions are candidate features from earlier PBP. Unknown venue status prevents a forecast. Starting quarterbacks must be confirmed before a bet can qualify. |
| Injuries | Existing optional provider retained. Keyless ESPN JSON fallback maps explicit athlete IDs and source teams, records observation/source timestamps and excludes unknown/conflicting/future rows. No commentary is scraped into Git. Missing listings never establish health. |
| Injury changes | Per-game status fingerprints detect changes even when aggregate counts are identical. Refreshes append new observations; original forecasts remain immutable. |
| Lineups | Current roster joins and minute/rotation models support conditional research scenarios; actual confirmed starting lineups and validated replacement effects remain unavailable. |
| Training | New league-specific regularized logistic candidates, optional efficiency/EPA features, finite C grid and convex Elo/model weight grid. Weights/features select on an earlier tuning period. Calibration fitting and a later calibration check are disjoint from final season tests. |
| Calibration | Identity versus Platt chosen before the final season. Reliability bands, sample counts, Brier and log loss retained. Retrospective calibration is labeled explicitly; it is not prospective betting approval. |
| Simulations | Existing 10,000-draw seeded score bootstrap is exposed across eligible scheduled games. It remains research because incremental predictive value and player/drive adjustments have not earned promotion. NBA possession simulator also remains research. |
| Market/selection | American break-even, proportional no-vig, raw EV, probability edge and uncertainty-adjusted edge are calculated separately. -150 breaks even at 60%. New public entry point cannot force three bets. |
| Eligibility | Requires exact league/artifact validation, 300+ out-of-sample games, calibration/edge evidence, verified fresh availability, confirmed NFL QBs, fresh two-sided observed prices, valid uncertainty bounds, 3 percentage-point conservative edge and 2% conservative EV. These thresholds are guards, not claimed optimized profitable settings. |
| Forecast history | Immutable SQLite forecasts and outcomes, exact input snapshots/hashes and first-pregame-per-game/model evaluation. Candidate and matched Elo forecasts are scored separately; model identity stays stable across identical weekly exports. |
| Accuracy | Original denominator and all original settled outcomes remain visible. Even integrity-flagged old records remain in the record, with diagnostics, instead of hiding losses. New research scores are separate. |
| Refresh jobs | Snapshot job targets every 15 minutes; source latency and Actions scheduling delays are explicit. Model fitting is an independent weekly/manual job; no sklearn retraining during inference. Upcoming dates are fetched individually from ESPN after the range endpoint returned HTTP 400. |
| Failure handling | Missing or stale data suppress recommendations. During total schedule failure, a cached slate can remain visible but cannot restore stale recommendations. Conflicting archived research outcomes preserve the original and generate a diagnostic. |
| UI | Existing styling, pages, history, odds and navigation retained. Small copy/detail changes distinguish recommendations, saved forecasts, incumbent predictions, research challengers and injury scenarios. |

## New chronological evaluation

Each final season is tested after earlier training, tuning and calibration windows. The archive has been inspected, so these are exploratory historical walk-forward results, **not an untouched prospective holdout**. No model was promoted on these numbers. Winner accuracy below covers every eligible game in the listed fold, not the original selected-nine denominator.

| League | Test season | Games | Candidate accuracy | Elo accuracy | Candidate Brier | Elo Brier | Candidate log loss | Elo log loss |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| NBA | 2024-25 | 1225 | 65.96% | 65.96% | 0.212682 | 0.213869 | 0.612911 | 0.615439 |
| NBA | 2025-26 | 1225 | 68.00% | 67.76% | 0.207321 | 0.209231 | 0.602566 | 0.606891 |
| NBA | 2026-27 | 71 | 63.38% | 60.56% | 0.217773 | 0.217117 | 0.624013 | 0.620535 |
| NFL | 2012 | 266 | 62.03% | 59.77% | 0.224792 | 0.227296 | 0.639243 | 0.645410 |
| NFL | 2013 | 266 | 65.41% | 62.41% | 0.220579 | 0.223975 | 0.630252 | 0.638116 |
| NFL | 2014 | 266 | 67.29% | 66.54% | 0.203603 | 0.212131 | 0.593853 | 0.613530 |
| NFL | 2015 | 267 | 62.55% | 67.79% | 0.228798 | 0.225207 | 0.649022 | 0.642637 |
| NFL | 2016 | 265 | 64.15% | 63.77% | 0.222193 | 0.222816 | 0.634436 | 0.636030 |
| NFL | 2017 | 267 | 66.29% | 64.04% | 0.220090 | 0.224816 | 0.630059 | 0.639799 |
| NFL | 2018 | 265 | 64.53% | 62.26% | 0.221014 | 0.229272 | 0.631587 | 0.649077 |
| NFL | 2019 | 266 | 63.91% | 63.91% | 0.225969 | 0.227347 | 0.643412 | 0.646669 |
| NFL | 2020 | 268 | 66.42% | 64.18% | 0.219938 | 0.222535 | 0.631552 | 0.636738 |
| NFL | 2021 | 284 | 60.56% | 61.27% | 0.233179 | 0.229959 | 0.658900 | 0.651872 |
| NFL | 2022 | 282 | 62.06% | 61.35% | 0.227911 | 0.230208 | 0.647075 | 0.652040 |
| NFL | 2023 | 285 | 61.40% | 62.11% | 0.231560 | 0.232625 | 0.656646 | 0.658370 |
| NFL | 2024 | 285 | 64.91% | 67.72% | 0.220083 | 0.214492 | 0.630247 | 0.618230 |
| NFL | 2025 | 284 | 62.32% | 64.08% | 0.227304 | 0.227745 | 0.645433 | 0.647108 |
| NFL | 2026 | 106 | 59.43% | 58.49% | 0.232573 | 0.234441 | 0.655580 | 0.660694 |

NBA Brier improves modestly in both completed test seasons, but its paired day-block log-loss tests are not significant (2024–25 p≈0.634; 2025–26 p≈0.368). The 71-game current NBA season has worse Brier (0.217773 versus 0.217117), despite higher winner accuracy. NFL results are mixed and include worse seasons. Therefore **no credible improvement is claimed, and the incumbent is not replaced by these challengers**. Current research predictions remain useful for a future fixed-policy comparison.

The existing research stack was also reviewed: the NBA efficiency logistic beat its histogram boosting alternative in the two completed evaluation seasons; the rotation ensemble reported 2025–26 Brier 0.20490 versus Elo 0.20848, then worse 2026–27 Brier on its small 52-game sample. Those are earlier reported research runs on different matched samples, not directly comparable to this new table. No research result is substituted for public accuracy.

All per-game predictions, chronological boundaries, tuning candidate scores, learned weights, seeds, input hashes, calibration bins and paired tests are stored in `data/models/evaluation.json`. Exact portable coefficient artifacts are versioned with hashes. Source revision/publication times for old archives cannot be reconstructed; the report explicitly labels this limitation.

## Calibration and missing wagering evidence

NBA current candidate uses a separately fitted Platt map; current NFL candidate retained identity calibration after the earlier check rejected Platt. Each fold includes probability-band counts, mean predicted probabilities, observed rates and winner accuracy. Sparse bands cannot establish reliability. No simulation frequency or scenario range is passed off as a confidence interval.

**Paper ROI, verified closing-line value and maximum wager drawdown are unavailable**: there are no qualifying contemporaneous frozen priced recommendations for the new engine. Historical schedule moneyline columns have no verified observation times, so they are not used to manufacture ROI. No market feature is trained from those untimestamped columns.

## Remaining evidence and data limits

- No challenger has earned independent prospective promotion; original 55.6% remains the headline until real additional original outcomes settle.
- A calibrated unconditional injury-aware probability is not established. Confirmed OUT players affect conditional research rotation scenarios, but causal player values, replacement effects and scenario participation weights remain unvalidated.
- Confirmed starting lineups, verified NFL starting QB/inactive lists, offensive-line impact, travel and point-in-time weather are not available as qualified trained features. Unknown inputs remain missing rather than being guessed.
- Historical pregame injury reports and quote observation times cannot be recreated from current reports. The new append-only observations build this evidence going forward.
- The free injury endpoint is best-effort with no contracted latency/completeness. Provider refusals and source failures are not bypassed.
- Archived research data contains inconsistent start/result confirmations. Their original outcomes are preserved and the conflict is reported; the new pipeline isolates that failure instead of aborting unrelated forecasts.

## Verification and release

Baseline suite: 224 tests passed. Updated suite and release verification are recorded below after the final run. Tests cover odds arithmetic, negative EV, stale/future/missing prices, missing injuries, QB uncertainty, explicit player/team identity, chronological leakage, artifact hashes, portable inference, calibration, ensemble weights, duplicate games, immutable history, first-forecast grading, injury changes, matched Elo and zero-pick outcomes. Existing simulation reproducibility tests are retained.

Production target: https://nba-nfl-moneylines.vercel.app (existing Vercel project `line-lab-picks`).

Release checks, commit and deployment identifiers will be appended after verification.

Final local checks: **243 tests passed** (`python -m unittest discover -s tests`); browser JavaScript syntax and Git whitespace checks passed. Portable sklearn exports were compared to sklearn probabilities to 1e-12 during fitting.

Live keyless run: 71 scheduled games, 57 NBA conditional injury scenario forecasts, 119 valid archived quote observations, zero recommendations. ESPN injury adapter independently parsed 87 NBA and 800 NFL entries with zero parsing errors. Captured-slate replay verified all 71 incumbent predictions (57 NBA, 14 NFL) against frozen Elo snapshots to 1e-12, preserved 5–4 / 55.6%, and appended new observations without changing the source-refresh timestamp.

The raw source quotes in that run were too old for the stricter 20-minute value gate; they remain labeled snapshots rather than invented current prices.

## Verified release identifiers

- Implementation commit: `11a5980027999513224aaa39b57ec6302ceb1961`.
- Immutable operational-observation commit: `531f36a33ce8c94a96c9d2d7688a1212b09adfe5` on `data/observations`.
- Initial GitHub CI: [successful run 41237527861](https://github.com/demetriusvharvey/test-01/actions/runs/41237527861); Python and JavaScript checks both passed.
- Initial production deployment: `dpl_EyViJTD4eX76AwhudL8fhGJxiuXL`, READY, exact implementation SHA confirmed.
- Production homepage and board both returned HTTP 200. Live board contained 71 research forecasts (57 NBA, 14 NFL), 57 conditional injury scenario sets, zero recommendations, all 12 legacy rows and unchanged 55.6%.
- Browser checks verified upcoming NBA/NFL controls, explicit unconfirmed NFL QBs, research-only labeling, zero recommendations and the original record. Final copy cleanup labels the section Recommendations and saved forecasts.

A further audit found 500 older research snapshots were rejected solely because their saved Elo benchmark was missing. The evaluator now preserves their first valid model prediction and scores it; paired Elo comparisons have their own matched sample and missing-benchmark count. It never reconstructs a missing old benchmark or substitutes a later prediction. In the available confirmed sample, three scored model forecasts have no original matched benchmark; paired differences are therefore unavailable. The ten existing start-time confirmation mismatches remain explicitly excluded from that separate research evaluation rather than being treated as losses or fabricated finals. These are not the original nine public results.

The first hosted refresh successfully executed predictions, but its publish step encountered a binary add/add conflict with the operational-observation commit made during that run. The snapshot was preserved, and the refresh is being rerun from the updated observation head. This was a release synchronization collision; the final refresh status is reported in the delivery message.

Production refresh verification uncovered a further NFL integration bug: recreating display-market rows dropped venue metadata even though the schedule had confirmed it. The board renderer now rejoins explicit schedule neutral/home values for priced games. Unknown venue cases also clear any legacy winner label. The live hosted refresh recovered successfully on attempt 2; the follow-up venue test covers both true neutral-site and explicit false home-site values.

The deployed-pipeline refresh on GitHub succeeded after the release synchronization retry. The final venue fix was also smoke-tested against the larger live captured slate: 90 reproducible forecasts, with the original accuracy unchanged. This smoke run preserved the captured source timestamp and was not substituted into historical results.

## Final hosted verification

- Final engine fix commit: `07150edabb102fa87c07e1df5cdb7b4dfd9f9832`.
- [Final CI run 41238314472](https://github.com/demetriusvharvey/test-01/actions/runs/41238314472): successful; 243 tests and browser-script syntax passed.
- [Hosted refresh run 41238314429](https://github.com/demetriusvharvey/test-01/actions/runs/41238314429): successful, including actual inference, append-only observation commit and board publication. The earlier synchronization collision recovered successfully on attempt 2 of run 41237527840.
- Published data commit: `d0dbe2eacb45016df08036361f0eb203fdbac410`. Production deployment `dpl_EPS77FVXm17Eeq9UHiwW6neceTZv`: READY and exact commit verified.
- Production board HTTP 200 at snapshot `2026-10-31T20:19:13.280035+00:00`: 90 scheduled games analyzed; 84 usable research forecasts (62 NBA, 22 NFL); 57 NBA conditional injury scenario sets; zero qualified recommendations. Six additional NFL games had unverified venue metadata in the current schedule source and were explicitly withheld rather than assuming home-field advantage.
- All 12 original public forecasts remain, with 5 wins / 4 losses / 3 pending and unchanged 55.6% accuracy. One conflicting/invalid source quote was quarantined.

No higher live prediction accuracy, positive paper ROI, fully calibrated injury-aware champion or completion of the missing independent validation is claimed. Those evidence requirements remain open; unqualified forecasts cannot bypass the recommendation gate.
