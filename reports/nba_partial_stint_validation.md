# NBA season-frozen lineup values in outcome prediction

Run: 2026-11-25T20:35:57.020835+00:00. H028.
Matched game features: 4947. Counts: {"2022-23": 1073, "2023-24": 1215, "2024-25": 1209, "2025-26": 1209, "2026-27": 241}.
Player ratings use strictly earlier seasons; actual same-game participation never becomes a pregame feature. No sample thresholds are lowered to force training. The measured supported subset and two coverage indicators supplement the existing features; unknown individual effects remain unavailable. This partial component is not total lineup value.

| Season | Status | Games | 27-feature Brier | 30-feature Brier | Elo Brier | Joint BH p |
|---|---|---:|---:|---:|---:|---:|
| 2024-25 | evaluated | 1209 | 0.21045 | 0.21065 | 0.21389 | 0.94511 |
| 2025-26 | evaluated | 1209 | 0.20485 | 0.20598 | 0.20848 | 0.68233 |
| 2026-27 | evaluated | 241 | 0.21753 | 0.21658 | 0.21293 | 0.93159 |

The archive was previously inspected; this is exploratory development, not independent confirmation. Full-game lineup coverage is selective and excludes ambiguous/overtime games. The 2021-22 warm-up source is imported only if available. Missing effects remain missing; no zero replacement value or probability is fabricated. Retrospective source retrieval does not establish historical injury/lineup publication times.

Detailed data and any candidate artifact: observations/nba_partial_stint_features/cf1ba45e43781ee2802152a66848f88e98ac927ff36bc3a09a42045e22af6b8a/evaluation.json. No public model promotion.
