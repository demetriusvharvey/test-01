# RotoBot simulator source review — October 28, 2026 ET

The user identified [@rotobot_ai](https://x.com/rotobot_ai) with a screenshot of
a post describing 5,000 NBA simulations of Philadelphia at Indiana **without
Tyrese Haliburton**. The visible image shows an approximately 70%/30% split
and says possessions are built from play-by-play. This is a single scenario
published by RotoBot, not a verified forecast record, a known point-in-time
injury report, or evidence that the team had a 70% true win probability. The
post does not establish what opponent lineups, rotations, pace, market odds
or validation method were used. A game can still be lost by the favored team.

RotoBot's [October 27 terms](https://rotobot.ai/terms-of-service) explicitly
permit automated access only through its official paid-subscription MCP.
They prohibit scraping, redistribution and use of its outputs to train or
benchmark a competing model. Its personal-use MCP allowance does not permit
publishing outputs to our shared picks website. This conflicts with the
user's zero-cost requirement and the site's independent-validation protocol.
No RotoBot outputs, odds or imagery are stored or published by this app.

The useful methodological idea is an independently developed possession
(NBA) or drive (NFL) simulator from properly licensed, pregame-available
play-by-play, roster, injury and team-efficiency sources. That would require
identifying the game's pace/possession process, opponent and position-level
matchups, player availability scenarios, score variance, reproducible seeds,
and an out-of-sample comparison with Elo and the same-time market baseline.
The current score bootstrap is not such a simulator and, on the archived
later-season sample, was less accurate and worse calibrated by Brier than Elo
in both leagues. H020 records the independent research test before any such
implementation; no RotoBot access or proprietary model is implied.
