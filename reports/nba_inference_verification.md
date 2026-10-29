# NBA trained-model inference verification

Run: 2026-10-29T20:16:09.043862+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.

| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |
|---|---:|---:|---|---:|---|---|
| CLE at ATL | 0.5777 | 0.4223 | conditional_research_only | 4 | 0.5681–0.6069 | ATL |
| MEM at POR | 0.8341 | 0.1659 | conditional_research_only | 2 | 0.8601–0.8632 | POR |
| SAC at NOP | 0.6536 | 0.3464 | conditional_research_only | 2 | 0.7198–0.7270 | NOP |
| CHA at WAS | 0.2379 | 0.7621 | conditional_research_only | 2 | 0.1879–0.1921 | CHA |
| CHI at BOS | 0.8751 | 0.1249 | conditional_research_only | 4 | 0.8571–0.8670 | BOS |
| DEN at PHX | 0.5348 | 0.4652 | conditional_research_only | 2 | 0.5534–0.5631 | PHX |
| DET at BKN | 0.1622 | 0.8378 | conditional_research_only | 2 | 0.0916–0.1031 | DET |
| HOU at DAL | 0.2755 | 0.7245 | conditional_research_only | 8 | 0.2439–0.2661 | HOU |
| IND at MIA | 0.6558 | 0.3442 | conditional_research_only | 4 | 0.6772–0.6842 | MIA |
| LAC at MIN | 0.6252 | 0.3748 | conditional_research_only | 2 | 0.7218–0.7535 | MIN |
| LAL at GSW | 0.3133 | 0.6867 | conditional_research_only | 8 | 0.3035–0.3688 | LAL |
| NYK at PHI | 0.4944 | 0.5056 | conditional_research_only | 2 | 0.4060–0.4060 | NYK |
| ORL at TOR | 0.7238 | 0.2762 | conditional_research_only | 1 | 0.6760–0.6760 | TOR |
| ATL at NOP | 0.3207 | 0.6793 | conditional_research_only | 2 | 0.3393–0.3475 | ATL |
| CLE at MIL | 0.2645 | 0.7355 | conditional_research_only | 4 | 0.2726–0.3056 | CLE |
| MIN at SAS | 0.6765 | 0.3235 | conditional_research_only | 1 | 0.6788–0.6788 | SAS |
| OKC at HOU | 0.4777 | 0.5223 | conditional_research_only | 4 | 0.4832–0.5041 | unresolved |
| PHI at CHA | 0.6156 | 0.3844 | conditional_research_only | 2 | 0.6740–0.6740 | CHA |
| POR at UTA | 0.1997 | 0.8003 | conditional_research_only | 4 | 0.1481–0.1536 | POR |
| SAC at MEM | 0.6044 | 0.3956 | conditional_research_only | 1 | 0.6106–0.6106 | MEM |
| BKN at IND | 0.6947 | 0.3053 | conditional_research_only | 2 | 0.7739–0.7775 | IND |
| BOS at ORL | 0.3181 | 0.6819 | conditional_research_only | 1 | 0.4160–0.4160 | BOS |
| LAC at GSW | 0.4080 | 0.5920 | conditional_research_only | 4 | 0.4567–0.4978 | LAC |
| TOR at LAL | 0.5710 | 0.4290 | conditional_research_only | 4 | 0.4867–0.5595 | unresolved |
| ATL at IND | 0.3233 | 0.6767 | conditional_research_only | 2 | 0.3503–0.3549 | ATL |
| BKN at NYK | 0.8459 | 0.1541 | conditional_research_only | 1 | 0.9085–0.9085 | NYK |
| BOS at HOU | 0.5284 | 0.4716 | conditional_research_only | 2 | 0.5783–0.5923 | HOU |
| CHI at PHI | 0.7599 | 0.2401 | conditional_research_only | 8 | 0.7252–0.7415 | PHI |
| DET at CHA | 0.4401 | 0.5599 | conditional_research_only | 2 | 0.4032–0.4351 | DET |
| MIA at LAL | 0.7299 | 0.2701 | conditional_research_only | 8 | 0.6415–0.7082 | LAL |
| MIL at MIN | 0.8301 | 0.1699 | conditional_research_only | 1 | 0.8632–0.8632 | MIN |
| NOP at MEM | 0.5097 | 0.4903 | conditional_research_only | 2 | 0.4296–0.4386 | NOP |
| OKC at CLE | 0.3940 | 0.6060 | conditional_research_only | 8 | 0.3277–0.3699 | OKC |
| PHX at GSW | 0.3719 | 0.6281 | conditional_research_only | 4 | 0.3983–0.4080 | PHX |
| POR at DEN | 0.5242 | 0.4758 | conditional_research_only | 2 | 0.4804–0.4869 | POR |
| SAC at DAL | 0.6674 | 0.3326 | conditional_research_only | 4 | 0.7310–0.7424 | DAL |
| TOR at LAC | 0.4684 | 0.5316 | conditional_research_only | 2 | 0.3584–0.3969 | TOR |
| UTA at SAS | 0.9022 | 0.0978 | conditional_research_only | 2 | 0.9468–0.9476 | SAS |
| WAS at ORL | 0.7729 | 0.2271 | conditional_research_only | 2 | 0.8436–0.8471 | ORL |
| ATL at WAS | 0.2102 | 0.7898 | conditional_research_only | 2 | 0.1962–0.2005 | ATL |
| CHA at BKN | 0.2402 | 0.7598 | conditional_research_only | 1 | 0.1604–0.1604 | CHA |
| CHI at NYK | 0.8061 | 0.1939 | conditional_research_only | 4 | 0.8316–0.8430 | NYK |
| CLE at OKC | 0.7171 | 0.2829 | conditional_research_only | 8 | 0.7361–0.7706 | OKC |
| DAL at SAS | 0.8425 | 0.1575 | conditional_research_only | 4 | 0.8683–0.8749 | SAS |
| IND at MEM | 0.4723 | 0.5277 | conditional_research_only | 2 | 0.3860–0.3909 | IND |
| LAL at SAC | 0.2165 | 0.7835 | conditional_research_only | 4 | 0.1606–0.2041 | LAL |
| MIA at LAC | 0.6414 | 0.3586 | conditional_research_only | 4 | 0.5133–0.5571 | LAC |
| MIL at BOS | 0.8808 | 0.1192 | conditional_research_only | 1 | 0.8695–0.8695 | BOS |
| MIN at HOU | 0.6289 | 0.3711 | conditional_research_only | 2 | 0.5914–0.6053 | HOU |
| PHI at DET | 0.7234 | 0.2766 | conditional_research_only | 4 | 0.7745–0.7965 | DET |
| POR at PHX | 0.4622 | 0.5378 | conditional_research_only | 4 | 0.4356–0.4517 | POR |
| TOR at DEN | 0.5340 | 0.4660 | conditional_research_only | 1 | 0.4535–0.4535 | TOR |
| UTA at NOP | 0.6757 | 0.3243 | conditional_research_only | 4 | 0.7546–0.7642 | NOP |
| MIA at GSW | 0.4898 | 0.5102 | conditional_research_only | 4 | 0.4494–0.4527 | MIA |
| ORL at PHX | 0.6137 | 0.3863 | conditional_research_only | 2 | 0.4934–0.5033 | unresolved |

Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.

## Multi-stat availability scenarios

| Game | Status | Scenarios | Home sensitivity range | Consistent winner |
|---|---|---:|---|---|
| CLE at ATL | conditional_research_only | 4 | 0.6144–0.6486 | ATL |
| MEM at POR | conditional_research_only | 2 | 0.8468–0.8550 | POR |
| SAC at NOP | conditional_research_only | 2 | 0.7548–0.7666 | NOP |
| CHA at WAS | conditional_research_only | 2 | 0.1881–0.1904 | CHA |
| CHI at BOS | conditional_research_only | 4 | 0.8834–0.9000 | BOS |
| DEN at PHX | conditional_research_only | 2 | 0.6056–0.6066 | PHX |
| DET at BKN | conditional_research_only | 2 | 0.1052–0.1211 | DET |
| HOU at DAL | conditional_research_only | 8 | 0.2663–0.3104 | HOU |
| IND at MIA | conditional_research_only | 4 | 0.6800–0.6846 | MIA |
| LAC at MIN | conditional_research_only | 2 | 0.7325–0.7737 | MIN |
| LAL at GSW | conditional_research_only | 8 | 0.2898–0.3763 | LAL |
| NYK at PHI | conditional_research_only | 2 | 0.3889–0.3902 | NYK |
| ORL at TOR | conditional_research_only | 1 | 0.6124–0.6124 | TOR |
| ATL at NOP | conditional_research_only | 2 | 0.3791–0.3944 | ATL |
| CLE at MIL | conditional_research_only | 4 | 0.3569–0.3912 | CLE |
| MIN at SAS | conditional_research_only | 1 | 0.6681–0.6681 | SAS |
| OKC at HOU | conditional_research_only | 4 | 0.5453–0.5863 | HOU |
| PHI at CHA | conditional_research_only | 2 | 0.6605–0.6618 | CHA |
| POR at UTA | conditional_research_only | 4 | 0.1575–0.1755 | POR |
| SAC at MEM | conditional_research_only | 1 | 0.6843–0.6843 | MEM |
| BKN at IND | conditional_research_only | 2 | 0.7456–0.7495 | IND |
| BOS at ORL | conditional_research_only | 1 | 0.4232–0.4232 | BOS |
| LAC at GSW | conditional_research_only | 4 | 0.4451–0.5099 | unresolved |
| TOR at LAL | conditional_research_only | 4 | 0.4925–0.5800 | unresolved |
| ATL at IND | conditional_research_only | 2 | 0.3828–0.3877 | ATL |
| BKN at NYK | conditional_research_only | 1 | 0.9007–0.9007 | NYK |
| BOS at HOU | conditional_research_only | 2 | 0.5279–0.5628 | HOU |
| CHI at PHI | conditional_research_only | 8 | 0.7375–0.7703 | PHI |
| DET at CHA | conditional_research_only | 2 | 0.3860–0.4244 | DET |
| MIA at LAL | conditional_research_only | 8 | 0.6260–0.7044 | LAL |
| MIL at MIN | conditional_research_only | 1 | 0.8587–0.8587 | MIN |
| NOP at MEM | conditional_research_only | 2 | 0.4584–0.4745 | NOP |
| OKC at CLE | conditional_research_only | 8 | 0.3232–0.3621 | OKC |
| PHX at GSW | conditional_research_only | 4 | 0.3786–0.3886 | PHX |
| POR at DEN | conditional_research_only | 2 | 0.4135–0.4293 | POR |
| SAC at DAL | conditional_research_only | 4 | 0.7862–0.7984 | DAL |
| TOR at LAC | conditional_research_only | 2 | 0.3600–0.4126 | TOR |
| UTA at SAS | conditional_research_only | 2 | 0.9327–0.9367 | SAS |
| WAS at ORL | conditional_research_only | 2 | 0.8762–0.8778 | ORL |
| ATL at WAS | conditional_research_only | 2 | 0.2078–0.2102 | ATL |
| CHA at BKN | conditional_research_only | 1 | 0.1934–0.1934 | CHA |
| CHI at NYK | conditional_research_only | 4 | 0.8499–0.8705 | NYK |
| CLE at OKC | conditional_research_only | 8 | 0.7435–0.7750 | OKC |
| DAL at SAS | conditional_research_only | 4 | 0.8442–0.8537 | SAS |
| IND at MEM | conditional_research_only | 2 | 0.4290–0.4342 | IND |
| LAL at SAC | conditional_research_only | 4 | 0.1435–0.1925 | LAL |
| MIA at LAC | conditional_research_only | 4 | 0.4924–0.5479 | unresolved |
| MIL at BOS | conditional_research_only | 1 | 0.8807–0.8807 | BOS |
| MIN at HOU | conditional_research_only | 2 | 0.5759–0.6099 | HOU |
| PHI at DET | conditional_research_only | 4 | 0.7719–0.7997 | DET |
| POR at PHX | conditional_research_only | 4 | 0.4214–0.4383 | POR |
| TOR at DEN | conditional_research_only | 1 | 0.4349–0.4349 | TOR |
| UTA at NOP | conditional_research_only | 4 | 0.7182–0.7438 | NOP |
| MIA at GSW | conditional_research_only | 4 | 0.4310–0.4405 | MIA |
| ORL at PHX | conditional_research_only | 2 | 0.4580–0.4591 | ORL |
## Ensemble scenario status

{"conditional_research_only": 55}
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