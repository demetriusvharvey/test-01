MASTER PROMPT: UPGRADE "LINE LAB" INTO AN EDGE-FINDING NBA/NFL MONEYLINE SYSTEM

ROLE
You are a senior quant researcher and ML engineer. Upgrade this repo so it (1) measures honestly whether it has a betting edge and (2) finds the specific situations where its probabilities beat the market. Be a skeptical scientist: most sports "patterns" are noise, and your job is to find the few that survive out-of-sample. Primary success metric: closing line value (CLV) vs a sharp close. ROI is secondary and always reported with confidence intervals and sample sizes.

REPO CONTEXT (verify by reading the code; correct anything I got wrong)
- scripts/pipeline.py (stdlib only, ~22KB): Elo per league (NBA K=20/HFA=55, NFL K=24/HFA=42, flat 0.75 season carryover, 6 fixed configs chosen on one validation season's Brier); build_market (merges 6 retail books from scraped AgentBets HTML, drops odds >95 min old or games starting within 20 min); choose_candidates (fair = median of retail devigged prices; p = 0.75*market + 0.25*Elo; edge = p - implied(best price) >= 0.01; max 3 picks/day); grade_ledger; render_board.
- scripts/refresh_feed.py: The Odds API snapshot to dist/feed.json (ODDS_API_KEY secret) plus NBA referee parsing (parse_referees). Not used by the model.
- data/predictions.json (frozen pick ledger, 1 row, 0 settled), data/referee_history.json (4 rows), dist/ (static Vercel site: index.html, app.js, board.json, hand-written data.js).
- .github/workflows/daily-picks.yml (hourly cron) and refresh-feed.yml commit results to main. Tests: unittest, 9 passing. Keep `python -m unittest discover -s tests` green at every commit.
- The nflverse games.csv the pipeline already downloads also contains referee, home/away moneyline, spread_line, total_line, over/under odds, home_rest/away_rest, roof, surface, temp, wind, home/away QB name and id, coaches, div_game, overtime. Only scores/location are used today. Use all of it.

NON-NEGOTIABLE RULES
1. Point-in-time only: every feature uses data known before the pick timestamp, with as-of timestamps stored.
2. Walk-forward validation only, never random splits. Keep a final untouched season for one-time confirmation.
3. Pre-register every pattern hypothesis in HYPOTHESES.md BEFORE testing it (what, why, direction, metric). Log every test run, including failures. Apply Benjamini-Hochberg false-discovery correction across all tests; report raw and adjusted p-values.
4. Use partial pooling/shrinkage (mixed-effects, empirical Bayes, or Bayesian hierarchical) for referee, team-by-referee, venue and coach effects. Show n and intervals next to every pattern. A pattern reaches production only if it replicates in at least 2 separate seasons AND holds out-of-sample.
5. Every module must earn its place: show walk-forward or shadow-mode evidence vs the previous version (log loss, Brier, CLV, ROI with CIs) or ship disabled by default. Write reports/<module>.md for each, including negative results.
6. No demographic features (race, ethnicity, etc.) for referees or players. Performance-based features only.
7. Licensed/official data only. Document ToS, licensing and rate limits of every source (including the scraped AgentBets pages) in DATA_SOURCES.md and flag risks. No sportsbook-account scraping. No auto-bet placement: the app informs, I bet manually.
8. Never fabricate, hardcode or cherry-pick results. If nothing beats the market, say so plainly. Keep the "not validated as profitable" language until the Phase 11 validation bar is met.
9. Secrets via env/Actions secrets. Ledger changes are backward-compatible: existing rows stay valid, and picks are immutable apart from grading/closing fields.

STEP 0: AUDIT AND PLAN
Write AUDIT.md (verify the context above; top 10 weaknesses ranked by impact on profitability) and PLAN.md (phases adapted to the real code). Start HYPOTHESES.md and DATA_SOURCES.md. Reuse and refactor existing code, make small commits with tests, and state assumptions instead of asking me questions unless blocked.

PHASE 1: STORAGE, ODDS HISTORY, BACKFILL
- Append-only odds_snapshot store (book, game id, market, both sides, source timestamp, fetched_at). Hourly JSON commits to git will bloat: choose and justify SQLite/DuckDB/parquet on a data branch or a free-tier hosted Postgres, keeping the static site working.
- Capture closing lines (last snapshot before start). Consider a frequent pre-tip job on game days and handle GitHub cron delays gracefully.
- Add The Odds API as a second odds source for cross-checking and fallback. Add data-quality checks (stale, duplicate, timezone, missing side) that suppress picks rather than guess.
- Split pipeline.py into a package (ingest, features, model, market, ledger, report) without changing behavior. Add parser fixture tests so scraped-HTML changes fail loudly.
- NFL backfill: ingest every games.csv column, plus nflverse play-by-play, injuries, depth charts and snap counts, plus weather (wind matters more than temperature; dome flag).
- NBA backfill: 5+ seasons of box scores, game-level officials (crew chief, referee, umpire; e.g. nba_api box score summary officials, verify availability/ToS), injuries/inactives, rest and travel. Store the timestamp each crew assignment became public and keep collecting daily going forward.
- Historical closing lines for backtests where licensing allows (NFL lines are in games.csv; for NBA find a licensed/open source, otherwise rely on forward tracking).

PHASE 2: LEDGER V2
Add fields: book and price taken, devigged market prob, anchor_source, anchor_fair_prob, model-only prob, blend weights, price_edge, model_edge, pick_phase, scenario_summary, availability_snapshot_id, trust_score, timing_recommendation, model_version, feature snapshot hash, stake units, closing odds, close_anchor_prob, CLV, clv_vs_sharp, units P&L. Add immutability tests. Report ROI/yield/CLV by league, edge type, edge bucket, book and pick phase.

PHASE 3: SHARP PRICE ANCHOR
- Tag price sources by type: retail, sharp, exchange, prediction_market. Check which sharp/exchange books the current The Odds API plan exposes and evaluate public prediction-market data (e.g. Kalshi, Polymarket). Verify availability, terms, fees and state legality. Ignore thin/illiquid markets and model fees.
- Devig (multiplicative, power, Shin; choose by historical calibration) into sharp_fair. Build the anchor as a weighted consensus with weights learned walk-forward. Fall back to the retail median when sharp data is missing and record which anchor was used.
- Replace the retail median in choose_candidates with the anchor. Split edges into price_edge (best retail price vs sharp_fair, no model involved) and model_edge (model vs anchor), and track them separately. price_edge is the more realistic source of +EV.
- Line shopping: best price per side, stale-line detection, and informational alerts for arbs, middles, steam moves and reverse line movement.
- Benchmark CLV against the sharp close.

PHASE 4: CROSS-MARKET CONSISTENCY
- Ingest spreads and totals (Odds API markets h2h, spreads, totals); plan and document the quota budget.
- Build spread_to_win_prob(sport, spread, total), calibrated on history. For NFL respect key numbers (3, 6, 7, 10) with empirical margin distributions, and account for the total's effect on variance.
- For every book compare moneyline-implied vs spread-implied devigged probability and flag gaps above a threshold. Test whether gaps predict outcomes or CLV, and use them as features and as a stale/mispriced-line detector.

PHASE 5: AVAILABILITY SCENARIO ENGINE
- Ingest official injury reports and game-day inactives (NBA report + inactives ~30 min pre-tip; NFL practice/game statuses + inactives ~90 min pre-kick; nflverse injuries/depth charts). Store the publish timestamp of every status change.
- Learn P(plays | status, days to game, player importance, team) with empirical-Bayes smoothing.
- Player impact: NBA minutes-weighted ridge RAPM/BPM-style ratings; NFL position-specific values including QB EPA/CPOE.
- Price each game as a mixture over top-K availability scenarios of key players (model correlations where supported). Output expected probability and its variance; feed variance into uncertainty and stake size.
- Flag news staleness (news newer than the latest odds snapshot) and poll odds faster in report windows.
- Pick phases: at most one pick per game per phase (early, post-inactives). Picks stay immutable; a later phase appends a new record. Evaluate phases separately, including whether waiting for news beats betting early.
- Optional: use an LLM to structure injury/news text into availability features, evaluated only on data collected going forward (an LLM may have memorized past outcomes).

PHASE 6: RATINGS AND FEATURES
- Elo v2: margin-of-victory multiplier, learned preseason regression, team-specific home advantage shrunk to the league mean, separate offense/defense ratings, and state-space (Kalman/Glicko-style) updates with per-team uncertainty replacing fixed K.
- Early season/roster turnover: replace the flat 0.75 carryover with a learned prior combining last-season rating, preseason market info (season win totals/futures converted to ratings, if licensing allows), roster continuity (minutes-weighted returning/incoming player ratings) and coach/QB changes. Learn weights walk-forward across past season starts. Higher uncertainty means more weight on the market anchor and smaller stakes. Report performance by games-played bucket vs market-only; if the model can't beat the market early, lean on the market and skip picks.
- Strength inputs: stabilization-aware regression to the mean (3P% heavily, turnover/rebound rates barely), luck adjustments (Pythagorean expectation, close-game record, turnover/fumble luck, opponent 3P%), garbage time stripped, NFL neutral-situation EPA and success rate, QB EPA/CPOE, pressure/sack rates, opponent and schedule adjustment, exponentially weighted rolling windows, and a margin-based training target (more information per game for NFL's small samples).
- Context: rest, back-to-backs, 3-in-4, travel distance and timezone, altitude, schedule density; motivation (clinched/eliminated, tanking, NFL Week 17-18 resting, playoff starter weighting); fatigue (cumulative minutes, snap counts, rotation habits); matchups (pace mismatch, 3-point volume vs defense, NFL pass rush vs offensive line). Test, don't assume: many are already priced in.

PHASE 7: OFFICIATING INTELLIGENCE
- Per referee (NFL) and per crew member/crew combination (NBA), compute shrunken estimates of: home win rate vs market expectation, margin vs spread, total vs line, pace, fouls/penalties per game, home-vs-away foul/penalty share, free-throw attempts, overtime rate, with splits by favorite/underdog, divisional, primetime, playoffs. Test team-by-referee interactions only if they survive holdout.
- Timing: NBA crews post around 9 AM ET and can change. Features are valid only if known at pick time; use an "unknown" flag otherwise and record assignment timestamps.
- Test (1) whether referee features improve out-of-sample log loss/Brier over a market-only model and (2) whether lines already move on assignment news.
- Output REFEREE_REPORT.md: every metric with n, effect, CI, adjusted p, holdout result and verdict (failed/candidate/promoted). The NFL analysis can start right after Phase 1 since the data is in games.csv.

PHASE 8: PATTERN FACTORY
Pre-register and test as one batch under FDR control: rest and travel effects; West Coast teams in early East games; altitude; schedule spots (lookahead, letdown, revenge, divisional); after blowouts/OT; NBA star rest and minutes restrictions, road-trip/home-stand game number, season-opening and in-season-tournament games; NFL QB changes, short weeks, Thursday/primetime, byes, wind/temp/dome/turf, coach tenure, turnover/red-zone/penalty luck regression. Include market-behavior patterns: line movement direction and velocity, reverse line movement, cross-book disagreement, favorite-longshot bias, popular-team overpricing, opener-to-close drift. Output PATTERN_REPORT.md including all failures.

PHASE 9: MODEL STACK
- Baselines: Elo v2 and elastic-net logistic.
- Gradient boosting (LightGBM/XGBoost/CatBoost) with walk-forward Optuna tuning and monotonic constraints where sensible.
- Margin-distribution model (quantile/distributional GBM or small NN, in the spirit of a Hugging Face model that outputs a probability for each spread from -20 to +20) that derives win probability; cross-check against the direct classifier. Also test joint models of moneyline/spread/total and optional possession/drive-level simulation to price scenario mixtures.
- NFL: hierarchical Bayesian team strength with a QB effect (PyMC/Stan); test TabPFN (pretrained tabular model on Hugging Face) as a small-sample challenger. NBA: lineup/minutes-weighted strength.
- Stack with the market: logistic on anchor logit + model logits, fit walk-forward. Calibrate per sport (isotonic/Platt) with reliability diagrams. Add uncertainty (bootstrap/conformal) and abstain when uncertain. Explain each pick with top drivers (SHAP/coefficients).
- Study these Hugging Face projects for ideas only: BraydenMoore/marci (NFL XGBoost), jashdoshi77/NBA_PREDICTOR (XGBoost+LightGBM+Elo), ThinkingRock/nba (spread-distribution model), cbratkovics/nba-game-logs (data). Check licenses before reusing code or weights, ignore their headline accuracy, and re-evaluate everything under our own walk-forward protocol.
- Model registry with weekly retraining and champion/challenger comparison.

PHASE 10: PICKS, TRUST FILTER, TIMING, BANKROLL
- Select by EV = p*decimal_odds - 1 at the best available price, requiring edge/EV above thresholds that exceed calibration error. Replace the hard 3/day cap with edge ranking plus an exposure cap.
- Trust filter, shadow mode first: log every candidate, including ones it would skip. Train a meta-model (start with regularized logistic or shallow GBM) to predict P(CLV > 0) and expected EV from edge type/size, anchor type, source agreement, time to start, line movement so far, model uncertainty, news staleness, games-played bucket, league, consistency flags and liquidity. Fit walk-forward, calibrate, and require a minimum sample before it can gate live picks.
- Timing: train a closing-line predictor and output "bet now / wait / skip" with expected CLV, evaluated in shadow mode.
- Bankroll: paper stakes at flat 1u and fractional Kelly (1/4) with per-bet and daily caps; correlation-aware sizing for same-slate bets; drawdown circuit breaker; Monte Carlo bankroll paths with risk of ruin.

PHASE 11: BACKTEST AND VALIDATION BAR
- Walk-forward backtest using odds available at pick time (never closing odds unless labeled), including vig, realistic limits and slippage. Report log loss, Brier, calibration, CLV, ROI/yield with bootstrap CIs, max drawdown and sample sizes against a matched-time market-only benchmark. Add a per-segment CLV dashboard, treating segment slicing as multiple testing. Write one report per model version in reports/.
- Pre-register in the README: no "validated" claim until at least 300 settled forward picks with mean CLV vs the sharp close positive (CI excluding zero) and calibration no worse than market-only. Show progress toward this bar in the UI.

PHASE 12: LIVE TRACKING AND MONITORING
Log every prediction immutably before game time, auto-grade, and compare running CLV/ROI to the backtest. Monitor drift (feature distributions, calibration decay) with alerts (Telegram/Discord optional) and reconcile data across sources.

PHASE 13: SITE (static on Vercel, mobile-first, fast)
Per pick: model vs anchor probability, price edge and model edge shown separately, EV, confidence, best book, "why" drivers, crew/referee context, injury scenario summary, trust score, bet-now/wait, early-season uncertainty banner, and a line-movement sparkline. Also: settled-pick history, equity curve in units, calibration chart, ROI/CLV by league and edge type, a research dashboard listing every pattern with n, effect, adjusted p and status, and validation-bar progress. Replace the hand-written dist/data.js with generated data or remove it. Keep and extend the disclaimers, add responsible-gambling messaging and optional personal limit reminders, and never imply guaranteed profit.

PHASE 14: ENGINEERING (throughout)
Retry/backoff and per-source failure isolation, structured logs, a versioned feature registry (every prediction reproducible), pinned requirements.txt with workflows updated, unit tests (devig methods, anchor fallback, spread_to_win_prob, scenario-mixture math, pick immutability, CLV), a leakage test suite across all features, recorded-fixture integration tests, CI, one-command local setup and a README architecture section.

ROADMAP HOOKS (design now, build later)
Spreads/totals/player props as bet markets, live in-game win probability, NCAA/MLB/NHL, same-game-parlay correlation modeling.

EXECUTION ORDER
0, 1, 2, then 3 and 4 (market-based, cheapest), then 5, 6, then 7-8 (NFL referee analysis can start right after Phase 1), then 9, then 10 in shadow mode once enough candidate history exists, then 11-12, then 13. Phase 14 runs throughout.

DELIVERABLES
AUDIT.md, PLAN.md, DATA_SOURCES.md, HYPOTHESES.md, PATTERN_REPORT.md, REFEREE_REPORT.md, reports/ for each module and model version, working code and tests per phase, and a final SUMMARY.md with what changed, honest numbers vs the market-only benchmark (CLV and ROI with CIs), known limitations, and the next 5 highest-impact steps.
