# Line Lab — daily moneylines

A deliberately small NBA/NFL picks page: daily experimental moneyline selections, observed prices at six US sportsbooks, and a live-pick accuracy counter. Predictions and scores are informational. No bets are placed.

## How it works

Every hour GitHub Actions downloads NBA historical team-game results from BoxScore Lab (CC BY 4.0; https://boxscorelab.com/downloads/), NFL schedules/results from nflverse (https://github.com/nflverse/nfldata), and bookmaker odds snapshots from AgentBets (https://agentbets.ai/odds/). AgentBets says its underlying odds update hourly, not every minute. Its pages are public and welcome automated clients. ESPN scoreboard data is used as a supplementary source of finalized scores.

The experimental model updates Elo team ratings sequentially from past completed games. It compares a small fixed set of Elo/home/rest configurations using chronological pre-game Brier scores on the latest sufficiently complete season, favoring its baseline unless the alternative improves validation Brier by at least 0.0005. This parameter selection is tuning, not an independent evaluation of the chosen model. It combines that estimate (25%) with the median proportional no-vig market probability (75%). It selects up to three upcoming same-day games where its assumption exceeds a tracked book's break-even probability by at least one percentage point; the blend, threshold, rest coefficients and model are **not validated as profitable**. The model has no injury, quarterback or referee-specific adjustments, and archives the NBA’s official referee assignments in data/referee_history.json for future testing; referee effects are not included in the forecast. Do not interpret its displayed probability as proven truth.

Predictions are saved to `data/predictions.json` before the event, one per event. Inputs and the predicted side remain frozen; only an official completed result grades a prediction. Ties are void; pending/void results do not enter wins divided by wins plus losses. The page uses the running prospective record, not historical or hindsight guesses. Accuracy is not a profit metric. Failed, stale, incomplete or unrecognized inputs suppress new picks rather than inventing lines. Live book prices can differ, and availability depends on jurisdiction.

The static Vercel site reads `dist/board.json` and checks for a newer deployment every minute while open. It **does not obtain minute-level odds**: the current source publishes approximately hourly, and scheduled jobs may be delayed. GitHub Actions commits snapshots; Vercel Git integration is required for those commits to update the public page.

Run locally: `python -m http.server 8000 --directory dist`. Test: `python -m unittest discover -s tests`.
