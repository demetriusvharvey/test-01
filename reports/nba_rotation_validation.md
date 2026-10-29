# NBA player rotation research

Free SportsDataverse player box imports. Projections use only earlier appearances; membership is inferred, not a verified pregame roster. Historical injuries, trades before first appearance and confirmed lineups remain unknown. No public pick is changed.

Parsed player rows: 114003. Rotation-covered games: 4883. Matched modeling examples: 4742. Source failures: 0.
Current roster snapshot: 519 source rows; 30 teams; 498 current IDs matched to historical box scores. Injury crosswalk unverified.

| Season | Games | Baseline logistic Brier | Rotation logistic Brier | Rotation accuracy |
|---|---:|---:|---:|---:|
| 2024-25 | 1209 | 0.2102 | 0.2102 | 0.6708 |
| 2025-26 | 1209 | 0.2064 | 0.2050 | 0.6948 |
| 2026-27 | 36 | 0.2173 | 0.2206 | 0.5833 |

This is a chronological exploratory comparison on already inspected archives, not independent validation or proof of player impact. Scoring/minute proxies do not measure defense or replacement effects. Source rights remain qualified, not automatically approved by a repository license.

Source manifest, hashes, column schemas and full results: data branch observations/nba_rotation/evaluation.json.
