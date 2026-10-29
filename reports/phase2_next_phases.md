# NBA engine: connected-phase implementation — October 29, 2026

## Implemented and exercised

- Phase 4 / NBA player features: ten additional projected box-stat features,
  current roster/injury scenarios, independent uncertain-player combinations,
  shared training/live minute allocation and missing-data rejection.
- Phase 6 / statistical ensemble: nonnegative weights learned from earlier
  held-out component predictions, then scored in a later season. Required
  injury components must have aligned scenarios and observation timestamps.
  Market/simulator inputs remain excluded; this is not the full hybrid model.
- Phase 9 / historical evaluation: identical matched-game comparisons,
  earlier-season training/calibration, preregistered H023/H024 hypotheses,
  calendar-day paired testing and joint multiple-test correction.
- Phase 10 / forward tracking: immutable pregame scenarios and separate
  model-specific winner records. Scenario disagreement is an abstention;
  confirmed finals alone produce results. No probability is invented for an
  unweighted availability range, and the site's Elo record is not rewritten.
- Phase 12 / model integrity: nonfinite learned coefficients, means, scales
  and calibration terms are rejected instead of producing misleading output.

## Actual archive results

SportsDataverse player archive: 114,003 parsed played-player rows across five
season files. H023 matched cohort: 4,758 modeling examples; the test seasons
contain 1,209, 1,209 and 52 games respectively. The remaining examples supply
older training and calibration. Historical membership/availability remains
inferred/unknown; these are not archived pregame injury reports.

| Test season | Games | Elo Brier | Scoring-rotation Brier | Multi-stat Brier | Ensemble Brier |
|---|---:|---:|---:|---:|---:|
| 2024-25 | 1,209 | 0.21389 | 0.20957 | 0.21089 | Not eligible: no earlier held-out component cohort |
| 2025-26 | 1,209 | 0.20848 | 0.20478 | 0.20478 | 0.20499 |
| 2026-27 partial | 52 | 0.21432 | 0.22669 | 0.22943 | 0.22702 |

Lower Brier is better. H024 ensemble log loss in 2025-26 was 0.59668 versus
Elo 0.60505; paired raw p=0.00840, joint H023/H024 BH p=0.02520. In the
partial current season it was worse: 0.63744 versus Elo 0.61360. That small
sample lacks enough dates for the registered day-block significance test.
These already inspected archives are exploratory, not independent confirmation.
No betting ROI, true win chance, or profitable edge is established.

Latest ensemble weights fitted from 2,418 earlier component forecasts:
70% scoring-rotation logistic, 30% multi-stat logistic, 0% team logistic,
0% Elo. These weights were chosen before scoring the 2026-27 sample; they
are retained as research despite its negative result. No optimistic test
season was chosen to justify a public switch.

## Live operation and verification

The research workflow successfully trained the new artifacts and exercised
all 55 upcoming NBA forecasts. Today’s three games passed current roster /
injury checks; all 55 ensemble scenario calls succeeded. Forecasts retain
model hashes, feature values, input times and explicit limitations. Hourly
runs persist observations to the existing data branch, and the weekly job
repeats the registered training/evaluation workflow without paid services.

183 automated tests pass locally and in CI. Tests cover same/future-date
leakage, shared historical/live features, non-scoring injury effects,
minute conservation, missing metrics, earlier-only ensemble weights,
scenario alignment, immutable earliest-forecast grading and invalid models.
The static site was preserved; no UI rebuild or new paid infrastructure was
introduced. Public picks still use Elo. The new forward records begin with
pending games, not manufactured wins.

## Remaining full-spec gaps

Full Phases 2, 4 and 6 are not declared complete. Missing items include
verified historical pregame availability, confirmed lineups, complete
defensive/causal player values, validated replacement effects, supported
availability mixture weights, NFL all-position player-value integration and
consistent independent forward evidence for a public model replacement.
NBA source-use qualifications remain unresolved for broader wagering use.
The statistical ensemble does not include a validated simulation/market blend.

Detailed generated reports: nba_player_box_validation.md,
nba_ensemble_validation.md and nba_inference_verification.md in this directory.
Training and evaluation artifacts persist under observations/nba_player_box
and observations/nba_ensemble on data/observations. Forward comparison and
conditional winner records persist in
observations/nba_ml_predictions/forward_evaluation.json.

## Main code changes

Created: scripts/line_lab/nba_player_features.py,
scripts/line_lab/nba_ensemble.py, scripts/research_nba_player_features.py,
scripts/research_nba_ensemble.py, tests/test_nba_player_features.py,
tests/test_nba_ensemble.py and reports/nba_player_method.md.

Updated: the NBA rotation, lineup, scenario, inference and forward-grading
modules; runner; statistical research/export and verification scripts;
weekly-research workflow; hypotheses/source/phase documentation; and NBA
inference/forward tests. Generated evaluation reports are committed by the
research workflow, while artifacts/immutable observations persist separately.
