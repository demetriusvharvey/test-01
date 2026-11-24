# NBA trained-model inference verification

Run: 2026-11-24T20:52:26.532468+00:00. Status: research_forecasts_recorded.
Actual scheduled games and trained efficiency logistic artifact. The baseline columns are team-only probabilities; availability ranges come from the separately trained rotation model. Conditional ranges are sensitivity checks, not confidence intervals or weighted predictions. These outputs do not replace public picks.

| Game | Baseline home probability | Baseline away probability | Availability status | Scenarios | Conditional home range | Consistent winner |
|---|---:|---:|---|---:|---|---|
| BOS at WAS | 0.1980 | 0.8020 | conditional_research_only | 2 | 0.2150–0.2150 | BOS |
| DAL at DEN | 0.7363 | 0.2637 | conditional_research_only | 2 | 0.7446–0.7499 | DEN |
| DET at ORL | 0.3944 | 0.6056 | conditional_research_only | 2 | 0.3766–0.4000 | DET |
| BKN at MIL | 0.6205 | 0.3795 | conditional_research_only | 1 | 0.6119–0.6119 | MIL |
| CHI at CHA | 0.5795 | 0.4205 | conditional_research_only | 8 | 0.5831–0.6048 | CHA |
| CLE at NYK | 0.6608 | 0.3392 | conditional_research_only | 4 | 0.6766–0.6935 | NYK |
| LAC at MEM | 0.6005 | 0.3995 | conditional_research_only | 1 | 0.6305–0.6305 | MEM |
| MIA at PHI | 0.5263 | 0.4737 | conditional_research_only | 4 | 0.5023–0.5455 | PHI |
| MIN at OKC | 0.5259 | 0.4741 | conditional_research_only | 4 | 0.4947–0.5181 | unresolved |
| PHX at HOU | 0.7080 | 0.2920 | conditional_research_only | 1 | 0.7170–0.7170 | HOU |
| SAC at GSW | 0.7523 | 0.2477 | conditional_research_only | 1 | 0.7497–0.7497 | GSW |
| SAS at POR | 0.4195 | 0.5805 | conditional_research_only | 4 | 0.3912–0.4391 | SAS |
| ATL at BOS | 0.6814 | 0.3186 | conditional_research_only | 1 | 0.6486–0.6486 | BOS |
| BKN at TOR | 0.8131 | 0.1869 | conditional_research_only | 1 | 0.8239–0.8239 | TOR |
| DAL at PHX | 0.6194 | 0.3806 | conditional_research_only | 2 | 0.6120–0.6185 | PHX |
| DEN at UTA | 0.2087 | 0.7913 | conditional_research_only | 2 | 0.2025–0.2114 | DEN |
| GSW at POR | 0.7112 | 0.2888 | conditional_research_only | 1 | 0.6984–0.6984 | POR |
| LAL at SAS | 0.6480 | 0.3520 | conditional_research_only | 4 | 0.6352–0.6797 | SAS |
| MEM at MIN | 0.7592 | 0.2408 | conditional_research_only | 1 | 0.7845–0.7845 | MIN |
| MIA at NYK | 0.6346 | 0.3654 | conditional_research_only | 8 | 0.6208–0.6606 | NYK |
| MIL at DET | 0.8755 | 0.1245 | conditional_research_only | 2 | 0.8874–0.8969 | DET |
| NOP at LAC | 0.6844 | 0.3156 | conditional_research_only | 1 | 0.6290–0.6290 | LAC |
| PHI at IND | 0.3891 | 0.6109 | conditional_research_only | 16 | 0.3621–0.3873 | PHI |
| BKN at CHA | 0.6902 | 0.3098 | conditional_research_only | 4 | 0.7081–0.7226 | CHA |
| IND at CHI | 0.5048 | 0.4952 | conditional_research_only | 16 | 0.5130–0.5251 | CHI |
| OKC at MIL | 0.2243 | 0.7757 | conditional_research_only | 4 | 0.2039–0.2195 | OKC |
| ORL at WAS | 0.3645 | 0.6355 | conditional_research_only | 2 | 0.3622–0.3622 | ORL |
| PHI at HOU | 0.6653 | 0.3347 | conditional_research_only | 2 | 0.6541–0.6717 | HOU |
| ATL at NYK | 0.6254 | 0.3746 | conditional_research_only | 4 | 0.6042–0.6227 | NYK |
| BOS at SAS | 0.5975 | 0.4025 | conditional_research_only | 4 | 0.5935–0.6402 | SAS |
| DEN at TOR | 0.4297 | 0.5703 | conditional_research_only | 1 | 0.4284–0.4284 | DEN |
| LAC at GSW | 0.6113 | 0.3887 | conditional_research_only | 1 | 0.6771–0.6771 | GSW |
| LAL at MEM | 0.3405 | 0.6595 | conditional_research_only | 1 | 0.3238–0.3238 | LAL |
| MIA at CLE | 0.5337 | 0.4663 | conditional_research_only | 2 | 0.5003–0.5240 | CLE |
| MIN at SAC | 0.1878 | 0.8122 | conditional_research_only | 1 | 0.1910–0.1910 | MIN |
| NOP at POR | 0.8359 | 0.1641 | conditional_research_only | 1 | 0.8342–0.8342 | POR |
| ORL at DET | 0.7168 | 0.2832 | conditional_research_only | 2 | 0.7106–0.7304 | DET |
| PHX at UTA | 0.3115 | 0.6885 | conditional_research_only | 2 | 0.3195–0.3314 | PHX |
| BOS at DAL | 0.2932 | 0.7068 | conditional_research_only | 2 | 0.2936–0.2993 | BOS |
| DEN at DET | 0.6080 | 0.3920 | conditional_research_only | 2 | 0.6087–0.6319 | DET |
| LAL at HOU | 0.5518 | 0.4482 | conditional_research_only | 1 | 0.5544–0.5544 | HOU |
| NOP at SAC | 0.5290 | 0.4710 | conditional_research_only | 1 | 0.5428–0.5428 | SAC |
| OKC at BKN | 0.1851 | 0.8149 | conditional_research_only | 4 | 0.1721–0.1858 | OKC |
| SAS at MIL | 0.1468 | 0.8532 | conditional_research_only | 4 | 0.1214–0.1441 | SAS |
| WAS at CHA | 0.5850 | 0.4150 | conditional_research_only | 8 | 0.5801–0.5973 | CHA |
| ATL at MIA | 0.5524 | 0.4476 | conditional_research_only | 2 | 0.5204–0.5440 | MIA |
| IND at CLE | 0.7272 | 0.2728 | conditional_research_only | 8 | 0.7198–0.7257 | CLE |
| LAC at PHX | 0.6550 | 0.3450 | conditional_research_only | 1 | 0.6912–0.6912 | PHX |
| MEM at PHI | 0.6642 | 0.3358 | conditional_research_only | 2 | 0.6752–0.6922 | PHI |
| MIN at POR | 0.5120 | 0.4880 | conditional_research_only | 1 | 0.5001–0.5001 | POR |
| NYK at CHI | 0.2708 | 0.7292 | conditional_research_only | 8 | 0.2561–0.2750 | NYK |
| TOR at HOU | 0.7066 | 0.2934 | conditional_research_only | 1 | 0.7006–0.7006 | HOU |
| UTA at GSW | 0.7245 | 0.2755 | conditional_research_only | 2 | 0.7274–0.7380 | GSW |

Each saved forecast carries model/input hashes, model and input observation times, missing inputs and uncertainty. Source freshness is limited to the archived assets. No unseen player/lineup data is manufactured.

## Multi-stat availability scenarios

| Game | Status | Scenarios | Home sensitivity range | Consistent winner |
|---|---|---:|---|---|
| BOS at WAS | conditional_research_only | 2 | 0.2093–0.2093 | BOS |
| DAL at DEN | conditional_research_only | 2 | 0.7674–0.7682 | DEN |
| DET at ORL | conditional_research_only | 2 | 0.4012–0.4326 | DET |
| BKN at MIL | conditional_research_only | 1 | 0.6502–0.6502 | MIL |
| CHI at CHA | conditional_research_only | 8 | 0.5010–0.5475 | CHA |
| CLE at NYK | conditional_research_only | 4 | 0.7017–0.7333 | NYK |
| LAC at MEM | conditional_research_only | 1 | 0.6119–0.6119 | MEM |
| MIA at PHI | conditional_research_only | 4 | 0.5152–0.5934 | PHI |
| MIN at OKC | conditional_research_only | 4 | 0.5175–0.5354 | OKC |
| PHX at HOU | conditional_research_only | 1 | 0.6843–0.6843 | HOU |
| SAC at GSW | conditional_research_only | 1 | 0.7627–0.7627 | GSW |
| SAS at POR | conditional_research_only | 4 | 0.3838–0.4164 | SAS |
| ATL at BOS | conditional_research_only | 1 | 0.6358–0.6358 | BOS |
| BKN at TOR | conditional_research_only | 1 | 0.8270–0.8270 | TOR |
| DAL at PHX | conditional_research_only | 2 | 0.6605–0.6615 | PHX |
| DEN at UTA | conditional_research_only | 2 | 0.2105–0.2166 | DEN |
| GSW at POR | conditional_research_only | 1 | 0.6755–0.6755 | POR |
| LAL at SAS | conditional_research_only | 4 | 0.6822–0.7109 | SAS |
| MEM at MIN | conditional_research_only | 1 | 0.7727–0.7727 | MIN |
| MIA at NYK | conditional_research_only | 8 | 0.6724–0.7284 | NYK |
| MIL at DET | conditional_research_only | 2 | 0.8776–0.8908 | DET |
| NOP at LAC | conditional_research_only | 1 | 0.6377–0.6377 | LAC |
| PHI at IND | conditional_research_only | 16 | 0.3635–0.4189 | PHI |
| BKN at CHA | conditional_research_only | 4 | 0.7290–0.7424 | CHA |
| IND at CHI | conditional_research_only | 16 | 0.5332–0.5690 | CHI |
| OKC at MIL | conditional_research_only | 4 | 0.2121–0.2244 | OKC |
| ORL at WAS | conditional_research_only | 2 | 0.3335–0.3335 | ORL |
| PHI at HOU | conditional_research_only | 2 | 0.6113–0.6590 | HOU |
| ATL at NYK | conditional_research_only | 4 | 0.6383–0.6734 | NYK |
| BOS at SAS | conditional_research_only | 4 | 0.6186–0.6501 | SAS |
| DEN at TOR | conditional_research_only | 1 | 0.3992–0.3992 | DEN |
| LAC at GSW | conditional_research_only | 1 | 0.6819–0.6819 | GSW |
| LAL at MEM | conditional_research_only | 1 | 0.3512–0.3512 | LAL |
| MIA at CLE | conditional_research_only | 2 | 0.5282–0.5558 | CLE |
| MIN at SAC | conditional_research_only | 1 | 0.2081–0.2081 | MIN |
| NOP at POR | conditional_research_only | 1 | 0.8267–0.8267 | POR |
| ORL at DET | conditional_research_only | 2 | 0.6833–0.7106 | DET |
| PHX at UTA | conditional_research_only | 2 | 0.3113–0.3193 | PHX |
| BOS at DAL | conditional_research_only | 2 | 0.2819–0.2829 | BOS |
| DEN at DET | conditional_research_only | 2 | 0.5908–0.6216 | DET |
| LAL at HOU | conditional_research_only | 1 | 0.5723–0.5723 | HOU |
| NOP at SAC | conditional_research_only | 1 | 0.5400–0.5400 | SAC |
| OKC at BKN | conditional_research_only | 4 | 0.1567–0.1664 | OKC |
| SAS at MIL | conditional_research_only | 4 | 0.1236–0.1391 | SAS |
| WAS at CHA | conditional_research_only | 8 | 0.5890–0.6055 | CHA |
| ATL at MIA | conditional_research_only | 2 | 0.4966–0.5244 | unresolved |
| IND at CLE | conditional_research_only | 8 | 0.7063–0.7119 | CLE |
| LAC at PHX | conditional_research_only | 1 | 0.6975–0.6975 | PHX |
| MEM at PHI | conditional_research_only | 2 | 0.6780–0.7212 | PHI |
| MIN at POR | conditional_research_only | 1 | 0.5164–0.5164 | POR |
| NYK at CHI | conditional_research_only | 8 | 0.2478–0.3022 | NYK |
| TOR at HOU | conditional_research_only | 1 | 0.7116–0.7116 | HOU |
| UTA at GSW | conditional_research_only | 2 | 0.7379–0.7449 | GSW |
## Ensemble scenario status

{"conditional_research_only": 53}
## Implementation acceptance

Status: passed; today’s games checked: 3.
This verifies model inference and conditional injury integration. It does not establish causal injury impacts, confirmed lineups, predictive interval coverage, wagering permissions, profitability or production promotion.

- PASS: today_has_forecasts
- PASS: nba:2026-11-24:BOS:WAS:probabilities
- PASS: nba:2026-11-24:BOS:WAS:pregame
- PASS: nba:2026-11-24:BOS:WAS:provenance
- PASS: nba:2026-11-24:BOS:WAS:missingness_and_uncertainty
- PASS: nba:2026-11-24:BOS:WAS:live_roster_injury_join
- PASS: nba:2026-11-24:BOS:WAS:scenario_reproducibility
- PASS: nba:2026-11-24:BOS:WAS:scenario_probabilities
- PASS: nba:2026-11-24:DAL:DEN:probabilities
- PASS: nba:2026-11-24:DAL:DEN:pregame
- PASS: nba:2026-11-24:DAL:DEN:provenance
- PASS: nba:2026-11-24:DAL:DEN:missingness_and_uncertainty
- PASS: nba:2026-11-24:DAL:DEN:live_roster_injury_join
- PASS: nba:2026-11-24:DAL:DEN:scenario_reproducibility
- PASS: nba:2026-11-24:DAL:DEN:scenario_probabilities
- PASS: nba:2026-11-24:DET:ORL:probabilities
- PASS: nba:2026-11-24:DET:ORL:pregame
- PASS: nba:2026-11-24:DET:ORL:provenance
- PASS: nba:2026-11-24:DET:ORL:missingness_and_uncertainty
- PASS: nba:2026-11-24:DET:ORL:live_roster_injury_join
- PASS: nba:2026-11-24:DET:ORL:scenario_reproducibility
- PASS: nba:2026-11-24:DET:ORL:scenario_probabilities