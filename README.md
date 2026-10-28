# Daily moneyline picks

An experimental NBA/NFL single-game moneyline board with sportsbook prices, a prospective pick record, a historical archive and documented research factors. Predictions are informational; the site never places bets. The model is **not validated as profitable**.

The baseline blends sequential team Elo with a retail-market consensus. Prior rest and recent scoring-margin experiments are disabled until the preregistered, multi-season protocol in [HYPOTHESES.md](HYPOTHESES.md) is satisfied. Their earlier two-season team-only tests do not establish a betting edge. Referees, injuries, lineups, quarterbacks and travel are not direct model inputs. Visitor ideas are stored only in that browser and are not automatically used by the model.

## Data and architecture

The standard-library Python program is `scripts/pipeline.py`, a compatibility entry point to `scripts/line_lab/` modules for ingestion, features, modeling, market checks, immutable ledger, observations and board generation. GitHub Actions updates approximately hourly; the static Vercel page checks for a newer snapshot each minute, but the underlying AgentBets source itself updates about hourly. Runs may be delayed, and stale, incomplete, conflicting or unverified prices suppress affected picks.

`data/observations` is a separate Git branch containing date-partitioned append-only SQLite quote observations and clearly labeled last-observed pregame price proxies. The recorded proxy is not necessarily the true closing line or a sharp close. The branch also stores attributed retrospective source files in season/dataset SQLite shards. Run the separate GitHub Actions backfill workflow, or set `PICKS_DATA_ROOT` to a research-data checkout and run `python scripts/backfill.py`. Historical backfill is **retrospective**, not a record of what was known at prediction time.

The optional second odds adapter reads `ODDS_API_KEY` from GitHub Actions secrets or the environment; if missing, no second-source fallback is available. Requests are limited to protect a free-tier quota. AgentBets reports that its underlying data come from The Odds API, so the two feeds cannot be treated as independent confirmation.

Sources, attribution, rights and risks are in [DATA_SOURCES.md](DATA_SOURCES.md); the verified baseline and limitations are in [AUDIT.md](AUDIT.md), the plan is in [PLAN.md](PLAN.md), and Phase 1 details are in [reports/phase1.md](reports/phase1.md). In particular, the upstream NBA data terms and gambling-use rights need review before adding direct NBA statistical backfills. No historical NBA close or publication timestamp is fabricated.

Predictions in `data/predictions.json` are frozen before the event. Only a final score grades a pick; ties are void and pending/void picks do not enter win rate. Starting prices are retained for picked games and labeled historical. Accuracy is not a profit metric; availability and actual sportsbook prices may differ.

Test: `python -m unittest discover -s tests`. Static preview: `python -m http.server 8000 --directory dist`.
