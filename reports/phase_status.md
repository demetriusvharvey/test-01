# Master-prompt phase status — October 29, 2026

This maps the newer 15-phase prompt supplied in the conversation, not the
older 14-phase docs/MASTER_PROMPT.md. Winner-only ranking, hidden probability
percentages, and removal of manual odds entry follow later user instructions.
Completed deployment and passing tests do not imply a completed prediction engine.

| Phase | Status against full specification | Verified work / remaining gap |
|---|---|---|
| Step 0: inspection | Complete | Existing architecture, workflows, sources, ledger and deployment inspected. |
| 1: free data pipeline | Partial | NBA/NFL scores, schedules and archives work. Verified pregame player roles, lineups, replacement data and historical timestamped odds are incomplete. |
| 2: NBA ML | Partial | Elo baseline and retrospective evaluations work. Calibrated, player-aware NBA ML is not trained or validated. |
| 3: NFL ML | Partial | Elo and position-status research path exist. All-position player contributions are not trained or active. |
| 4: injuries/player impact | Partial | Current reports, frozen position features, scenario math and player-exposure learner exist. Actual player coefficients, replacements, NBA lineup source and justified uncertain-status scenarios are missing. |
| 5: simulations | Partial | Seeded NBA scoring-unit and NFL drive simulators execute. They lost to Elo on exploratory samples and lack validated player inputs. |
| 6: ensemble | Partial | Calibration/blend research helpers exist. No learned ensemble has demonstrated improvement or been promoted. |
| 7: odds | Partial; scope changed | Attributed snapshots and payout/EV mathematics work. Full historical coverage absent; manual-entry UI intentionally removed. |
| 8: selection | Partial; scope changed | Odds-independent top-three winner ranking works per newer request. Full uncertainty-aware, injury-adjusted selection is not established. |
| 9: historical testing | Partial | Chronological Elo/simulator replays and prospective paired evaluation work. Historical injury/odds coverage, untouched tests and verified ROI are unavailable. |
| 10: automation/grading | Partial | Hourly capture, frozen forecasts, final grading and weekly research work. The complete player-aware model cannot yet run; no minute-level service is promised. |
| 11: website | Partial; requested UI deployed | Picks, history, accuracy, variables, compact slate and quotes work. Full real player-impact/simulation model outputs cannot be displayed as validated predictions. |
| 12: reliability/security | Implemented for current pipeline | Retries, source failures, validation, secret handling, immutable archives and CI work. New data integrations still require their own verification. |
| 13: improvement | Partial | Registry, scheduled training attempts and forward comparisons work. No challenger has earned production promotion; player source integration missing. |
| 14: tests | Partial against full specification | Existing implemented suite passes. Tests cannot verify missing live source integrations or establish predictive validity. |
| 15: deployment | Complete for current implementation | Static production site deployed on Vercel; GitHub CI and workflows verified after commits. |

No full-spec completion is claimed for a partial phase. The most important
unfinished work is verified player-level input integration and independent
evaluation, not additional UI polish. A new research training report records
eligible unique player-exposure games and failures rather than silently
pretending that the player learner has been trained.
