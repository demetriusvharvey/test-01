# NBA chronological statistical ensemble

Run: 2026-10-31T20:11:31.346834+00:00. H024 was registered after inspecting H023.
Weights are learned from earlier held-out component predictions only. All test comparisons use identical games. The previously inspected archive is exploratory, not independent confirmation.

| Season | Games | Ensemble Brier | Elo Brier | Ensemble log loss | Elo log loss | Earlier-selected component | Raw p | Joint BH p |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| 2025-26 | 1209 | 0.20490 | 0.20848 | 0.59642 | 0.60505 | rotation | 0.00590 | 0.01770 |
| 2026-27 | 55 | 0.23080 | 0.22053 | 0.65053 | 0.62783 | rotation | unavailable | unavailable |

## Learned weights

- Test 2025-26: trained on 1209 earlier component forecasts from 2024-25; weights {"elo": 0.0, "multi_stat": 0.3, "rotation": 0.5, "team": 0.2}.
- Test 2026-27: trained on 2418 earlier component forecasts from 2024-25, 2025-26; weights {"elo": 0.0, "multi_stat": 0.3, "rotation": 0.7, "team": 0.0}.

Weights are nonnegative and sum to one. A ten-percentage-point grid is fixed before testing; no test-season outcomes choose the weights. Individual component metrics, matched predictions, failure/null tests and training hashes are retained in the data artifact. BH adjustment includes both related H023 and H024 season-test families.

This is a statistical ensemble, not the full market/simulation ensemble from the master prompt. Market and simulator inputs have not earned inclusion. Current injury scenarios are combined only when required components have matching scenarios and timestamps. A team-only result is explicitly labeled and is not claimed injury-adjusted. No public pick changes.

Artifact: observations/nba_ensemble/52afe312e1788325c3bb9d79f58314d0428761e01fb2f7cfb92afd301a6f582f/evaluation.json.
