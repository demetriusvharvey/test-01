# Implementation status — October 28, 2026 ET

This report records what is verified. It does not certify a profitable betting
system or a completed player-impact model.

## Implemented and deployed

- Existing static Vercel design, previous picks, records, accuracy, quotes,
  daily quote and Variables page remain. The page now offers an expandable
  eight-day NBA/NFL slate and a browser-local manual FanDuel quote/payout
  calculator. Unpriced games retain blank prices, with provider-sourced injury
  counts displayed for all reported positions when available. User-entered
  prices are timestamped observations, not independent FanDuel verification.
- The hourly GitHub Actions workflow reads NBA team final-score files, nflverse
  final games, current PropLine schedules/scores/injury context, attributed
  AgentBets book snapshots and optional Odds API data. The new key was observed
  to activate both NBA and NFL injury/score endpoints without exposing it.
  The Odds API remains unconfigured. Schedule gaps and source failures are
  surfaced; the hourly job and its source do not provide minute-level updates.
- Earlier picks remain immutable apart from explicit grading and price proxy
  fields. Explicit final-score status is required to grade. Append-only SQLite
  research files live on the `data/observations` branch; Vercel publishes
  static JSON, not runtime SQLite writes.
- A deterministic score-bootstrap challenger uses historical paired scores,
  point-in-time team scoring rates and 10,000 draws per eligible live matchup.
  Its score projections and limitations are saved with timestamped forecasts;
  5,000 draws per game were used for a chronological retrospective evaluation.
  It does **not** model player impact, lineups, possessions, NFL drives or
  turnovers. It does not influence picks.
- Arithmetic for American/decimal odds, no-vig proportions, break-even, EV,
  profit and payout is tested. The live selection path withholds all **new**
  recommendations while no forward-validated model and qualified independent
  market evidence exist; research candidates are still recorded. A high win
  probability alone cannot bypass the release gate.

## Archive and model results

Five NBA team-game files are archived: 2022-23 (1,230), 2023-24 (1,230),
2024-25 (1,225), 2025-26 (1,225), and a partial 2026-27 (52). The archived
nflverse schedule file parsed 4,470 historical NFL final games at the test
checkpoint. Additional NFL play-by-play, injuries, snap counts and depth
charts were archived separately but are **not** proven point-in-time model
features. The source list and hashes are in `reports/simulation_validation.md`.

| League | Later retrospective games | Score challenger accuracy / Brier / log loss | Same-game Elo accuracy / Brier / log loss |
|---|---:|---|---|
| NBA | 1,277 | 59.20% / 0.2369 / 0.6670 | 67.35% / 0.2093 / 0.6069 |
| NFL | 675 | 59.41% / 0.2380 / 0.6697 | 64.74% / 0.2231 / 0.6368 |

The score challenger lost to Elo in both tests, so it stays disabled for
selection. These seasons have been inspected previously and are not an
untouched holdout. The 50% uninformative home forecast had Brier 0.2500 on
both samples. No historical NBA odds with verified pregame book/timestamp,
independent sharp close, or matched-time market baseline is established.
Nflverse schedule odds fields lack certified book and publication time, so
historical betting ROI, CLV and true EV validation are **unavailable**. No
actual placed wagers are recorded.

## Verification and remaining blockers

Local Python unit and fixture suite: **136 passing**; browser-script syntax
check and Python compilation pass. GitHub CI, weekly research evaluation,
hourly data update and Vercel deployment are checked separately after commits.
The frontend has no npm package, type checker, or lint configuration; the
production artifact is the existing static `dist/` directory.

The master prompt is **not fully complete**. Verified rights-compatible
historical NBA injuries/lineups/player usage, historical NFL position-group
contributions at forecast time, quantified replacement-player effects,
questionable-player scenario probabilities, calibrated machine learning and
ensemble weights, validated possession/drive simulations, historical
timestamped executable odds and a qualified independent market benchmark are
missing. Some requested models exist only as guarded research challengers.
No forward sample, untouched later seasons, certified sharp close or return
confidence interval can be created by running more code today. A model cannot
be safely promoted on the present evidence.

## Winner-only mode and slate UI — October 28, 2026

The daily public board now ranks and freezes up to three team-Elo winner
forecasts per ET game date without sportsbook odds or value thresholds. It can
select a positive-moneyline team when its Elo estimate favors that team; a
fixture verifies a +210 selection. All scheduled games with available ratings
show a predicted winner in a compact, filtered upcoming slate. The slate opens
to today's games, with NBA/NFL filters, six rows per page and a bounded scroll
area. Each row expands to show odds and available injury context. Prices never
change the winner forecast. The new accuracy counter counts this winner-only
record; old research selections are kept separately.

The full master prompt remains **incomplete**. Injury reports and all-position
status counts can be displayed, but player-level replacement impact and
conditional questionable-player availability are not inputs to the Elo
forecast. NBA upstream data rights, verified pregame historical availability,
calibrated machine learning, an outperforming simulation/ensemble and a
market-matched untouched test remain unresolved. The independent NBA scoring
unit and NFL drive challenger was implemented, tested and found inferior to
Elo on the exploratory matched samples. Neither the top-three rank nor a
positive sportsbook moneyline establishes a validated edge or reliable win.

## Top-three audit and injury timing — October 28, 2026

The weekly research workflow completed a chronological day-start replay of
the fixed top-three Elo selection rule on 2024–2026 archived results. It
selected 1,388 games on 494 dates, with 1,038 correct (74.78%), Brier 0.1777
and log loss 0.5360. The day-block bootstrap accuracy interval was
72.51%–76.94%; NBA was 75.58% on 1,208 and NFL was 69.44% on 180. These
archives were acquired after the games and the rule has no injury input or
matched-time market benchmark. The replay is separate from the forward site
record; see `reports/winner_accuracy_replay.md` for source hashes and bins.

Active cards now flag an injury report observed after their frozen forecast.
This makes the timing gap visible; it does not imply the injury status changed
or that the model quantified player impacts. No forecast history is rewritten.
Local suite: 147 passing; browser script syntax check passed. The status
of the new GitHub CI and deployment is verified after the corresponding commit.

## Position-aware research path — October 28, 2026

An NFL-only position-status challenger now records all nine position groups
and three game designations from captured nflverse reports before kickoff. A
chronological, regularized logistic adjustment can train when enough eligible
frozen reports and confirmed later outcomes exist, then record same-time
shadow forecasts against Elo for paired forward evaluation. Its tests are
synthetic integrity checks, not evidence that injury adjustment improves
prediction. It is not used by the public winner picks. See
`reports/position_status_challenger.md`. The full player-impact, NBA injury,
simulation, market validation and untouched-forward requirements remain open.
