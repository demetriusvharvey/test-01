# NBA season-frozen lineup values in outcome prediction

Run: 2026-11-04T18:47:01.535319+00:00. H027.
Matched game features: 6. Counts: {"2023-24": 5, "2025-26": 1}.
Player ratings use strictly earlier seasons; actual same-game participation never becomes a pregame feature. No sample thresholds are lowered to force training. Low-support/unseen projected players withhold this model.

| Season | Status | Games | 27-feature Brier | 28-feature Brier | Elo Brier | Joint BH p |
|---|---|---:|---:|---:|---:|---:|
| 2024-25 | insufficient_matched_training_calibration_or_test | — | — | — | — | — |
| 2025-26 | insufficient_matched_training_calibration_or_test | — | — | — | — | — |
| 2026-27 | insufficient_matched_training_calibration_or_test | — | — | — | — | — |

The archive was previously inspected; this is exploratory development, not independent confirmation. Full-game lineup coverage is selective and excludes ambiguous/overtime games. The 2021-22 warm-up source is imported only if available. Missing effects remain missing; no zero replacement value or probability is fabricated. Retrospective source retrieval does not establish historical injury/lineup publication times.

Detailed data and any candidate artifact: observations/nba_stint_features/0745eeb4599c455f2ddb8448a8d9c7e990b7726926ae3d024928e5432e09b119/evaluation.json. No public model promotion.
