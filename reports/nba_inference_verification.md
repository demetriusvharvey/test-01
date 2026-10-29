# NBA trained-model inference verification

Run: 2026-10-29T14:57:37.641647+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. Research outputs only; not the public pick list. No injury adjustment or validated future accuracy is claimed.

| Game | Home probability | Away probability | Availability scenario status |
|---|---:|---:|---|
| CLE at ATL | 0.5974 | 0.4026 | conditional_research_only |
| MEM at POR | 0.8927 | 0.1073 | conditional_research_only |
| SAC at NOP | 0.7154 | 0.2846 | conditional_research_only |
| CHA at WAS | 0.2364 | 0.7636 | conditional_research_only |
| CHI at BOS | 0.8618 | 0.1382 | conditional_research_only |
| DEN at PHX | 0.4551 | 0.5449 | conditional_research_only |
| DET at BKN | 0.1383 | 0.8617 | conditional_research_only |
| HOU at DAL | 0.2574 | 0.7426 | conditional_research_only |
| IND at MIA | 0.6275 | 0.3725 | conditional_research_only |
| LAC at MIN | 0.5780 | 0.4220 | conditional_research_only |
| LAL at GSW | 0.2849 | 0.7151 | conditional_research_only |
| NYK at PHI | 0.5003 | 0.4997 | conditional_research_only |
| ORL at TOR | 0.6853 | 0.3147 | conditional_research_only |
| ATL at NOP | 0.3744 | 0.6256 | conditional_research_only |
| CLE at MIL | 0.2808 | 0.7192 | conditional_research_only |
| MIN at SAS | 0.7146 | 0.2854 | conditional_research_only |
| OKC at HOU | 0.4316 | 0.5684 | conditional_research_only |
| PHI at CHA | 0.5861 | 0.4139 | conditional_research_only |
| POR at UTA | 0.1673 | 0.8327 | conditional_research_only |
| SAC at MEM | 0.5250 | 0.4750 | conditional_research_only |
| BKN at IND | 0.7039 | 0.2961 | conditional_research_only |
| BOS at ORL | 0.3911 | 0.6089 | conditional_research_only |
| LAC at GSW | 0.3461 | 0.6539 | conditional_research_only |
| TOR at LAL | 0.5905 | 0.4095 | conditional_research_only |
| ATL at IND | 0.3089 | 0.6911 | conditional_research_only |
| BKN at NYK | 0.8606 | 0.1394 | conditional_research_only |
| BOS at HOU | 0.5323 | 0.4677 | conditional_research_only |
| CHI at PHI | 0.7810 | 0.2190 | conditional_research_only |
| DET at CHA | 0.3990 | 0.6010 | conditional_research_only |
| MIA at LAL | 0.7675 | 0.2325 | conditional_research_only |
| MIL at MIN | 0.8216 | 0.1784 | conditional_research_only |
| NOP at MEM | 0.3931 | 0.6069 | conditional_research_only |
| OKC at CLE | 0.3756 | 0.6244 | conditional_research_only |
| PHX at GSW | 0.4319 | 0.5681 | conditional_research_only |
| POR at DEN | 0.5466 | 0.4534 | conditional_research_only |
| SAC at DAL | 0.6141 | 0.3859 | conditional_research_only |
| TOR at LAC | 0.5205 | 0.4795 | conditional_research_only |
| UTA at SAS | 0.9083 | 0.0917 | conditional_research_only |
| WAS at ORL | 0.8085 | 0.1915 | conditional_research_only |
| ATL at WAS | 0.1941 | 0.8059 | conditional_research_only |
| CHA at BKN | 0.2129 | 0.7871 | conditional_research_only |
| CHI at NYK | 0.7994 | 0.2006 | conditional_research_only |
| CLE at OKC | 0.7326 | 0.2674 | conditional_research_only |
| DAL at SAS | 0.8588 | 0.1412 | conditional_research_only |
| IND at MEM | 0.4304 | 0.5696 | conditional_research_only |
| LAL at SAC | 0.2065 | 0.7935 | conditional_research_only |
| MIA at LAC | 0.6841 | 0.3159 | conditional_research_only |
| MIL at BOS | 0.8574 | 0.1426 | conditional_research_only |
| MIN at HOU | 0.5978 | 0.4022 | conditional_research_only |
| PHI at DET | 0.7325 | 0.2675 | conditional_research_only |
| POR at PHX | 0.4737 | 0.5263 | conditional_research_only |
| TOR at DEN | 0.5715 | 0.4285 | conditional_research_only |
| UTA at NOP | 0.6861 | 0.3139 | conditional_research_only |
| MIA at GSW | 0.5061 | 0.4939 | conditional_research_only |
| ORL at PHX | 0.5954 | 0.4046 | conditional_research_only |

Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.

## Implementation acceptance

Status: passed; today’s games checked: 3.
This verifies model inference and conditional injury integration. It does not establish causal injury impacts, confirmed lineups, predictive interval coverage, wagering permissions, profitability or production promotion.

- PASS: today_has_forecasts
- PASS: nba:2026-10-29:CLE:ATL:probabilities
- PASS: nba:2026-10-29:CLE:ATL:pregame
- PASS: nba:2026-10-29:CLE:ATL:provenance
- PASS: nba:2026-10-29:CLE:ATL:missingness_and_uncertainty
- PASS: nba:2026-10-29:CLE:ATL:live_roster_injury_join
- PASS: nba:2026-10-29:CLE:ATL:scenario_reproducibility
- PASS: nba:2026-10-29:CLE:ATL:scenario_probabilities
- PASS: nba:2026-10-29:MEM:POR:probabilities
- PASS: nba:2026-10-29:MEM:POR:pregame
- PASS: nba:2026-10-29:MEM:POR:provenance
- PASS: nba:2026-10-29:MEM:POR:missingness_and_uncertainty
- PASS: nba:2026-10-29:MEM:POR:live_roster_injury_join
- PASS: nba:2026-10-29:MEM:POR:scenario_reproducibility
- PASS: nba:2026-10-29:MEM:POR:scenario_probabilities
- PASS: nba:2026-10-29:SAC:NOP:probabilities
- PASS: nba:2026-10-29:SAC:NOP:pregame
- PASS: nba:2026-10-29:SAC:NOP:provenance
- PASS: nba:2026-10-29:SAC:NOP:missingness_and_uncertainty
- PASS: nba:2026-10-29:SAC:NOP:live_roster_injury_join
- PASS: nba:2026-10-29:SAC:NOP:scenario_reproducibility
- PASS: nba:2026-10-29:SAC:NOP:scenario_probabilities