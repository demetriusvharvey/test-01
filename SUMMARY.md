# Work summary

## Completed

- Step 0: audited the current system, cataloged data rights and limitations, established a phased plan, and preregistered future hypotheses. No backtest was claimed as validation.
- Phase 1: modularized the existing pipeline, added a separate append-only SQLite data branch, checked source timestamps/duplicates/mismatches, and preserved historical picks. The live update ran successfully and captured 71 timestamped odds observations. The backfill job successfully stored 30 source shards: the full nflverse schedule file, 2021–2026 NFL play-by-play/injuries/depth charts/snap counts, and five NBA team-game seasons. Current seasons are partial and all backfilled assets are marked retrospective.
- Model-first amendment: new paper selections use the team model without market probabilities as inputs. The model and a retail reference are logged prospectively; qualified sharp-market arms remain absent. A conservative guard prevents staking while evidence and point-in-time news checks are unavailable. Timestamped NFL QB efficiency summaries are collected as shadow-only research. The UI separates the old model's picks from new paper selections and provides an inconclusive study scoreboard. Following deployment, the first update recorded 12 prospective NBA forecasts; the NFL shadow job saved 63 quarterback/team summaries. Both jobs completed successfully and 29 tests passed.

## Honest comparison

At the initial model-first deployment checkpoint, there are no qualified matched-time sharp-market observations, certified sharp closing lines, or settled prospective pure-model picks. Therefore sharp-market log loss, sharp CLV, ROI confidence intervals and a model-ahead verdict are **not available**. No positive expected value or profit has been demonstrated. See [reports/model_vs_market.md](reports/model_vs_market.md).

The model is still a simple, uncalibrated Elo baseline. The full 10+ seasons of NBA history, player-level lineup/injury effects, NFL QB/EPA/weather models, ensemble, independent sharp source, fitted challenger, disagreement calibration and validation/staking gate requested by the amendment are not complete. Existing retrospective source rows cannot safely stand in for point-in-time information. Odds are refreshed approximately hourly, not minute-by-minute. No purchases or subscriptions were made.

## Next five priorities

1. Configure an existing free The Odds API key as the GitHub Actions `ODDS_API_KEY` secret for fallback and cross-checks; the key is currently absent. This is not an independent sharp source and its free quota is limited.
2. Establish genuinely licensed, independently sourced sharp pregame/closing prices and 10+ seasons of NBA history with clearly documented rights; do not assume an hourly retail proxy is a sharp close.
3. Capture timestamped injuries, lineups, quarterback status and weather from permitted sources and establish reliable first-observed times before adding them as features.
4. Accumulate prospective matched-time paper forecasts and outcomes; run the preregistered chronological tests, multiple-testing correction and untouched confirmation before approving any model change or stake.
5. Develop and shadow-test calibration, QB/EPA and lineup-based challengers with uncertainty and leakage checks; promote only with the documented evidence.
