# Data sources and rights

Checked October 27, 2026 ET. This is operational source documentation, not a legal opinion. A public URL, an MIT code license, or a source's own CC label does not by itself resolve all upstream rights. Keep source IDs, time of observation, provider update times and data versions; never infer that a revised historical row was available before the original event.

| Source | Current use and coverage | Published terms, cadence and limitations | Decision / attribution |
| --- | --- | --- | --- |
| [AgentBets odds pages](https://agentbets.ai/odds/) and [agent odds index](https://agentbets.ai/llms-odds.txt) | Current market input: six US sportsbook pages, NBA/NFL, moneylines. | Provider describes hourly updates and explicitly offers agents free, unauthenticated odds lookups; its [MCP documentation](https://agentbets.ai/mcp/) describes public endpoints. Its [methodology](https://agentbets.ai/odds/betus-vs-bovada/) says odds come from The Odds API, so the two feeds are not independent. A right to bulk archive and republish the full scraped page feed has not been verified. The page timestamp is a page snapshot timestamp, not necessarily each bookmaker's own update time. | Retain current informational display while documenting this risk; do not call the values true live/closing prices. Prefer permitted API results where available. No sportsbook account scraping. |
| [The Odds API v4](https://the-odds-api.com/liveapi/guides/v4/) and [terms](https://the-odds-api.com/terms-and-conditions.html) | An optional adapter checks both leagues with `ODDS_API_KEY` and the legacy `refresh_feed.py` also uses that key. | The provider permits storing, displaying and analyzing data subject to its terms; do not resell raw data as a competing feed. Its [free plan](https://the-odds-api.com/) has 500 monthly credits; 24 hourly calls for both leagues would exceed it. [Caesars and Fanatics](https://the-odds-api.com/sports-odds-data/bookmaker-apis.html) are shown as paid-plan-only. Historical endpoint requires a paid plan. Rate limits and quota headers must be honored. | Use only an existing key with a conservative budget; never commit or log keys. Missing key means the optional second source is unavailable. No account creation or paid plan. |
| [BoxScore Lab downloads](https://boxscorelab.com/downloads/) | Five NBA team-game-result seasons, 2022-23 to current (last partial). | Provider declares its CSVs CC BY 4.0 with dated attribution; refreshed nightly. It states statistics derive from NBA Stats. [NBA.com terms, section 9](https://api-hub.nba.com/termsofuse) restrict NBA Statistics in connection with gambling; whether and how that applies to this downstream dataset is unresolved. Its attribution and upstream rights must not be conflated. | Cite “BoxScore Lab, boxscorelab.com, data through [source build date].” Record this upstream conflict; do not add direct NBA Stats gambling backfills while rights are unverified. |
| [nflverse / nflreadr](https://nflreadr.nflverse.com/), [schedule](https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html) | NFL schedules and scores from nflverse; play-by-play, injuries, depth charts and snap counts are available as separate datasets. | [nflreadpy](https://nflreadpy.nflverse.com/) describes most nflverse data as CC BY 4.0 and FTN data as CC BY-SA 4.0; [nflreadr](https://nflreadr.nflverse.com/) also states underlying data belong to their respective owners and terms apply. Availability and updates differ by dataset. Game/schedule rows may change retroactively. | Attribute nflverse and upstream provider where specified, preserve dataset-specific provenance, hashes and observed time. No claim that historical injury/depth revisions were available pregame without a timestamped source. |
| [NBA referee assignments](https://official.nba.com/referee-assignments/) and [NBA injury reports](https://official.nba.com/nba-injury-report-2026-27-season/) | Current NBA assignments are archived as first **observed** snapshots; no referee effects or injury features are active. | Assignment crews can change. Official reports can change during the day. NBA terms and redistribution permissions are separate from public accessibility. First observed time is not first publication time. | Preserve existing assignments for provenance; do not claim historically reconstructed publication times or add gambling-model inputs without confirmed rights. |
| ESPN scoreboards | Supplementary schedules and final scores used for grading. | ESPN public endpoint is not evidence of a general bulk-data redistribution license. Event date and league IDs need validation; game finals must be explicitly final. | Use only for supplementary verification under current project behavior; record source and event ID, and review terms before bulk historical redistribution. |
| Historical NFL schedule odds | nflverse schedule includes home/away moneylines and spread/total fields. | The source dictionary identifies odds, but the last observed/close timing, book and availability timestamp are not established by the currently consumed row. | Store as retrospective reference with provenance; do not call it a closing line, sharp line, or point-in-time pick price until verified. |
| Historical NBA odds, game officials, injury/inactive records | No licensed, timestamped historical feed established by this project. | The Odds API historical feed is paid. Kaggle or community repository license labels may not establish NBA underlying rights; NBA.com terms limit gambling use. | Leave missing/unknown rather than fabricate timestamps or bypass terms. Seek a properly licensed source before use. |
| [RotoBot AI](https://rotobot.ai/), [terms](https://rotobot.ai/terms-of-service) | No current integration. User supplied a screenshot of @rotobot_ai describing 5,000 possession-based simulations of 76ers at Pacers without Haliburton. | Terms checked October 28, 2026: automated use is permitted only via its official MCP with an account and active subscription; scraping the site/apps is prohibited. MCP access is personal; outputs cannot be redistributed or used for a competing product. The terms also prohibit using outputs to train or benchmark a competing model. This conflicts with the project's $0 budget, shared public site and independent validation requirement. A public post alone does not establish accuracy, pregame data rights, or full model inputs. | Do not scrape posts or add RotoBot probabilities to the board, training or automated evaluation. The idea of simulating possessions from independently licensed, time-ordered play-by-play is a research direction, not access to RotoBot's model or data. |

The site is informational and does not place bets. Accuracy is win rate, not profitability. Source outages, stale data and unconfirmed rights are limitations, not evidence of a betting advantage.

The model-first shadow job captures daily season-to-date NFL QB pass-play summaries from observed nflverse files and records both source hashes and retrieval times. It uses only games finalized before the local game day. The summaries are descriptive, do not confirm an upcoming starter or injury status, do not adjust for opponents, and are not inputs to live predictions. Daily aggregate snapshots preserve the features used by the research record, but the underlying live release may later change; retaining a full immutable daily source vintage is not yet implemented.

The NFL shadow job also captures recent [nflverse injury and practice reports](https://nflreadr.nflverse.com/reference/load_injuries.html) once per day, with the first-observed time and source-file hash. The source says its injury data updates daily at 7 a.m. UTC and its dictionary describes a `date_modified` field; that field is preserved as raw source text, not presumed to be the first public announcement. nflverse describes most of its data as CC BY 4.0; underlying provider terms remain subject to review. These snapshots do not establish a confirmed starter, complete inactive list or timely current news, and are not used for picks.

The optional [PropLine NBA/NFL injury, schedule and score endpoints](https://prop-line.com/docs) are disabled until the user obtains a key and accepts [its terms](https://prop-line.com/terms). As checked October 28, 2026, the free tier lists 1,000 daily requests and the provider describes its injury source as ESPN with ten-minute refreshes. The board's roughly hourly update remains the limiting cadence. A response is reduced to aggregate status counts by team and reported position, with observed time and an incomplete-data warning; the raw player-level response is never committed. Scores are used only with an explicit `final` status, held in memory, and filtered before publishing individual selection results. A local daily limit of 200 attempts keeps ordinary use below the free quota; a failed run may not persist its reservations. Source failure never silently falls back to direct ESPN. The injury status is not a prediction input, a confirmed starting lineup, or a guarantee of full report coverage. Upstream rights still require review for any broader model or dataset use. Setup: [docs/NBA_AVAILABILITY.md](docs/NBA_AVAILABILITY.md).

The earliest `position-status-v1` snapshots used `training_eligible` to mean
field completeness, not approved data rights. A true value in those historical
snapshots is not authorization to train. Later snapshots set it to false and
store completeness separately; any training requires its own documented rights
decision and the preregistered time-order and holdout checks.

The H016 availability challenger additionally captures aggregate status
differences before the forecast, with its source and first-observed time. It
requires nonempty reports for both teams, rejects conflicting or future values
and keeps an unavailable report distinct from a zero-injury roster. In the
current registry, NBA data remain ineligible for training until upstream rights
are reviewed; NFL training requires observed nflverse reports and a matching
nflverse-confirmed outcome. This limited input does not establish that a player
will play, quantify player importance, or authorize a live adjustment.

Direct ESPN scoreboard automation needs rights review. [Disney's terms of
use](https://disneytermsofuse.com/english/) contain restrictions on automated
access to Disney products; ESPN is a Disney brand. The existing public-scoreboard
endpoint has not been established as an authorized exception, so its current
use is a source-rights risk rather than a verified license. A rights-cleared
schedule and final-status replacement is still required for full compliance.

The prospective paper-replay process uses `data/research_permissions.json` as a separate, initially empty allowlist. An entry must document the league, exact quote provider, model-feature source (`nflverse+espn` or `boxscorelab+espn`), permitted outcome sources, a rights-evidence link, a positive rights-verification decision and a review time no later than the prediction. Captured source hashes must also be present. No source is approved merely because it is public or appears in a file. The gate records source uncertainty; it is not a substitute for legal review or a way to manufacture historical availability timestamps.

### Independent scoring-process research input

`research_possession_simulator.py` reads archived BoxScore Lab team box scores
and nflverse play-by-play shards from `data/observations` in GitHub Actions.
It does not download RotoBot content. `reports/scoring_process_validation.md`
records exact archived asset hashes, observation counts and a matched-game Elo
comparison when the weekly research workflow succeeds. NBA source upstream
wagering rights remain unresolved, so archive usage is confined to research;
neither league's simulation influences published selections. The report may
be absent or stale when Actions or an input source is unavailable.


### NBA multi-stat rotation features (H023)

The existing archived SportsDataverse ESPN player boxes contain assists,
turnovers, offensive/defensive rebounds, steals, blocks, field-goal attempts,
three-point attempts, free-throw attempts and fouls. These are parsed as
optional validated nonnegative numbers; absent/invalid entries remain unknown.
No new service or subscription is enabled. Earlier same-team player rates and
projected regulation minutes supply shared historical/live feature definitions.
Historical rosters remain inferred from prior appearances, not verified injury
snapshots. Source attribution/usage qualifications above remain in force.
Outputs are separately versioned research artifacts, not a qualified wagering
feed or proof of defensive player value.

### NBA play-by-play lineup research

The SportsDataverse `espn_nba_pbp` release supplies public CSV/Parquet exports:
https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_nba_pbp
Season files 2022–2027 are archived for six NBA seasons, including warm-up.
The optional research environment pins PyArrow 19.0.1 alongside the existing
sklearn dependency; the app runtime does not require either dependency.
Downloads are capped at 35 MB with bounded retries; completed seasons are
cached, and current-season Parquet refreshes are bounded to 12-hour intervals.
Source roster/starter IDs are joined exactly, not by fuzzy player names.
Only uniquely reconstructed, score/time-consistent segments are accepted;
full-game mode additionally requires per-player box-minute agreement and
excludes overtime. ESPN exports contain ambiguous action/clock sequences;
low reconstruction coverage is disclosed rather than treated as full coverage.
Publisher attribution and upstream-use qualifications remain unchanged.
This research import grants no claimed NBA wagering-data permission.
