# NBA trained-model inference verification

Run: 2026-10-31T20:11:32.181947+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.

| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |
|---|---:|---:|---|---:|---|---|
| ATL at NOP | 0.3300 | 0.6700 | conditional_research_only | 1 | 0.3499–0.3499 | ATL |
| CLE at MIL | 0.3122 | 0.6878 | conditional_research_only | 2 | 0.2643–0.2999 | CLE |
| MIN at SAS | 0.6765 | 0.3235 | conditional_research_only | 4 | 0.6832–0.6981 | SAS |
| OKC at HOU | 0.4777 | 0.5223 | conditional_research_only | 1 | 0.4719–0.4719 | OKC |
| PHI at CHA | 0.6156 | 0.3844 | conditional_research_only | 2 | 0.6018–0.6234 | CHA |
| SAC at MEM | 0.6147 | 0.3853 | conditional_research_only | 8 | 0.6078–0.6300 | MEM |
| BKN at IND | 0.6947 | 0.3053 | conditional_research_only | 2 | 0.7095–0.7260 | IND |
| BOS at ORL | 0.3181 | 0.6819 | conditional_research_only | 1 | 0.3588–0.3588 | BOS |
| LAC at GSW | 0.4080 | 0.5920 | conditional_research_only | 2 | 0.4367–0.4368 | LAC |
| TOR at LAL | 0.5710 | 0.4290 | conditional_research_only | 2 | 0.4990–0.5486 | unresolved |
| ATL at IND | 0.3489 | 0.6511 | conditional_research_only | 2 | 0.3774–0.3966 | ATL |
| BKN at NYK | 0.8459 | 0.1541 | conditional_research_only | 1 | 0.8785–0.8785 | NYK |
| BOS at HOU | 0.5284 | 0.4716 | conditional_research_only | 1 | 0.4966–0.4966 | BOS |
| CHI at PHI | 0.7599 | 0.2401 | conditional_research_only | 4 | 0.7832–0.7983 | PHI |
| DET at CHA | 0.4401 | 0.5599 | conditional_research_only | 1 | 0.4293–0.4293 | DET |
| MIA at LAL | 0.7299 | 0.2701 | conditional_research_only | 2 | 0.6774–0.7193 | LAL |
| MIL at MIN | 0.8301 | 0.1699 | conditional_research_only | 2 | 0.8606–0.8608 | MIN |
| NOP at MEM | 0.4578 | 0.5422 | conditional_research_only | 8 | 0.4434–0.4667 | NOP |
| OKC at CLE | 0.3400 | 0.6600 | conditional_research_only | 2 | 0.3336–0.3738 | OKC |
| PHX at GSW | 0.3719 | 0.6281 | conditional_research_only | 2 | 0.3988–0.3989 | PHX |
| POR at DEN | 0.6198 | 0.3802 | conditional_research_only | 1 | 0.6381–0.6381 | DEN |
| SAC at DAL | 0.7349 | 0.2651 | conditional_research_only | 1 | 0.7638–0.7638 | DAL |
| TOR at LAC | 0.4684 | 0.5316 | conditional_research_only | 1 | 0.3993–0.3993 | TOR |
| UTA at SAS | 0.9022 | 0.0978 | conditional_research_only | 2 | 0.9476–0.9509 | SAS |
| WAS at ORL | 0.7729 | 0.2271 | conditional_research_only | 1 | 0.8484–0.8484 | ORL |
| ATL at WAS | 0.2299 | 0.7701 | conditional_research_only | 1 | 0.2229–0.2229 | ATL |
| CHA at BKN | 0.2402 | 0.7598 | conditional_research_only | 1 | 0.1938–0.1938 | CHA |
| CHI at NYK | 0.8061 | 0.1939 | conditional_research_only | 2 | 0.8323–0.8323 | NYK |
| CLE at OKC | 0.7619 | 0.2381 | conditional_research_only | 2 | 0.7328–0.7658 | OKC |
| DAL at SAS | 0.8425 | 0.1575 | conditional_research_only | 2 | 0.8607–0.8688 | SAS |
| IND at MEM | 0.4370 | 0.5630 | conditional_research_only | 16 | 0.3948–0.4373 | IND |
| LAL at SAC | 0.1667 | 0.8333 | conditional_research_only | 2 | 0.1483–0.1753 | LAL |
| MIA at LAC | 0.6414 | 0.3586 | conditional_research_only | 1 | 0.5836–0.5836 | LAC |
| MIL at BOS | 0.8808 | 0.1192 | conditional_research_only | 1 | 0.8985–0.8985 | BOS |
| MIN at HOU | 0.6289 | 0.3711 | conditional_research_only | 2 | 0.5853–0.5857 | HOU |
| PHI at DET | 0.7234 | 0.2766 | conditional_research_only | 2 | 0.7200–0.7379 | DET |
| POR at PHX | 0.5598 | 0.4402 | conditional_research_only | 1 | 0.5269–0.5269 | PHX |
| TOR at DEN | 0.5340 | 0.4660 | conditional_research_only | 1 | 0.5147–0.5147 | DEN |
| UTA at NOP | 0.6596 | 0.3404 | conditional_research_only | 1 | 0.7422–0.7422 | NOP |
| MIA at GSW | 0.4898 | 0.5102 | conditional_research_only | 2 | 0.4592–0.4593 | MIA |
| ORL at PHX | 0.6137 | 0.3863 | conditional_research_only | 1 | 0.4962–0.4962 | ORL |
| BOS at CHA | 0.4538 | 0.5462 | conditional_research_only | 1 | 0.4664–0.4664 | BOS |
| MIN at NOP | 0.3351 | 0.6649 | conditional_research_only | 2 | 0.2850–0.2853 | MIN |
| OKC at MEM | 0.1517 | 0.8483 | conditional_research_only | 8 | 0.1358–0.1472 | OKC |
| PHI at CLE | 0.6158 | 0.3842 | conditional_research_only | 4 | 0.5625–0.6266 | CLE |
| POR at LAL | 0.6227 | 0.3773 | conditional_research_only | 2 | 0.5881–0.6354 | LAL |
| SAS at SAC | 0.1407 | 0.8593 | conditional_research_only | 2 | 0.1019–0.1084 | SAS |
| TOR at MIL | 0.2314 | 0.7686 | conditional_research_only | 1 | 0.1987–0.1987 | TOR |
| UTA at DAL | 0.6889 | 0.3111 | conditional_research_only | 1 | 0.7891–0.7891 | DAL |
| WAS at ATL | 0.8637 | 0.1363 | conditional_research_only | 1 | 0.8688–0.8688 | ATL |
| BKN at ATL | 0.8778 | 0.1222 | conditional_research_only | 1 | 0.8740–0.8740 | ATL |
| DEN at IND | 0.3232 | 0.6768 | conditional_research_only | 2 | 0.3043–0.3217 | DEN |
| HOU at PHX | 0.3981 | 0.6019 | conditional_research_only | 1 | 0.3584–0.3584 | HOU |
| NYK at CLE | 0.5497 | 0.4503 | conditional_research_only | 2 | 0.5061–0.5499 | CLE |
| ORL at GSW | 0.4911 | 0.5089 | conditional_research_only | 2 | 0.4072–0.4073 | ORL |
| SAS at POR | 0.4161 | 0.5839 | conditional_research_only | 2 | 0.3454–0.3611 | SAS |
| WAS at OKC | 0.9199 | 0.0801 | conditional_research_only | 1 | 0.9339–0.9339 | OKC |

Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.

## Multi-stat availability scenarios

| Game | Status | Scenarios | Home sensitivity range | Consistent winner |
|---|---|---:|---|---|
| ATL at NOP | conditional_research_only | 1 | 0.3869–0.3869 | ATL |
| CLE at MIL | conditional_research_only | 2 | 0.3182–0.3484 | CLE |
| MIN at SAS | conditional_research_only | 4 | 0.6348–0.6609 | SAS |
| OKC at HOU | conditional_research_only | 1 | 0.4878–0.4878 | OKC |
| PHI at CHA | conditional_research_only | 2 | 0.5643–0.6112 | CHA |
| SAC at MEM | conditional_research_only | 8 | 0.6979–0.7056 | MEM |
| BKN at IND | conditional_research_only | 2 | 0.6662–0.6754 | IND |
| BOS at ORL | conditional_research_only | 1 | 0.3817–0.3817 | BOS |
| LAC at GSW | conditional_research_only | 2 | 0.4361–0.4385 | LAC |
| TOR at LAL | conditional_research_only | 2 | 0.4900–0.5312 | unresolved |
| ATL at IND | conditional_research_only | 2 | 0.3986–0.4087 | ATL |
| BKN at NYK | conditional_research_only | 1 | 0.8634–0.8634 | NYK |
| BOS at HOU | conditional_research_only | 1 | 0.4098–0.4098 | BOS |
| CHI at PHI | conditional_research_only | 4 | 0.7772–0.8089 | PHI |
| DET at CHA | conditional_research_only | 1 | 0.4003–0.4003 | DET |
| MIA at LAL | conditional_research_only | 2 | 0.6421–0.6791 | LAL |
| MIL at MIN | conditional_research_only | 2 | 0.8747–0.8755 | MIN |
| NOP at MEM | conditional_research_only | 8 | 0.4961–0.5054 | unresolved |
| OKC at CLE | conditional_research_only | 2 | 0.3647–0.3967 | OKC |
| PHX at GSW | conditional_research_only | 2 | 0.3769–0.3791 | PHX |
| POR at DEN | conditional_research_only | 1 | 0.6002–0.6002 | DEN |
| SAC at DAL | conditional_research_only | 1 | 0.8024–0.8024 | DAL |
| TOR at LAC | conditional_research_only | 1 | 0.4016–0.4016 | TOR |
| UTA at SAS | conditional_research_only | 2 | 0.9367–0.9427 | SAS |
| WAS at ORL | conditional_research_only | 1 | 0.8779–0.8779 | ORL |
| ATL at WAS | conditional_research_only | 1 | 0.2402–0.2402 | ATL |
| CHA at BKN | conditional_research_only | 1 | 0.2333–0.2333 | CHA |
| CHI at NYK | conditional_research_only | 2 | 0.8332–0.8332 | NYK |
| CLE at OKC | conditional_research_only | 2 | 0.7145–0.7414 | OKC |
| DAL at SAS | conditional_research_only | 2 | 0.8486–0.8618 | SAS |
| IND at MEM | conditional_research_only | 16 | 0.4733–0.4930 | IND |
| LAL at SAC | conditional_research_only | 2 | 0.1469–0.1688 | LAL |
| MIA at LAC | conditional_research_only | 1 | 0.5562–0.5562 | LAC |
| MIL at BOS | conditional_research_only | 1 | 0.9042–0.9042 | BOS |
| MIN at HOU | conditional_research_only | 2 | 0.4822–0.4842 | MIN |
| PHI at DET | conditional_research_only | 2 | 0.7134–0.7513 | DET |
| POR at PHX | conditional_research_only | 1 | 0.5341–0.5341 | PHX |
| TOR at DEN | conditional_research_only | 1 | 0.4924–0.4924 | TOR |
| UTA at NOP | conditional_research_only | 1 | 0.7151–0.7151 | NOP |
| MIA at GSW | conditional_research_only | 2 | 0.4304–0.4328 | MIA |
| ORL at PHX | conditional_research_only | 1 | 0.4502–0.4502 | ORL |
| BOS at CHA | conditional_research_only | 1 | 0.4203–0.4203 | BOS |
| MIN at NOP | conditional_research_only | 2 | 0.2546–0.2561 | MIN |
| OKC at MEM | conditional_research_only | 8 | 0.2115–0.2177 | OKC |
| PHI at CLE | conditional_research_only | 4 | 0.5008–0.5825 | CLE |
| POR at LAL | conditional_research_only | 2 | 0.5620–0.6021 | LAL |
| SAS at SAC | conditional_research_only | 2 | 0.0881–0.0971 | SAS |
| TOR at MIL | conditional_research_only | 1 | 0.2206–0.2206 | TOR |
| UTA at DAL | conditional_research_only | 1 | 0.7720–0.7720 | DAL |
| WAS at ATL | conditional_research_only | 1 | 0.8577–0.8577 | ATL |
| BKN at ATL | conditional_research_only | 1 | 0.8383–0.8383 | ATL |
| DEN at IND | conditional_research_only | 2 | 0.3314–0.3407 | DEN |
| HOU at PHX | conditional_research_only | 1 | 0.4213–0.4213 | HOU |
| NYK at CLE | conditional_research_only | 2 | 0.4595–0.4934 | NYK |
| ORL at GSW | conditional_research_only | 2 | 0.3413–0.3434 | ORL |
| SAS at POR | conditional_research_only | 2 | 0.3450–0.3694 | SAS |
| WAS at OKC | conditional_research_only | 1 | 0.9159–0.9159 | OKC |
## Ensemble scenario status

{"conditional_research_only": 57}
## Implementation acceptance

Status: passed; today’s games checked: 6.
This verifies model inference and conditional injury integration. It does not establish causal injury impacts, confirmed lineups, predictive interval coverage, wagering permissions, profitability or production promotion.

- PASS: today_has_forecasts
- PASS: nba:2026-10-31:ATL:NOP:probabilities
- PASS: nba:2026-10-31:ATL:NOP:pregame
- PASS: nba:2026-10-31:ATL:NOP:provenance
- PASS: nba:2026-10-31:ATL:NOP:missingness_and_uncertainty
- PASS: nba:2026-10-31:ATL:NOP:live_roster_injury_join
- PASS: nba:2026-10-31:ATL:NOP:scenario_reproducibility
- PASS: nba:2026-10-31:ATL:NOP:scenario_probabilities
- PASS: nba:2026-10-31:CLE:MIL:probabilities
- PASS: nba:2026-10-31:CLE:MIL:pregame
- PASS: nba:2026-10-31:CLE:MIL:provenance
- PASS: nba:2026-10-31:CLE:MIL:missingness_and_uncertainty
- PASS: nba:2026-10-31:CLE:MIL:live_roster_injury_join
- PASS: nba:2026-10-31:CLE:MIL:scenario_reproducibility
- PASS: nba:2026-10-31:CLE:MIL:scenario_probabilities
- PASS: nba:2026-10-31:MIN:SAS:probabilities
- PASS: nba:2026-10-31:MIN:SAS:pregame
- PASS: nba:2026-10-31:MIN:SAS:provenance
- PASS: nba:2026-10-31:MIN:SAS:missingness_and_uncertainty
- PASS: nba:2026-10-31:MIN:SAS:live_roster_injury_join
- PASS: nba:2026-10-31:MIN:SAS:scenario_reproducibility
- PASS: nba:2026-10-31:MIN:SAS:scenario_probabilities
- PASS: nba:2026-10-31:OKC:HOU:probabilities
- PASS: nba:2026-10-31:OKC:HOU:pregame
- PASS: nba:2026-10-31:OKC:HOU:provenance
- PASS: nba:2026-10-31:OKC:HOU:missingness_and_uncertainty
- PASS: nba:2026-10-31:OKC:HOU:live_roster_injury_join
- PASS: nba:2026-10-31:OKC:HOU:scenario_reproducibility
- PASS: nba:2026-10-31:OKC:HOU:scenario_probabilities
- PASS: nba:2026-10-31:PHI:CHA:probabilities
- PASS: nba:2026-10-31:PHI:CHA:pregame
- PASS: nba:2026-10-31:PHI:CHA:provenance
- PASS: nba:2026-10-31:PHI:CHA:missingness_and_uncertainty
- PASS: nba:2026-10-31:PHI:CHA:live_roster_injury_join
- PASS: nba:2026-10-31:PHI:CHA:scenario_reproducibility
- PASS: nba:2026-10-31:PHI:CHA:scenario_probabilities
- PASS: nba:2026-10-31:SAC:MEM:probabilities
- PASS: nba:2026-10-31:SAC:MEM:pregame
- PASS: nba:2026-10-31:SAC:MEM:provenance
- PASS: nba:2026-10-31:SAC:MEM:missingness_and_uncertainty
- PASS: nba:2026-10-31:SAC:MEM:live_roster_injury_join
- PASS: nba:2026-10-31:SAC:MEM:scenario_reproducibility
- PASS: nba:2026-10-31:SAC:MEM:scenario_probabilities