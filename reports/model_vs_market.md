# Model versus market — prospective paper study

## Status

**Inconclusive. No model has been shown to beat a market or to earn money.** The original ledger contains legacy blended-model predictions; those are retained as originally recorded and are not relabeled pure-model results. New selections use a market-independent team Elo estimate and are marked paper-only. No wagers are placed, and no user wager or actual profit is assumed.

## The three requested arms

| Arm | Implementation and current evidence |
| --- | --- |
| A: pure model | Game-result-based Elo, home advantage and neutral-site handling. Odds do not enter the forecast; current book prices are used only to calculate estimated EV and select a paper candidate. Rest and scoring-margin additions remain disabled. This is a baseline, **not** the requested fully built injury-adjusted ensemble and not yet calibrated. |
| B: fitted pure model + sharp anchor | A walk-forward, regularized logistic-fit utility is present in `scripts/line_lab/calibration.py` for shadow research. It requires at least 500 unique, settled prior sharp-anchored games by default, strict pregame and settlement timestamps, and produces a non-promoted model. No qualified sharp data exist; no fitted result is claimed or used. |
| C: no-vig sharp market-only | Not available. AgentBets and The Odds API share upstream data, and the available retail median is not a verified sharp anchor. Retail-market log loss and Brier skill, when settled prospective games arrive, are descriptive references only and cannot satisfy the sharp benchmark or staking gate. |

The system records paired model and retail-reference forecasts at the same pregame timestamp, with model inputs and book observations; the first forecast for each game is chosen before looking at outcomes. Final outcomes are appended separately. A legacy fixed 75:25 retail blend is retained only as a labeled reference; it is not the amendment's fitted sharp-blend arm. No previously generated prediction is relabeled.

## Evidence and limitations

- Matched-time sharp comparisons: **0**; model-vs-sharp log loss, Brier skill and paired p-value: **unavailable**.
- Sharp closing-line value: **unavailable**. A last observed retail quote is not a sharp close, and no estimate is substituted.
- The first post-deployment run recorded 12 prospective NBA game forecasts and no confirmed outcomes; these are forecasts for the comparison study, not 12 selected bets. There were no settled pure-model paper selections at that checkpoint, so ROI and its interval are **unavailable**. Later ROI is calculated from one hypothetical unit per recorded model selection, using the recorded initial best available price; it is not a user's actual return.
- The guard records the retail/model gap but has no trained disagreement curve, independent sharp anchor, or point-in-time injury, lineup, quarterback and weather checks. These are explicitly unknown. The current real-stake cap is zero; every new selection is paper-only.
- NFL team ratings use the available historical game results since 2010. The available licensed NBA team-game files cover five seasons including one incomplete season, not the requested 10+ completed seasons. NBA player-level lineup data and a suitably licensed, timestamped availability feed are not established. NFL play-by-play, injuries, depth charts and snaps have been backfilled as retrospective assets but are not yet model inputs. A daily shadow collector records timestamped quarterback EPA/CPOE summaries from previously completed games. It does not infer a confirmed starter, does not adjust for opponent, and does not alter the live prediction.
- Platt calibration, a fitted sharp-blend utility and a game-day-block parameter-bootstrap helper exist for shadow research with minimum data gates, but no promoted fit or uncertainty interval has been validated. Raw Elo estimates shown by the site are explicitly labeled uncalibrated.
- Paired day-block permutation and Benjamini–Hochberg helpers exist, but no qualified sharp-market test has run. A truly untouched final confirmation cohort, nested tuning, required replications, a trained disagreement threshold, and the statistical staking decision remain incomplete. The [preregistration](../HYPOTHESES.md) is a plan, not a result. No segment is approved for staking.

The scoreboard labels its reference as retail, includes sample counts, and refuses to draw a model-ahead/market-ahead verdict without the required evidence. Its game-day-block bootstrap interval is shown only after at least 30 paper picks across 10 game days; it is exploratory, not proof of profit. A day-block sign-permutation test assumes within-day label exchangeability; its adequacy and the effect of serial dependence must be reviewed before relying on a p-value. Every H004 check, including insufficient-data and computational-failure states, is appended to the data branch with an input hash.
