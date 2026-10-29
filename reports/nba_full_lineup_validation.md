# NBA uniquely reconstructed regulation-game lineup associations

Run 2026-10-29T20:10:34.968234+00:00. H026. Source failures: 0.
Source IDs, unique period constraints and explicit substitutions reconstruct stints. Ambiguous games are rejected. Scope: uniquely reconstructed regulation-game. Full-game mode also validates each player against box minutes and excludes overtime. This is postgame training data, not historical pregame availability. No public pick changes.

| Source season | Games seen | Accepted | Rejected | Stints |
|---|---:|---:|---:|---:|
| 2023 | 1321 | 136 | 1185 | 3842 |
| 2024 | 1320 | 107 | 1213 | 3017 |
| 2025 | 1324 | 91 | 1233 | 2654 |
| 2026 | 1325 | 85 | 1240 | 2670 |
| 2027 | 68 | 1 | 67 | 33 |

| Test season | Status | Matched games | Stints | Player MSE | Team MSE | League MSE | BH p |
|---|---|---:|---:|---:|---:|---:|---:|
| 2024-25 | insufficient_matched_stints | — | 7 | — | — | — | — |
| 2025-26 | insufficient_matched_stints | — | 89 | — | — | — | — |
| 2026-27 | insufficient_matched_stints | — | 0 | — | — | — | — |

MSE is minute-weighted squared error in net points per 48 minutes; lower is better. These are stint-rate errors, not game-winner accuracy. Ridge penalties are selected on a distinct prior season. Low-sample players are nuisance controls in training; only effects backed by 120 actual training minutes are published or admitted to validation/test rows. Unknown-player test rows are excluded. This selective coverage must not be described as all-game validation.

Ratings control observed teammates/opponents but remain observational associations. H026 tests are jointly corrected with H025. They are not possession RAPM, complete defensive ratings or causal injury effects. Full-game replacement and probability conversion require separate evaluation. All rejected-game reasons, source hashes, thresholds and fold artifacts are retained. No wagering-source approval or profit is established.

Artifact: observations/nba_full_lineups/7f7908fd7b6631d4229816bde8dfd27670c5b9cd23e5bfd9ada861148ae63b40/evaluation.json.
