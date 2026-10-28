# Retrospective top-three winner ranking

A chronological day-start replay of fixed NBA/NFL Elo on archived final scores. The archive was retrieved after these games: this is not the live published forecast record, an untouched holdout, a verified pregame injury test, or proof of wagering profit. The model does not use injuries or sportsbook prices.

| Selection | Games | Accuracy | Brier | Log loss |
|---|---:|---:|---:|---:|
| Three highest-ranked per day | 1388 | 0.7478 | 0.1777 | 0.5360 |
| Every model favorite | 3956 | 0.6593 | 0.2145 | 0.6174 |
| 50% baseline on selected games | 1388 | 0.7478 | 0.2500 | 0.6931 |

Selected days: 494. Day-block accuracy interval: [0.7251082251082251, 0.7693950177935943].

| Winner forecast range | Games | Mean forecast | Observed win rate |
|---|---:|---:|---:|
| 0.50–0.60 | 93 | 0.5602 | 0.5269 |
| 0.60–0.70 | 271 | 0.6591 | 0.6089 |
| 0.70–0.80 | 578 | 0.7515 | 0.7699 |
| 0.80–1.00 | 446 | 0.8493 | 0.8498 |

Selection favors strong favorites and accuracy alone does not establish a pricing advantage. Sources lack original pregame publication timestamps; NBA upstream gambling-use rights remain unresolved. No old outcome is added to the site’s forward winner record.

## Archived sources

- https://boxscorelab.com/downloads/2022-23-team-game-results.csv — 1230 games, SHA-256 `40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86`, archived 2026-10-28T04:04:05.730265+00:00
- https://boxscorelab.com/downloads/2023-24-team-game-results.csv — 1230 games, SHA-256 `3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce`, archived 2026-10-28T04:04:05.850963+00:00
- https://boxscorelab.com/downloads/2024-25-team-game-results.csv — 1225 games, SHA-256 `61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b`, archived 2026-10-28T04:04:06.000392+00:00
- https://boxscorelab.com/downloads/2025-26-team-game-results.csv — 1225 games, SHA-256 `f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1`, archived 2026-10-28T04:04:06.133243+00:00
- https://boxscorelab.com/downloads/2026-27-team-game-results.csv — 52 games, SHA-256 `4a3b5337bb72d910289d77cb731317399a992105d84241424972b68015846c6b`, archived 2026-10-28T04:04:06.242851+00:00
- https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv — 4470 games, SHA-256 `5357a754c00d97c448ba366226b024afb96afbae980a88f0c1a188c456b8033d`, archived 2026-10-28T04:03:50.008929+00:00

## Machine-readable results

```json
{
  "accuracy_day_block_interval": [
    0.7251082251082251,
    0.7693950177935943
  ],
  "all_model_favorites": {
    "accuracy": 0.6592517694641051,
    "brier": 0.21453022203091707,
    "games": 3956,
    "log_loss": 0.6174272798404677
  },
  "by_calendar_year": {
    "2024": {
      "accuracy": 0.746641074856046,
      "brier": 0.17941961690136699,
      "games": 521,
      "log_loss": 0.5387270553134316
    },
    "2025": {
      "accuracy": 0.7377358490566037,
      "brier": 0.18601209404444927,
      "games": 530,
      "log_loss": 0.5545914891820531
    },
    "2026": {
      "accuracy": 0.7655786350148368,
      "brier": 0.16196532576620107,
      "games": 337,
      "log_loss": 0.5027153063930833
    }
  },
  "by_league": {
    "NBA": {
      "accuracy": 0.7557947019867549,
      "brier": 0.1745346898569589,
      "games": 1208,
      "log_loss": 0.5289567893677878
    },
    "NFL": {
      "accuracy": 0.6944444444444444,
      "brier": 0.1989357760287427,
      "games": 180,
      "log_loss": 0.5835863432387084
    }
  },
  "first_test_date": "2024-01-01",
  "reliability": [
    {
      "actual_win_rate": 0.5268817204301075,
      "games": 93,
      "mean_forecast": 0.5601535485011532,
      "range": "0.50\u20130.60"
    },
    {
      "actual_win_rate": 0.6088560885608856,
      "games": 271,
      "mean_forecast": 0.6591419919302297,
      "range": "0.60\u20130.70"
    },
    {
      "actual_win_rate": 0.7698961937716263,
      "games": 578,
      "mean_forecast": 0.7514544707977047,
      "range": "0.70\u20130.80"
    },
    {
      "actual_win_rate": 0.8497757847533632,
      "games": 446,
      "mean_forecast": 0.8493467614400029,
      "range": "0.80\u20131.00"
    }
  ],
  "sample_game_ids": [
    "nba:2024-01-01:CHA:DEN",
    "nba:2024-01-01:DET:HOU",
    "nba:2024-01-01:IND:MIL",
    "nba:2024-01-02:CHA:SAC",
    "nba:2024-01-02:SAS:MEM"
  ],
  "selected": {
    "accuracy": 0.7478386167146974,
    "brier": 0.17769909584465424,
    "games": 1388,
    "log_loss": 0.5360413136449964
  },
  "selected_days": 494,
  "source_games": 9432,
  "uninformative_50_percent": {
    "accuracy": 0.7478386167146974,
    "brier": 0.25,
    "games": 1388,
    "log_loss": 0.6931471805599453
  }
}
```
