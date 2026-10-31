# Retrospective top-three winner ranking

A chronological day-start replay of fixed NBA/NFL Elo on archived final scores. The archive was retrieved after these games: this is not the live published forecast record, an untouched holdout, a verified pregame injury test, or proof of wagering profit. The model does not use injuries or sportsbook prices.

| Selection | Games | Accuracy | Brier | Log loss |
|---|---:|---:|---:|---:|
| Three highest-ranked per day | 1397 | 0.7473 | 0.1781 | 0.5368 |
| Every model favorite | 3975 | 0.6594 | 0.2146 | 0.6176 |
| 50% baseline on selected games | 1397 | 0.7473 | 0.2500 | 0.6931 |

Selected days: 497. Day-block accuracy interval: [0.725, 0.7702219040801718].

| Winner forecast range | Games | Mean forecast | Observed win rate |
|---|---:|---:|---:|
| 0.50–0.60 | 94 | 0.5595 | 0.5319 |
| 0.60–0.70 | 273 | 0.6590 | 0.6081 |
| 0.70–0.80 | 580 | 0.7515 | 0.7672 |
| 0.80–1.00 | 450 | 0.8494 | 0.8511 |

Selection favors strong favorites and accuracy alone does not establish a pricing advantage. Sources lack original pregame publication timestamps; NBA upstream gambling-use rights remain unresolved. No old outcome is added to the site’s forward winner record.

## Archived sources

- https://boxscorelab.com/downloads/2022-23-team-game-results.csv — 1230 games, SHA-256 `40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86`, archived 2026-10-28T04:04:05.730265+00:00
- https://boxscorelab.com/downloads/2023-24-team-game-results.csv — 1230 games, SHA-256 `3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce`, archived 2026-10-28T04:04:05.850963+00:00
- https://boxscorelab.com/downloads/2024-25-team-game-results.csv — 1225 games, SHA-256 `61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b`, archived 2026-10-28T04:04:06.000392+00:00
- https://boxscorelab.com/downloads/2025-26-team-game-results.csv — 1225 games, SHA-256 `f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1`, archived 2026-10-28T04:04:06.133243+00:00
- https://boxscorelab.com/downloads/2026-27-team-game-results.csv — 71 games, SHA-256 `e077cfdfc275c09b9abdd43f88d839a7352ccba32cd3cc57169052fbe99bad23`, archived 2026-10-30T19:18:42.663614+00:00
- https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv — 4470 games, SHA-256 `5357a754c00d97c448ba366226b024afb96afbae980a88f0c1a188c456b8033d`, archived 2026-10-28T04:03:50.008929+00:00

## Machine-readable results

```json
{
  "accuracy_day_block_interval": [
    0.725,
    0.7702219040801718
  ],
  "all_model_favorites": {
    "accuracy": 0.65937106918239,
    "brier": 0.2146227248544714,
    "games": 3975,
    "log_loss": 0.6176166961348298
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
      "accuracy": 0.7630057803468208,
      "brier": 0.16398103021364674,
      "games": 346,
      "log_loss": 0.5068161305307614
    }
  },
  "by_league": {
    "NBA": {
      "accuracy": 0.7551355792933443,
      "brier": 0.1750148126687908,
      "games": 1217,
      "log_loss": 0.5299286150085964
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
      "actual_win_rate": 0.5319148936170213,
      "games": 94,
      "mean_forecast": 0.5595168758632656,
      "range": "0.50\u20130.60"
    },
    {
      "actual_win_rate": 0.608058608058608,
      "games": 273,
      "mean_forecast": 0.6589962507605587,
      "range": "0.60\u20130.70"
    },
    {
      "actual_win_rate": 0.7672413793103449,
      "games": 580,
      "mean_forecast": 0.7515371979998073,
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
    "accuracy": 0.7473156764495347,
    "brier": 0.17809696972304373,
    "games": 1397,
    "log_loss": 0.5368422807791192
  },
  "selected_days": 497,
  "source_games": 9451,
  "uninformative_50_percent": {
    "accuracy": 0.7473156764495347,
    "brier": 0.25,
    "games": 1397,
    "log_loss": 0.6931471805599453
  }
}
```
