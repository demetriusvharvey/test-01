# Weekly model challenger registry

Run 2026-10-29T18:54:16.110612+00:00: 2869 forecast snapshots, 12 outcome records, 573 matched rows before eligibility.
Availability: 81 team-status and 0 NFL position-status matched snapshots before time and source eligibility checks.

| League | Model | Status | Eligible training games | Validation season | Promoted |
| --- | --- | --- | ---: | --- | --- |
| NBA | pure-elasticnet-v1 | insufficient data | 0 | — | no |
| NBA | pure-stumpboost-v1 | insufficient data | 0 | — | no |
| NBA | availability-logistic-v1 | insufficient data | 0 | — | no |
| NBA | nfl-position-status-logistic-v1 | insufficient data | 0 | — | no |
| NFL | pure-elasticnet-v1 | insufficient data | 0 | — | no |
| NFL | pure-stumpboost-v1 | insufficient data | 0 | — | no |
| NFL | availability-logistic-v1 | insufficient data | 0 | — | no |
| NFL | nfl-position-status-logistic-v1 | insufficient data | 0 | — | no |

Both pure challengers use rating difference, home advantage and games-played difference, without odds, an anchor, spreads or totals. The fixed-grid monotonic boosted-stump model is a standard-library research implementation, not XGBoost, LightGBM, CatBoost or Optuna. Inner validation uses a later prior season; the artifact is refit only on data settled before this run, then may produce separately logged future shadow forecasts. It is never automatically promoted by training alone.

The availability challengers have 81 team-count and 0 NFL position-group snapshots before time and rights screening. They learn from frozen pregame listed statuses on top of Elo; neither has individual player value, is a complete lineup model, or changes picks.

The default training gate requires at least 500 earlier training games, 100 validation games and three seasons with eligible point-in-time data. Eligibility and missingness can make the useful sample much smaller than raw snapshot counts. NBA inputs are blocked pending rights review. No model-vs-sharp or profit result is assumed.
