# Research notes

## Professional techniques we can actually verify

- **William Benter:** In his published horse-racing work, Benter describes combining fundamental forecasts with information from public odds and assessing calibration. Horse racing is not NBA or NFL; we use this as a methodological direction rather than claiming access to his model or reproducing its returns. Source: https://gwern.net/doc/statistics/decision/1994-benter.pdf
- **Gadoon “Spanky” Kyrollos:** In an interview, he describes building tools that monitor sportsbook price discrepancies and line movement. We record source, time, and both sides and avoid assuming a line move has a single cause. This project does not replicate his software. Source: https://www.reviewjournal.com/sports/betting/meet-spanky-who-left-rat-race-to-become-top-pro-sports-bettor-2882980/
- **OddsMatrix article:** It highlights injuries, referee tendencies, scheduling patterns, analytics, line shopping and disciplined bankroll management. It is marketing material for an industry data provider; its celebrity wealth, success and proprietary method claims are not independently verified. Source: https://oddsmatrix.com/top-sports-bettors/
- **Probability quality:** Walsh and Joshi compare calibration-based model selection with accuracy-based selection on NBA data and a single betting season. This is evidence for testing calibration, not a reproducible profitability promise. Source: https://doi.org/10.1016/j.mlwa.2024.100539

## Inputs and cautions

1. Moneyline quotes on both sides, quote timestamps, provider, settlement, market movement and closing prices when verified. Proportional no-vig probabilities provide a market baseline but do not establish truth.
2. Opponent-adjusted team performance and expected lineups; for football, quarterback and participation context. Freeze each feature at the time it could actually be known.
3. Injury designations, likely replacements, rest days, back-to-backs, travel direction/time zone, byes and home advantage. A study of NBA seasons 2014–2018 found a back-to-back performance disadvantage; individual games and already-adjusted market prices can differ. https://pubmed.ncbi.nlm.nih.gov/35980109/
4. NBA game-day referee assignments: https://official.nba.com/referee-assignments/ (typically posted around 9 AM ET). Crews can change. Assignment is a fact; isolated team records or an official's raw home/away record are not a causal adjustment. Referee research in last-two-minute reports shows the importance of context; do not extrapolate a numeric edge to a full game. https://www.nature.com/articles/s41598-023-31799-y
5. NFL schedule, rosters, injuries and play-by-play can be sourced from nflverse, with varying refresh times: https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html
6. The Odds API describes FanDuel H2H and historical snapshots: https://the-odds-api.com/liveapi/guides/v4/. Verify rights, plans, freshness, coverage, state and terms independently.

## Required evaluation before any model claim

Maintain an append-only timestamped source history with point-in-time lineups and odds, game outcomes and grading rules. Fit and calibrate on past games only, use rolling chronological evaluation on later games, and benchmark against a matched-time market-only forecast. Report Brier score, log loss, calibration curves, uncertainty and sample sizes; compare ROI at genuinely available prices after vig and account for pushes/ties, line movement, data gaps and execution costs. Use strict out-of-sample ablation before deciding whether schedule or referee variables contribute beyond the market. Closing-line value is useful evidence about prices but does not alone prove profitability. None of this evaluation has been completed here.
