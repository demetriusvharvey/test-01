# NBA daily winner ranking comparison

Run 2026-11-11T18:52:24.713055+00:00. H029.
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
| 2026-27 | elo | 17 / 20 | 50 | 0.78000 | 0.686–0.878 | 0.15908 | unavailable |
| 2026-27 | team14 | 17 / 20 | 50 | 0.80000 | 0.725–0.880 | 0.15520 | 1.00000 |
| 2026-27 | player27 | 17 / 20 | 50 | 0.84000 | 0.755–0.922 | 0.13123 | 1.00000 |
| 2026-27 | lineup30 | 17 / 20 | 50 | 0.82000 | 0.735–0.902 | 0.13474 | 1.00000 |

Intervals resample entire calendar days using a fixed seed; small samples receive no interval. Paired tests compare selected outcomes on matched dates; models may choose different games. Multiple-test adjustment includes the related earlier outcome studies. Calibration bins and fixed-threshold coverage tables are retained in the artifact; thresholds are not optimized on these test results.

Archive coverage is not a verified historical schedule. A missing model/game excludes the entire date from the primary comparison, and exclusion counts are retained. The historical model features inferred membership and unknown historical availability; current conditional injury ranking is a separate forward policy. Previously inspected seasons are exploratory. No public record changes, model promotion, odds-based edge or ROI claim.

Artifact: observations/nba_winner_selection/c73ef7108645a8d60e58dd938f11f4a5fc3e7770b8c043459bd8f60120724350/evaluation.json.
