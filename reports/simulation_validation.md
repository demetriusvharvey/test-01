# Score-simulation challenger evaluation

The score bootstrap draws paired historical score variation around earlier team offense/defense estimates. It is not a drive, possession, player or injury simulator. It does not affect the live selection engine. Simulation count reduces Monte Carlo noise, not model error.

| League | Test seasons | Games | Simulator accuracy | Simulator Brier | Simulator log loss | Elo games | Elo Brier | Home baseline Brier |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| NBA | 2025-26, 2026-27 | 1277 | 0.5920 | 0.2369 | 0.6670 | 1277 | 0.2093 | 0.2500 |
| NFL | 2024, 2025, 2026 | 675 | 0.5941 | 0.2380 | 0.6697 | 675 | 0.2231 | 0.2500 |

These baselines may cover a slightly different set when ratings are unavailable; compare only matched games before promoting. Historical odds, lineup and injury timing are insufficient for a betting ROI or validated edge. The tested seasons have been inspected in prior research, so they are not untouched.

Archived source files (each read as the most recently archived retrospective version):

- https://boxscorelab.com/downloads/2022-23-team-game-results.csv — 1230 games; archived 2026-10-28T04:04:05.730265+00:00; SHA-256 `40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86`
- https://boxscorelab.com/downloads/2023-24-team-game-results.csv — 1230 games; archived 2026-10-28T04:04:05.850963+00:00; SHA-256 `3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce`
- https://boxscorelab.com/downloads/2024-25-team-game-results.csv — 1225 games; archived 2026-10-28T04:04:06.000392+00:00; SHA-256 `61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b`
- https://boxscorelab.com/downloads/2025-26-team-game-results.csv — 1225 games; archived 2026-10-28T04:04:06.133243+00:00; SHA-256 `f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1`
- https://boxscorelab.com/downloads/2026-27-team-game-results.csv — 52 games; archived 2026-10-28T04:04:06.242851+00:00; SHA-256 `4a3b5337bb72d910289d77cb731317399a992105d84241424972b68015846c6b`
- https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv — 4470 games; archived 2026-10-28T04:03:50.008929+00:00; SHA-256 `5357a754c00d97c448ba366226b024afb96afbae980a88f0c1a188c456b8033d`

## Machine-readable results

```json
{
  "NBA": {
    "comparison_games": 1277,
    "draws_per_game": 5000,
    "elo": {
      "accuracy": 0.6734534064212999,
      "brier": 0.20931390622386242,
      "games": 1277,
      "log_loss": 0.6069234862547711
    },
    "first_test_season": "2025-26",
    "notes": "Retrospective final-score inputs; time-ordered within the dataset, no documented pregame publication timestamps. No historical NBA odds or matched-time market comparison. This is not an untouched holdout or evidence of ROI.",
    "score_bootstrap": {
      "accuracy": 0.5920125293657008,
      "brier": 0.23690896629600625,
      "games": 1277,
      "log_loss": 0.666961026140613
    },
    "seasons": [
      "2025-26",
      "2026-27"
    ],
    "uninformative_home_baseline": {
      "accuracy": 0.5520751761942052,
      "brier": 0.25,
      "games": 1277,
      "log_loss": 0.6931471805599453
    }
  },
  "NFL": {
    "comparison_games": 675,
    "draws_per_game": 5000,
    "elo": {
      "accuracy": 0.6474074074074074,
      "brier": 0.22311480361560915,
      "games": 675,
      "log_loss": 0.6368455623484052
    },
    "first_test_season": "2024",
    "notes": "Retrospective final-score inputs; time-ordered within the dataset, no documented pregame publication timestamps. No historical NBA odds or matched-time market comparison. This is not an untouched holdout or evidence of ROI.",
    "score_bootstrap": {
      "accuracy": 0.5940740740740741,
      "brier": 0.2380101767111111,
      "games": 675,
      "log_loss": 0.6696659044819325
    },
    "seasons": [
      "2024",
      "2025",
      "2026"
    ],
    "uninformative_home_baseline": {
      "accuracy": 0.5333333333333333,
      "brier": 0.25,
      "games": 675,
      "log_loss": 0.6931471805599453
    }
  }
}
```
