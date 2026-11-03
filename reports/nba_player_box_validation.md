# NBA multi-stat player rotation comparison

Run: 2026-11-03T18:02:19.154641+00:00. Hypothesis H023.
Parsed played-player rows: 142823. Identical matched modeling games: 4782.
Separate older training, prior-season calibration and later-season testing. Archive previously inspected; exploratory only. All metrics use identical games. No public pick is changed.

| Season | Games | Team Brier | Rotation Brier | Multi-stat Brier | Elo Brier | Multi-stat accuracy | Log loss delta vs rotation | Raw p | BH p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1209 | 0.21020 | 0.20951 | 0.21045 | 0.21389 | 0.66501 | 0.00231 | 0.40586 | 0.60879 |
| 2025-26 | 1209 | 0.20638 | 0.20475 | 0.20485 | 0.20848 | 0.68817 | -0.00010 | 0.94511 | 0.94511 |
| 2026-27 | 76 | 0.23682 | 0.24137 | 0.23863 | 0.22263 | 0.53947 | -0.00866 | 0.23588 | 0.60879 |

A negative log-loss delta favors the candidate. BH adjustment covers every season reported for H023; prior archived hypotheses are not independent confirmation. Boosting metrics and all failures are retained in the machine-readable evaluation.

The learner estimates coefficients for projected box statistics; it does not estimate causal player values. Prior per-minute rates feed projected rotations with minutes conserved. Missing player statistics withhold the multi-stat projection instead of becoming zero. Current injury scenarios use the same summary definitions and enumerate listed uncertain players without fabricated weights.

Steals, blocks and rebounds do not capture all defense. Historical rosters and availability are inferred/unknown. Current source timestamps do not establish historical pregame publication. No ROI or source-use approval is established.

Detailed artifact: observations/nba_player_box/32541312672f0c60e1a22a5b15eb3c659a405fc6c1915fcd58cf883a0224a1d9/evaluation.json. Trained artifacts remain separate and disabled for public picks.
