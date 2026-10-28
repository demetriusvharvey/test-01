# Hypothesis registry

Registry opened during Step 0. Existing rest/form tests were exploratory and were run before this registry existed; none of their results is a preregistered finding or a final holdout. Do not rewrite this history. All new hypotheses and analysis choices must be committed before testing.

## Protocol

Specify population, point-in-time inputs and missingness, direction, baseline, outcome, metric, testing family, sample and seasons before running a test. Use chronological walk-forward evaluation; select and tune only within prior windows. Apply Benjamini–Hochberg to all raw p-values within the preregistered family and report raw/adjusted p-values, sample counts, effect sizes, intervals and failures. A candidate must replicate in at least two separate seasons and pass a genuinely untouched later holdout; a season previously examined for feature selection cannot be relabeled untouched. Evaluate the full blend against a matched-time market-only benchmark as well as its team component. Leave a feature disabled/shadow until its evidence satisfies these gates. No demographic features.

| ID | Hypothesis and direction | Comparison and primary metric | Current status |
| --- | --- | --- | --- |
| H001 | Pre-game rest-day differences improve NBA/NFL predictions versus the identical team model without rest. | Walk-forward Brier and log loss of the **full matched-time market blend**, per league; positive improvement means lower loss. | Registered for future testing; no compliant results. Earlier two-season team-component exploration is not validation. |
| H002 | A team's pre-game rolling five-game scoring margin improves NBA/NFL predictions versus the identical team model without it. | Same matched-time market-blend comparison; separate leagues and the combined rest/form specification are in the same multiple-testing family. | Registered for future testing; no compliant results. Earlier exploration is not validation. |
| H003 | Available best retail prices more favorable than a matched-time independently sourced market anchor produce positive subsequent CLV, after costs and data-quality filters. | Mean CLV vs a verified sharp close, with sample and confidence interval; no retrospective assumption that an hourly observed quote is a true close. | Not testable until sufficient forward, licensed snapshots and a sharp-close source exist. |

Research runs must be recorded in `reports/` with candidate versions, data hashes, periods, family, raw/adjusted p-values, effect intervals, failures, and whether any holdout was touched. No preregistered test has been run as part of Step 0.
