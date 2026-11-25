# NBA daily winner ranking comparison

Run 2026-11-25T20:36:02.175273+00:00. H029.
Fixed top-three winner ranking, no sportsbook input. All four models use the same complete archived dates. This evaluates the daily selection objective, not betting profitability.

| Season | Model | Complete / archive days | Selected | Accuracy | Day-block 95% interval | Selected Brier | Joint BH p |
|---|---|---:|---:|---:|---|---:|---:|
| 2024-25 | elo | 159 / 162 | 466 | 0.73820 | 0.696–0.778 | 0.18082 | unavailable |
| 2024-25 | team14 | 159 / 162 | 466 | 0.75536 | 0.715–0.797 | 0.17429 | 1.00000 |
| 2024-25 | player27 | 159 / 162 | 466 | 0.76824 | 0.728–0.808 | 0.16831 | 0.69183 |
| 2024-25 | lineup30 | 159 / 162 | 466 | 0.75751 | 0.716–0.800 | 0.17138 | 1.00000 |
| 2025-26 | elo | 160 / 163 | 475 | 0.76632 | 0.726–0.803 | 0.17126 | unavailable |
| 2025-26 | team14 | 160 / 163 | 475 | 0.76842 | 0.732–0.804 | 0.17382 | 1.00000 |
| 2025-26 | player27 | 160 / 163 | 475 | 0.77053 | 0.732–0.806 | 0.17212 | 1.00000 |
| 2025-26 | lineup30 | 160 / 163 | 475 | 0.76842 | 0.731–0.804 | 0.17180 | 1.00000 |
| 2026-27 | elo | 31 / 34 | 92 | 0.77174 | 0.696–0.848 | 0.16451 | unavailable |
| 2026-27 | team14 | 31 / 34 | 92 | 0.77174 | 0.696–0.846 | 0.17034 | 1.00000 |
| 2026-27 | player27 | 31 / 34 | 92 | 0.80435 | 0.731–0.871 | 0.14993 | 1.00000 |
| 2026-27 | lineup30 | 31 / 34 | 92 | 0.79348 | 0.720–0.868 | 0.15225 | 1.00000 |

Intervals resample entire calendar days using a fixed seed; small samples receive no interval. Paired tests compare selected outcomes on matched dates; models may choose different games. Multiple-test adjustment includes the related earlier outcome studies. Calibration bins and fixed-threshold coverage tables are retained in the artifact; thresholds are not optimized on these test results.

Archive coverage is not a verified historical schedule. A missing model/game excludes the entire date from the primary comparison, and exclusion counts are retained. The historical model features inferred membership and unknown historical availability; current conditional injury ranking is a separate forward policy. Previously inspected seasons are exploratory. No public record changes, model promotion, odds-based edge or ROI claim.

Artifact: observations/nba_winner_selection/cf1ba45e43781ee2802152a66848f88e98ac927ff36bc3a09a42045e22af6b8a/evaluation.json.
