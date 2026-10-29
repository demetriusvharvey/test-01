# NBA lineup/replacement engine progress — October 29, 2026

## Implemented

- Free, cached SportsDataverse/ESPN play-by-play imports for 2021-22 through
  the partial 2026-27 season, with source hashes and retrieval timestamps.
  Parquet keeps individual downloads below 35 MB. No paid service is enabled.
- Strict first-quarter reconstruction from source starters/substitution IDs.
- Separate regulation-game reconstruction: initial lineups must be uniquely
  determined from source actions, replayed substitutions must remain valid,
  and every player's total minutes must match the rounded box within 1.1 min.
  Overtime/ambiguous games are excluded, never guessed.
- Ridge player associations controlling observed teammates/opponents, with
  separate earlier training, previous-season penalty selection and later test.
  Low-sample training participants remain nuisance controls. Published player
  effects require 120 actual training minutes.
- Conditional replacement analysis at projected minutes. An unknown player's
  value stays unknown; a missing all-available counterfactual produces no
  replacement delta. Ratings are observational, not causal injury effects.
- A strictly season-frozen lineup feature in the NBA outcome pipeline (H027),
  and a separate missingness-aware alternative (H028) preserving the measured
  supported component and each team's coverage. Neither fills individual
  unknown effects with zero or claims a partial component is total strength.
- Separate lineup-research scheduling and owned data paths, preventing daily
  jobs from canceling queued lineup training. Bounded rebase/push retries
  preserve disjoint observations. Public winner records are not rewritten.
- Live listed-player history checks: an assumed-available listed player with
  no role history withholds the projection instead of disappearing silently.

## Actual data and evaluation

The five recent source files supplied 20,410 accepted first-quarter stints.
Full-game reconstruction plus the 2021-22 warm-up supplied 15,987 accepted
stints in 546 regulation games across six season files. This is selective
coverage, not a claim that every NBA game's lineup can be reconstructed.

H025 fitted a first-quarter candidate with 522 supported player coefficients
and 303 unpublished nuisance controls. It did not establish a useful held-out
advantage over the league baseline. H026's strict full-game stint comparison
lacked the required matched validation coverage. All insufficient-data and
negative results remain recorded.

H027 produced only six complete-case game examples, so no outcome model was
fitted and no training threshold was lowered. H028 retained 4,758 matched
games by separating the supported component from coverage. Mean supported
projected-minute coverage was 74.21% home and 74.09% away; only six examples
had complete coverage. The remaining player effects were not imputed.

| Test season | Games | 27-feature Brier | 30-feature Brier | Elo Brier |
|---|---:|---:|---:|---:|
| 2024-25 | 1,209 | 0.21045 | 0.21065 | 0.21389 |
| 2025-26 | 1,209 | 0.20485 | 0.20598 | 0.20848 |
| 2026-27 partial | 52 | 0.22760 | 0.22909 | 0.21432 |

Lower is better. The new inputs did not improve Brier or log loss over the
matched 27-feature baseline in any tested season. H028's joint adjusted
log-loss p-values were 0.90101 and 0.42646 for the two full test seasons;
the partial season lacked enough dates for the registered test. These are
exploratory results from already inspected archives, not independent proof.
The public picks continue using Elo. No historical gambling ROI is computed.

## Verification and phase status

199 tests pass locally. The suite covers lineup membership, score/time
conservation, rejection of ambiguous/overtime games, per-player minute checks,
unknown-value handling, season leakage, partial coverage, conditional scenarios
and nonfinite model rejection. CI and the daily workflow verify repository
integration; latest workflow outcomes are visible in GitHub Actions.

This advances Phases 1, 4, 9, 10 and 12 and connects a trained 30-feature NBA
candidate to Phase 2. It does not complete the full NBA/NFL specification or
establish a better public winner model. Verified historical injury snapshots,
confirmed current starting lineups, complete defensive/causal replacement
values, NFL all-position player values and independent forward confirmation
remain missing. NBA source-use qualifications remain documented separately.
A missing predictor is reported, not replaced with a fabricated probability.

Generated reports: nba_lineup_validation.md, nba_full_lineup_validation.md,
nba_stint_feature_validation.md and nba_partial_stint_validation.md.
Artifacts and original/failed comparisons persist under observations/nba_lineups,
observations/nba_full_lineups, observations/nba_stint_features and
observations/nba_partial_stint_features on data/observations.
