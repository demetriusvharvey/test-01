# NBA multi-stat player rotation comparison

Run: 2026-11-10T18:13:54.235923+00:00. Hypothesis H023.
Parsed played-player rows: 143887. Identical matched modeling games: 4835.
Separate older training, prior-season calibration and later-season testing. Archive previously inspected; exploratory only. All metrics use identical games. No public pick is changed.

| Season | Games | Team Brier | Rotation Brier | Multi-stat Brier | Elo Brier | Multi-stat accuracy | Log loss delta vs rotation | Raw p | BH p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1209 | 0.21020 | 0.20951 | 0.21045 | 0.21389 | 0.66501 | 0.00231 | 0.40586 | 0.99660 |
| 2025-26 | 1209 | 0.20638 | 0.20475 | 0.20485 | 0.20848 | 0.68817 | -0.00010 | 0.94511 | 0.99660 |
| 2026-27 | 129 | 0.20817 | 0.21196 | 0.21234 | 0.20599 | 0.60465 | -0.00002 | 0.99660 | 0.99660 |

A negative log-loss delta favors the candidate. BH adjustment covers every season reported for H023; prior archived hypotheses are not independent confirmation. Boosting metrics and all failures are retained in the machine-readable evaluation.

The learner estimates coefficients for projected box statistics; it does not estimate causal player values. Prior per-minute rates feed projected rotations with minutes conserved. Missing player statistics withhold the multi-stat projection instead of becoming zero. Current injury scenarios use the same summary definitions and enumerate listed uncertain players without fabricated weights.

Steals, blocks and rebounds do not capture all defense. Historical rosters and availability are inferred/unknown. Current source timestamps do not establish historical pregame publication. No ROI or source-use approval is established.

Detailed artifact: observations/nba_player_box/2b153e132977ec9ecb4191069339944d915404a2d12425615784ecef73dcec60/evaluation.json. Trained artifacts remain separate and disabled for public picks.
