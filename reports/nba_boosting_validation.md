# NBA efficiency model comparison

Fixed-config sklearn logistic and histogram gradient boosting, trained before a distinct calibration season and evaluated in later seasons. No random game splits or test-driven promotion. Archive already inspected; not an untouched holdout. Player/injury inputs unavailable; no market baseline or wagering-source qualification. Research only.

| Season | Test games | Logistic Brier | Boosting Brier | Elo Brier | Logistic accuracy | Boosting accuracy |
|---|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1225 | 0.2104 | 0.2237 | 0.2139 | 0.6727 | 0.6424 |
| 2025-26 | 1225 | 0.2077 | 0.2126 | 0.2092 | 0.6824 | 0.6645 |
| 2026-27 | 92 | 0.2337 | 0.2261 | 0.2196 | 0.5870 | 0.6087 |

Input hash: d07cc160ba42e2c2a7908434eb22760f32decaf72f69329b92bcea9072eeccfb. Detailed results: data branch observations/nba_statistical/d07cc160ba42e2c2a7908434eb22760f32decaf72f69329b92bcea9072eeccfb/boosting_evaluation.json.

Features include earlier Elo, scoring, rest and home court plus earlier offensive/defensive efficiency, effective FG%, estimated possessions, turnover/rebounding proxies, FT rate and 3P%. Rebounding is a per-possession proxy, not rebound-chance percentage. No player-adjusted rating is implied.
