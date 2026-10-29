# Phase 2 NBA model checkpoint

The historical team-feature statistical model is now trained and calibrated,
and an actual sklearn gradient-boosting comparison has been evaluated.
On 1,225 games in 2024-25, calibrated efficiency logistic Brier was 0.2104
versus Elo 0.2139; 2025-26 was 0.2077 versus 0.2092 on 1,225 games.
The partial 2026-27 sample (52 games) favored Elo: 0.2110 versus logistic
0.2186. Histogram gradient boosting did not improve on the logistic model.

The protocol fixes configuration before testing, trains on older seasons,
calibrates on a distinct later season and scores the following season.
Artifacts include feature order, learned model and calibrator, season ranges,
input hashes and missing-input metadata. No public model is automatically
replaced. These seasons were already inspected, not untouched confirmation.

Full Phase 2 remains incomplete: player values, projected minutes, lineups,
replacement effects, verified upstream NBA wagering-use permissions and
independent future confirmation have not been supplied or established.
The code cannot honestly manufacture these inputs. Team-level improvement
does not establish an injury-adjusted model, a wagering edge or future accuracy.
