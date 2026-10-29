# NBA daily winner selection: H029 implementation

This connects the prediction engine's evaluation to the requested daily shortlist
objective. It advances the selection, backtesting and forward-tracking components
without changing the site's existing Elo picks or historical record.

The historical comparison uses chronological held-out probabilities for four
models: fixed Elo, 14-feature team logistic, 27-feature player logistic and
30-feature coverage-aware logistic. Each ET date must have predictions for
every NBA game in the archived results slate. Incomplete dates are reported
and excluded as whole dates. This does not verify the archive against an
independent historical schedule. Models rank their own up-to-three winners;
50/50 estimates abstain. No sportsbook odds or wager profitability is involved.

The report includes selected-game accuracy, Brier/log loss, calibration bins,
seeded whole-day accuracy intervals, paired day tests and related-test BH
adjustments. Fixed 0.50/0.60/0.70/0.80 coverage curves are descriptive; no
threshold is selected because it looks best in the test seasons. The archive
was already inspected, so these remain exploratory comparisons. Historical
availability was inferred/unknown; this is not a historical injury backtest.

Actual complete-date primary results:

| Season | Dates | Selected per model | Elo | Team 14 | Player 27 | Lineup 30 |
|---|---:|---:|---:|---:|---:|---:|
| 2024-25 | 159 / 162 | 466 | 73.82% | 75.54% | 76.82% | 75.75% |
| 2025-26 | 160 / 163 | 475 | 76.63% | 76.84% | 77.05% | 76.84% |
| 2026-27 partial | 6 / 9 | 18 | 72.22% | 72.22% | 88.89% | 88.89% |

The candidate-versus-Elo differences were not statistically confirmed after
related-test adjustment. Eighteen selected games are insufficient for the
registered uncertainty calculation; 16/18 is not an established 89% forward
accuracy rate. No public promotion or profit claim follows from these results.

The forward policy is separate from that historical proxy. It freezes the
first usable daily decision per model. It considers only NBA games still more
than five minutes away on the current ET date, requires complete model coverage
of that eligible slate, and selects up to three scenario-consistent winners.
Conditional models rank by the minimum of the selected team's listed scenario
probabilities; that is not a confidence interval or a weighted availability
estimate. A valid disagreement is an abstention. A missing/stale report is an
unavailable source that may be retried, not a losing prediction or forced zero.

Each decision saves a matched Elo selection from the identical snapshot, input
prediction hashes, model/policy versions and timestamps. The immutable decision
store rejects updates/deletes. Persistent attempts record missing-data days,
so outages cannot quietly vanish from coverage reporting. Original predictions
and the site's separate winner ledger remain unchanged.

Grading reads only the existing qualified confirmed-final store. Pending games
stay pending; ties are neutral/void winner outcomes, not betting losses. Paired
accuracy differences use only dates whose model and matched-Elo selections
have completely settled. An early single final cannot create a premature
paired lead. The 300-settled-game review floor is a review trigger, not evidence
of validity and not permission to deploy. No automatic promotion is performed.

Artifacts: observations/nba_winner_selection/<source hash>/evaluation.json and
observations/nba_ranked_forecasts/<ET day>.sqlite plus evaluation.json on the
data branch. Root modules are nba_winner_selection.py and nba_ranked_forward.py;
research runs through the existing zero-cost lineup workflow. Daily capture
and grading run through the existing pipeline. No UI rebuild or paid API.
