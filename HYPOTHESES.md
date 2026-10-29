# Hypothesis registry

Registry opened during Step 0. Existing rest/form tests were exploratory and were run before this registry existed; none of their results is a preregistered finding or a final holdout. Do not rewrite this history. All new hypotheses and analysis choices must be committed before testing.

## Protocol

Specify population, point-in-time inputs and missingness, direction, baseline, outcome, metric, testing family, sample and seasons before running a test. Use chronological walk-forward evaluation; select and tune only within prior windows. Apply Benjamini–Hochberg to all raw p-values within the preregistered family and report raw/adjusted p-values, sample counts, effect sizes, intervals and failures. A candidate must replicate in at least two separate seasons and pass a genuinely untouched later holdout; a season previously examined for feature selection cannot be relabeled untouched. Evaluate the full blend against a matched-time market-only benchmark as well as its team component. Leave a feature disabled/shadow until its evidence satisfies these gates. No demographic features.

| ID | Hypothesis and direction | Comparison and primary metric | Current status |
| --- | --- | --- | --- |
| H001 | Pre-game rest-day differences improve NBA/NFL predictions versus the identical team model without rest. | Walk-forward Brier and log loss of the **full matched-time market blend**, per league; positive improvement means lower loss. | Registered for future testing; no compliant results. Earlier two-season team-component exploration is not validation. |
| H002 | A team's pre-game rolling five-game scoring margin improves NBA/NFL predictions versus the identical team model without it. | Same matched-time market-blend comparison; separate leagues and the combined rest/form specification are in the same multiple-testing family. | Registered for future testing; no compliant results. Earlier exploration is not validation. |
| H003 | Available best retail prices more favorable than a matched-time independently sourced market anchor produce positive subsequent CLV, after costs and data-quality filters. | Mean CLV vs a verified sharp close, with sample and confidence interval; no retrospective assumption that an hourly observed quote is a true close. | Not testable until sufficient forward, licensed snapshots and a sharp-close source exist. |

Research runs must be recorded in `reports/` with candidate versions, data hashes, periods, family, raw/adjusted p-values, effect intervals, failures, and whether any holdout was touched. No preregistered test has been run as part of Step 0.

## Model-first head-to-head preregistration (before new tests)

**H004 — pure team model versus sharp market.** On the first eligible, timestamp-matched pregame forecast for each NBA/NFL game collected after this registration, the market-independent model has lower mean paired log loss than a no-vig sharp market anchor. Define the paired difference as `logloss(model) - logloss(sharp)`; negative favors the model. Outcomes are confirmed final non-ties. The two league-level hypotheses are one family; adjust their p-values with Benjamini–Hochberg. The primary paired test is a pre-specified game-day-block sign permutation, two-sided, 10,000 draws, seed 20261028; report the number of games and game days and a game-day-block bootstrap interval. A fitted model-plus-sharp blend is the third shadow arm; fitting and evaluation must be strictly walk-forward and use only earlier timestamped, settled observations. Until a licensed, genuinely sharp anchor and sufficient data exist, all sharp-arm metrics are unavailable. A retail median is an explicitly labeled descriptive comparator, not a substitute for a sharp anchor in the staking rule.

**H005 — prospective pure-model paper returns and sharp CLV.** With one fixed paper unit per pregame selected side at the recorded best observable price, report mean paper ROI and a game-day-block bootstrap interval, and calculate mean CLV only against an independently verified sharp pregame close. No claim of profit or approval for staking from a retail proxy or unknown price. The model-first staking gate additionally requires at least 300 settled prospective selections in the relevant approved segment, adjusted paired evidence that the pure model beats sharp-market log loss, a positive sharp-CLV interval excluding zero, and a bootstrap ROI interval whose lower end is not below zero. The final confirmation sample must be untouched and separate from tuning; currently none exists. This stringent lower-bound rule is a conservative interpretation of “not clearly negative.” No part of this gate places a wager.

Before evaluating a paired test or a bootstrap interval, require at least 30 eligible games on 10 distinct game days. Smaller samples remain descriptive and inconclusive. This minimum was added before any prospective sharp-market test was run.

**Disagreement guard.** A disagreement curve, if a sharp source becomes available, will be fit on earlier fully observed games only. Candidate thresholds require separate walk-forward selection, clean injury/lineup/quarterback/weather data with verified as-of times, and preregistered replication/FDR checks before staking could be permitted. Until then all selections are paper-only; no threshold or confidence level is invented.

**H006 — NFL quarterback efficiency challenger.** A model using a pregame, opponent-adjusted quarterback EPA/CPOE summary built only from previously completed games and observed source snapshots improves walk-forward NFL log loss against the same pure team baseline. Consider EPA and CPOE variants a single multiple-testing family; report all attempted variants, adjusted p-values, day-block intervals, sample sizes and missingness. The initial extractor may log descriptive season-to-date pass-play summaries in shadow mode, with explicit shrinkage and retrieval timestamps, but must not feed predictions or be treated as an opponent-adjusted model. Forecasts or past tests cannot use an asset that was first retrieved after the relevant prediction time. Quarterback and injury status remain unknown unless independently observed before kickoff. No H006 test has run.

## Additional preregistration before Phase 5–12 analyses

These are research proposals, not results. All source status, model-input and final-outcome timestamps must precede the relevant forecast or training cutoff. Compare forecasts on the **same games and times** using paired log loss as primary outcome, Brier as secondary, day-block uncertainty and the existing minimum of 30 games on 10 days for inference. Correct all variants and league/slice tests in each named family with BH; show missingness, effect, CI, raw and adjusted p, every failure, and whether data was used to tune. Require replication in two independently evaluated seasons and a distinct, untouched later season before promotion. A segment must also meet H004–H005 before real-stake status. If a source or enough observations are absent, record `not_testable`, not a pass.

For the H010 exploratory batch, use a two-sided game-day-block sign test and a BH-adjusted alpha of 0.05; a result in the opposite direction or above the threshold is not a detected effect. Passing that preliminary screen is not promotion and does not waive independent replications or the untouched holdout. The grid for H008 carryover shadow exploration is fixed at 0, 0.25, 0.5, 0.75 and 1 before running it on real eligible data.

- **H007 — availability family.** A pregame, source-timestamped availability-scenario mixture improves pure-model log loss versus the identical model without it; NBA and NFL each form members of the family. Starting-player likelihood by designation is estimated only from earlier reports and verified participation, with shrinkage toward earlier league rates. Test uncertainty calibration as a secondary metric. No current injury or lineup source is assumed complete.
- **H008 — team-rating family.** Each of margin-scaled Elo, learned season carryover, shrunk team home advantage and a calibrated uncertainty-aware strength challenger lowers pure-model log loss versus the fixed baseline, separately for NBA and NFL. The cross-product of attempted variants and leagues is one family. Any tuning is nested within earlier seasons; games-played buckets are secondary slices in that same family.
- **H009 — officiating family.** Pre-announced referee or crew effects, partially pooled toward the league mean, improve matched-time market-only log loss and Brier; test NBA and NFL separately and include any team-by-official interactions in the same family. Direction is improved loss, not an assumed home bias. Report each effect with sample and interval; assignment or line timing that cannot be established is excluded.
- **H010 — schedule and weather family.** Relative to a matched-time market baseline, investigate: (a) home disadvantage when the home team has at least two fewer rest days; (b) a team on the second game of a back-to-back underperforming its market probability; (c) a West Coast team playing an early Eastern road game underperforming its market probability; (d) Denver/Utah home advantage in high-altitude games beyond the market; (e) an NFL divisional underdog exceeding the market expectation; (f) an outdoor NFL underdog in measured sustained wind of at least 15 mph exceeding the market expectation; (g) a team with a verified change in starting quarterback underperforming its market probability; and (h) the home team after a prior overtime game underperforming its market probability. Direction is expressed as a signed win-minus-market residual for the specified side; loss comparison is secondary. The eight definitions, their league splits, and any tested thresholds constitute one family. Unsupported weather, starter or point-in-time inputs are missing, never inferred from an outcome.
- **H011 — model-stack family.** Pure, odds-independent regularized logistic, boosted, margin-distribution and calibrated/team-uncertainty challengers improve matched-time log loss versus the frozen pure baseline, by league. A fitted sharp-plus-model blend is a separate shadow arm and is not the pick engine. All attempted model/league configurations and early-season slices are one family. Large models, Bayesian and TabPFN variants require documented licenses, dependencies and prior-only tuning.
- **H012 — trust and timing family.** A pregame candidate filter and closing-price predictor fitted solely on earlier settled, time-matched samples improve out-of-sample sharp CLV versus selecting every eligible paper candidate; candidates, exclusions, timing and missed opportunities must all be logged. The filter remains shadow-only until genuine sharp closes and adequate samples exist. Variants, leagues and thresholds form one family. No automatic wagering.

## H015 — prospective paper replay protocol (registered before evaluation)

Replay the first frozen, selected model-first paper candidate for each game and league in forecast order, using only rights-qualified quotes and features observed before that forecast. No later quote, outcome, correction or closing line may determine the selection. The paired comparator is the same book's simultaneous two-sided multiplicative no-vig probability; the primary descriptive differences are candidate-minus-market log loss and Brier on the same settled non-tied games. Report by league and model version; a retail comparator is not a sharp benchmark.

The initial **illustrative execution scenario**, fixed before running it, starts with 100 paper units, risks at most one unit per selection and three units per local game day, and reduces the winning net payout by 2% as an adverse slippage sensitivity. These are assumptions, not verified sportsbook limits or fills. Keep cash reserved while a result is unknown, apply verified final settlements only when observed, and separately disclose pending and void/unknown cases. Do not count an unconfirmed tie, cancellation or postponement as a loss or an automatic void. Report paper ROI, game-day-block bootstrap intervals, sample size and maximum drawdown; a certified independent sharp close is required for sharp CLV. Day-block intervals are unavailable below 30 games and 10 days. Do not describe a small sample or assumed fills as proof of profitability.

This replay is an instrument for H004/H005, not a new optimization or a final untouched holdout. Any future feature/threshold choices, additional variants and segment tests require prior registration, a fully disclosed multiple-testing family, separate seasonal replications and a later untouched confirmation. No execution or user wager is created.

## H011 implementation registration: boosted-stump shadow challenger

Before any real-data run of this variant, compare an odds-independent, regularized logistic gradient-boosted decision-stump model with the frozen team baseline using the same three pregame features as the elastic-net challenger. Enforce increasing constraints for the home-minus-away team rating and home-court adjustment, leave the games-played difference unconstrained, and do not use market prices. Use the fixed inner grid `(25 stumps, 0.05 learning rate, 10 L2)`, `(50, 0.05, 10)` and `(50, 0.10, 10)`, with at least 30 examples in each leaf. Choose by log loss on the most recent eligible prior season after fitting only on outcomes observed before that season began; the minimum is 500 earlier training games, 100 inner-validation games and three seasons. Refit the chosen setting on all eligible past data for future shadow forecasts.

This fixed-grid pure-Python challenger is not XGBoost, LightGBM, CatBoost or Optuna and does not satisfy those specific package requirements. It is included in the existing H011 multiple-testing family, with raw and BH-adjusted paired p-values, day-block intervals and every failed attempt retained. The inner-validation season is not an untouched holdout. An apparent win cannot promote a model without the other preregistered season, holdout, sharp-market and profit gates.

## H012 implementation registration: trust and timing shadow models

Before any real-data fit, use the following fixed, pregame-observed inputs: model edge, price edge, source disagreement, hours to start, observed line movement, model uncertainty, hours since verified news, games played and verified available liquidity. Missing values are excluded rather than filled with a healthy-player assumption. A source-qualified independent sharp anchor must be observed before the prediction. Labels require a separately certified, rights-qualified sharp close observed before the start and certified after the start, with the certification itself available before the training cutoff. The first candidate per game and side is chosen before looking at its label.

Fit a regularized logistic model for whether sharp CLV is positive, and a regularized linear model for the later change in selected-side sharp probability. Use the most recent prior eligible season for inner validation, at least 500 earlier observations and 100 validation observations over three seasons; all earlier training labels must be available before the validation period. Fixed regularization is 0.01, with no threshold search in this initial version. These models, their scores and their prospective predictions are shadow-only. Timing output is a predicted price-probability movement, not a bet-now/wait instruction or proof of expected profit. An unavailable sharp source produces `insufficient_data`, not a zero value. H012 variants and league tests remain one multiple-testing family and cannot gate stakes or promote themselves.

## H013 — additional schedule and market pattern definitions

Registered before implementation or evaluation. Apply the same first-eligible-pregame forecast, rights, time, direction, day-block test, minimum sample and untouched-holdout rules as H010. Test the following with H010 as one combined BH family, including all league splits. Earlier H010 runs had no eligible outcomes and therefore performed no statistical tests.

1. **H013a:** exactly one team lost its previous game by at least 20 NBA points or 21 NFL points; test whether that team exceeds its pregame retail win probability (positive).
2. **H013b:** exactly one team won its previous game by at least 20 NBA points or 21 NFL points; test whether that team falls short of its pregame retail win probability (negative).
3. **H013c:** exactly one NFL team has at most five rest days while its opponent has more; test whether that team falls short of its retail probability (negative).
4. **H013d:** exactly one NFL team has at least 13 rest days while its opponent has fewer; test whether that team exceeds its retail probability (positive).
5. **H013e:** both teams have played fewer than ten games this season; test whether the pregame underdog exceeds its retail probability, separately by league (positive).
6. **H013f:** a pregame underdog has retail no-vig probability below 35%; test whether that underdog falls short of its retail probability, separately by league (negative).
7. **H013g:** the range of same-time book-level no-vig home probabilities is at least eight percentage points; test whether the home team falls short of the retail median, separately by league (negative).
8. **H013h:** an NFL game begins at or after 8 p.m. ET with a non-even market favorite; test whether that favorite falls short of its retail probability (negative).

Previous-game margins, team games played and all book prices must be preserved in the forecast's pregame snapshot. Missing, tied, contradictory or unverified values remain unknown. These exploratory definitions do not prove a causal mechanism, and the market may already reflect the schedule or news.

## H016 — player availability as a shadow model input

Registered before collecting or testing this feature. For each future NBA/NFL
game with observed, time-qualified injury status for both teams, compare a
ridge-regularized logistic adjustment to the simultaneously frozen pure-team
forecast with the unchanged forecast. Inputs are the home-minus-away counts of
players listed out, doubtful, and questionable/game-time-decision. They are
coarse signals, not player-importance estimates; more missing players are
hypothesized to favor the opponent. An absent report, empty team report,
future timestamp, malformed response, conflicting status or unreviewed source
is unknown and must not be imputed as a healthy roster. Keep source, observation
time, game time and a versioned feature snapshot, with no raw NBA feed dataset
published to the public repository. Do not train NBA data until its rights are
explicitly established.

Use only one earliest eligible pregame observation per game and results
actually observed before training. Require at least 500 previous training
games, a later prior-season validation of at least 100 games, and three
seasons before producing a candidate. Tune only a fixed regularization grid
on that prior validation season and refit only with data known before the
forecast. Evaluate future forecasts on the same timestamps against the frozen
team baseline using paired log loss and Brier, with NBA and NFL in one
multiple-testing family and game-day blocking. Do not promote before two
independent season replications, an untouched later holdout, and the other
registered market-validation conditions. No effect size, play probability,
player impact, or claim of better predictions is assumed in advance.

## H017 — user-requested confidence ordering

The user requested ranking the model's most likely winners rather than sorting
by estimated return. On every run, consider all eligible same-day games, take
only the side with the higher independent model win probability, retain the
existing timestamp, book-count and price-qualification checks, and rank the
remaining sides by that win probability. Ties have a deterministic game-id
order. Existing frozen selections remain unchanged. This is a user-directed
presentation and selection preference, not evidence of an advantage or a
calibrated confidence measure. A future matched-time replay should compare
the first three qualified sides under this ordering with the previous EV
ordering using accuracy, log loss, Brier and execution-aware return; log all
outcomes and report counts. Do not force a selection when nothing qualifies,
and do not label a price edge proven from an unvalidated forecast.

## H018 — availability by position

Register before any test: compare an injury model with position-level counts
against the identical frozen team model without those counts, on the same
pregame games. NFL positions include offensive, defensive and specialist
positions; NBA positions include any labels actually provided by the source.
Position and player importance must be learned from earlier, rights-qualified
data, not assigned by hand or inferred from final results. Incomplete reports,
unknown positions, unconfirmed starters and missing team reports remain unknown.
The provider's observed time is the time this system received a report, not a
claimed publication time. Only aggregated status counts are retained.

The recording process produces a versioned, time-qualified snapshot, with a
separate position completeness flag. Training eligibility remains false until
rights are reviewed; the process does not train a model or change predictions.
Future analysis is part of the H007/H016 availability family and must preserve
its sample, multiple-testing, time-order, rights, replication and untouched
holdout gates. Do not train on a source until its relevant usage rights are
reviewed, and do not promote position features without evidence they improve
the matched-time benchmark.

## H019 — score bootstrap challenger (registered before evaluation)

For NBA and NFL separately, estimate each team's scoring and prevention from
earlier final scores, shrink small team samples toward the earlier league
mean, then simulate paired score variation from earlier same-league games.
Hypothesis: the score bootstrap improves Brier score and log loss over the
existing Elo baseline on later games. Use a fixed seeded 5,000-draw
retrospective evaluation, comparing only games with both forecasts and
respecting game-date order. Also show the naive 50% home baseline. The
retrospective seasons used here have already been inspected and are **not**
an untouched holdout. Source revisions lack historical publication timestamps.
No betting ROI, player impact, possessions or drives may be inferred from
this test. The live 10,000-draw snapshot remains disabled for pick selection
until a later untouched evaluation, matched-time market comparison and the
same source-rights and prospective promotion gates as H016 pass.

## H020 — independent possession/drive simulator concept

The @rotobot_ai example motivates a possible independently built NBA
possession/NFL drive simulator, **not** ingestion or benchmarking of RotoBot
outputs. With source-rights-qualified, time-ordered play-by-play and pregame
player availability, test whether an independently estimated possession/drive
process improves paired out-of-sample log loss and Brier over Elo and a
matched-time market baseline. Preregister feature and scenario choices,
calibrate on prior seasons, reserve an untouched later season, and leave the
new component disabled unless it improves both calibration and the market
comparison. Record every failed variant. The existing score-bootstrap
challenger lost to Elo (NBA 0.2369 vs 0.2093 Brier; NFL 0.2380 vs 0.2231),
which is a reason to demand stronger empirical evidence, not to increase
the simulation count. RotoBot's terms preclude automated ingestion or using
its outputs to benchmark a competing model under the current $0/public-site
requirements; see DATA_SOURCES.md.

### H020 implementation checkpoint — scoring-process-v1

The first independently implemented challenger uses BoxScore Lab box scores to
**estimate** NBA possession counts with FGA − offensive rebounds + turnovers
+ 0.44 × FTA and to derive abstract 0/1/2/3-point scoring units. These units
are not observed play-by-play possessions: free throws can share a possession
with a field-goal attempt. The NFL component groups nflverse `fixed_drive`
play rows and measures offensive points from each drive's first preplay to
last postplay offensive score. Defensive scores, returns and unusual plays
remain unmodeled. The simulator shrinks earlier offense and opponent defense
rates toward the league, samples earlier paired game unit counts, and draws
points from an exponentially tilted historical scoring-unit distribution.
Seeds and 5,000 draws are fixed. Same-day finals are withheld in walk-forward
analysis. Evaluation uses the already inspected 2026–27 NBA and 2025 NFL
seasons; it is exploratory and not an untouched test or a market comparison.
Missing pregame player availability and unresolved NBA upstream gambling-use
rights keep both research-only. No live pick or UI probability is changed.

The first archived evaluation completed in GitHub Actions. On matched games,
NBA scoring-process-v1 Brier was **0.2468 versus Elo 0.2116** (52 games;
2026–27 to date). NFL was **0.2473 versus Elo 0.2338** (326 games across
2025 and 2026 to date). Log loss also favored Elo in both. The challenger
failed this gate and remains excluded from picks. This sample is neither an
untouched holdout nor a same-time market comparison. The next defensible
change needs point-in-time player availability and a validation/holdout split;
re-running more simulated outcomes from the same assumptions cannot repair
this failure.

## H021 — day-start top-three winner ranking audit

Registered before running the new archive evaluation. Population: archived NBA
and NFL games on ET dates, excluding ties; fixed Elo NBA K=20/HFA=55 and NFL
K=24/HFA=42, using only results strictly before each game date. On a day with
multiple eligible games, choose the three sides with the largest Elo winner
estimate, breaking ties by game ID. Test dates begin January 1, 2024 after
initial training seasons. Report accuracy, Brier and log loss of the selected
sides, all eligible model favorites and a 50% uninformative baseline. Report
league split, calendar-year split and 0.50–0.59, 0.60–0.69, 0.70–0.79 and
0.80–1.00 reliability bins with sample sizes. Include a seeded 2,000-draw
calendar-day-block bootstrap interval for top-three accuracy when at least
30 selected games and ten days exist. Do not fit thresholds or calibration on
these same observed test dates. Source files were first archived after these
games; the evaluation is an exploratory retrospective day-start proxy, not a
record of published pregame forecasts, verified pregame injuries or a fresh
untouched season. It cannot prove the model's current accuracy or betting
value. Archive research only for NBA because upstream usage rights remain
unresolved. The actual forward winner accuracy continues to use only the
immutable `data/winner_predictions.json` ledger.

## H022 — NFL position-status research challenger

Registered before running a real-data evaluation. A frozen pregame nflverse
injury/practice snapshot for both teams supplies out, doubtful and questionable
count differences in nine position groups (QB, back, receiver/TE, offensive
line, front, linebacker, secondary, special teams, other). No practice-only
status is converted into a game designation, and no unlisted player is assumed
healthy. Add these counts as regularized logit adjustments to the frozen Elo
home probability; choose the penalty on a later prior season, with at least
500 earlier games, 100 validation games and three eligible seasons. This
tests whether position-aware statuses improve future log loss and Brier beyond
team-wide counts and Elo. Record candidate predictions before kickoff and
compare on the same game and timestamp against frozen Elo by calendar-day
block. Treat H016 and H022 as one multiple-test family with adjusted p-values.
Never promote based on training/validation alone, a small prospective sample,
or the most favorable position coefficient. This is not a player-impact model,
cannot supply justified questionable-player probabilities, and does not
influence picks until independent later results establish benefit. NBA
upstream status rights remain unresolved and are excluded from this challenger.

## H023 — NBA lagged multi-stat rotation challenger

Registered before running this new feature comparison. Add earlier-appearance
projected assists, turnovers, offensive and defensive rebounds, steals, blocks,
field-goal attempts, three-point attempts, free-throw attempts and fouls to the
existing fourteen team and three rotation features. Use the last ten earlier
same-team appearances, infer historical membership only from earlier playing
records within 21 days, cap rotations at twelve players and regulation minutes
at 48 per player / 240 per team. No same-date player outcomes may enter features.
Missing metrics are unavailable, never zero. Historical membership is inferred;
this is not a reconstruction of historical injury reports or confirmed lineups.

Fixed C=1 standardized logistic, separate prior-season Platt calibration and
100-iteration histogram boosting use the existing training protocol. Compare
team-only, scoring-rotation and multi-stat models on exactly the same games in
each later season. Direction: lower calibrated log loss and Brier than the
scoring-rotation baseline. Run paired calendar-day sign-randomization tests of
log-loss differences with seed 20261028 and apply BH correction across every
reported season; report null/negative results as well. Archive already inspected,
so this is exploratory research, not untouched confirmation or promotion.

Current injury scenarios may substitute verified current roster membership and
listed absences into the same projected-stat feature definitions. Enumerate
uncertain players independently without invented scenario probabilities. Steals,
blocks and rebounds are box-score indicators, not RAPM or complete defensive
value; minutes redistribution is a proxy, not validated replacement impact.
Unknown historical availability, source-use qualifications, market performance
and independent forward validation remain explicit limitations. No sportsbook
prices enter the learner and no public pick switches based on these tests.

## H024 — NBA convex ensemble of chronological component predictions

Registered after inspecting H023's negative/mixed results, before this test.
This is related follow-up research, not independent confirmation. Components:
fixed Elo and the team, scoring-rotation and multi-stat calibrated logistic
models. Fit nonnegative weights summing to one on a 0.1 grid using only
component predictions from earlier held-out seasons. Require 500 earlier games
and 30 days. Minimize earlier log loss; deterministic ties favor fewer nonzero
weights. Evaluate the following season once on identical games, without
changing the grid after observing its results. Compare Brier/log loss/accuracy
against every component and a component selected using earlier log loss only.
Direction: lower later log loss than Elo. Report a fixed-seed paired day-block
test vs Elo with BH correction across H023 and H024 season tests together.

No market input or price edge is claimed. The already inspected archive is
exploratory, not an untouched final test. Do not promote based on this report.
If current injury scenarios are available, apply the learned convex weights to
matching component scenarios; otherwise withhold a scenario requiring a
missing component. Do not assign participation weights or claim that weighting
correlated components creates independent evidence. An ensemble selecting only
Elo/team inputs must not be described as injury-adjusted.

## H025 — NBA verified first-quarter stint player associations

Registered after source-schema inspection, before model fitting. Reconstruct
first-quarter stints only from exactly five box-score starters per team and
explicit entering/leaving player IDs. Require complete source End Game status,
regular-season identity agreement, nonincreasing clocks, monotone scores,
valid substitution membership and a first-quarter end marker. Exclude ambiguous
games; do not infer later-period opening lineups. Report all exclusions and
coverage. Same-game lineups/scores are postgame training inputs/targets only,
never fabricated pregame availability features.

Fit signed home/away player ridge effects on net points per 48 minutes, weighted
by stint duration, controlling simultaneous teammates/opponents. This is an
observational time-based adjusted plus-minus association, not possession RAPM
or a causal injury effect. Require 120 earlier stint minutes per player and
exclude unknown-player evaluation rows rather than assign zero. Compare on
identical rows with league-intercept and team ridge baselines. Train older
seasons, choose alpha from [100,1000,10000] on a separate previous season and
report later-season minute-weighted MSE and unique game/player/stint counts.
Direction: lower held-out MSE than team ridge. No game-winner, calibration or
profit claim follows from a stint-rate improvement. Use whole-day paired tests
and BH correction over reported seasons where supported. Archive research
only; historical pregame participation and NBA source qualifications remain
unresolved. Public picks do not change.

An exported research artifact may report projected lineup-strength differences
under supported current roster scenarios, including how redistributing minutes
to known replacements changes the estimate. Unknown-player values stay unknown.
Do not convert a strength delta into a winning probability without a separately
trained and evaluated outcome model.

H025 implementation clarification before the first successful fit: the initial
recursive filtering produced zero training rows and therefore fitted no models.
Retain every observed training player as a regularized nuisance column so
low-sample participants are controlled rather than assumed zero. Publish only
effects backed by 120 actual training minutes; validation/test rows must contain
only those supported players. Unknown test players remain excluded. No penalty
grid, metric, evaluation boundary or sample threshold is relaxed. Record the
number of unpublished nuisance columns separately from supported player values.

## H026 — uniquely reconstructed later-quarter lineup validation

Registered after H025's weak/limited first-quarter results, before fitting the
expanded model. Later-period initial lineups may be deduced only when explicit
on-court actions/substitutions uniquely establish exactly five initial players
per team. Replaying every substitution must preserve membership and clocks.
Require quarter 1 to agree with recorded starters, exactly 48 regulation game
minutes and each player's reconstructed full-game minutes to agree with the
source's rounded box minutes within 1.1 minutes. Reject ambiguous periods,
unknown identities, clock corrections and overtime games; do not guess a fifth
starter. Report all exclusions, accepted games and coverage. These are
postgame reconstruction constraints, not verified pregame lineups.

Apply H025's fixed ridge/alpha/minute thresholds and separate-season
training/calibration/test to full-game stints. Metric/direction: lower later
minute-weighted net-rate MSE than team ridge; retain league baseline and
negative results. Correct H025/H026 season tests jointly. Ratings remain
observational associations, not possession RAPM, causal injury effects,
complete defense or game-winner probabilities. More data does not justify a
production switch by itself. Record the full-game model separately.

## H027 — season-frozen lineup-value feature in the NBA outcome model

Registered after H025, before this new outcome-model test. For each game season,
fit a fixed-alpha=1000 player ridge rating using only earlier seasons' accepted
full-game stints. Include all observed training players as nuisance controls;
publish/consume only effects supported by 120 earlier training minutes. Never
use the game's actual lineup/participation as a pregame feature. Project from
prior player appearances and infer historical membership as in H023, marking
historical pregame availability unknown. Add only the projected home-minus-away
lineup association /20 to H023's 27 features. An unknown projected player effect
withholds the new feature, rather than becoming zero.

Add the free 2021-22 player/PBP season as warm-up where available. Keep the
existing 500-training/200-calibration game requirements and fixed logistic/GBM
configuration. Compare 27 versus 28 features and Elo on identical later games;
direction is lower calibrated log loss/Brier. Fit/calibrate strictly in older
seasons. Correct related H023/H024/H027 game-outcome tests jointly; do not treat
this follow-up on inspected archives as independent confirmation. Preserve
insufficient-data and negative results. Current injury scenarios must use the
same season-frozen rating definitions, not a differently refitted rating.
No public promotion or wagering-edge claim follows from this test.

## H028 — measured partial lineup component plus explicit coverage

Registered after H027 yielded only six complete-case examples and no fitted
outcome model. Preserve that failed/insufficient study. Without lowering the
120-minute effect threshold, 500-game training floor or 200-game calibration
floor, test three supplemental inputs: the difference in the measured
minute-weighted contribution from supported players, home supported-minute
fraction, and away supported-minute fraction. These are NOT total lineup
values. Unobserved player coefficients remain unavailable; no individual
unknown effect is set to zero. The sum over the known subset is a measured
partial component, paired with explicit unknown exposure indicators.

Keep all 27 prior box/team features and fixed chronological fitting protocol.
Use prior-season-frozen ratings exactly as H027; no same-game participation
becomes a predictor. Compare 27 versus 30 features and Elo on identical later
outcomes. Direction: lower calibrated log loss/Brier. Correct related
H023/H024/H027/H028 outcome tests jointly. Retain null/negative results and
report coverage; a partial component is not a verified full defensive or
replacement value. Current scenarios must retain missing-effect/coverage
flags. No public-model promotion follows from this exploratory follow-up.
