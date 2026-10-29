# Player-impact training status

Checked 2026-10-29T18:54:58.209923+00:00.
This job never changes public picks. Counts are unique eligible games, not repeated forecast snapshots.

| League | Input records | Eligible games | Seasons | Status |
|---|---:|---:|---:|---|
| NBA | 0 | 0 | 0 | insufficient verified input |
| NFL | 0 | 0 | 0 | insufficient verified input |

Required input: observations/player_exposures.json with verified pregame expected shares, player/team identities, roster verification, source-use qualification and chronological observation/result timestamps. Final minutes/snaps are not accepted as pregame projections. No source is enabled or approved by the presence of this file. Missing data remains missing.

Default thresholds: three seasons, 500 earlier training games, 100 later validation games, 20 training appearances per estimated player. Unknown-player effects remain unavailable. No trained player model or improvement is implied when these thresholds fail.
