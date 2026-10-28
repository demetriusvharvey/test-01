# Line Lab

A research desk for NBA and NFL single-game moneylines: attributed snapshots, injury and schedule notes, NBA referee assignments, and a browser-based odds calculator. No bets are placed. The current site is a dated research snapshot and does not have a trained Line Lab prediction model.

## Start locally

Serve the `dist/` folder with any static web server, for example `python -m http.server 8000 --directory dist` and open `http://localhost:8000`. No build or browser dependencies are needed.

## Automation: what is and is not connected

- The user's existing ChatGPT morning brief runs separately and includes referee and schedule research. Its results do **not** update this website automatically.
- `.github/workflows/refresh-feed.yml` is a GitHub Actions workflow scheduled at 14:17 and 22:17 UTC daily and available with manual dispatch. GitHub schedules can be delayed, repository Actions permissions may prevent execution, and the first run must be checked.
- `scripts/refresh_feed.py` attempts to collect the NBA's official game-day referee table and, optionally, NBA/NFL FanDuel H2H prices via The Odds API. Add `ODDS_API_KEY` as a **GitHub Actions secret** to enable odds. The key is never written to feed output. A missing key or fetch error is recorded rather than misrepresented as a live price. API access, quota and coverage depend on the provider.
- The workflow writes `dist/feed.json` in this repository. The hosted ChatGPT Site and its dated `dist/data.js` board are **not** linked to this file: they will not update when the workflow runs. A verified data writer or a deployment/synchronization integration is needed before unattended Site updates can be claimed. A successfully saved workflow does not prove that it has run.
- GitHub-hosted automation output is a snapshot, not a guarantee of a currently available price. Compare with the sportsbook and include source and time.

## Research and validation

Read `RESEARCH.md`. All public model probabilities in the board are independently attributed, may have shared inputs or stale injury data, and are not proven edges. Referee and rest observations remain context only. There is no trained model, historical archive, validated strategy, backtest, ROI, or confidence interval in this project. NFL ties can affect moneyline settlement and the simple two-outcome calculator.

Run the feed tests with `python -m unittest discover -s tests`. The page calculator is client-side; it has no access to or control over a betting account.
