# Independent scoring-process simulator evaluation

Research-only challenger. The NBA model estimates possessions from box scores rather than reconstructing play-by-play. NFL outcomes represent observed *offensive* drive scoring; defensive and return scores are not modeled. No current player availability, market prices, RotoBot outputs, or game-specific injury scenarios are used. The site does not use these probabilities for picks.

| League | Archived source games | Matched test games | Simulator Brier | Elo Brier | Simulator log loss | Elo log loss |
|---|---:|---:|---:|---:|---:|---:|
| NBA | 4962 | 52 | 0.2468 | 0.2116 | 0.6860 | 0.6087 |
| NFL | 1263 | 326 | 0.2473 | 0.2338 | 0.6886 | 0.6597 |

Matched chronological evaluation uses the same games for Elo and challenger. The seasons and sources have been inspected before; this is exploratory, not a fresh untouched holdout. Simulation count reduces sampling noise, not estimation error. NBA upstream data rights for wagering remain unresolved, so this asset is not connected to published betting opportunities. NFL pregame roster and all-position injury scenarios are missing; NFL challenger also stays research-only. No historical betting ROI is claimed.

## Source provenance

- NBA https://boxscorelab.com/downloads/2022-23-team-game-results.csv — 1230 parsed games, 2460 rows, archived 2026-10-28T04:04:05.730265+00:00, SHA-256 `40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86`, license `CC-BY-4.0; upstream NBA gambling-use terms unresolved`
- NBA https://boxscorelab.com/downloads/2023-24-team-game-results.csv — 1230 parsed games, 2460 rows, archived 2026-10-28T04:04:05.850963+00:00, SHA-256 `3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce`, license `CC-BY-4.0; upstream NBA gambling-use terms unresolved`
- NBA https://boxscorelab.com/downloads/2024-25-team-game-results.csv — 1225 parsed games, 2460 rows, archived 2026-10-28T04:04:06.000392+00:00, SHA-256 `61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b`, license `CC-BY-4.0; upstream NBA gambling-use terms unresolved`
- NBA https://boxscorelab.com/downloads/2025-26-team-game-results.csv — 1225 parsed games, 2460 rows, archived 2026-10-28T04:04:06.133243+00:00, SHA-256 `f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1`, license `CC-BY-4.0; upstream NBA gambling-use terms unresolved`
- NBA https://boxscorelab.com/downloads/2026-27-team-game-results.csv — 52 parsed games, 104 rows, archived 2026-10-28T04:04:06.242851+00:00, SHA-256 `4a3b5337bb72d910289d77cb731317399a992105d84241424972b68015846c6b`, license `CC-BY-4.0; upstream NBA gambling-use terms unresolved`
- NFL https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2021.csv.gz — 233 parsed games, 49922 rows, archived 2026-10-28T04:03:50.621124+00:00, SHA-256 `e8743a568f99667a8bdcd29ba12224ee1782ad2b7916bee78ee335c099383739`, license `CC-BY-4.0`
- NFL https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2022.csv.gz — 232 parsed games, 49434 rows, archived 2026-10-28T04:03:53.220290+00:00, SHA-256 `0c69a71eb39498956c7b1d5c1ca52ce7fe679934a95d1af249facb5ea9829ea4`, license `CC-BY-4.0`
- NFL https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2023.csv.gz — 229 parsed games, 49665 rows, archived 2026-10-28T04:03:55.819849+00:00, SHA-256 `4649804ee0f0a40b41e51ec75a1ce921949d7fab5459213488656b92f78560e8`, license `CC-BY-4.0`
- NFL https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2024.csv.gz — 241 parsed games, 49492 rows, archived 2026-10-28T04:03:58.268338+00:00, SHA-256 `23370d5d10f8104d80d46a1fc5e61f4f6f5a3263fe96fe2dd629913cfcb08c06`, license `CC-BY-4.0`
- NFL https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2025.csv.gz — 231 parsed games, 48771 rows, archived 2026-10-28T04:04:00.607205+00:00, SHA-256 `2f135887790a013fd004e609e37096bb4816d5cc80b9f19122e1bad478961978`, license `CC-BY-4.0`
- NFL https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz — 97 parsed games, 18738 rows, archived 2026-10-28T04:04:03.535035+00:00, SHA-256 `30f31f1faf184be5a3014395c6830ed81ac5f60a03790e3e4a849dc020a70396`, license `CC-BY-4.0`

## Machine-readable results

```json
{
  "NBA": {
    "evaluation": {
      "draws_per_game": 5000,
      "elo_matched": {
        "accuracy": 0.5769230769230769,
        "brier": 0.2116147533885309,
        "games": 52,
        "log_loss": 0.6087016488895803
      },
      "forecasted_games": 52,
      "simulator": {
        "accuracy": 0.5576923076923077,
        "brier": 0.24678229615384614,
        "games": 52,
        "log_loss": 0.6860316133570831
      },
      "test_seasons": [
        "2026-27"
      ],
      "winner": "elo_or_insufficient"
    },
    "observations": 4962,
    "sources": [
      {
        "license": "CC-BY-4.0; upstream NBA gambling-use terms unresolved",
        "parsed_games": 1230,
        "retrieved_at": "2026-10-28T04:04:05.730265+00:00",
        "sha256": "40b9a2c4f50d040396c53a45e86d174dcfcb0af3d8105a1c53f33432cf088a86",
        "source_rows": 2460,
        "url": "https://boxscorelab.com/downloads/2022-23-team-game-results.csv"
      },
      {
        "license": "CC-BY-4.0; upstream NBA gambling-use terms unresolved",
        "parsed_games": 1230,
        "retrieved_at": "2026-10-28T04:04:05.850963+00:00",
        "sha256": "3f181cbcc8bda22aa878e59e34f638fc10961a9af9b6aaf2d622cccb8028afce",
        "source_rows": 2460,
        "url": "https://boxscorelab.com/downloads/2023-24-team-game-results.csv"
      },
      {
        "license": "CC-BY-4.0; upstream NBA gambling-use terms unresolved",
        "parsed_games": 1225,
        "retrieved_at": "2026-10-28T04:04:06.000392+00:00",
        "sha256": "61d696baa530a865f06169be4cfc0992de731c400317e484f9fa146cd6c2321b",
        "source_rows": 2460,
        "url": "https://boxscorelab.com/downloads/2024-25-team-game-results.csv"
      },
      {
        "license": "CC-BY-4.0; upstream NBA gambling-use terms unresolved",
        "parsed_games": 1225,
        "retrieved_at": "2026-10-28T04:04:06.133243+00:00",
        "sha256": "f2872cc98025595469847db9da3210521d7ea52ab5d43ce39ffd4f1e6ffbacf1",
        "source_rows": 2460,
        "url": "https://boxscorelab.com/downloads/2025-26-team-game-results.csv"
      },
      {
        "license": "CC-BY-4.0; upstream NBA gambling-use terms unresolved",
        "parsed_games": 52,
        "retrieved_at": "2026-10-28T04:04:06.242851+00:00",
        "sha256": "4a3b5337bb72d910289d77cb731317399a992105d84241424972b68015846c6b",
        "source_rows": 104,
        "url": "https://boxscorelab.com/downloads/2026-27-team-game-results.csv"
      }
    ]
  },
  "NFL": {
    "evaluation": {
      "draws_per_game": 5000,
      "elo_matched": {
        "accuracy": 0.6012269938650306,
        "brier": 0.23377259768687136,
        "games": 326,
        "log_loss": 0.6596925315895844
      },
      "forecasted_games": 326,
      "simulator": {
        "accuracy": 0.558282208588957,
        "brier": 0.24732355966257666,
        "games": 326,
        "log_loss": 0.6885676824194161
      },
      "test_seasons": [
        "2025",
        "2026"
      ],
      "winner": "elo_or_insufficient"
    },
    "observations": 1263,
    "sources": [
      {
        "license": "CC-BY-4.0",
        "parsed_games": 233,
        "retrieved_at": "2026-10-28T04:03:50.621124+00:00",
        "sha256": "e8743a568f99667a8bdcd29ba12224ee1782ad2b7916bee78ee335c099383739",
        "source_rows": 49922,
        "url": "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2021.csv.gz"
      },
      {
        "license": "CC-BY-4.0",
        "parsed_games": 232,
        "retrieved_at": "2026-10-28T04:03:53.220290+00:00",
        "sha256": "0c69a71eb39498956c7b1d5c1ca52ce7fe679934a95d1af249facb5ea9829ea4",
        "source_rows": 49434,
        "url": "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2022.csv.gz"
      },
      {
        "license": "CC-BY-4.0",
        "parsed_games": 229,
        "retrieved_at": "2026-10-28T04:03:55.819849+00:00",
        "sha256": "4649804ee0f0a40b41e51ec75a1ce921949d7fab5459213488656b92f78560e8",
        "source_rows": 49665,
        "url": "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2023.csv.gz"
      },
      {
        "license": "CC-BY-4.0",
        "parsed_games": 241,
        "retrieved_at": "2026-10-28T04:03:58.268338+00:00",
        "sha256": "23370d5d10f8104d80d46a1fc5e61f4f6f5a3263fe96fe2dd629913cfcb08c06",
        "source_rows": 49492,
        "url": "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2024.csv.gz"
      },
      {
        "license": "CC-BY-4.0",
        "parsed_games": 231,
        "retrieved_at": "2026-10-28T04:04:00.607205+00:00",
        "sha256": "2f135887790a013fd004e609e37096bb4816d5cc80b9f19122e1bad478961978",
        "source_rows": 48771,
        "url": "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2025.csv.gz"
      },
      {
        "license": "CC-BY-4.0",
        "parsed_games": 97,
        "retrieved_at": "2026-10-28T04:04:03.535035+00:00",
        "sha256": "30f31f1faf184be5a3014395c6830ed81ac5f60a03790e3e4a849dc020a70396",
        "source_rows": 18738,
        "url": "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz"
      }
    ]
  }
}
```
