# Execution plan

The ordering below follows `docs/MASTER_PROMPT.md`. Complete and test one phase, commit it, and report before the next. Phase 14 safeguards are incorporated throughout. No automatic bet placement, paid service, account creation, or display of per-pick model probabilities is authorized by this plan.

## Step 0 — audit and preregister (this commit)

Record the actual baseline and ten material weaknesses, evidence/rights, assumptions, protocol and untested hypotheses in `AUDIT.md`, `DATA_SOURCES.md`, `HYPOTHESES.md` and this plan. Existing rest/form analysis was exploratory and does not become a preregistered result retroactively.

## Phase 1 — collect reproducible source data

1. Split the monolithic script into an importable package with compatibility wrappers and tests. Keep the established market selection behavior except for explicitly documented fail-closed source-quality and research-protocol controls; never rewrite old predictions.
2. Use date-partitioned SQLite files on a separate Git data branch for append-only, point-in-time odds snapshots. Store provider, raw and normalized IDs, market, both sides, source update time, observed time and game start. Keep observations after a start out of the pregame store, preserve raw provenance, deduplicate idempotently and select a clearly labeled **last observed pregame** quote, not a certified or sharp close. Warn when the scheduler or source leaves an excessive gap. Keep large research backfills out of the source/production branch.
3. Integrate The Odds API only if an existing `ODDS_API_KEY` is present, limit requests for the free plan, record quota metadata without secrets, and treat disagreement as a quality issue. A missing key must not be described as an active second source. Obtain no account, subscription or credentials on the user's behalf.
4. Add strict tests and realistic fixtures for both sources, duplicate and missing sides, stale/future/naive timestamps, event matching, start times and source disagreement. A missing or invalid required input suppresses a candidate; no invented prices or timestamps.
5. Preserve every NFL schedule column including odds, roof, surface, weather, referee, rest, coaches and QB. Catalog/ingest properly licensed nflverse play-by-play, injuries, depth charts and snap counts without asserting that a historical revision was known pregame. Store source manifest, retrieval time and content hashes; gate unverified source rights. Keep retrospective scores and prices separately labeled and never claim these are pick-time prices.
6. Capture the five available BoxScore Lab team-game seasons with dated attribution; document incomplete seasons, NBA upstream rights, and which summaries are not complete player-level box scores. Preserve NBA official crew *first observed* time and changes; historical officials/injuries require a separately authorized/licensed source, and their historical public timestamp is unknown unless evidenced. Do not use them as features.
7. Mark historical NFL schedule moneylines as retrospective lines of uncertain timing until source documentation proves they are closes. Do not backfill NBA odds or official availability using unsupported timestamps. Investigate free licensed sources; record concrete blockers instead of fabricating data.
8. Suspend live promotion of the pre-existing exploratory rest/form additions until the master-prompt gates are met; keep them in research/shadow code and preserve the public record. The two-period check alone is not enough to promote them. Document the operational change.

## Next phases — do not start without the requested checkpoint

- **2:** backward-compatible immutable ledger v2, actual price/book, phase, provenance and separately recorded closings; reporting with samples and intervals.
- **3–4:** licensed sharp/exchange anchor and cross-market consistency, all shadowed and benchmarked.
- **5–8:** availability, ratings, officiating and preregistered pattern research with time-of-knowledge controls, shrinkage and FDR.
- **9–10:** walk-forward model challengers, calibration, uncertainty, trust/timing and paper bankroll; no automatic wagering.
- **11–12:** precommitted forward validation, monitoring, drift and reporting.
- **13:** only user-approved UI changes; retain the user's earlier instruction to hide individual model-chance percentages unless they expressly change it.

## Validation standard

Preregister hypotheses before new tests, log every run including failures, apply Benjamini–Hochberg adjustment for the defined family, require two independent replications and a truly untouched later confirmation, and compare against a matched-time market-only benchmark. Existing previously inspected seasons are not an untouched final holdout. No profitability or validation claim until the Phase 11 forward bar is achieved.

## Model-first amendment — requested after Phase 1

The newly requested `docs/MODEL_FIRST_AMMENDUM.md` overrides the legacy 75:25 live decision formula. Preserve the original immutable record, create pure-model paper selections using odds only to price them, and log timestamp-matched pure/retail-reference shadow forecasts. A genuinely sharp anchor and fitted model+sharp challenger must remain unavailable until licensed data and walk-forward training exist. Keep the pre-registered gates above in force. Existing exploratory models or future source files are not automatically eligible for staking, and no automatic bet placement is added. Historical NBA coverage is under ten completed seasons; player-level NBA lineup and time-stamped injury/official sources remain missing, so a complete amendment implementation cannot be claimed without those inputs. Do not label uncalibrated Elo probabilities as calibrated.
