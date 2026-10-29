# Pattern research report

As of 2026-10-29T20:10:01.095825+00:00: 2113 archived forecast snapshots, 12 separately observed outcomes, 477 matched rows before rights/time eligibility.
All results are shadow-only. No pattern is promoted; insufficient data is not a failure or a success. H010 and H013 form one Benjamini–Hochberg family across the definitions and leagues below. Only valid tests enter the correction.

| Hypothesis | League | Definition | Games / days | Mean win-minus-market | 95% day-block interval | Raw p | Adjusted p | Holdout | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| H010a | NBA | home at least two fewer rest days | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010a | NFL | home at least two fewer rest days | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010b | NBA | one team on back-to-back | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010c | NBA | Pacific road team, early Eastern start | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010d | NBA | verified high-altitude Denver/Utah home game | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010e | NFL | divisional underdog | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010f | NFL | outdoor sustained wind at least 15 mph, underdog | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010g | NFL | one confirmed starting-quarterback change | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010h | NBA | home team after overtime | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H010h | NFL | home team after overtime | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013a | NBA | one team after a loss of at least 20 | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013a | NFL | one team after a loss of at least 21 | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013b | NBA | one team after a win of at least 20 | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013b | NFL | one team after a win of at least 21 | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013c | NFL | exactly one team on a short week | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013d | NFL | exactly one team after a bye | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013e | NBA | early-season underdog | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013e | NFL | early-season underdog | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013f | NBA | underdog below 35% no-vig | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013f | NFL | underdog below 35% no-vig | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013g | NBA | home team with wide book disagreement | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013g | NFL | home team with wide book disagreement | 0 / 0 | — | — | — | — | not_tested | not_testable |
| H013h | NFL | prime-time favorite | 0 / 0 | — | — | — | — | not_tested | not_testable |

A result requires at least 30 games over 10 distinct game days even for an exploratory day-block test. Publication-time gaps, missing features, unsettled games and sources without verified rights are excluded. Day-block sign randomization assumes exchangeable signs across days; serial dependence and assumptions need review. For promotion, require two separate season replications, a genuinely untouched later holdout and the broader model-first validation gate.

A blank p-value means no qualified test was possible. Definitions and directions are in [HYPOTHESES.md](HYPOTHESES.md). Future reports must retain failures, all attempted variants, raw/adjusted p-values and sample counts.
