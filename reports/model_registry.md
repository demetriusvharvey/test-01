# Weekly model challenger registry

Run 2026-10-28T23:43:39.936975+00:00: 951 forecast snapshots, 0 outcome records, 0 matched rows before eligibility.
Availability: 0 matched snapshots before time and source eligibility checks.

| League | Model | Status | Eligible training games | Validation season | Promoted |
| --- | --- | --- | ---: | --- | --- |
| NBA | pure-elasticnet-v1 | insufficient data | 0 | — | no |
| NBA | pure-stumpboost-v1 | insufficient data | 0 | — | no |
| NBA | availability-logistic-v1 | insufficient data | 0 | — | no |
| NFL | pure-elasticnet-v1 | insufficient data | 0 | — | no |
| NFL | pure-stumpboost-v1 | insufficient data | 0 | — | no |
| NFL | availability-logistic-v1 | insufficient data | 0 | — | no |

Both pure challengers use rating difference, home advantage and games-played difference, without odds, an anchor, spreads or totals. The fixed-grid monotonic boosted-stump model is a standard-library research implementation, not XGBoost, LightGBM, CatBoost or Optuna. Inner validation uses a later prior season; the artifact is refit only on data settled before this run, then may produce separately logged future shadow forecasts. It is never automatically promoted by training alone.

The availability challenger has 0 matched snapshots before time and rights screening. It learns only from recorded team-status counts on top of a frozen team forecast; it has no individual player value, is not a complete lineup model, and does not change picks.

The default training gate requires at least 500 earlier training games, 100 validation games and three seasons with eligible point-in-time data. Eligibility and missingness can make the useful sample much smaller than raw snapshot counts. NBA inputs are blocked pending rights review. No model-vs-sharp or profit result is assumed.
