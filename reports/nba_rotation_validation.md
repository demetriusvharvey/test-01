# NBA player rotation research

Free SportsDataverse player box imports. Projections use only earlier appearances; membership is inferred, not a verified pregame roster. Historical injuries, trades before first appearance and confirmed lineups remain unknown. No public pick is changed.

Parsed player rows: 143887. Rotation-covered games: 4976. Matched modeling examples: 4835. Source failures: 0.
Current roster snapshot: 522 source rows; 30 teams; 503 current IDs matched to historical box scores. Injury crosswalk unverified.

| Season | Games | Baseline logistic Brier | Rotation logistic Brier | Rotation accuracy |
|---|---:|---:|---:|---:|
| 2024-25 | 1209 | 0.2102 | 0.2095 | 0.6782 |
| 2025-26 | 1209 | 0.2064 | 0.2048 | 0.6840 |
| 2026-27 | 129 | 0.2082 | 0.2120 | 0.6357 |

This is a chronological exploratory comparison on already inspected archives, not independent validation or proof of player impact. Scoring/minute proxies do not measure defense or replacement effects. Source rights remain qualified, not automatically approved by a repository license.

Source manifest, hashes, column schemas and full results: data branch observations/nba_rotation/evaluation.json.
