# NBA logistic baseline protocol

The fixed score-based logistic learner uses earlier-day Elo difference,
20-game average points scored/allowed differences, win-rate difference,
rest difference and home court. Teams need ten earlier games. NBA K=20,
home advantage=55 and season carryover=.75 are fixed. All same-day features
are frozen before any results from that date are applied.

For each eligible test season, train on seasons older than the immediately
preceding season, calibrate with Platt scaling on that preceding season,
then score the later season. Fixed ridge penalty .1 and 200 training epochs;
calibration uses 300 iterations. Compare logistic, calibrated logistic, Elo,
home-team and uninformative baselines on the same games. Store accuracy,
Brier, log loss, reliability bins, feature definitions and coefficients.
No threshold tuning, model selection or production promotion uses test results.

This archive has been inspected already; the results are exploratory,
chronological retrospective comparisons, not untouched verification.
Historical injury/lineup inputs, NBA source-use qualification and matched
market odds are absent. Full Phase 2 remains incomplete regardless of result.
