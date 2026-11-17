# NBA trained-model inference verification

Run: 2026-11-17T19:22:22.655782+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.

| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |
|---|---:|---:|---|---:|---|---|
| CHA at LAL | 0.7905 | 0.2095 | conditional_research_only | 1 | 0.8054–0.8054 | LAL |
| DET at SAS | 0.6386 | 0.3614 | conditional_research_only | 1 | 0.5843–0.5843 | SAS |
| NYK at TOR | 0.4947 | 0.5053 | insufficient_rotation_history | 0 | unavailable | unresolved |
| POR at MIN | 0.5530 | 0.4470 | conditional_research_only | 1 | 0.5710–0.5710 | MIN |
| UTA at LAC | 0.8042 | 0.1958 | conditional_research_only | 1 | 0.7822–0.7822 | LAC |
| ATL at OKC | 0.7203 | 0.2797 | conditional_research_only | 4 | 0.6732–0.6865 | OKC |
| BOS at DEN | 0.4330 | 0.5670 | conditional_research_only | 2 | 0.4725–0.4783 | BOS |
| CHI at BKN | 0.4941 | 0.5059 | conditional_research_only | 4 | 0.4872–0.4965 | CHI |
| DET at NOP | 0.2247 | 0.7753 | conditional_research_only | 2 | 0.1872–0.1904 | DET |
| GSW at DAL | 0.3727 | 0.6273 | conditional_research_only | 8 | 0.3404–0.3690 | GSW |
| HOU at IND | 0.2661 | 0.7339 | insufficient_rotation_history | 0 | unavailable | unresolved |
| MEM at CLE | 0.7590 | 0.2410 | conditional_research_only | 16 | 0.7378–0.7710 | CLE |
| MIL at MIA | 0.8184 | 0.1816 | conditional_research_only | 8 | 0.8297–0.8387 | MIA |
| PHI at ORL | 0.5585 | 0.4415 | conditional_research_only | 4 | 0.5524–0.5844 | ORL |
| PHX at SAC | 0.3289 | 0.6711 | conditional_research_only | 8 | 0.3395–0.3646 | PHX |
| UTA at LAL | 0.8966 | 0.1034 | conditional_research_only | 1 | 0.8925–0.8925 | LAL |
| WAS at TOR | 0.8234 | 0.1766 | insufficient_rotation_history | 0 | unavailable | unresolved |
| GSW at MEM | 0.3972 | 0.6028 | conditional_research_only | 4 | 0.3543–0.3758 | GSW |
| LAC at SAS | 0.8069 | 0.1931 | conditional_research_only | 1 | 0.8019–0.8019 | SAS |
| NYK at MIN | 0.6273 | 0.3727 | conditional_research_only | 1 | 0.6511–0.6511 | MIN |
| POR at MIL | 0.1698 | 0.8302 | conditional_research_only | 2 | 0.1541–0.1548 | POR |
| CHA at ATL | 0.7180 | 0.2820 | conditional_research_only | 4 | 0.7184–0.7306 | ATL |
| HOU at DEN | 0.5169 | 0.4831 | insufficient_rotation_history | 0 | unavailable | unresolved |
| IND at CLE | 0.7803 | 0.2197 | conditional_research_only | 8 | 0.7724–0.7880 | CLE |
| NOP at OKC | 0.8730 | 0.1270 | conditional_research_only | 2 | 0.8549–0.8575 | OKC |
| ORL at BKN | 0.2920 | 0.7080 | conditional_research_only | 1 | 0.2536–0.2536 | ORL |
| PHX at UTA | 0.2966 | 0.7034 | conditional_research_only | 1 | 0.3285–0.3285 | PHX |
| SAC at LAL | 0.8818 | 0.1182 | conditional_research_only | 8 | 0.8762–0.8876 | LAL |
| TOR at DET | 0.6946 | 0.3054 | insufficient_rotation_history | 0 | unavailable | unresolved |
| WAS at CHI | 0.6519 | 0.3481 | conditional_research_only | 8 | 0.6208–0.6295 | CHI |
| BOS at SAC | 0.1276 | 0.8724 | conditional_research_only | 16 | 0.1431–0.1602 | BOS |
| LAC at DAL | 0.4564 | 0.5436 | conditional_research_only | 8 | 0.4420–0.4730 | LAC |
| MEM at MIN | 0.8024 | 0.1976 | conditional_research_only | 4 | 0.8231–0.8362 | MIN |
| MIL at PHI | 0.8134 | 0.1866 | conditional_research_only | 8 | 0.8199–0.8392 | PHI |
| NOP at SAS | 0.8867 | 0.1133 | conditional_research_only | 2 | 0.8843–0.8865 | SAS |
| POR at NYK | 0.4856 | 0.5144 | conditional_research_only | 1 | 0.4772–0.4772 | POR |
| BOS at GSW | 0.3313 | 0.6687 | conditional_research_only | 2 | 0.3711–0.3765 | BOS |
| DAL at UTA | 0.3803 | 0.6197 | conditional_research_only | 8 | 0.3939–0.4241 | DAL |
| DEN at CHI | 0.2661 | 0.7339 | conditional_research_only | 4 | 0.2368–0.2435 | DEN |
| DET at ATL | 0.4363 | 0.5637 | conditional_research_only | 4 | 0.3877–0.4022 | DET |
| IND at NYK | 0.7775 | 0.2225 | conditional_research_only | 2 | 0.7937–0.7945 | NYK |
| OKC at MIA | 0.3742 | 0.6258 | conditional_research_only | 4 | 0.4191–0.4337 | OKC |
| ORL at WAS | 0.2991 | 0.7009 | conditional_research_only | 2 | 0.2855–0.2855 | ORL |
| BKN at MIN | 0.8784 | 0.1216 | conditional_research_only | 1 | 0.8995–0.8995 | MIN |
| CLE at CHI | 0.2789 | 0.7211 | conditional_research_only | 16 | 0.2646–0.2893 | CLE |
| LAC at HOU | 0.7451 | 0.2549 | insufficient_rotation_history | 0 | unavailable | unresolved |
| MEM at CHA | 0.5935 | 0.4065 | conditional_research_only | 4 | 0.5950–0.6171 | CHA |
| MIL at TOR | 0.8188 | 0.1812 | insufficient_rotation_history | 0 | unavailable | unresolved |
| OKC at IND | 0.2241 | 0.7759 | conditional_research_only | 2 | 0.2382–0.2391 | OKC |
| PHX at NOP | 0.3855 | 0.6145 | conditional_research_only | 2 | 0.3803–0.3853 | PHX |
| POR at PHI | 0.4779 | 0.5221 | conditional_research_only | 4 | 0.4672–0.4998 | POR |
| SAS at SAC | 0.1254 | 0.8746 | conditional_research_only | 8 | 0.1315–0.1445 | SAS |
| UTA at LAL | 0.8966 | 0.1034 | conditional_research_only | 1 | 0.8925–0.8925 | LAL |
| BOS at WAS | 0.1288 | 0.8712 | conditional_research_only | 4 | 0.1451–0.1480 | BOS |
| DAL at DEN | 0.7645 | 0.2355 | conditional_research_only | 8 | 0.7595–0.7816 | DEN |
| DET at ORL | 0.3751 | 0.6249 | conditional_research_only | 1 | 0.3511–0.3511 | DET |

Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.

## Multi-stat availability scenarios

| Game | Status | Scenarios | Home sensitivity range | Consistent winner |
|---|---|---:|---|---|
| CHA at LAL | conditional_research_only | 1 | 0.8021–0.8021 | LAL |
| DET at SAS | conditional_research_only | 1 | 0.6220–0.6220 | SAS |
| NYK at TOR | insufficient_rotation_history | 0 | unavailable | unresolved |
| POR at MIN | conditional_research_only | 1 | 0.5419–0.5419 | MIN |
| UTA at LAC | conditional_research_only | 1 | 0.7770–0.7770 | LAC |
| ATL at OKC | conditional_research_only | 4 | 0.6661–0.6917 | OKC |
| BOS at DEN | conditional_research_only | 2 | 0.4936–0.4973 | BOS |
| CHI at BKN | conditional_research_only | 4 | 0.4805–0.5186 | unresolved |
| DET at NOP | conditional_research_only | 2 | 0.2035–0.2133 | DET |
| GSW at DAL | conditional_research_only | 8 | 0.2777–0.3089 | GSW |
| HOU at IND | insufficient_rotation_history | 0 | unavailable | unresolved |
| MEM at CLE | conditional_research_only | 16 | 0.7420–0.8001 | CLE |
| MIL at MIA | conditional_research_only | 8 | 0.8423–0.8587 | MIA |
| PHI at ORL | conditional_research_only | 4 | 0.5500–0.6023 | ORL |
| PHX at SAC | conditional_research_only | 8 | 0.3300–0.3731 | PHX |
| UTA at LAL | conditional_research_only | 1 | 0.8905–0.8905 | LAL |
| WAS at TOR | insufficient_rotation_history | 0 | unavailable | unresolved |
| GSW at MEM | conditional_research_only | 4 | 0.3186–0.3630 | GSW |
| LAC at SAS | conditional_research_only | 1 | 0.8218–0.8218 | SAS |
| NYK at MIN | conditional_research_only | 1 | 0.6068–0.6068 | MIN |
| POR at MIL | conditional_research_only | 2 | 0.1480–0.1481 | POR |
| CHA at ATL | conditional_research_only | 4 | 0.7093–0.7329 | ATL |
| HOU at DEN | insufficient_rotation_history | 0 | unavailable | unresolved |
| IND at CLE | conditional_research_only | 8 | 0.7843–0.8172 | CLE |
| NOP at OKC | conditional_research_only | 2 | 0.8418–0.8495 | OKC |
| ORL at BKN | conditional_research_only | 1 | 0.2462–0.2462 | ORL |
| PHX at UTA | conditional_research_only | 1 | 0.3075–0.3075 | PHX |
| SAC at LAL | conditional_research_only | 8 | 0.8585–0.8800 | LAL |
| TOR at DET | insufficient_rotation_history | 0 | unavailable | unresolved |
| WAS at CHI | conditional_research_only | 8 | 0.6131–0.6486 | CHI |
| BOS at SAC | conditional_research_only | 16 | 0.1544–0.1830 | BOS |
| LAC at DAL | conditional_research_only | 8 | 0.4331–0.4703 | LAC |
| MEM at MIN | conditional_research_only | 4 | 0.7876–0.8188 | MIN |
| MIL at PHI | conditional_research_only | 8 | 0.8272–0.8558 | PHI |
| NOP at SAS | conditional_research_only | 2 | 0.8862–0.8920 | SAS |
| POR at NYK | conditional_research_only | 1 | 0.4958–0.4958 | POR |
| BOS at GSW | conditional_research_only | 2 | 0.4340–0.4377 | BOS |
| DAL at UTA | conditional_research_only | 8 | 0.4056–0.4423 | DAL |
| DEN at CHI | conditional_research_only | 4 | 0.2276–0.2555 | DEN |
| DET at ATL | conditional_research_only | 4 | 0.3914–0.4197 | DET |
| IND at NYK | conditional_research_only | 2 | 0.7958–0.8075 | NYK |
| OKC at MIA | conditional_research_only | 4 | 0.4491–0.4811 | OKC |
| ORL at WAS | conditional_research_only | 2 | 0.2672–0.2672 | ORL |
| BKN at MIN | conditional_research_only | 1 | 0.8862–0.8862 | MIN |
| CLE at CHI | conditional_research_only | 16 | 0.2213–0.2743 | CLE |
| LAC at HOU | insufficient_rotation_history | 0 | unavailable | unresolved |
| MEM at CHA | conditional_research_only | 4 | 0.5543–0.6025 | CHA |
| MIL at TOR | insufficient_rotation_history | 0 | unavailable | unresolved |
| OKC at IND | conditional_research_only | 2 | 0.2530–0.2672 | OKC |
| PHX at NOP | conditional_research_only | 2 | 0.3676–0.3815 | PHX |
| POR at PHI | conditional_research_only | 4 | 0.4654–0.5189 | unresolved |
| SAS at SAC | conditional_research_only | 8 | 0.1272–0.1497 | SAS |
| UTA at LAL | conditional_research_only | 1 | 0.8905–0.8905 | LAL |
| BOS at WAS | conditional_research_only | 4 | 0.1534–0.1554 | BOS |
| DAL at DEN | conditional_research_only | 8 | 0.7772–0.8021 | DEN |
| DET at ORL | conditional_research_only | 1 | 0.3949–0.3949 | DET |
## Ensemble scenario status

{"conditional_research_only": 49, "ensemble_component_unavailable": 7}
## Implementation acceptance

Status: incomplete; today’s games checked: 5.
This verifies model inference and conditional injury integration. It does not establish causal injury impacts, confirmed lineups, predictive interval coverage, wagering permissions, profitability or production promotion.

- PASS: today_has_forecasts
- PASS: nba:2026-11-17:CHA:LAL:probabilities
- PASS: nba:2026-11-17:CHA:LAL:pregame
- PASS: nba:2026-11-17:CHA:LAL:provenance
- PASS: nba:2026-11-17:CHA:LAL:missingness_and_uncertainty
- PASS: nba:2026-11-17:CHA:LAL:live_roster_injury_join
- PASS: nba:2026-11-17:CHA:LAL:scenario_reproducibility
- PASS: nba:2026-11-17:CHA:LAL:scenario_probabilities
- PASS: nba:2026-11-17:DET:SAS:probabilities
- PASS: nba:2026-11-17:DET:SAS:pregame
- PASS: nba:2026-11-17:DET:SAS:provenance
- PASS: nba:2026-11-17:DET:SAS:missingness_and_uncertainty
- PASS: nba:2026-11-17:DET:SAS:live_roster_injury_join
- PASS: nba:2026-11-17:DET:SAS:scenario_reproducibility
- PASS: nba:2026-11-17:DET:SAS:scenario_probabilities
- PASS: nba:2026-11-17:NYK:TOR:probabilities
- PASS: nba:2026-11-17:NYK:TOR:pregame
- PASS: nba:2026-11-17:NYK:TOR:provenance
- PASS: nba:2026-11-17:NYK:TOR:missingness_and_uncertainty
- MISSING: nba:2026-11-17:NYK:TOR:live_roster_injury_join
- MISSING: nba:2026-11-17:NYK:TOR:scenario_reproducibility
- MISSING: nba:2026-11-17:NYK:TOR:scenario_probabilities
- PASS: nba:2026-11-17:POR:MIN:probabilities
- PASS: nba:2026-11-17:POR:MIN:pregame
- PASS: nba:2026-11-17:POR:MIN:provenance
- PASS: nba:2026-11-17:POR:MIN:missingness_and_uncertainty
- PASS: nba:2026-11-17:POR:MIN:live_roster_injury_join
- PASS: nba:2026-11-17:POR:MIN:scenario_reproducibility
- PASS: nba:2026-11-17:POR:MIN:scenario_probabilities
- PASS: nba:2026-11-17:UTA:LAC:probabilities
- PASS: nba:2026-11-17:UTA:LAC:pregame
- PASS: nba:2026-11-17:UTA:LAC:provenance
- PASS: nba:2026-11-17:UTA:LAC:missingness_and_uncertainty
- PASS: nba:2026-11-17:UTA:LAC:live_roster_injury_join
- PASS: nba:2026-11-17:UTA:LAC:scenario_reproducibility
- PASS: nba:2026-11-17:UTA:LAC:scenario_probabilities