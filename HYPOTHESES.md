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
separate eligibility flag; it does not train a model or change predictions.
Future analysis is part of the H007/H016 availability family and must preserve
its sample, multiple-testing, time-order, rights, replication and untouched
holdout gates. Do not train on a source until its relevant usage rights are
reviewed, and do not promote position features without evidence they improve
the matched-time benchmark.
