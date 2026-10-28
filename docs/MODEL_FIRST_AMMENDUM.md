ADDENDUM: MODEL-FIRST MODE (overrides docs/MASTER_PROMPT.md where they conflict)

GOAL
The model, not the market, decides the picks. Build the strongest market-independent predictor possible and prove with data whether it beats the market. All earlier RULES still apply (point-in-time features, walk-forward only, no fabricated results, no auto-betting, licensed data only, no demographic features).

1. PICK ENGINE
- Remove the 75/25 market blend and the median-market "fair probability" from pick selection.
- The pure model (no odds-derived inputs: no market probability, line movement, spreads or totals as features) outputs p. EV = p * decimal_odds - 1, computed at the best available price. Odds are used only to price the bet, benchmark the model, measure CLV, and run guardrails.
- Keep the market-aware model (fitted blend with the sharp anchor) as a shadow challenger, not as the engine.

2. MAKE THE PURE MODEL AS STRONG AS POSSIBLE
- Train on all available history (10+ seasons), since it needs no odds data.
- NBA: player-level, injury-adjusted lineup strength (minutes-weighted RAPM/BPM-style ratings), rest/travel/schedule, pace and matchup features, margin-distribution outputs.
- NFL: QB-adjusted EPA/CPOE, neutral-situation efficiency, pressure rates, injuries, weather, rest, coaches, hierarchical Bayesian team strength.
- Elo v2 with margin of victory, learned preseason regression, and per-team uncertainty. Availability-scenario engine for injuries. Walk-forward hyperparameter tuning with nested validation. Ensembles (gradient boosting, regularized logistic, Bayesian, TabPFN challenger) and per-sport calibration. Pre-registered pattern features (referees, schedule spots, etc.) only after they pass the FDR and replication rules.
- Output a calibrated probability plus uncertainty for each game.

3. DISAGREEMENT GUARD (the main way model-first systems lose money)
- When the model and the market differ a lot, the model is usually missing information. Build a disagreement calibration curve: actual win rate by bucket of (model p minus market fair p), fitted walk-forward.
- For gaps above a learned threshold, run an automated missing-information check (late injury/lineup news, QB or key-player status, weather, data errors) and log the result. Bet such games only if the check is clean and the curve shows large gaps historically win. Otherwise paper-only.
- Cap stake size as a function of disagreement size and model uncertainty.

4. HEAD-TO-HEAD EXPERIMENT
- Run three arms on the same games at the same timestamps: A) pure model, B) fitted model+market blend, C) market-only (devigged sharp anchor).
- Pre-registered decision rule: arm A is allowed to drive real-money staking only in leagues/segments where, on walk-forward holdout data, it beats arm C on log loss (paired test, e.g. Diebold-Mariano) AND has positive mean CLV vs the sharp close AND a bootstrap ROI CI is not clearly negative. Everywhere else it stays in paper mode. Segment slicing is multiple testing: apply FDR correction.
- Report the Brier skill score of A vs C by league, month, and games-played bucket.

5. APP CHANGES
- Picks show the model's probability and EV as the headline, with market price shown as context.
- Add a live scoreboard: model vs market log loss, CLV, and ROI with CIs, plus a verdict per league ("model ahead / market ahead / inconclusive").
- Status badge per pick: Staking (segment proven) or Paper (segment unproven).
- Keep the disclaimers and the validation bar: no "validated" claim before 300 settled forward picks with positive CLV (CI above zero).

DELIVERABLES
reports/model_vs_market.md (all arms, all segments, including losses) and an update to SUMMARY.md with plain-language findings: where the model beats the market, where it doesn't, and what to improve next.
