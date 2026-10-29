# NBA multi-stat player rotation comparison

Run: 2026-10-29T19:07:16.210946+00:00. Hypothesis H023.
Parsed played-player rows: 114003. Identical matched modeling games: 4758.
Separate older training, prior-season calibration and later-season testing. Archive previously inspected; exploratory only. All metrics use identical games. No public pick is changed.

| Season | Games | Team Brier | Rotation Brier | Multi-stat Brier | Elo Brier | Multi-stat accuracy | Log loss delta vs rotation | Raw p | BH p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1209 | 0.21020 | 0.20957 | 0.21089 | 0.21389 | 0.66584 | 0.00335 | 0.31357 | 0.62714 |
| 2025-26 | 1209 | 0.20638 | 0.20478 | 0.20478 | 0.20848 | 0.68652 | -0.00036 | 0.82482 | 0.82482 |
| 2026-27 | 52 | 0.21772 | 0.22669 | 0.22943 | 0.21432 | 0.53846 | 0.00187 | unavailable | unavailable |

A negative log-loss delta favors the candidate. BH adjustment covers every season reported for H023; prior archived hypotheses are not independent confirmation. Boosting metrics and all failures are retained in the machine-readable evaluation.

The learner estimates coefficients for projected box statistics; it does not estimate causal player values. Prior per-minute rates feed projected rotations with minutes conserved. Missing player statistics withhold the multi-stat projection instead of becoming zero. Current injury scenarios use the same summary definitions and enumerate listed uncertain players without fabricated weights.

Steals, blocks and rebounds do not capture all defense. Historical rosters and availability are inferred/unknown. Current source timestamps do not establish historical pregame publication. No ROI or source-use approval is established.

Detailed artifact: observations/nba_player_box/a826d95c62c2b347832cfd974d1a317c2f4b2dda64a2a367be28cf08ed578064/evaluation.json. Trained artifacts remain separate and disabled for public picks.
