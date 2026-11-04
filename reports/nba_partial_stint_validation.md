# NBA season-frozen lineup values in outcome prediction

Run: 2026-11-04T18:48:04.398506+00:00. H028.
Matched game features: 4797. Counts: {"2022-23": 1073, "2023-24": 1215, "2024-25": 1209, "2025-26": 1209, "2026-27": 91}.
Player ratings use strictly earlier seasons; actual same-game participation never becomes a pregame feature. No sample thresholds are lowered to force training. The measured supported subset and two coverage indicators supplement the existing features; unknown individual effects remain unavailable. This partial component is not total lineup value.

| Season | Status | Games | 27-feature Brier | 30-feature Brier | Elo Brier | Joint BH p |
|---|---|---:|---:|---:|---:|---:|
| 2024-25 | evaluated | 1209 | 0.21045 | 0.21065 | 0.21389 | 0.94511 |
| 2025-26 | evaluated | 1209 | 0.20485 | 0.20598 | 0.20848 | 0.47175 |
| 2026-27 | evaluated | 91 | 0.23693 | 0.23453 | 0.22309 | 0.67780 |

The archive was previously inspected; this is exploratory development, not independent confirmation. Full-game lineup coverage is selective and excludes ambiguous/overtime games. The 2021-22 warm-up source is imported only if available. Missing effects remain missing; no zero replacement value or probability is fabricated. Retrospective source retrieval does not establish historical injury/lineup publication times.

Detailed data and any candidate artifact: observations/nba_partial_stint_features/7d38d5328f4794a3d5aa97009b64576422d17a992b75de7626539724694a34cd/evaluation.json. No public model promotion.
