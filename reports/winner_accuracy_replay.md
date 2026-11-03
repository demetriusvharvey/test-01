# Retrospective top-three winner ranking

A chronological day-start replay of fixed NBA/NFL Elo on archived final scores. The archive was retrieved after these games: this is not the live published forecast record, an untouched holdout, a verified pregame injury test, or proof of wagering profit. The model does not use injuries or sportsbook prices.

| Selection | Games | Accuracy | Brier | Log loss |
|---|---:|---:|---:|---:|
| Three highest-ranked per day | 1406 | 0.7475 | 0.1781 | 0.5368 |
| Every model favorite | 3996 | 0.6592 | 0.2147 | 0.6178 |
| 50% baseline on selected games | 1406 | 0.7475 | 0.2500 | 0.6931 |

Selected days: 500. Day-block accuracy interval: [0.7254763585038815, 0.7703081232492998].

| Winner forecast range | Games | Mean forecast | Observed win rate |
|---|---:|---:|---:|
| 0.50–0.60 | 95 | 0.5597 | 0.5368 |
| 0.60–0.70 | 277 | 0.6591 | 0.6101 |
| 0.70–0.80 | 582 | 0.7514 | 0.7663 |
| 0.80–1.00 | 452 | 0.8494 | 0.8518 |

Selection favors strong favorites and accuracy alone does not establish a pricing advantage. Sources lack original pregame publication timestamps; NBA upstream gambling-use rights remain unresolved. No old outcome is added to the site’s forward winner record.

## Archived sources

- https://boxscorelab.com/downloads/2022-23-team-game-results.csv — 1230 games, SHA-256 `40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86`, archived 2026-10-28T04:04:05.730265+00:00
- https://boxscorelab.com/downloads/2023-24-team-game-results.csv — 1230 games, SHA-256 `3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce`, archived 2026-10-28T04:04:05.850963+00:00
- https://boxscorelab.com/downloads/2024-25-team-game-results.csv — 1225 games, SHA-256 `61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b`, archived 2026-10-28T04:04:06.000392+00:00
- https://boxscorelab.com/downloads/2025-26-team-game-results.csv — 1225 games, SHA-256 `f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1`, archived 2026-10-28T04:04:06.133243+00:00
- https://boxscorelab.com/downloads/2026-27-team-game-results.csv — 92 games, SHA-256 `535341d1c1befceeb2048bc69fa6a0e0a93936ec4d280e36811d73c18c2a81f2`, archived 2026-11-02T22:44:12.627464+00:00
- https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv — 4470 games, SHA-256 `5357a754c00d97c448ba366226b024afb96afbae980a88f0c1a188c456b8033d`, archived 2026-10-28T04:03:50.008929+00:00

## Machine-readable results

```json
{
  "accuracy_day_block_interval": [
    0.7254763585038815,
    0.7703081232492998
  ],
  "all_model_favorites": {
    "accuracy": 0.6591591591591591,
    "brier": 0.2146938128769715,
    "games": 3996,
    "log_loss": 0.617753211980167
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
      "accuracy": 0.7633802816901408,
      "brier": 0.16428223238870135,
      "games": 355,
      "log_loss": 0.5074170557207768
    }
  },
  "by_league": {
    "NBA": {
      "accuracy": 0.7553017944535073,
      "brier": 0.17502103023000457,
      "games": 1226,
      "log_loss": 0.5299329511278094
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
      "actual_win_rate": 0.5368421052631579,
      "games": 95,
      "mean_forecast": 0.5596929005178977,
      "range": "0.50\u20130.60"
    },
    {
      "actual_win_rate": 0.6101083032490975,
      "games": 277,
      "mean_forecast": 0.6591367993860787,
      "range": "0.60\u20130.70"
    },
    {
      "actual_win_rate": 0.7663230240549829,
      "games": 582,
      "mean_forecast": 0.7514200226048516,
      "range": "0.70\u20130.80"
    },
    {
      "actual_win_rate": 0.8517699115044248,
      "games": 452,
      "mean_forecast": 0.8493520650276762,
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
    "accuracy": 0.7475106685633002,
    "brier": 0.17808266198233236,
    "games": 1406,
    "log_loss": 0.5368018064478391
  },
  "selected_days": 500,
  "source_games": 9472,
  "uninformative_50_percent": {
    "accuracy": 0.7475106685633002,
    "brier": 0.25,
    "games": 1406,
    "log_loss": 0.6931471805599453
  }
}
```
