# NBA efficiency model comparison

Fixed-config sklearn logistic and histogram gradient boosting, trained before a distinct calibration season and evaluated in later seasons. No random game splits or test-driven promotion. Archive already inspected; not an untouched holdout. Player/injury inputs unavailable; no market baseline or wagering-source qualification. Research only.

| Season | Test games | Logistic Brier | Boosting Brier | Elo Brier | Logistic accuracy | Boosting accuracy |
|---|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1225 | 0.2104 | 0.2237 | 0.2139 | 0.6727 | 0.6424 |
| 2025-26 | 1225 | 0.2077 | 0.2126 | 0.2092 | 0.6824 | 0.6645 |
| 2026-27 | 52 | 0.2186 | 0.2226 | 0.2110 | 0.6154 | 0.6346 |

Input hash: f3546dd1ba1a08212f32e1c896c4c8c1f0de0851da060f8a42c0086bf4331d3f. Detailed results: data branch observations/nba_statistical/f3546dd1ba1a08212f32e1c896c4c8c1f0de0851da060f8a42c0086bf4331d3f/boosting_evaluation.json.

Features include earlier Elo, scoring, rest and home court plus earlier offensive/defensive efficiency, effective FG%, estimated possessions, turnover/rebounding proxies, FT rate and 3P%. Rebounding is a per-possession proxy, not rebound-chance percentage. No player-adjusted rating is implied.
