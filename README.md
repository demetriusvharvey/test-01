# Daily moneyline picks

An NBA/NFL single-game moneyline board with sportsbook prices, a pick record, a historical archive and documented research factors. Predictions are informational; the site never places bets. The model is **not validated as profitable**.

The current research engine predicts from team Elo and completed game results independently of odds. It examines the model's preferred side of each priced game and compares the price, but **does not release new recommendations** because those estimates are not calibrated or validated against a matched-time market benchmark. Previous selections remain frozen and visible. No verified sharp source, sharp CLV, completed head-to-head validation or actual user returns are available. See [reports/model_vs_market.md](reports/model_vs_market.md).

Prior rest and scoring-margin experiments remain disabled until the preregistered protocol in [HYPOTHESES.md](HYPOTHESES.md) is satisfied. Referees, injuries, lineups, quarterbacks and travel are not direct model inputs. Visitor ideas are stored only in that browser and are not automatically used by the model.

An availability challenger records timestamped status-count differences before
forecasts, trains only on eligible earlier outcomes, and is evaluated against
the simultaneously frozen team baseline. It does not change live picks and
does not estimate individual player impact. NBA collection requires the free
provider setup in [docs/NBA_AVAILABILITY.md](docs/NBA_AVAILABILITY.md); NBA
model training additionally remains blocked while upstream rights are reviewed.
Empty, conflicting, stale or future reports never mean a healthy team.
Current source reports are also grouped by all reported NBA/NFL positions,
including NFL offense, defense and special teams, and stored as aggregate
pregame research snapshots. Missing positions remain unknown. The position
snapshots do not affect live predictions and have not been validated.

A seeded score-bootstrap simulator produces 10,000 paired home/away score
draws for each priced game with sufficient earlier team scores. It is a
**score-level challenger only**: it does not simulate possessions, drives,
turnovers, player rotations or weather and is not an injury-impact engine.
Its results are archived with timestamped research forecasts and shown as
score context in the upcoming-game slate; they never change picks. Run
`python -m scripts.research_simulator --data-root .data-store --output reports/simulation_validation.md`
to compare it chronologically with Elo using archived source assets.

The game slate includes verified schedule events for the next eight days,
including unpriced games. The manual FanDuel calculator timestamps a game,
team, entered American odds and stake in that browser's local storage, then
calculates break-even and payout. It does not verify the price, share the
entry across devices, assess a validated edge, or place a wager.

New recommendations are withheld while Elo remains uncalibrated and its
apparent price advantage lacks matched-time market validation. Previously
saved selections and their grading remain visible under "Saved earlier" on
the current day or in the date archive. Research candidates are
still logged; releasing a new selection requires explicit forward-validation
and qualified-market evidence.

That same optional key enables the provider's NBA/NFL schedules, scores and injury
context without any additional account. A daily request cap protects the free
tier; current odds still come from hourly AgentBets snapshots.

The preregistered validation bar requires at least 300 settled prospective paper picks in the relevant segment, positive sharp closing-line value with a confidence interval excluding zero, and calibration no worse than a matched-time market benchmark. The stricter model-first protocol also requires adjusted head-to-head evidence, a nonnegative lower paper-ROI interval, two independent season replications and a later untouched holdout. An hourly retail quote is not a verified sharp close. Until these requirements are met, the model is not validated as profitable; no system action places a bet.

## Data and architecture

The standard-library Python program is `scripts/pipeline.py`, a compatibility entry point to `scripts/line_lab/` components. GitHub Actions updates approximately hourly; the static Vercel page checks for a newer snapshot each minute, but the underlying AgentBets source itself updates about hourly. Runs may be delayed, and stale, incomplete, conflicting or unverified prices suppress affected picks. To compare books fairly, a game displays only prices within 15 minutes of its most recent available source snapshot; the raw observed quotes are separately retained for research.

`data/observations` is a separate Git branch containing date-partitioned append-only SQLite quote observations, paper forecasts and clearly labeled last-observed pregame price proxies. The proxy is not necessarily the true closing line or a sharp close. The branch also stores attributed retrospective source files in season/dataset SQLite shards. Run the separate GitHub Actions backfill workflow, or set `PICKS_DATA_ROOT` to a research-data checkout and run `python scripts/backfill.py`. Historical backfill is **retrospective**, not a record of what was known at prediction time.

The optional second odds adapter reads `ODDS_API_KEY` from GitHub Actions secrets or the environment; if missing, no second-source fallback is available. Requests are limited to protect a free-tier quota. AgentBets reports that its underlying data come from The Odds API, so the two feeds cannot be treated as independent confirmation.

Sources, attribution, rights and risks are in [DATA_SOURCES.md](DATA_SOURCES.md); the audit is in [AUDIT.md](AUDIT.md), the plan is in [PLAN.md](PLAN.md), and the Phase 1 report is in [reports/phase1.md](reports/phase1.md). NBA upstream data rights need review before adding direct NBA statistical backfills. No historical NBA close or publication timestamp is fabricated.

Predictions in `data/predictions.json` are frozen before the event. A pick is graded only when the scoreboard explicitly reports final status and any available supplemental score agrees; missing or conflicting confirmations remain pending. Ties are void and pending/void picks do not enter win rate. Starting prices are retained for picked games and labeled historical. Accuracy is not a profit metric; availability and actual sportsbook prices may differ.

The pipeline uses Python 3.12 and the standard library; there are no pip dependencies. A one-command local check is `python -m unittest discover -s tests`. Static preview: `python -m http.server 8000 --directory dist`. The browser JavaScript can be checked with `node --check dist/app.js`. GitHub CI runs the checks on pushes and pull requests.

The pipeline snapshots a versioned feature definition and source hashes with each new prediction, and logs selected and skipped paper candidates. The weekly research workflow attempts preregistered tests and an odds-independent challenger, then compares later challenger forecasts with frozen baseline forecasts from the same time; insufficient data and errors are recorded, not treated as successes. Its fitted artifacts and drift-monitoring outputs stay in shadow mode and do not automatically change predictions. See [reports/phase9_model_stack.md](reports/phase9_model_stack.md), [reports/challenger_forward.md](reports/challenger_forward.md), [reports/phase11_validation.md](reports/phase11_validation.md), and [reports/phase14_engineering.md](reports/phase14_engineering.md).

The current acceptance-by-acceptance implementation status, archived season
counts, negative score-simulator result, and remaining data blockers are in
[reports/implementation_status.md](reports/implementation_status.md).
