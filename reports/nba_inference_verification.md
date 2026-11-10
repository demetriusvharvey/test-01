# NBA trained-model inference verification

Run: 2026-11-10T18:13:57.696791+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.

| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |
|---|---:|---:|---|---:|---|---|
| BOS at PHI | 0.3946 | 0.6054 | conditional_research_only | 1 | 0.4298–0.4298 | BOS |
| LAC at PHX | 0.5937 | 0.4063 | conditional_research_only | 2 | 0.6322–0.6389 | PHX |
| MIA at UTA | 0.2970 | 0.7030 | conditional_research_only | 4 | 0.2866–0.3236 | MIA |
| MIL at NYK | 0.8555 | 0.1445 | conditional_research_only | 8 | 0.8554–0.8625 | NYK |
| OKC at POR | 0.3974 | 0.6026 | conditional_research_only | 1 | 0.3979–0.3979 | OKC |
| ORL at SAC | 0.3491 | 0.6509 | conditional_research_only | 8 | 0.2865–0.3206 | ORL |
| BKN at NOP | 0.7149 | 0.2851 | conditional_research_only | 32 | 0.7185–0.7280 | NOP |
| BOS at TOR | 0.5227 | 0.4773 | conditional_research_only | 8 | 0.5514–0.6069 | TOR |
| CLE at NYK | 0.5890 | 0.4110 | conditional_research_only | 4 | 0.5822–0.5850 | NYK |
| DEN at MEM | 0.2112 | 0.7888 | conditional_research_only | 4 | 0.1803–0.1850 | DEN |
| GSW at HOU | 0.7364 | 0.2636 | conditional_research_only | 8 | 0.7507–0.7574 | HOU |
| LAL at MIL | 0.2108 | 0.7892 | conditional_research_only | 16 | 0.1943–0.2203 | LAL |
| OKC at POR | 0.3974 | 0.6026 | conditional_research_only | 1 | 0.3979–0.3979 | OKC |
| ORL at UTA | 0.3188 | 0.6812 | conditional_research_only | 4 | 0.2809–0.3105 | ORL |
| SAS at CHI | 0.1306 | 0.8694 | conditional_research_only | 8 | 0.1140–0.1225 | SAS |
| WAS at IND | 0.7552 | 0.2448 | conditional_research_only | 2 | 0.7388–0.7456 | IND |
| CHA at PHX | 0.6151 | 0.3849 | conditional_research_only | 4 | 0.6018–0.6204 | PHX |
| DAL at MIN | 0.7719 | 0.2281 | conditional_research_only | 2 | 0.8040–0.8060 | MIN |
| DET at WAS | 0.1879 | 0.8121 | conditional_research_only | 2 | 0.1833–0.1887 | DET |
| TOR at PHI | 0.4331 | 0.5669 | conditional_research_only | 8 | 0.3845–0.4397 | TOR |
| ATL at CHI | 0.2283 | 0.7717 | conditional_research_only | 4 | 0.2246–0.2324 | ATL |
| CLE at MIA | 0.4069 | 0.5931 | conditional_research_only | 4 | 0.4151–0.4412 | CLE |
| GSW at SAS | 0.7986 | 0.2014 | conditional_research_only | 8 | 0.8034–0.8136 | SAS |
| MEM at NOP | 0.5837 | 0.4163 | conditional_research_only | 32 | 0.5896–0.6063 | NOP |
| MIL at ORL | 0.7191 | 0.2809 | conditional_research_only | 8 | 0.7620–0.7832 | ORL |
| NYK at IND | 0.3735 | 0.6265 | conditional_research_only | 2 | 0.3588–0.3607 | NYK |
| OKC at LAC | 0.2675 | 0.7325 | conditional_research_only | 2 | 0.2417–0.2471 | OKC |
| POR at SAC | 0.1943 | 0.8057 | conditional_research_only | 4 | 0.1946–0.2093 | POR |
| UTA at HOU | 0.9078 | 0.0922 | conditional_research_only | 4 | 0.8975–0.9047 | HOU |
| BKN at MEM | 0.6966 | 0.3034 | conditional_research_only | 16 | 0.6879–0.6964 | MEM |
| CHI at MIN | 0.8608 | 0.1392 | conditional_research_only | 4 | 0.8742–0.8790 | MIN |
| DAL at CLE | 0.7584 | 0.2416 | conditional_research_only | 4 | 0.7816–0.7844 | CLE |
| DEN at NOP | 0.2781 | 0.7219 | conditional_research_only | 8 | 0.2553–0.2627 | DEN |
| DET at MIA | 0.3332 | 0.6668 | conditional_research_only | 2 | 0.3386–0.3620 | DET |
| ATL at MIL | 0.2422 | 0.7578 | conditional_research_only | 4 | 0.2439–0.2533 | ATL |
| CHA at LAC | 0.6171 | 0.3829 | conditional_research_only | 8 | 0.5591–0.5853 | LAC |
| DAL at BOS | 0.8203 | 0.1797 | conditional_research_only | 2 | 0.8260–0.8278 | BOS |
| HOU at WAS | 0.1907 | 0.8093 | conditional_research_only | 4 | 0.1785–0.1850 | HOU |
| IND at PHI | 0.7066 | 0.2934 | conditional_research_only | 1 | 0.7362–0.7362 | PHI |
| LAL at PHX | 0.4273 | 0.5727 | conditional_research_only | 4 | 0.4300–0.4567 | LAL |
| NYK at TOR | 0.5542 | 0.4458 | conditional_research_only | 16 | 0.5605–0.6176 | TOR |
| OKC at SAC | 0.1102 | 0.8898 | conditional_research_only | 4 | 0.1110–0.1203 | OKC |
| SAS at UTA | 0.1055 | 0.8945 | conditional_research_only | 4 | 0.1099–0.1211 | SAS |
| CHI at CLE | 0.8332 | 0.1668 | conditional_research_only | 8 | 0.8394–0.8458 | CLE |
| GSW at NOP | 0.4628 | 0.5372 | conditional_research_only | 32 | 0.4650–0.4817 | GSW |
| HOU at MIA | 0.3687 | 0.6313 | conditional_research_only | 4 | 0.3651–0.3912 | HOU |
| MEM at WAS | 0.5237 | 0.4763 | conditional_research_only | 8 | 0.5341–0.5506 | WAS |
| ORL at BOS | 0.8162 | 0.1838 | conditional_research_only | 2 | 0.7562–0.7690 | BOS |
| PHI at BKN | 0.2439 | 0.7561 | conditional_research_only | 4 | 0.2239–0.2254 | PHI |
| PHX at DEN | 0.6663 | 0.3337 | conditional_research_only | 1 | 0.6750–0.6750 | DEN |
| POR at MIN | 0.5969 | 0.4031 | conditional_research_only | 1 | 0.6174–0.6174 | MIN |
| CHA at LAL | 0.7837 | 0.2163 | conditional_research_only | 16 | 0.7558–0.7886 | LAL |
| DET at SAS | 0.6092 | 0.3908 | conditional_research_only | 2 | 0.6052–0.6141 | SAS |
| NYK at TOR | 0.5542 | 0.4458 | conditional_research_only | 16 | 0.5605–0.6176 | TOR |
| POR at MIN | 0.5969 | 0.4031 | conditional_research_only | 1 | 0.6174–0.6174 | MIN |
| UTA at LAC | 0.8127 | 0.1873 | conditional_research_only | 4 | 0.7576–0.7757 | LAC |

Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.

## Multi-stat availability scenarios

| Game | Status | Scenarios | Home sensitivity range | Consistent winner |
|---|---|---:|---|---|
| BOS at PHI | conditional_research_only | 1 | 0.4604–0.4604 | BOS |
| LAC at PHX | conditional_research_only | 2 | 0.6423–0.6469 | PHX |
| MIA at UTA | conditional_research_only | 4 | 0.2984–0.3514 | MIA |
| MIL at NYK | conditional_research_only | 8 | 0.8456–0.8635 | NYK |
| OKC at POR | conditional_research_only | 1 | 0.4105–0.4105 | OKC |
| ORL at SAC | conditional_research_only | 8 | 0.2821–0.3050 | ORL |
| BKN at NOP | conditional_research_only | 32 | 0.6959–0.7332 | NOP |
| BOS at TOR | conditional_research_only | 8 | 0.5248–0.5981 | TOR |
| CLE at NYK | conditional_research_only | 4 | 0.5555–0.5764 | NYK |
| DEN at MEM | conditional_research_only | 4 | 0.2093–0.2115 | DEN |
| GSW at HOU | conditional_research_only | 8 | 0.7089–0.7330 | HOU |
| LAL at MIL | conditional_research_only | 16 | 0.1912–0.2510 | LAL |
| OKC at POR | conditional_research_only | 1 | 0.4105–0.4105 | OKC |
| ORL at UTA | conditional_research_only | 4 | 0.2765–0.3007 | ORL |
| SAS at CHI | conditional_research_only | 8 | 0.1169–0.1442 | SAS |
| WAS at IND | conditional_research_only | 2 | 0.7588–0.7613 | IND |
| CHA at PHX | conditional_research_only | 4 | 0.5977–0.6327 | PHX |
| DAL at MIN | conditional_research_only | 2 | 0.7922–0.7949 | MIN |
| DET at WAS | conditional_research_only | 2 | 0.1697–0.1717 | DET |
| TOR at PHI | conditional_research_only | 8 | 0.4237–0.4978 | TOR |
| ATL at CHI | conditional_research_only | 4 | 0.2389–0.2790 | ATL |
| CLE at MIA | conditional_research_only | 4 | 0.3755–0.4208 | CLE |
| GSW at SAS | conditional_research_only | 8 | 0.7836–0.8064 | SAS |
| MEM at NOP | conditional_research_only | 32 | 0.5599–0.5939 | NOP |
| MIL at ORL | conditional_research_only | 8 | 0.7686–0.7899 | ORL |
| NYK at IND | conditional_research_only | 2 | 0.3574–0.3741 | NYK |
| OKC at LAC | conditional_research_only | 2 | 0.2511–0.2549 | OKC |
| POR at SAC | conditional_research_only | 4 | 0.2075–0.2173 | POR |
| UTA at HOU | conditional_research_only | 4 | 0.8849–0.8927 | HOU |
| BKN at MEM | conditional_research_only | 16 | 0.6950–0.7095 | MEM |
| CHI at MIN | conditional_research_only | 4 | 0.8468–0.8720 | MIN |
| DAL at CLE | conditional_research_only | 4 | 0.7901–0.7951 | CLE |
| DEN at NOP | conditional_research_only | 8 | 0.2630–0.2883 | DEN |
| DET at MIA | conditional_research_only | 2 | 0.3118–0.3508 | DET |
| ATL at MIL | conditional_research_only | 4 | 0.2617–0.2759 | ATL |
| CHA at LAC | conditional_research_only | 8 | 0.5465–0.5877 | LAC |
| DAL at BOS | conditional_research_only | 2 | 0.8038–0.8064 | BOS |
| HOU at WAS | conditional_research_only | 4 | 0.1842–0.1882 | HOU |
| IND at PHI | conditional_research_only | 1 | 0.7303–0.7303 | PHI |
| LAL at PHX | conditional_research_only | 4 | 0.4170–0.4853 | LAL |
| NYK at TOR | conditional_research_only | 16 | 0.4943–0.5861 | unresolved |
| OKC at SAC | conditional_research_only | 4 | 0.1244–0.1310 | OKC |
| SAS at UTA | conditional_research_only | 4 | 0.1153–0.1258 | SAS |
| CHI at CLE | conditional_research_only | 8 | 0.8250–0.8548 | CLE |
| GSW at NOP | conditional_research_only | 32 | 0.4230–0.4809 | GSW |
| HOU at MIA | conditional_research_only | 4 | 0.3670–0.4117 | HOU |
| MEM at WAS | conditional_research_only | 8 | 0.5027–0.5093 | WAS |
| ORL at BOS | conditional_research_only | 2 | 0.7195–0.7298 | BOS |
| PHI at BKN | conditional_research_only | 4 | 0.2269–0.2370 | PHI |
| PHX at DEN | conditional_research_only | 1 | 0.6564–0.6564 | DEN |
| POR at MIN | conditional_research_only | 1 | 0.6139–0.6139 | MIN |
| CHA at LAL | conditional_research_only | 16 | 0.7306–0.8057 | LAL |
| DET at SAS | conditional_research_only | 2 | 0.5956–0.6034 | SAS |
| NYK at TOR | conditional_research_only | 16 | 0.4943–0.5861 | unresolved |
| POR at MIN | conditional_research_only | 1 | 0.6139–0.6139 | MIN |
| UTA at LAC | conditional_research_only | 4 | 0.7445–0.7606 | LAC |
## Ensemble scenario status

{"conditional_research_only": 56}
## Implementation acceptance

Status: passed; today’s games checked: 6.
This verifies model inference and conditional injury integration. It does not establish causal injury impacts, confirmed lineups, predictive interval coverage, wagering permissions, profitability or production promotion.

- PASS: today_has_forecasts
- PASS: nba:2026-11-10:BOS:PHI:probabilities
- PASS: nba:2026-11-10:BOS:PHI:pregame
- PASS: nba:2026-11-10:BOS:PHI:provenance
- PASS: nba:2026-11-10:BOS:PHI:missingness_and_uncertainty
- PASS: nba:2026-11-10:BOS:PHI:live_roster_injury_join
- PASS: nba:2026-11-10:BOS:PHI:scenario_reproducibility
- PASS: nba:2026-11-10:BOS:PHI:scenario_probabilities
- PASS: nba:2026-11-10:LAC:PHX:probabilities
- PASS: nba:2026-11-10:LAC:PHX:pregame
- PASS: nba:2026-11-10:LAC:PHX:provenance
- PASS: nba:2026-11-10:LAC:PHX:missingness_and_uncertainty
- PASS: nba:2026-11-10:LAC:PHX:live_roster_injury_join
- PASS: nba:2026-11-10:LAC:PHX:scenario_reproducibility
- PASS: nba:2026-11-10:LAC:PHX:scenario_probabilities
- PASS: nba:2026-11-10:MIA:UTA:probabilities
- PASS: nba:2026-11-10:MIA:UTA:pregame
- PASS: nba:2026-11-10:MIA:UTA:provenance
- PASS: nba:2026-11-10:MIA:UTA:missingness_and_uncertainty
- PASS: nba:2026-11-10:MIA:UTA:live_roster_injury_join
- PASS: nba:2026-11-10:MIA:UTA:scenario_reproducibility
- PASS: nba:2026-11-10:MIA:UTA:scenario_probabilities
- PASS: nba:2026-11-10:MIL:NYK:probabilities
- PASS: nba:2026-11-10:MIL:NYK:pregame
- PASS: nba:2026-11-10:MIL:NYK:provenance
- PASS: nba:2026-11-10:MIL:NYK:missingness_and_uncertainty
- PASS: nba:2026-11-10:MIL:NYK:live_roster_injury_join
- PASS: nba:2026-11-10:MIL:NYK:scenario_reproducibility
- PASS: nba:2026-11-10:MIL:NYK:scenario_probabilities
- PASS: nba:2026-11-10:OKC:POR:probabilities
- PASS: nba:2026-11-10:OKC:POR:pregame
- PASS: nba:2026-11-10:OKC:POR:provenance
- PASS: nba:2026-11-10:OKC:POR:missingness_and_uncertainty
- PASS: nba:2026-11-10:OKC:POR:live_roster_injury_join
- PASS: nba:2026-11-10:OKC:POR:scenario_reproducibility
- PASS: nba:2026-11-10:OKC:POR:scenario_probabilities
- PASS: nba:2026-11-10:ORL:SAC:probabilities
- PASS: nba:2026-11-10:ORL:SAC:pregame
- PASS: nba:2026-11-10:ORL:SAC:provenance
- PASS: nba:2026-11-10:ORL:SAC:missingness_and_uncertainty
- PASS: nba:2026-11-10:ORL:SAC:live_roster_injury_join
- PASS: nba:2026-11-10:ORL:SAC:scenario_reproducibility
- PASS: nba:2026-11-10:ORL:SAC:scenario_probabilities