# NBA efficiency model comparison

Fixed-config sklearn logistic and histogram gradient boosting, trained before a distinct calibration season and evaluated in later seasons. No random game splits or test-driven promotion. Archive already inspected; not an untouched holdout. Player/injury inputs unavailable; no market baseline or wagering-source qualification. Research only.

| Season | Test games | Logistic Brier | Boosting Brier | Elo Brier | Logistic accuracy | Boosting accuracy |
|---|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1225 | 0.2104 | 0.2237 | 0.2139 | 0.6727 | 0.6424 |
| 2025-26 | 1225 | 0.2077 | 0.2126 | 0.2092 | 0.6824 | 0.6645 |
| 2026-27 | 71 | 0.2235 | 0.2210 | 0.2171 | 0.6197 | 0.6338 |

Input hash: 1ec11cd0fbd0e39ba07b8349dee93a2c00d0162f6d07202e06dd2c7c6a67ed5f. Detailed results: data branch observations/nba_statistical/1ec11cd0fbd0e39ba07b8349dee93a2c00d0162f6d07202e06dd2c7c6a67ed5f/boosting_evaluation.json.

Features include earlier Elo, scoring, rest and home court plus earlier offensive/defensive efficiency, effective FG%, estimated possessions, turnover/rebounding proxies, FT rate and 3P%. Rebounding is a per-possession proxy, not rebound-chance percentage. No player-adjusted rating is implied.
