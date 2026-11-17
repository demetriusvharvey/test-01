# Retrospective top-three winner ranking

A chronological day-start replay of fixed NBA/NFL Elo on archived final scores. The archive was retrieved after these games: this is not the live published forecast record, an untouched holdout, a verified pregame injury test, or proof of wagering profit. The model does not use injuries or sportsbook prices.

| Selection | Games | Accuracy | Brier | Log loss |
|---|---:|---:|---:|---:|
| Three highest-ranked per day | 1444 | 0.7507 | 0.1765 | 0.5330 |
| Every model favorite | 4100 | 0.6615 | 0.2139 | 0.6158 |
| 50% baseline on selected games | 1444 | 0.7507 | 0.2500 | 0.6931 |

Selected days: 513. Day-block accuracy interval: [0.7275261324041812, 0.7732598208132323].

| Winner forecast range | Games | Mean forecast | Observed win rate |
|---|---:|---:|---:|
| 0.50–0.60 | 97 | 0.5597 | 0.5464 |
| 0.60–0.70 | 281 | 0.6589 | 0.6085 |
| 0.70–0.80 | 595 | 0.7514 | 0.7697 |
| 0.80–1.00 | 471 | 0.8491 | 0.8535 |

Selection favors strong favorites and accuracy alone does not establish a pricing advantage. Sources lack original pregame publication timestamps; NBA upstream gambling-use rights remain unresolved. No old outcome is added to the site’s forward winner record.

## Archived sources

- https://boxscorelab.com/downloads/2022-23-team-game-results.csv — 1230 games, SHA-256 `40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86`, archived 2026-10-28T04:04:05.730265+00:00
- https://boxscorelab.com/downloads/2023-24-team-game-results.csv — 1230 games, SHA-256 `3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce`, archived 2026-10-28T04:04:05.850963+00:00
- https://boxscorelab.com/downloads/2024-25-team-game-results.csv — 1225 games, SHA-256 `61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b`, archived 2026-10-28T04:04:06.000392+00:00
- https://boxscorelab.com/downloads/2025-26-team-game-results.csv — 1225 games, SHA-256 `f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1`, archived 2026-10-28T04:04:06.133243+00:00
- https://boxscorelab.com/downloads/2026-27-team-game-results.csv — 196 games, SHA-256 `b2cf7285abba5c3c755bedaa0febe1a871556ce579b16be0fb924af9bf80bb03`, archived 2026-11-16T16:07:08.833458+00:00
- https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv — 4470 games, SHA-256 `5357a754c00d97c448ba366226b024afb96afbae980a88f0c1a188c456b8033d`, archived 2026-10-28T04:03:50.008929+00:00

## Machine-readable results

```json
{
  "accuracy_day_block_interval": [
    0.7275261324041812,
    0.7732598208132323
  ],
  "all_model_favorites": {
    "accuracy": 0.6614634146341464,
    "brier": 0.21385686060860318,
    "games": 4100,
    "log_loss": 0.6158290163547578
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
      "accuracy": 0.7735368956743003,
      "brier": 0.159654407747717,
      "games": 393,
      "log_loss": 0.4962939959686578
    }
  },
  "by_league": {
    "NBA": {
      "accuracy": 0.7587025316455697,
      "brier": 0.17325931393105173,
      "games": 1264,
      "log_loss": 0.5257976928144787
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
      "actual_win_rate": 0.5463917525773195,
      "games": 97,
      "mean_forecast": 0.5597173640784364,
      "range": "0.50\u20130.60"
    },
    {
      "actual_win_rate": 0.608540925266904,
      "games": 281,
      "mean_forecast": 0.6589441429114082,
      "range": "0.60\u20130.70"
    },
    {
      "actual_win_rate": 0.7697478991596639,
      "games": 595,
      "mean_forecast": 0.7513608407601037,
      "range": "0.70\u20130.80"
    },
    {
      "actual_win_rate": 0.8535031847133758,
      "games": 471,
      "mean_forecast": 0.8490597647936773,
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
    "accuracy": 0.7506925207756233,
    "brier": 0.17645998095153953,
    "games": 1444,
    "log_loss": 0.5330012641970003
  },
  "selected_days": 513,
  "source_games": 9576,
  "uninformative_50_percent": {
    "accuracy": 0.7506925207756233,
    "brier": 0.25,
    "games": 1444,
    "log_loss": 0.6931471805599453
  }
}
```
