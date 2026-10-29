# NBA trained-model inference verification

Run: 2026-10-29T19:07:16.839942+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.

| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |
|---|---:|---:|---|---:|---|---|
| CLE at ATL | 0.5777 | 0.4223 | conditional_research_only | 4 | 0.5728–0.6122 | ATL |
| MEM at POR | 0.8341 | 0.1659 | conditional_research_only | 1 | 0.8589–0.8589 | POR |
| SAC at NOP | 0.6536 | 0.3464 | conditional_research_only | 2 | 0.7242–0.7305 | NOP |
| CHA at WAS | 0.2379 | 0.7621 | conditional_research_only | 2 | 0.1870–0.1903 | CHA |
| CHI at BOS | 0.8751 | 0.1249 | conditional_research_only | 2 | 0.8616–0.8628 | BOS |
| DEN at PHX | 0.5348 | 0.4652 | conditional_research_only | 2 | 0.5558–0.5678 | PHX |
| DET at BKN | 0.1622 | 0.8378 | conditional_research_only | 2 | 0.0907–0.1024 | DET |
| HOU at DAL | 0.2755 | 0.7245 | conditional_research_only | 8 | 0.2454–0.2663 | HOU |
| IND at MIA | 0.6558 | 0.3442 | conditional_research_only | 4 | 0.6771–0.6830 | MIA |
| LAC at MIN | 0.6252 | 0.3748 | conditional_research_only | 2 | 0.7264–0.7578 | MIN |
| LAL at GSW | 0.3133 | 0.6867 | conditional_research_only | 8 | 0.3068–0.3737 | LAL |
| NYK at PHI | 0.4944 | 0.5056 | conditional_research_only | 2 | 0.4013–0.4017 | NYK |
| ORL at TOR | 0.7238 | 0.2762 | conditional_research_only | 1 | 0.6747–0.6747 | TOR |
| ATL at NOP | 0.3207 | 0.6793 | conditional_research_only | 2 | 0.3403–0.3475 | ATL |
| CLE at MIL | 0.2645 | 0.7355 | conditional_research_only | 4 | 0.2792–0.3132 | CLE |
| MIN at SAS | 0.6765 | 0.3235 | conditional_research_only | 1 | 0.6799–0.6799 | SAS |
| OKC at HOU | 0.4777 | 0.5223 | conditional_research_only | 4 | 0.4842–0.5015 | unresolved |
| PHI at CHA | 0.6156 | 0.3844 | conditional_research_only | 2 | 0.6792–0.6796 | CHA |
| POR at UTA | 0.1997 | 0.8003 | conditional_research_only | 2 | 0.1518–0.1540 | POR |
| SAC at MEM | 0.6044 | 0.3956 | conditional_research_only | 1 | 0.6131–0.6131 | MEM |
| BKN at IND | 0.6947 | 0.3053 | conditional_research_only | 2 | 0.7789–0.7816 | IND |
| BOS at ORL | 0.3181 | 0.6819 | conditional_research_only | 1 | 0.4178–0.4178 | BOS |
| LAC at GSW | 0.4080 | 0.5920 | conditional_research_only | 4 | 0.4631–0.5043 | unresolved |
| TOR at LAL | 0.5710 | 0.4290 | conditional_research_only | 4 | 0.4838–0.5579 | unresolved |
| ATL at IND | 0.3233 | 0.6767 | conditional_research_only | 2 | 0.3527–0.3563 | ATL |
| BKN at NYK | 0.8459 | 0.1541 | conditional_research_only | 1 | 0.9099–0.9099 | NYK |
| BOS at HOU | 0.5284 | 0.4716 | conditional_research_only | 2 | 0.5801–0.5926 | HOU |
| CHI at PHI | 0.7599 | 0.2401 | conditional_research_only | 4 | 0.7309–0.7332 | PHI |
| DET at CHA | 0.4401 | 0.5599 | conditional_research_only | 2 | 0.4062–0.4389 | DET |
| MIA at LAL | 0.7299 | 0.2701 | conditional_research_only | 8 | 0.6352–0.7034 | LAL |
| MIL at MIN | 0.8301 | 0.1699 | conditional_research_only | 1 | 0.8611–0.8611 | MIN |
| NOP at MEM | 0.5097 | 0.4903 | conditional_research_only | 2 | 0.4279–0.4357 | NOP |
| OKC at CLE | 0.3940 | 0.6060 | conditional_research_only | 8 | 0.3247–0.3656 | OKC |
| PHX at GSW | 0.3719 | 0.6281 | conditional_research_only | 4 | 0.4006–0.4126 | PHX |
| POR at DEN | 0.5242 | 0.4758 | conditional_research_only | 1 | 0.4836–0.4836 | POR |
| SAC at DAL | 0.6674 | 0.3326 | conditional_research_only | 4 | 0.7337–0.7450 | DAL |
| TOR at LAC | 0.4684 | 0.5316 | conditional_research_only | 2 | 0.3547–0.3931 | TOR |
| UTA at SAS | 0.9022 | 0.0978 | conditional_research_only | 2 | 0.9475–0.9483 | SAS |
| WAS at ORL | 0.7729 | 0.2271 | conditional_research_only | 2 | 0.8437–0.8466 | ORL |
| ATL at WAS | 0.2102 | 0.7898 | conditional_research_only | 2 | 0.1960–0.1995 | ATL |
| CHA at BKN | 0.2402 | 0.7598 | conditional_research_only | 1 | 0.1573–0.1573 | CHA |
| CHI at NYK | 0.8061 | 0.1939 | conditional_research_only | 2 | 0.8383–0.8397 | NYK |
| CLE at OKC | 0.7171 | 0.2829 | conditional_research_only | 8 | 0.7396–0.7729 | OKC |
| DAL at SAS | 0.8425 | 0.1575 | conditional_research_only | 4 | 0.8689–0.8754 | SAS |
| IND at MEM | 0.4723 | 0.5277 | conditional_research_only | 2 | 0.3828–0.3866 | IND |
| LAL at SAC | 0.2165 | 0.7835 | conditional_research_only | 4 | 0.1606–0.2048 | LAL |
| MIA at LAC | 0.6414 | 0.3586 | conditional_research_only | 4 | 0.5052–0.5490 | LAC |
| MIL at BOS | 0.8808 | 0.1192 | conditional_research_only | 1 | 0.8665–0.8665 | BOS |
| MIN at HOU | 0.6289 | 0.3711 | conditional_research_only | 2 | 0.5912–0.6035 | HOU |
| PHI at DET | 0.7234 | 0.2766 | conditional_research_only | 4 | 0.7760–0.7987 | DET |
| POR at PHX | 0.4622 | 0.5378 | conditional_research_only | 2 | 0.4410–0.4531 | POR |
| TOR at DEN | 0.5340 | 0.4660 | conditional_research_only | 1 | 0.4488–0.4488 | TOR |
| UTA at NOP | 0.6757 | 0.3243 | conditional_research_only | 4 | 0.7578–0.7668 | NOP |
| MIA at GSW | 0.4898 | 0.5102 | conditional_research_only | 4 | 0.4478–0.4510 | MIA |
| ORL at PHX | 0.6137 | 0.3863 | conditional_research_only | 2 | 0.4894–0.5016 | unresolved |

Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.

## Multi-stat availability scenarios

| Game | Status | Scenarios | Home sensitivity range | Consistent winner |
|---|---|---:|---|---|
| CLE at ATL | conditional_research_only | 4 | 0.6298–0.6670 | ATL |
| MEM at POR | conditional_research_only | 1 | 0.8566–0.8566 | POR |
| SAC at NOP | conditional_research_only | 2 | 0.7638–0.7740 | NOP |
| CHA at WAS | conditional_research_only | 2 | 0.1895–0.1923 | CHA |
| CHI at BOS | conditional_research_only | 2 | 0.8836–0.8948 | BOS |
| DEN at PHX | conditional_research_only | 2 | 0.6000–0.6051 | PHX |
| DET at BKN | conditional_research_only | 2 | 0.1006–0.1165 | DET |
| HOU at DAL | conditional_research_only | 8 | 0.2657–0.3073 | HOU |
| IND at MIA | conditional_research_only | 4 | 0.6761–0.6818 | MIA |
| LAC at MIN | conditional_research_only | 2 | 0.7496–0.7916 | MIN |
| LAL at GSW | conditional_research_only | 8 | 0.2940–0.3865 | LAL |
| NYK at PHI | conditional_research_only | 2 | 0.3868–0.3874 | NYK |
| ORL at TOR | conditional_research_only | 1 | 0.6089–0.6089 | TOR |
| ATL at NOP | conditional_research_only | 2 | 0.3762–0.3898 | ATL |
| CLE at MIL | conditional_research_only | 4 | 0.3709–0.4097 | CLE |
| MIN at SAS | conditional_research_only | 1 | 0.6671–0.6671 | SAS |
| OKC at HOU | conditional_research_only | 4 | 0.5574–0.5937 | HOU |
| PHI at CHA | conditional_research_only | 2 | 0.6549–0.6555 | CHA |
| POR at UTA | conditional_research_only | 2 | 0.1533–0.1629 | POR |
| SAC at MEM | conditional_research_only | 1 | 0.6900–0.6900 | MEM |
| BKN at IND | conditional_research_only | 2 | 0.7583–0.7630 | IND |
| BOS at ORL | conditional_research_only | 1 | 0.4317–0.4317 | BOS |
| LAC at GSW | conditional_research_only | 4 | 0.4570–0.5250 | unresolved |
| TOR at LAL | conditional_research_only | 4 | 0.4763–0.5706 | unresolved |
| ATL at IND | conditional_research_only | 2 | 0.3837–0.3898 | ATL |
| BKN at NYK | conditional_research_only | 1 | 0.9059–0.9059 | NYK |
| BOS at HOU | conditional_research_only | 2 | 0.5349–0.5689 | HOU |
| CHI at PHI | conditional_research_only | 4 | 0.7404–0.7621 | PHI |
| DET at CHA | conditional_research_only | 2 | 0.3796–0.4191 | DET |
| MIA at LAL | conditional_research_only | 8 | 0.6110–0.6966 | LAL |
| MIL at MIN | conditional_research_only | 1 | 0.8610–0.8610 | MIN |
| NOP at MEM | conditional_research_only | 2 | 0.4547–0.4690 | NOP |
| OKC at CLE | conditional_research_only | 8 | 0.3160–0.3548 | OKC |
| PHX at GSW | conditional_research_only | 4 | 0.3854–0.3987 | PHX |
| POR at DEN | conditional_research_only | 1 | 0.4070–0.4070 | POR |
| SAC at DAL | conditional_research_only | 4 | 0.7954–0.8060 | DAL |
| TOR at LAC | conditional_research_only | 2 | 0.3414–0.3967 | TOR |
| UTA at SAS | conditional_research_only | 2 | 0.9362–0.9404 | SAS |
| WAS at ORL | conditional_research_only | 2 | 0.8802–0.8821 | ORL |
| ATL at WAS | conditional_research_only | 2 | 0.2024–0.2053 | ATL |
| CHA at BKN | conditional_research_only | 1 | 0.1900–0.1900 | CHA |
| CHI at NYK | conditional_research_only | 2 | 0.8530–0.8667 | NYK |
| CLE at OKC | conditional_research_only | 8 | 0.7496–0.7809 | OKC |
| DAL at SAS | conditional_research_only | 4 | 0.8474–0.8558 | SAS |
| IND at MEM | conditional_research_only | 2 | 0.4183–0.4246 | IND |
| LAL at SAC | conditional_research_only | 4 | 0.1418–0.1944 | LAL |
| MIA at LAC | conditional_research_only | 4 | 0.4724–0.5319 | unresolved |
| MIL at BOS | conditional_research_only | 1 | 0.8783–0.8783 | BOS |
| MIN at HOU | conditional_research_only | 2 | 0.5726–0.6058 | HOU |
| PHI at DET | conditional_research_only | 4 | 0.7714–0.7996 | DET |
| POR at PHX | conditional_research_only | 2 | 0.4090–0.4141 | POR |
| TOR at DEN | conditional_research_only | 1 | 0.4250–0.4250 | TOR |
| UTA at NOP | conditional_research_only | 4 | 0.7252–0.7503 | NOP |
| MIA at GSW | conditional_research_only | 4 | 0.4268–0.4356 | MIA |
| ORL at PHX | conditional_research_only | 2 | 0.4381–0.4433 | ORL |
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