# Phase 14: engineering

The pipeline has an append-only odds and forecast archive, frozen and hashed pick inputs, a versioned active feature registry, time-order and immutability checks, per-source isolation, a scheduler heartbeat, structured run summaries and tests covering the new research modules. Public non-metered data requests retry transient failures with bounded backoff; permanent HTTP failures fail promptly. The optional metered odds client has its own quota controls and does not acquire extra retry calls.

Python 3.12 is configured in workflows with pinned setup action revisions; the application uses only the standard library and has no pip packages to install. A separate read-only CI job tests Python and checks the browser script syntax on pushes and pull requests. Local setup and architecture are documented in the README.

Known engineering work remains: fully automated point-in-time lineage for each external source, more recorded real-provider fixtures and operational alerts, complete leakage tests for every future model, a qualified low-latency data source, and scaling the append-only git/SQLite store as history grows. Daily GitHub schedules and the underlying public odds pages are not a minute-by-minute feed.
