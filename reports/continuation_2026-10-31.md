# Production inference and evaluation continuation — October 31, 2026

Starting production commit: `26055c8f3ce26a81052c89cb526cbb752487fe4c`.
Starting production deployment: `dpl_4WD9mPDVrr4AK8y2tVAHg7GYi3hB` (READY).

## Findings and implemented changes

- The deployed winner forecast still uses the incumbent Elo, not the separately fitted logistic ensemble. This is intentional: no challenger has earned independent promotion. Explicit per-game fallback reasons and structured workflow logs now expose that choice, missing artifacts, rejected inference and degraded efficiency coverage.
- The prior forward benchmark was `row['elo']`, a fixed-parameter feature-generator Elo, while production chooses Elo parameters using earlier seasons and can include earlier same-day confirmed finals. The ledger now freezes the actual production incumbent at the same prediction timestamp. Fixed Elo remains separately recorded. Old snapshots keep their original bytes and are labeled `legacy_fixed_elo`, never relabeled as newly matched production evidence.
- An approved prediction could previously nest itself as its own `research_model`, making JSON serialization recursive. Approved predictions now serialize normally. Missing required efficiency inputs force an explicit incumbent fallback even if the loaded challenger is approved.
- Reapplying inference to a blocked, started or unavailable game could retain an old public forecast object. Those fields are now cleared before fresh eligibility checks.
- The original forward writer attempted to JSON-serialize entire parser finals, including Python date/datetime fields. It now serializes a normalized minimal final, validates team identity, integer nonnegative scores, source and start time, and preserves immutable subsequent confirmations.
- Forward evaluation now respects an explicit as-of time for both forecasts and observed outcomes. The first forecast is selected by parsed instants, not lexically sorted timezone strings. Contradictory earliest forecasts and results remain unscored with diagnostics; later favorable snapshots never replace them. A changed start time remains pending with a diagnostic. Ties are void rather than indefinitely pending.
- Candidate and actual-incumbent comparisons use exactly the same frozen game sample. All-game model results remain separate, and missing benchmark coverage is counted. Per-league counts, calibration, accuracy intervals, pending/void counts and always-home winner accuracy are available.

## Historical reproduction, without tuning

Command: `python -m scripts.audit_forecast_evaluation`.

All 18 stored folds reproduced their reported counts, accuracy, Brier and log loss to 1e-12. Duplicate games, cross-fold repeated games, overlapping training/tuning/calibration dates, same-day/future feature cutoffs and mismatched published denominators fail verification. The detailed output is `reports/forecast_evaluation_audit.json`, linked to the exact original evaluation bytes by SHA-256.

These are the previously fitted candidate probabilities, not a newly selected or retrained model. Historical fixed Elo is explicitly labeled as such.

| League/season | Test dates | Games | Candidate accuracy | Fixed Elo accuracy | Candidate Brier | Fixed Elo Brier | Candidate-minus-Elo Brier 95% interval |
|---|---|---:|---:|---:|---:|---:|---|
| NBA 2024–25 | 2024-10-22–2025-04-13 | 1,225 | 65.96% | 65.96% | 0.212682 | 0.213869 | [-0.005556, 0.003523] |
| NBA 2025–26 | 2025-10-21–2026-04-12 | 1,225 | 68.00% | 67.76% | 0.207321 | 0.209231 | [-0.005772, 0.002147] |
| NBA 2026–27 | 2026-10-20–2026-10-29 | 71 | 63.38% | 60.56% | 0.217773 | 0.217117 | [-0.014199, 0.018621] |
| NFL 2025 | 2025-09-04–2026-02-08 | 284 | 62.32% | 64.08% | 0.227304 | 0.227745 | [-0.004184, 0.003269] |
| NFL 2026 | 2026-09-09–2026-10-26 | 106 | 59.43% | 58.49% | 0.232573 | 0.234441 | [-0.016590, 0.011485] |

Intervals use 2,000 paired day-block bootstrap replicates and fixed seed 20261101. They are exploratory, without multiple-comparison adjustment, and do not establish prospective promotion. Accuracy intervals use Wilson and are labeled descriptive because game dependence is not adjusted. Always-home is a deterministic winner rule, so no invented fitted probability is assigned to it.

The completed NBA-season Brier intervals include zero. Recent NFL evidence is mixed. No probability or accuracy improvement, profitability or promotion is claimed from these changes. No old historical result is reset.

## Live record and operational limits

The initial live board at `2026-10-31T23:28:57.355642+00:00` returned HTTP 200 with 6 wins, 4 losses, 2 pending and 60% from the same 12 original predictions. The earlier 55.6% was 5/9 before another original result settled. This natural settlement is not credited to this patch.

Injury/source refresh remains scheduled at minutes 9, 24, 39 and 54 each hour in GitHub Actions. This is a target cadence, subject to execution delays and upstream latency, not a real-time guarantee. ESPN fallback lists do not establish complete healthy rosters. Conditional injury scenarios remain research; verified starting lineups, NFL starting QBs, calibrated individual replacement effects and contemporaneous historical injury/odds coverage remain evidence gaps.

The existing 20-minute freshness and independent evidence gates remain in force. No paid data sources, subscriptions or hosting upgrades were added. Manual FanDuel entries remain browser-local, timestamped payout/break-even calculations, not automatically qualified recommendations. No verified historical price timestamps means no market baseline, preferred-price segment ROI or betting ROI can be claimed.

## Checks

- Full suite: **259 tests passed** (`python -m unittest discover -s tests`), versus 243 on the starting commit.
- JavaScript syntax and Git whitespace checks passed.
- Captured-slate replay against hashed archived data: **86 forecasts**, every incumbent probability reproduced to 1e-12, original public accuracy preserved, no qualified bets. The replay did not replace the source-refresh timestamp or publish refreshed data.
- Sixteen additional tests exercise outcome serialization, first-instant selection, as-of leakage, matched denominators, conflicting confirmations, invalid finals, ties, changed start times, stale forecasts, actual production benchmarks, approved-model serialization, historical leakage and reproducible intervals.

Deployment and hosted-refresh evidence is recorded after the release checks; a successful code build alone does not prove refreshed data used the new engine.
