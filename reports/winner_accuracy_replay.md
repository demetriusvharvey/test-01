# Retrospective top-three winner ranking

A chronological day-start replay of fixed NBA/NFL Elo on archived final scores. The archive was retrieved after these games: this is not the live published forecast record, an untouched holdout, a verified pregame injury test, or proof of wagering profit. The model does not use injuries or sportsbook prices.

| Selection | Games | Accuracy | Brier | Log loss |
|---|---:|---:|---:|---:|
| Three highest-ranked per day | 1394 | 0.7475 | 0.1778 | 0.5361 |
| Every model favorite | 3972 | 0.6594 | 0.2145 | 0.6174 |
| 50% baseline on selected games | 1394 | 0.7475 | 0.2500 | 0.6931 |

Selected days: 496. Day-block accuracy interval: [0.7246065808297568, 0.7705035971223022].

| Winner forecast range | Games | Mean forecast | Observed win rate |
|---|---:|---:|---:|
| 0.50–0.60 | 93 | 0.5602 | 0.5269 |
| 0.60–0.70 | 272 | 0.6592 | 0.6066 |
| 0.70–0.80 | 579 | 0.7515 | 0.7686 |
| 0.80–1.00 | 450 | 0.8494 | 0.8511 |

Selection favors strong favorites and accuracy alone does not establish a pricing advantage. Sources lack original pregame publication timestamps; NBA upstream gambling-use rights remain unresolved. No old outcome is added to the site’s forward winner record.

## Archived sources

- https://boxscorelab.com/downloads/2022-23-team-game-results.csv — 1230 games, SHA-256 `40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86`, archived 2026-10-28T04:04:05.730265+00:00
- https://boxscorelab.com/downloads/2023-24-team-game-results.csv — 1230 games, SHA-256 `3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce`, archived 2026-10-28T04:04:05.850963+00:00
- https://boxscorelab.com/downloads/2024-25-team-game-results.csv — 1225 games, SHA-256 `61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b`, archived 2026-10-28T04:04:06.000392+00:00
- https://boxscorelab.com/downloads/2025-26-team-game-results.csv — 1225 games, SHA-256 `f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1`, archived 2026-10-28T04:04:06.133243+00:00
- https://boxscorelab.com/downloads/2026-27-team-game-results.csv — 68 games, SHA-256 `e786108261eb1044225c34f4e3beb0f7115399ce83f01e9017e3cf4ec22dcb6e`, archived 2026-10-29T18:57:43.768736+00:00
- https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv — 4470 games, SHA-256 `5357a754c00d97c448ba366226b024afb96afbae980a88f0c1a188c456b8033d`, archived 2026-10-28T04:03:50.008929+00:00

## Machine-readable results

```json
{
  "accuracy_day_block_interval": [
    0.7246065808297568,
    0.7705035971223022
  ],
  "all_model_favorites": {
    "accuracy": 0.6593655589123867,
    "brier": 0.21453700237139103,
    "games": 3972,
    "log_loss": 0.6174227005668756
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
      "accuracy": 0.7638483965014577,
      "brier": 0.16254541859056348,
      "games": 343,
      "log_loss": 0.5036005267618807
    }
  },
  "by_league": {
    "NBA": {
      "accuracy": 0.7553542009884678,
      "brier": 0.17463646551940684,
      "games": 1214,
      "log_loss": 0.5290772026203819
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
      "actual_win_rate": 0.6066176470588235,
      "games": 272,
      "mean_forecast": 0.6592063670182038,
      "range": "0.60\u20130.70"
    },
    {
      "actual_win_rate": 0.768566493955095,
      "games": 579,
      "mean_forecast": 0.7515242458419821,
      "range": "0.70\u20130.80"
    },
    {
      "actual_win_rate": 0.8511111111111112,
      "games": 450,
      "mean_forecast": 0.8494118475235471,
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
    "accuracy": 0.7474892395982783,
    "brier": 0.17777410963108578,
    "games": 1394,
    "log_loss": 0.5361156856270525
  },
  "selected_days": 496,
  "source_games": 9448,
  "uninformative_50_percent": {
    "accuracy": 0.7474892395982783,
    "brier": 0.25,
    "games": 1394,
    "log_loss": 0.6931471805599453
  }
}
```
