# NBA Phase 2 inference checkpoint — October 29, 2026

The team-efficiency logistic and rotation logistic artifacts now produce actual
immutable pregame forecasts. Each includes version/input hashes, export and
observation times, missing inputs and uncertainty. The live roster/injury join
was verified on all three games in the October 29 acceptance run.

The injury model now enumerates independent availability combinations for each
listed uncertain player (up to six players / 64 scenarios). Confirmed out
players are excluded in every scenario. Both teams can have opposite or mixed
availability. Above the compute bound, or with stale/unmatched data, it returns
an explicit unavailable status instead of an incomplete range. An unchanged
winner across the scenarios is recorded; a winner reversal remains unresolved.
The resulting range is conditional sensitivity, not a confidence interval.
Unlisted players are assumed available only inside these labeled scenarios.

The hourly pipeline now grades the earliest eligible saved team-model forecast
against its paired pregame Elo probability. Only explicitly confirmed finals
from the existing result qualification pipeline are accepted. Repeat runs do
not add games, tied scores are flagged, schedule/identity mismatches are
excluded and conflicting confirmed finals fail rather than silently rewriting
a result. Archived older forecasts without a saved baseline are excluded.
Results persist in observations/nba_ml_predictions/forward_evaluation.json and
an immutable confirmed_outcomes.sqlite on the data branch.

175 tests pass locally, including mixed injury scenarios, winner reversal,
compute limits, first-forecast selection, paired metrics and idempotent grading.
Current-season team statistics, player boxes and rosters now refresh inside
the daily pipeline with a 12-hour success cache, a 3-hour failure backoff,
bounded requests and schema checks. No completed season is redownloaded.
Successful reobservations of unchanged roster content have separate immutable
receipts; the original content archive is never rewritten. A failed refresh
cannot make a stale roster look fresh.

Public picks still use Elo. The new models have not earned promotion: recent
retrospective performance did not consistently beat Elo, forward sample size
is not yet established, and verified defensive/replacement effects are absent.
No new player-impact coefficients or unsupported participation weights were
invented. Full Phase 2 remains incomplete on those substantive requirements.
