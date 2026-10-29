# NBA statistical baseline evaluation

Real archived scores; all features use earlier game dates. Logistic trains on earlier seasons, Platt calibration uses a separate later season, and testing uses the next season. These archives were inspected previously: chronological, not untouched. No injury input, source permission or betting edge is implied. Research only.

| Test season | Training | Calibration | Test games | Calibrated accuracy | Calibrated Brier | Elo Brier | Calibrated log loss | Elo log loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-25 | 1073 | 1230 | 1225 | 0.5780 | 0.2392 | 0.2139 | 0.6713 | 0.6154 |
| 2025-26 | 2303 | 1225 | 1225 | 0.6237 | 0.2324 | 0.2092 | 0.6575 | 0.6069 |
| 2026-27 | 3528 | 1225 | 52 | 0.6154 | 0.2359 | 0.2110 | 0.6644 | 0.6072 |

Input SHA-256: 7b16fc7a23fd26bdada043325a070b21566e58ff6b8ad4b1f0a5a4c4bf7791ad. Detailed metrics, reliability bins and artifacts are on the data branch under observations/nba_statistical/7b16fc7a23fd26bdada043325a070b21566e58ff6b8ad4b1f0a5a4c4bf7791ad/evaluation.json.

This evaluates the score-based NBA logistic baseline, not full player-aware Phase 2. Player/lineup inputs, gradient boosting, source-use qualification and independent future confirmation remain open. No production promotion occurs.
