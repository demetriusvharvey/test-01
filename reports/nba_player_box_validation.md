# NBA multi-stat player rotation comparison

Run: 2026-10-31T20:11:27.434630+00:00. Hypothesis H023.
Parsed played-player rows: 142241. Identical matched modeling games: 4761.
Separate older training, prior-season calibration and later-season testing. Archive previously inspected; exploratory only. All metrics use identical games. No public pick is changed.

| Season | Games | Team Brier | Rotation Brier | Multi-stat Brier | Elo Brier | Multi-stat accuracy | Log loss delta vs rotation | Raw p | BH p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1209 | 0.21020 | 0.20951 | 0.21045 | 0.21389 | 0.66501 | 0.00231 | 0.40586 | 0.81172 |
| 2025-26 | 1209 | 0.20638 | 0.20475 | 0.20485 | 0.20848 | 0.68817 | -0.00010 | 0.94511 | 0.94511 |
| 2026-27 | 55 | 0.22411 | 0.23089 | 0.23203 | 0.22053 | 0.56364 | -0.00016 | unavailable | unavailable |

A negative log-loss delta favors the candidate. BH adjustment covers every season reported for H023; prior archived hypotheses are not independent confirmation. Boosting metrics and all failures are retained in the machine-readable evaluation.

The learner estimates coefficients for projected box statistics; it does not estimate causal player values. Prior per-minute rates feed projected rotations with minutes conserved. Missing player statistics withhold the multi-stat projection instead of becoming zero. Current injury scenarios use the same summary definitions and enumerate listed uncertain players without fabricated weights.

Steals, blocks and rebounds do not capture all defense. Historical rosters and availability are inferred/unknown. Current source timestamps do not establish historical pregame publication. No ROI or source-use approval is established.

Detailed artifact: observations/nba_player_box/52afe312e1788325c3bb9d79f58314d0428761e01fb2f7cfb92afd301a6f582f/evaluation.json. Trained artifacts remain separate and disabled for public picks.
