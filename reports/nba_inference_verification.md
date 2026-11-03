# NBA trained-model inference verification

Run: 2026-11-03T18:02:23.537696+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.

| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |
|---|---:|---:|---|---:|---|---|
| ATL at WAS | 0.2655 | 0.7345 | conditional_research_only | 16 | 0.2549–0.2730 | ATL |
| CHA at BKN | 0.2306 | 0.7694 | conditional_research_only | 1 | 0.2078–0.2078 | CHA |
| CHI at NYK | 0.8132 | 0.1868 | conditional_research_only | 1 | 0.8342–0.8342 | NYK |
| CLE at OKC | 0.7065 | 0.2935 | conditional_research_only | 4 | 0.7004–0.7073 | OKC |
| DAL at SAS | 0.8228 | 0.1772 | conditional_research_only | 4 | 0.8223–0.8344 | SAS |
| IND at MEM | 0.5498 | 0.4502 | scenario_limit_exceeded | 0 | unavailable | unresolved |
| LAL at SAC | 0.2087 | 0.7913 | conditional_research_only | 1 | 0.1841–0.1841 | LAL |
| MIA at LAC | 0.5265 | 0.4735 | conditional_research_only | 4 | 0.4785–0.4866 | MIA |
| MIL at BOS | 0.8703 | 0.1297 | conditional_research_only | 2 | 0.8834–0.8850 | BOS |
| MIN at HOU | 0.6108 | 0.3892 | conditional_research_only | 4 | 0.5769–0.5914 | HOU |
| PHI at DET | 0.7320 | 0.2680 | conditional_research_only | 1 | 0.7342–0.7342 | DET |
| POR at PHX | 0.4959 | 0.5041 | conditional_research_only | 2 | 0.5056–0.5077 | PHX |
| TOR at DEN | 0.6427 | 0.3573 | conditional_research_only | 2 | 0.6121–0.6210 | DEN |
| UTA at NOP | 0.7240 | 0.2760 | conditional_research_only | 1 | 0.7038–0.7038 | NOP |
| MIA at GSW | 0.4551 | 0.5449 | conditional_research_only | 8 | 0.4376–0.4513 | MIA |
| ORL at PHX | 0.6703 | 0.3297 | conditional_research_only | 4 | 0.5975–0.6117 | PHX |
| BOS at CHA | 0.4246 | 0.5754 | conditional_research_only | 2 | 0.4210–0.4248 | BOS |
| MIN at NOP | 0.3389 | 0.6611 | conditional_research_only | 2 | 0.2938–0.3044 | MIN |
| OKC at MEM | 0.1780 | 0.8220 | conditional_research_only | 4 | 0.1683–0.1713 | OKC |
| PHI at CLE | 0.5976 | 0.4024 | conditional_research_only | 4 | 0.5502–0.5584 | CLE |
| POR at LAL | 0.5516 | 0.4484 | conditional_research_only | 1 | 0.5582–0.5582 | LAL |
| SAS at SAC | 0.1243 | 0.8757 | conditional_research_only | 1 | 0.0944–0.0944 | SAS |
| TOR at MIL | 0.2653 | 0.7347 | conditional_research_only | 2 | 0.2267–0.2334 | TOR |
| UTA at DAL | 0.7454 | 0.2546 | conditional_research_only | 4 | 0.7481–0.7638 | DAL |
| WAS at ATL | 0.8201 | 0.1799 | conditional_research_only | 16 | 0.8134–0.8272 | ATL |
| BKN at ATL | 0.8750 | 0.1250 | conditional_research_only | 4 | 0.8587–0.8657 | ATL |
| DEN at IND | 0.2449 | 0.7551 | insufficient_rotation_history | 0 | unavailable | unresolved |
| HOU at PHX | 0.4216 | 0.5784 | conditional_research_only | 4 | 0.4159–0.4203 | HOU |
| NYK at CLE | 0.5381 | 0.4619 | conditional_research_only | 4 | 0.4840–0.4923 | NYK |
| ORL at GSW | 0.5365 | 0.4635 | conditional_research_only | 16 | 0.4584–0.4848 | ORL |
| SAS at POR | 0.4191 | 0.5809 | conditional_research_only | 1 | 0.3746–0.3746 | SAS |
| WAS at OKC | 0.8944 | 0.1056 | conditional_research_only | 4 | 0.9028–0.9058 | OKC |
| BKN at DAL | 0.7594 | 0.2406 | conditional_research_only | 4 | 0.7771–0.7915 | DAL |
| BOS at MIL | 0.1972 | 0.8028 | conditional_research_only | 2 | 0.1754–0.1776 | BOS |
| LAL at DET | 0.6692 | 0.3308 | conditional_research_only | 1 | 0.6987–0.6987 | DET |
| MIA at SAC | 0.3019 | 0.6981 | conditional_research_only | 1 | 0.2565–0.2565 | MIA |
| NOP at LAC | 0.6286 | 0.3714 | conditional_research_only | 4 | 0.6130–0.6207 | LAC |
| PHI at CHI | 0.2960 | 0.7040 | conditional_research_only | 1 | 0.2678–0.2678 | PHI |
| UTA at MIN | 0.8679 | 0.1321 | conditional_research_only | 2 | 0.8742–0.8796 | MIN |
| CLE at CHA | 0.5044 | 0.4956 | conditional_research_only | 4 | 0.5299–0.5382 | CHA |
| DEN at HOU | 0.6162 | 0.3838 | conditional_research_only | 2 | 0.6156–0.6179 | HOU |
| IND at DAL | 0.6050 | 0.3950 | scenario_limit_exceeded | 0 | unavailable | unresolved |
| LAL at ATL | 0.5260 | 0.4740 | conditional_research_only | 4 | 0.4766–0.4913 | LAL |
| MEM at TOR | 0.8140 | 0.1860 | conditional_research_only | 8 | 0.8448–0.8524 | TOR |
| NOP at GSW | 0.5933 | 0.4067 | conditional_research_only | 8 | 0.6091–0.6222 | GSW |
| SAS at PHX | 0.3251 | 0.6749 | conditional_research_only | 2 | 0.2921–0.2939 | SAS |
| WAS at DET | 0.8926 | 0.1074 | conditional_research_only | 4 | 0.9174–0.9200 | DET |
| BOS at PHI | 0.4122 | 0.5878 | conditional_research_only | 2 | 0.4186–0.4224 | BOS |
| LAC at PHX | 0.5625 | 0.4375 | conditional_research_only | 8 | 0.5779–0.5879 | PHX |
| MIA at UTA | 0.3216 | 0.6784 | conditional_research_only | 1 | 0.3164–0.3164 | MIA |
| MIL at NYK | 0.8236 | 0.1764 | conditional_research_only | 1 | 0.8496–0.8496 | NYK |
| OKC at POR | 0.4210 | 0.5790 | conditional_research_only | 1 | 0.4243–0.4243 | OKC |
| ORL at SAC | 0.3127 | 0.6873 | conditional_research_only | 2 | 0.2181–0.2268 | ORL |

Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.

## Multi-stat availability scenarios

| Game | Status | Scenarios | Home sensitivity range | Consistent winner |
|---|---|---:|---|---|
| ATL at WAS | conditional_research_only | 16 | 0.2657–0.2938 | ATL |
| CHA at BKN | conditional_research_only | 1 | 0.2455–0.2455 | CHA |
| CHI at NYK | conditional_research_only | 1 | 0.8350–0.8350 | NYK |
| CLE at OKC | conditional_research_only | 4 | 0.6530–0.6770 | OKC |
| DAL at SAS | conditional_research_only | 4 | 0.8143–0.8271 | SAS |
| IND at MEM | scenario_limit_exceeded | 0 | unavailable | unresolved |
| LAL at SAC | conditional_research_only | 1 | 0.1814–0.1814 | LAL |
| MIA at LAC | conditional_research_only | 4 | 0.4682–0.4808 | MIA |
| MIL at BOS | conditional_research_only | 2 | 0.8712–0.8736 | BOS |
| MIN at HOU | conditional_research_only | 4 | 0.5238–0.5497 | HOU |
| PHI at DET | conditional_research_only | 1 | 0.7537–0.7537 | DET |
| POR at PHX | conditional_research_only | 2 | 0.5126–0.5169 | PHX |
| TOR at DEN | conditional_research_only | 2 | 0.6046–0.6164 | DEN |
| UTA at NOP | conditional_research_only | 1 | 0.6917–0.6917 | NOP |
| MIA at GSW | conditional_research_only | 8 | 0.4165–0.4581 | MIA |
| ORL at PHX | conditional_research_only | 4 | 0.5538–0.5681 | PHX |
| BOS at CHA | conditional_research_only | 2 | 0.3855–0.3908 | BOS |
| MIN at NOP | conditional_research_only | 2 | 0.2627–0.2829 | MIN |
| OKC at MEM | conditional_research_only | 4 | 0.2162–0.2243 | OKC |
| PHI at CLE | conditional_research_only | 4 | 0.5474–0.5739 | CLE |
| POR at LAL | conditional_research_only | 1 | 0.5668–0.5668 | LAL |
| SAS at SAC | conditional_research_only | 1 | 0.0964–0.0964 | SAS |
| TOR at MIL | conditional_research_only | 2 | 0.2838–0.2940 | TOR |
| UTA at DAL | conditional_research_only | 4 | 0.7424–0.7586 | DAL |
| WAS at ATL | conditional_research_only | 16 | 0.7982–0.8197 | ATL |
| BKN at ATL | conditional_research_only | 4 | 0.8334–0.8419 | ATL |
| DEN at IND | insufficient_rotation_history | 0 | unavailable | unresolved |
| HOU at PHX | conditional_research_only | 4 | 0.4344–0.4392 | HOU |
| NYK at CLE | conditional_research_only | 4 | 0.4781–0.5051 | unresolved |
| ORL at GSW | conditional_research_only | 16 | 0.3875–0.4384 | ORL |
| SAS at POR | conditional_research_only | 1 | 0.3771–0.3771 | SAS |
| WAS at OKC | conditional_research_only | 4 | 0.8902–0.8975 | OKC |
| BKN at DAL | conditional_research_only | 4 | 0.7725–0.7873 | DAL |
| BOS at MIL | conditional_research_only | 2 | 0.1923–0.1957 | BOS |
| LAL at DET | conditional_research_only | 1 | 0.7135–0.7135 | DET |
| MIA at SAC | conditional_research_only | 1 | 0.2585–0.2585 | MIA |
| NOP at LAC | conditional_research_only | 4 | 0.5991–0.6112 | LAC |
| PHI at CHI | conditional_research_only | 1 | 0.2703–0.2703 | PHI |
| UTA at MIN | conditional_research_only | 2 | 0.8794–0.8899 | MIN |
| CLE at CHA | conditional_research_only | 4 | 0.4814–0.5084 | unresolved |
| DEN at HOU | conditional_research_only | 2 | 0.6549–0.6554 | HOU |
| IND at DAL | scenario_limit_exceeded | 0 | unavailable | unresolved |
| LAL at ATL | conditional_research_only | 4 | 0.4398–0.4551 | LAL |
| MEM at TOR | conditional_research_only | 8 | 0.7917–0.8072 | TOR |
| NOP at GSW | conditional_research_only | 8 | 0.5839–0.6244 | GSW |
| SAS at PHX | conditional_research_only | 2 | 0.2999–0.3035 | SAS |
| WAS at DET | conditional_research_only | 4 | 0.9262–0.9313 | DET |
| BOS at PHI | conditional_research_only | 2 | 0.4161–0.4215 | BOS |
| LAC at PHX | conditional_research_only | 8 | 0.5911–0.6073 | PHX |
| MIA at UTA | conditional_research_only | 1 | 0.3336–0.3336 | MIA |
| MIL at NYK | conditional_research_only | 1 | 0.8352–0.8352 | NYK |
| OKC at POR | conditional_research_only | 1 | 0.4641–0.4641 | OKC |
| ORL at SAC | conditional_research_only | 2 | 0.1872–0.1934 | ORL |
## Ensemble scenario status

{"conditional_research_only": 50, "ensemble_component_unavailable": 3}
## Implementation acceptance

Status: incomplete; today’s games checked: 0.
This verifies model inference and conditional injury integration. It does not establish causal injury impacts, confirmed lineups, predictive interval coverage, wagering permissions, profitability or production promotion.

- MISSING: today_has_forecasts