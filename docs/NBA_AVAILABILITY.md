# Optional NBA player-status context

The board's current prediction does not use NBA injury status or lineups. A
disabled-by-default connector can add descriptive player-status counts to
game details; it never changes a predicted winner or a model weight. A short
link to the NBA's current official report is always shown.

The connector calls PropLine's NBA injury endpoint and the NBA and NFL schedule
and score endpoints during a board update, only if a user has provided their own key. As of
October 28, 2026, the provider advertises a free tier and ESPN-sourced injury
status, refreshed about every 10 minutes. Our board still updates about hourly,
so the displayed counts can be older than the provider's feed. Reports may be
incomplete, and no listing is not proof that a player is healthy. No player
names or raw provider responses are stored or published by this connector.

To activate it:

1. Review [PropLine's pricing](https://prop-line.com/pricing) and
   [terms](https://prop-line.com/terms), then obtain a free key if acceptable.
   Creating a key or calling the API signifies agreement to their terms.
2. In the GitHub repository's Actions secrets, add `PROPLINE_API_KEY`. Do not
   paste a secret into a public file, an issue, or a chat.
3. Run the existing Update picks workflow or wait for its next scheduled run.
   A key automatically enables the connection; to disable it without deleting
   the key, set the Actions variable `PROPLINE_ENABLED` to `false`.
4. Check the board and the workflow logs after the run. Source outages,
   malformed payloads, future timestamps, and unknown teams are treated as
   unavailable or incomplete, not as healthy rosters. A selected PropLine
   scoreboard fails closed if unavailable; it does not fall back silently to
   the unverified direct ESPN endpoint.

Publication and retained data must remain within the provider's terms and any
upstream rights. The connector only publishes aggregate per-team status counts
for displayed games and does not write the raw league feed to either Git branch.
Validated prediction effects require rights-compatible historical availability,
lineups/minutes and outcome data, as well as forward and time-ordered tests.

The integration reserves at most 180 calls per UTC day across schedule, score,
and NBA injury requests, well below the advertised 1,000-request free limit. A
regular hourly run makes at most five calls; errors also consume the local budget.
An exhausted or unavailable budget stops calls instead of upgrading a plan.
An explicitly postponed or cancelled score status overrides an upcoming event.
Provider score rows are held in memory; only individual results for recorded
selections can be published, while supplemental results use their own sources.
