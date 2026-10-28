# Daily moneyline picks

An experimental NBA/NFL single-game moneyline board with odds from six US sportsbooks, a prospective pick record, a historical archive and a description of the factors being tested. Predictions are informational; the site does not place bets.

## Data and updates

GitHub Actions runs approximately hourly. It collects NBA team-game results from BoxScore Lab (CC BY 4.0; https://boxscorelab.com/downloads/), NFL results and schedules from nflverse (https://github.com/nflverse/nfldata), bookmaker odds from AgentBets (https://agentbets.ai/odds/), and supplementary completed scores from ESPN. AgentBets snapshots update about hourly, not every minute. The browser checks for a newer deployment each minute; this does not make the underlying feed update each minute. A stale or unavailable feed suppresses current prices and new predictions.

## Model and evaluation

Team Elo ratings update sequentially from completed games; an NBA/NFL home adjustment is included, except at known NFL neutral sites. The model blends its team estimate with the median proportional no-vig market probability (one part team estimate, three parts market). Up to three same-day selections are frozen before game time when the best tracked price exceeds the model's assumed break-even price by at least one percentage point. At least three books are required. This experimental blend and threshold are not validated as profitable.

Rest-day difference and a rolling five-game scoring-margin difference are the currently supported feature candidates. On each run the system selects a candidate on an earlier season, then promotes it only if it improves sequential Brier score by at least 0.0005 on both that selection season and a separate later season, each with at least 1,000 NBA or 200 NFL results. The score tests the Elo component alone: historical point-in-time market prices are not available for a complete test of the blend. Tuning, repeatedly reusing historical periods, and passing a holdout do not establish future accuracy, positive expected value, or profits. The model updates when new results arrive, but does not invent or evaluate arbitrary features from a single win or loss.

The site labels rest and form as in use or being tested for each league. NBA referee crews are archived in `data/referee_history.json`; referee effects, injuries, quarterbacks, travel, time zones and lineups are not directly incorporated. The market can reflect some of this information. Visitors can save variable ideas locally in their browser; these notes are not transmitted or automatically fed into the model.

## Record and historical odds

Predictions live in `data/predictions.json`, frozen before their event, one per matchup. Only an official completed result grades a pick. Ties are void; pending and void picks are excluded from the win-rate denominator. A pick archive contains only prospective predictions, not hindsight forecasts or a user's actual wagers. Starting prices at each book are stored for new picks. For the original legacy selection, `data/legacy_pick_quotes.json` preserves quotes from its exact timestamped earlier board snapshot; the migration checks the pick ID, prediction timestamp and best price before attaching them. Historical prices are clearly labeled and may no longer be available. Accuracy is not a profit metric.

Vercel's Git integration publishes committed `dist/` snapshots. Run locally: `python -m http.server 8000 --directory dist`. Test: `python -m unittest discover -s tests`.
