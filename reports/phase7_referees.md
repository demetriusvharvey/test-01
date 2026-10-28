# Phase 7: officiating research

The [referee report](../REFEREE_REPORT.md) summarizes all 20 referees with an eligible 2021–2025 NFL regular-season sample from the saved retrospective schedule asset, including sample sizes and partially pooled home-win rates with approximate intervals. It records the asset hash and retrieval date and labels the associated moneylines as timing-unverified. No causal claim, point-in-time backtest, adjusted p-value, season replication or holdout is asserted.

Code can select an NBA crew only if the exact game/date and assignment were observed before the prediction, and can compute a shadow shrunk market residual only from prior time-stamped assignments, market observations and confirmed outcomes. Missing assignments remain unknown. Synthetic tests verify those gates. No officiating input changes the active model or authorizes a bet.

The requested NBA historical crews and injury data, NFL play-by-play penalty splits, game-level foul rates, pace/total effects, team/referee interaction analysis and independent market validation are not complete. Historical schedule records may identify the actual official after a game; they do not establish that the official was known at the pick time. H009 is not yet testable under the preregistered protocol.

For current NBA picks, the board may now display the exact crew from the official game-day page when the current page date and unambiguous away/home teams match and the page was observed before tipoff. It displays the observation time and warns that assignments can change. A missing, stale, ambiguous or unavailable report remains unconfirmed; NFL crews remain unconfirmed. The names are context, not a model input or an estimated referee tendency.
