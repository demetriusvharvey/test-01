# NBA multi-stat player rotation comparison

Run: 2026-10-29T20:16:05.459415+00:00. Hypothesis H023.
Parsed played-player rows: 141945. Identical matched modeling games: 4758.
Separate older training, prior-season calibration and later-season testing. Archive previously inspected; exploratory only. All metrics use identical games. No public pick is changed.

| Season | Games | Team Brier | Rotation Brier | Multi-stat Brier | Elo Brier | Multi-stat accuracy | Log loss delta vs rotation | Raw p | BH p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1209 | 0.21020 | 0.20951 | 0.21045 | 0.21389 | 0.66501 | 0.00231 | 0.40586 | 0.81172 |
| 2025-26 | 1209 | 0.20638 | 0.20475 | 0.20485 | 0.20848 | 0.68817 | -0.00010 | 0.94511 | 0.94511 |
| 2026-27 | 52 | 0.21772 | 0.22605 | 0.22760 | 0.21432 | 0.55769 | -0.00031 | unavailable | unavailable |

A negative log-loss delta favors the candidate. BH adjustment covers every season reported for H023; prior archived hypotheses are not independent confirmation. Boosting metrics and all failures are retained in the machine-readable evaluation.

The learner estimates coefficients for projected box statistics; it does not estimate causal player values. Prior per-minute rates feed projected rotations with minutes conserved. Missing player statistics withhold the multi-stat projection instead of becoming zero. Current injury scenarios use the same summary definitions and enumerate listed uncertain players without fabricated weights.

Steals, blocks and rebounds do not capture all defense. Historical rosters and availability are inferred/unknown. Current source timestamps do not establish historical pregame publication. No ROI or source-use approval is established.

Detailed artifact: observations/nba_player_box/fda18341426b352cf00d2b5222bd9d71f56cf05f7838a3a5517ff5745573a46a/evaluation.json. Trained artifacts remain separate and disabled for public picks.
