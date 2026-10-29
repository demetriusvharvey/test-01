# NBA player features and injury integration

This implements the NBA portion of the Phase 4 player-feature pipeline and
connects it to Phase 2 model training and Phase 9/10 evaluation. It does not
complete the full NBA/NFL player-impact specification.

The independent multi-stat logistic model has 27 features: fourteen team
features, three rotation features and ten projected box-stat differences.
Player inputs cover assists, turnovers, offensive/defensive rebounds, steals,
blocks, field-goal attempts, three-point attempts, free-throw attempts and fouls.
The learner fits their coefficients; no manual injury penalty is introduced.

Training and live scenarios share projection definitions. Each player uses up
to ten earlier same-team appearances. Historical membership is inferred from
an earlier appearance within 21 days. Rotations have at most twelve players,
at least eight with history, 240 total minutes and a 48-minute player cap.
Current membership comes from the captured roster; listed confirmed absences
are removed and uncertain-player states are enumerated independently. No
unsupported participation probabilities or scenario mixture are fabricated.
Missing player metrics withhold the multi-stat forecast instead of becoming
zero. Source freshness and identity checks remain mandatory.

H023 was committed before the archive comparison. Team-only, scoring-rotation
and multi-stat models are evaluated on identical later-season games, using
older training and a separate previous-season calibration. Results, sources,
input hashes, coefficients and artifacts persist on the data branch. The
calendar-day paired log-loss tests use a fixed seed and BH correction over
all reported H023 seasons. The archive was previously inspected, so this is
exploratory evidence, not untouched confirmation.

The hourly forward grader separately tracks each conditional model's earliest
eligible pregame winner. All scenarios must choose the same team; otherwise
the game is an abstention. Confirmed finals alone determine wins and losses.
Repeated updates do not multiply games or select a better-looking revision.
No Brier score is assigned to an unweighted scenario range. This record is
separate from the site's current Elo winner record and never rewrites it.

Remaining Phase 4 gaps: verified historical availability, confirmed lineups,
complete defensive/causal player values, validated replacement effects,
supported scenario weights and NFL all-position player-value integration.
Box-score events do not measure every defensive contribution. Source-use
qualifications remain unresolved for broader NBA wagering deployment. No
public-model promotion or profit claim follows from this implementation.


H023 has now run on 114,003 played-player rows and 4,758 identical matched
modeling examples. The extra statistics did not consistently improve later
results. The model remains separate from public picks. H024 follows this
negative result explicitly: a convex ensemble learns weights from earlier
held-out component predictions and is evaluated in a subsequent season.
Weights never come from the season being scored. Related H023/H024 day-block
tests receive a joint multiple-test adjustment. Conditional ensemble outputs
require aligned injury scenarios; an ensemble using only team/Elo inputs is
explicitly marked team-only.
