# NBA season-frozen lineup values in outcome prediction

Run: 2026-11-11T18:52:17.688436+00:00. H028.
Matched game features: 4843. Counts: {"2022-23": 1073, "2023-24": 1215, "2024-25": 1209, "2025-26": 1209, "2026-27": 137}.
Player ratings use strictly earlier seasons; actual same-game participation never becomes a pregame feature. No sample thresholds are lowered to force training. The measured supported subset and two coverage indicators supplement the existing features; unknown individual effects remain unavailable. This partial component is not total lineup value.

| Season | Status | Games | 27-feature Brier | 30-feature Brier | Elo Brier | Joint BH p |
|---|---|---:|---:|---:|---:|---:|
| 2024-25 | evaluated | 1209 | 0.21045 | 0.21065 | 0.21389 | 0.99660 |
| 2025-26 | evaluated | 1209 | 0.20485 | 0.20598 | 0.20848 | 0.68233 |
| 2026-27 | evaluated | 137 | 0.21502 | 0.21418 | 0.20547 | 0.99660 |

The archive was previously inspected; this is exploratory development, not independent confirmation. Full-game lineup coverage is selective and excludes ambiguous/overtime games. The 2021-22 warm-up source is imported only if available. Missing effects remain missing; no zero replacement value or probability is fabricated. Retrospective source retrieval does not establish historical injury/lineup publication times.

Detailed data and any candidate artifact: observations/nba_partial_stint_features/c73ef7108645a8d60e58dd938f11f4a5fc3e7770b8c043459bd8f60120724350/evaluation.json. No public model promotion.
