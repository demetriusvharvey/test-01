# NBA season-frozen lineup values in outcome prediction

Run: 2026-10-29T20:53:48.091186+00:00. H027.
Matched game features: 6. Counts: {"2023-24": 5, "2025-26": 1}.
Player ratings use strictly earlier seasons; actual same-game participation never becomes a pregame feature. No sample thresholds are lowered to force training. Low-support/unseen projected players withhold this model.

| Season | Status | Games | 27-feature Brier | 28-feature Brier | Elo Brier | Joint BH p |
|---|---|---:|---:|---:|---:|---:|
| 2024-25 | insufficient_matched_training_calibration_or_test | — | — | — | — | — |
| 2025-26 | insufficient_matched_training_calibration_or_test | — | — | — | — | — |
| 2026-27 | insufficient_matched_training_calibration_or_test | — | — | — | — | — |

The archive was previously inspected; this is exploratory development, not independent confirmation. Full-game lineup coverage is selective and excludes ambiguous/overtime games. The 2021-22 warm-up source is imported only if available. Missing effects remain missing; no zero replacement value or probability is fabricated. Retrospective source retrieval does not establish historical injury/lineup publication times.

Detailed data and any candidate artifact: observations/nba_stint_features/7e7cd7605508ac1de3bc11c96045827cf52598a86487fc9552cf93db6a1b31a7/evaluation.json. No public model promotion.
