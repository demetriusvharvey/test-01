# Weekly model challenger registry

Run 2026-10-28T12:52:20.604780+00:00: 180 forecast snapshots, 0 outcome records, 0 matched rows before eligibility.

| League | Status | Eligible training games | Validation season | Promoted |
| --- | --- | ---: | --- | --- |
| NBA | insufficient data | 0 | — | no |
| NFL | insufficient data | 0 | — | no |

The pure elastic-net challenger uses only rating difference, home advantage and games-played difference; it does not take odds, a market anchor, spreads or totals as features. Inner validation uses a later prior season; the artifact is refit only on data settled before this run, then may produce separately logged future shadow forecasts. It is never automatically promoted by training alone.

The default training gate requires at least 500 earlier training games, 100 validation games and three seasons with eligible point-in-time data. Eligibility and missingness can make the useful sample much smaller than raw snapshot counts. NBA inputs are blocked pending rights review. No model-vs-sharp or profit result is assumed.
