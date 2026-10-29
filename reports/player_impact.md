# Player-exposure learner — October 29, 2026

The repository now includes a regularized logistic player-exposure learner
for NBA or NFL research. It estimates associations above a frozen baseline
probability using verified pregame expected participation shares, signed by
home/away team. Player/team identity is validated against the supplied frozen
roster. It requires three seasons, 500 earlier training games, 100 later
validation games and 20 training appearances per estimated player by default.
The penalty is selected on the later season, without refitting the artifact
on that season's outcomes. This is validation, not an untouched final test.

This is a repository-side learning component, not an operational source
integration. No qualifying real player-exposure dataset has been supplied,
no real player coefficients have been trained, and no live picks use it.
Archived postgame snap counts, team box scores and aggregate injury counts
cannot substitute for historical pregame projected roles. Underlying source
permissions and stable player IDs must also be verified. Replacement-player
and causal effects are still unestablished. The component refuses unknown
nonzero player exposures rather than assigning zero value.

155 tests pass. Synthetic tests verify future-data rejection, roster
alignment, rejection of postgame participation, chronological validation
and unknown-player handling. They are not a predictive-performance result.
