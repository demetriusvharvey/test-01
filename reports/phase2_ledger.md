# Phase 2: ledger v2

New model-first paper records capture the observed best book and quote, model-only probability, a separately labeled retail median reference, price/model differences, model input snapshot and SHA-256, phase, and pending availability/timing fields. Real book taken, real price, stake and actual P&L remain unknown; a site-generated paper pick is not a wager. Legacy rows retain their original structure and meaning.

Final outcomes are checked against the event and team and append one-unit **simulated** P&L. A last-observed pregame quote at the same recorded book can be attached once with timestamps and an explicit non-certified-retail-proxy label. The price comparison is not sharp CLV. No sharp close, user return, or later adjustment to the original decision is invented. Transitions are checked against a copy of the old ledger before publication and are limited to grading or closing fields.

Paper-return summaries group by league, edge type, edge bucket, book, and pick phase. Each reports sample size; day-block intervals require 30 settled picks on 10 days. They are descriptive and do not establish an edge. Legacy rows are excluded from simulated-v2 return statistics. No empirical model comparison has passed the production bar.

Limitations: quoted initial odds are not guaranteed available, actual fills are unknown, retail snapshots may be stale or separated from true tipoff, no independent sharp close exists, and a post-inactives phase is not yet enabled. The public board still reports legacy win rate separately from the forward research scoreboard.
