# NBA first-quarter lineup associations

Run 2026-10-29T19:37:01.079455+00:00. H025. Source failures: 0.
Actual starters and explicit substitution IDs reconstruct first-quarter stints only. Whole games with ambiguous reconstruction are rejected. This is postgame training data, not historical pregame availability. No public pick changes.

| Source season | Games seen | Accepted | Rejected | Stints |
|---|---:|---:|---:|---:|
| 2023 | 1321 | 811 | 510 | 5151 |
| 2024 | 1320 | 800 | 520 | 5073 |
| 2025 | 1324 | 734 | 590 | 4698 |
| 2026 | 1325 | 760 | 565 | 5207 |
| 2027 | 68 | 38 | 30 | 281 |

| Test season | Status | Matched games | Stints | Player MSE | Team MSE | League MSE | BH p |
|---|---|---:|---:|---:|---:|---:|---:|
| 2024-25 | insufficient_matched_stints | — | 0 | — | — | — | — |
| 2025-26 | insufficient_matched_stints | — | 0 | — | — | — | — |
| 2026-27 | insufficient_matched_stints | — | 0 | — | — | — | — |

MSE is minute-weighted squared error in net points per 48 minutes; lower is better. These are stint-rate errors, not game-winner accuracy. Ridge penalties are selected on a distinct prior season. Only players with at least 120 earlier stint minutes are estimated; rows with unknown effects are excluded, including test rows. This selective coverage must not be described as all-game validation.

Ratings control observed teammates/opponents but remain observational, first-quarter associations. They are not possession RAPM, complete defensive ratings or causal injury effects. Full-game replacement and probability conversion require separate evaluation. All rejected-game reasons, source hashes, thresholds and fold artifacts are retained. No wagering-source approval or profit is established.

Artifact: observations/nba_lineups/230eda6b12b5334847cb9dfd02c78631acb82a37ea4a4e9e2032611930840c2e/evaluation.json.
