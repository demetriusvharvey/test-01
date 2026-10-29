# NBA verified first-quarter lineup associations

Run 2026-10-29T19:52:19.724766+00:00. H025. Source failures: 0.
Source IDs, unique period constraints and explicit substitutions reconstruct stints. Ambiguous games are rejected. Scope: verified first-quarter. Full-game mode also validates each player against box minutes and excludes overtime. This is postgame training data, not historical pregame availability. No public pick changes.

| Source season | Games seen | Accepted | Rejected | Stints |
|---|---:|---:|---:|---:|
| 2023 | 1321 | 811 | 510 | 5151 |
| 2024 | 1320 | 800 | 520 | 5073 |
| 2025 | 1324 | 734 | 590 | 4698 |
| 2026 | 1325 | 760 | 565 | 5207 |
| 2027 | 68 | 38 | 30 | 281 |

| Test season | Status | Matched games | Stints | Player MSE | Team MSE | League MSE | BH p |
|---|---|---:|---:|---:|---:|---:|---:|
| 2024-25 | evaluated | 95 | 141 | 4866.624 | 4913.502 | 4825.575 | 0.74643 |
| 2025-26 | evaluated | 122 | 222 | 6071.154 | 6087.744 | 6086.975 | 0.74643 |
| 2026-27 | evaluated | 14 | 29 | 5840.600 | 5841.836 | 5816.795 | unavailable |

MSE is minute-weighted squared error in net points per 48 minutes; lower is better. These are stint-rate errors, not game-winner accuracy. Ridge penalties are selected on a distinct prior season. Low-sample players are nuisance controls in training; only effects backed by 120 actual training minutes are published or admitted to validation/test rows. Unknown-player test rows are excluded. This selective coverage must not be described as all-game validation.

Ratings control observed teammates/opponents but remain observational associations. H026 tests are jointly corrected with H025. They are not possession RAPM, complete defensive ratings or causal injury effects. Full-game replacement and probability conversion require separate evaluation. All rejected-game reasons, source hashes, thresholds and fold artifacts are retained. No wagering-source approval or profit is established.

Artifact: observations/nba_lineups/230eda6b12b5334847cb9dfd02c78631acb82a37ea4a4e9e2032611930840c2e/evaluation.json.
