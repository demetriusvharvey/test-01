# Retrospective top-three winner ranking

A chronological day-start replay of fixed NBA/NFL Elo on archived final scores. The archive was retrieved after these games: this is not the live published forecast record, an untouched holdout, a verified pregame injury test, or proof of wagering profit. The model does not use injuries or sportsbook prices.

| Selection | Games | Accuracy | Brier | Log loss |
|---|---:|---:|---:|---:|
| Three highest-ranked per day | 1468 | 0.7493 | 0.1771 | 0.5347 |
| Every model favorite | 4161 | 0.6604 | 0.2144 | 0.6172 |
| 50% baseline on selected games | 1468 | 0.7493 | 0.2500 | 0.6931 |

Selected days: 521. Day-block accuracy interval: [0.7258503401360544, 0.7710344827586207].

| Winner forecast range | Games | Mean forecast | Observed win rate |
|---|---:|---:|---:|
| 0.50–0.60 | 98 | 0.5601 | 0.5408 |
| 0.60–0.70 | 283 | 0.6590 | 0.6042 |
| 0.70–0.80 | 604 | 0.7516 | 0.7699 |
| 0.80–1.00 | 483 | 0.8493 | 0.8509 |

Selection favors strong favorites and accuracy alone does not establish a pricing advantage. Sources lack original pregame publication timestamps; NBA upstream gambling-use rights remain unresolved. No old outcome is added to the site’s forward winner record.

## Archived sources

- https://boxscorelab.com/downloads/2022-23-team-game-results.csv — 1230 games, SHA-256 `40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86`, archived 2026-10-28T04:04:05.730265+00:00
- https://boxscorelab.com/downloads/2023-24-team-game-results.csv — 1230 games, SHA-256 `3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce`, archived 2026-10-28T04:04:05.850963+00:00
- https://boxscorelab.com/downloads/2024-25-team-game-results.csv — 1225 games, SHA-256 `61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b`, archived 2026-10-28T04:04:06.000392+00:00
- https://boxscorelab.com/downloads/2025-26-team-game-results.csv — 1225 games, SHA-256 `f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1`, archived 2026-10-28T04:04:06.133243+00:00
- https://boxscorelab.com/downloads/2026-27-team-game-results.csv — 257 games, SHA-256 `7b71f8186b050bcc59f9b5f2fc0aded6d64c4baa5ca4b99dcf036c15d42130c6`, archived 2026-11-24T13:16:37.491531+00:00
- https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv — 4470 games, SHA-256 `5357a754c00d97c448ba366226b024afb96afbae980a88f0c1a188c456b8033d`, archived 2026-10-28T04:03:50.008929+00:00

## Machine-readable results

```json
{
  "accuracy_day_block_interval": [
    0.7258503401360544,
    0.7710344827586207
  ],
  "all_model_favorites": {
    "accuracy": 0.6604181687094448,
    "brier": 0.21444670094209467,
    "games": 4161,
    "log_loss": 0.6172111290244517
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
      "accuracy": 0.7673860911270983,
      "brier": 0.16302401354605864,
      "games": 417,
      "log_loss": 0.5044195891055804
    }
  },
  "by_league": {
    "NBA": {
      "accuracy": 0.7569875776397516,
      "brier": 0.174096742401167,
      "games": 1288,
      "log_loss": 0.527878658353141
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
      "actual_win_rate": 0.5408163265306123,
      "games": 98,
      "mean_forecast": 0.5601170571008677,
      "range": "0.50\u20130.60"
    },
    {
      "actual_win_rate": 0.6042402826855123,
      "games": 283,
      "mean_forecast": 0.6589889295595488,
      "range": "0.60\u20130.70"
    },
    {
      "actual_win_rate": 0.7698675496688742,
      "games": 604,
      "mean_forecast": 0.7515769190515841,
      "range": "0.70\u20130.80"
    },
    {
      "actual_win_rate": 0.8509316770186336,
      "games": 483,
      "mean_forecast": 0.8492805586157328,
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
    "accuracy": 0.7493188010899182,
    "brier": 0.1771424004753929,
    "games": 1468,
    "log_loss": 0.5347093009140417
  },
  "selected_days": 521,
  "source_games": 9637,
  "uninformative_50_percent": {
    "accuracy": 0.7493188010899182,
    "brier": 0.25,
    "games": 1468,
    "log_loss": 0.6931471805599453
  }
}
```
