# NBA trained-model inference verification

Run: 2026-10-29T18:54:24.963260+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.

| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |
|---|---:|---:|---|---:|---|---|
| CLE at ATL | 0.5974 | 0.4026 | conditional_research_only | 4 | 0.6015–0.6519 | ATL |
| MEM at POR | 0.8927 | 0.1073 | conditional_research_only | 1 | 0.9335–0.9335 | POR |
| SAC at NOP | 0.7154 | 0.2846 | conditional_research_only | 2 | 0.8221–0.8241 | NOP |
| CHA at WAS | 0.2364 | 0.7636 | conditional_research_only | 2 | 0.1702–0.1702 | CHA |
| CHI at BOS | 0.8618 | 0.1382 | conditional_research_only | 2 | 0.8224–0.8355 | BOS |
| DEN at PHX | 0.4551 | 0.5449 | conditional_research_only | 2 | 0.4765–0.4909 | DEN |
| DET at BKN | 0.1383 | 0.8617 | conditional_research_only | 2 | 0.0538–0.0631 | DET |
| HOU at DAL | 0.2574 | 0.7426 | conditional_research_only | 8 | 0.2123–0.2424 | HOU |
| IND at MIA | 0.6275 | 0.3725 | conditional_research_only | 4 | 0.6287–0.6382 | MIA |
| LAC at MIN | 0.5780 | 0.4220 | conditional_research_only | 2 | 0.7234–0.7687 | MIN |
| LAL at GSW | 0.2849 | 0.7151 | conditional_research_only | 8 | 0.2899–0.3700 | LAL |
| NYK at PHI | 0.5003 | 0.4997 | conditional_research_only | 2 | 0.3667–0.3684 | NYK |
| ORL at TOR | 0.6853 | 0.3147 | conditional_research_only | 1 | 0.6109–0.6109 | TOR |
| ATL at NOP | 0.3744 | 0.6256 | conditional_research_only | 2 | 0.4247–0.4282 | ATL |
| CLE at MIL | 0.2808 | 0.7192 | conditional_research_only | 4 | 0.2926–0.3392 | CLE |
| MIN at SAS | 0.7146 | 0.2854 | conditional_research_only | 1 | 0.7269–0.7269 | SAS |
| OKC at HOU | 0.4316 | 0.5684 | conditional_research_only | 4 | 0.4388–0.4557 | OKC |
| PHI at CHA | 0.5861 | 0.4139 | conditional_research_only | 2 | 0.6969–0.6985 | CHA |
| POR at UTA | 0.1673 | 0.8327 | conditional_research_only | 2 | 0.1082–0.1089 | POR |
| SAC at MEM | 0.5250 | 0.4750 | conditional_research_only | 1 | 0.4943–0.4943 | SAC |
| BKN at IND | 0.7039 | 0.2961 | conditional_research_only | 2 | 0.8477–0.8507 | IND |
| BOS at ORL | 0.3911 | 0.6089 | conditional_research_only | 1 | 0.5729–0.5729 | ORL |
| LAC at GSW | 0.3461 | 0.6539 | conditional_research_only | 4 | 0.4498–0.5106 | unresolved |
| TOR at LAL | 0.5905 | 0.4095 | conditional_research_only | 4 | 0.4879–0.5770 | unresolved |
| ATL at IND | 0.3089 | 0.6911 | conditional_research_only | 2 | 0.3629–0.3685 | ATL |
| BKN at NYK | 0.8606 | 0.1394 | conditional_research_only | 1 | 0.9439–0.9439 | NYK |
| BOS at HOU | 0.5323 | 0.4677 | conditional_research_only | 2 | 0.6412–0.6523 | HOU |
| CHI at PHI | 0.7810 | 0.2190 | conditional_research_only | 4 | 0.7395–0.7582 | PHI |
| DET at CHA | 0.3990 | 0.6010 | conditional_research_only | 2 | 0.3798–0.4204 | DET |
| MIA at LAL | 0.7675 | 0.2325 | conditional_research_only | 8 | 0.6650–0.7429 | LAL |
| MIL at MIN | 0.8216 | 0.1784 | conditional_research_only | 1 | 0.8665–0.8665 | MIN |
| NOP at MEM | 0.3931 | 0.6069 | conditional_research_only | 2 | 0.2365–0.2391 | NOP |
| OKC at CLE | 0.3756 | 0.6244 | conditional_research_only | 8 | 0.2782–0.3278 | OKC |
| PHX at GSW | 0.4319 | 0.5681 | conditional_research_only | 4 | 0.5365–0.5519 | GSW |
| POR at DEN | 0.5466 | 0.4534 | conditional_research_only | 1 | 0.4509–0.4509 | POR |
| SAC at DAL | 0.6141 | 0.3859 | conditional_research_only | 4 | 0.7106–0.7353 | DAL |
| TOR at LAC | 0.5205 | 0.4795 | conditional_research_only | 2 | 0.3491–0.4052 | TOR |
| UTA at SAS | 0.9083 | 0.0917 | conditional_research_only | 2 | 0.9614–0.9617 | SAS |
| WAS at ORL | 0.8085 | 0.1915 | conditional_research_only | 2 | 0.8830–0.8830 | ORL |
| ATL at WAS | 0.1941 | 0.8059 | conditional_research_only | 2 | 0.1843–0.1843 | ATL |
| CHA at BKN | 0.2129 | 0.7871 | conditional_research_only | 1 | 0.0930–0.0930 | CHA |
| CHI at NYK | 0.7994 | 0.2006 | conditional_research_only | 2 | 0.8439–0.8557 | NYK |
| CLE at OKC | 0.7326 | 0.2674 | conditional_research_only | 8 | 0.7707–0.8096 | OKC |
| DAL at SAS | 0.8588 | 0.1412 | conditional_research_only | 4 | 0.8879–0.8996 | SAS |
| IND at MEM | 0.4304 | 0.5696 | conditional_research_only | 2 | 0.2552–0.2598 | IND |
| LAL at SAC | 0.2065 | 0.7935 | conditional_research_only | 4 | 0.1307–0.1771 | LAL |
| MIA at LAC | 0.6841 | 0.3159 | conditional_research_only | 4 | 0.4906–0.5543 | unresolved |
| MIL at BOS | 0.8574 | 0.1426 | conditional_research_only | 1 | 0.8227–0.8227 | BOS |
| MIN at HOU | 0.5978 | 0.4022 | conditional_research_only | 2 | 0.5611–0.5730 | HOU |
| PHI at DET | 0.7325 | 0.2675 | conditional_research_only | 4 | 0.8023–0.8288 | DET |
| POR at PHX | 0.4737 | 0.5263 | conditional_research_only | 2 | 0.4039–0.4178 | POR |
| TOR at DEN | 0.5715 | 0.4285 | conditional_research_only | 1 | 0.4257–0.4257 | TOR |
| UTA at NOP | 0.6861 | 0.3139 | conditional_research_only | 4 | 0.8111–0.8144 | NOP |
| MIA at GSW | 0.5061 | 0.4939 | conditional_research_only | 4 | 0.4754–0.4808 | MIA |
| ORL at PHX | 0.5954 | 0.4046 | conditional_research_only | 2 | 0.3927–0.4065 | ORL |

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