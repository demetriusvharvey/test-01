# NBA Phase 2 inference checkpoint — October 29, 2026

Actual trained model artifacts now produce timestamped calibrated probabilities
for real upcoming NBA games, separately from the public Elo winner ledger.
The research workflow verified artifact loading, feature construction and
immutable forecast persistence on the actual slate. Each record includes
model/version and input hashes, model export time, input observation time,
missing-input flags and uncertainty. Predictions cover only the next eight
days. Final same-game scores and minutes never enter their own features.

The statistical-model training-to-inference component is operational.
165 tests pass. This is not a declaration that the complete player-aware
Phase 2 specification is finished: the live injury/roster join has not been
verified and incorporated into calibrated forecasts; replacement/defensive
player effects remain unvalidated. No public winner is silently switched.
The inference uses the team-efficiency logistic model, not a player-aware
model or the exploratory rotation model.
