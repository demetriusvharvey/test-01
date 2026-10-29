# Odds-independent slate observations — October 29, 2026

The pipeline now records every eligible future NBA/NFL scheduled game in an
append-only SQLite archive on the existing data branch, independent of odds,
book counts, recommendation rank or EV. Each observation freezes the team
model, source hashes, neutral-site flag and available NFL position-status
features. A separate immutable outcome table accepts only finals already
qualified by the pipeline. The weekly position-model loader consumes these
rows after the corresponding result is observed; it still applies all
time-ordering, source and minimum-sample training checks.

This removes sportsbook-coverage selection from future training collection.
It does not retroactively reconstruct pregame injuries or add historical
games to the public selected-winner record. Missing history and unconfirmed
NFL venues are rejected; missing injury features remain null. Injury effects
are still not included in the current public Elo probability.

The archive also feeds pure statistical-model training and paired challenger
evaluation. Future challenger predictions are recorded for eligible scheduled
games without odds. Saved game counts support the existing logistic/boosting
features. An integrity fixture verifies an unpriced NFL game from frozen
inputs through a later confirmed final and matched-time challenger Brier
comparison. Conflicting observed outcomes are excluded. This does not
establish a successful model or authorize its promotion.

152 local tests passed, including unpriced-game persistence, duplicate
idempotence, immutable storage, confirmed-outcome joins and blocked history.
The complete master specification remains open for player-level replacement
effects, NBA pregame injury coverage, verified historical odds and independent
future model validation. Those requirements are not certified by these tests.
