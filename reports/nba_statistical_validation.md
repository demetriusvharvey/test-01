# NBA statistical baseline evaluation

Real archived scores; all features use earlier game dates. Logistic trains on earlier seasons, Platt calibration uses a separate later season, and testing uses the next season. These archives were inspected previously: chronological, not untouched. No injury input, source permission or betting edge is implied. Research only.

| Test season | Training | Calibration | Test games | Calibrated accuracy | Calibrated Brier | Elo Brier | Calibrated log loss | Elo log loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1073 | 1230 | 1225 | 0.5780 | 0.2392 | 0.2139 | 0.6713 | 0.6154 |
| 2025-26 | 2303 | 1225 | 1225 | 0.6237 | 0.2324 | 0.2092 | 0.6575 | 0.6069 |
| 2026-27 | 3528 | 1225 | 145 | 0.6138 | 0.2309 | 0.2059 | 0.6541 | 0.5949 |

Input SHA-256: 434516dbd769e77563539192a32d755d8e53050c653017b97fa90c6ff2b50d31. Detailed metrics, reliability bins and artifacts are on the data branch under observations/nba_statistical/434516dbd769e77563539192a32d755d8e53050c653017b97fa90c6ff2b50d31/evaluation.json.

This evaluates the score-based NBA logistic baseline, not full player-aware Phase 2. Player/lineup inputs, gradient boosting, source-use qualification and independent future confirmation remain open. No production promotion occurs.
