# NBA efficiency model comparison

Fixed-config sklearn logistic and histogram gradient boosting, trained before a distinct calibration season and evaluated in later seasons. No random game splits or test-driven promotion. Archive already inspected; not an untouched holdout. Player/injury inputs unavailable; no market baseline or wagering-source qualification. Research only.

| Season | Test games | Logistic Brier | Boosting Brier | Elo Brier | Logistic accuracy | Boosting accuracy |
|---|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1225 | 0.2104 | 0.2237 | 0.2139 | 0.6727 | 0.6424 |
| 2025-26 | 1225 | 0.2077 | 0.2126 | 0.2092 | 0.6824 | 0.6645 |
| 2026-27 | 68 | 0.2187 | 0.2156 | 0.2122 | 0.6176 | 0.6471 |

Input hash: 5d8604cba23a0abee360be6747cb4bbe198e1c5c2bcd25b76e46b4ff1da2d949. Detailed results: data branch observations/nba_statistical/5d8604cba23a0abee360be6747cb4bbe198e1c5c2bcd25b76e46b4ff1da2d949/boosting_evaluation.json.

Features include earlier Elo, scoring, rest and home court plus earlier offensive/defensive efficiency, effective FG%, estimated possessions, turnover/rebounding proxies, FT rate and 3P%. Rebounding is a per-possession proxy, not rebound-chance percentage. No player-adjusted rating is implied.
