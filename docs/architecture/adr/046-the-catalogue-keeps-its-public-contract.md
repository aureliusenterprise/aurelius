# 046. The catalogue keeps its public contract while its implementation is replaced

- **Status:** Accepted
- **Date:** 2026-10-09
- **Deciders:** Aurelius Enterprise

## Decision

We will replace the implementation of the metadata catalogue without changing what its users
and integrations see: the same HTTP interface, the same request and response shapes, the same
error codes, and the same user interface. A difference visible to a client is allowed only as a
named, recorded deviation; anything not named is a defect.

The sharp edge: the old behaviour, including its quirks, is the specification. Fixing a quirk is
a deviation and needs a record, not a quiet improvement.

## Context

The catalogue is used by people through its web interface and by other systems through its HTTP
interface: ingestion jobs, lineage collectors, scripts written by data teams. Those consumers
are outside our control and many are not even known to us. The current implementation is costly
to run and to change: it needs several separate storage and indexing systems, and the team that
maintains it works mostly in a different language.

Replacing the implementation is the goal; replacing the consumers is not. Every client that has
to change multiplies the cost of the migration and delays the day the old system can be switched
off. At the same time, a replacement that is "mostly compatible" leaves each consumer to discover
the differences in production.

## Requirements

- **R1 — Existing clients keep working.** A client that works against the current catalogue works
  against the new one without being changed.
- **R2 — The user interface is reused.** People keep the screens they know; no parallel interface
  has to be built or learned during the migration.
- **R3 — Differences are known before they are met.** Every difference a client could observe is
  listed, with its reason, before it ships.
- **R4 — The migration can stop at any increment.** At every point the new system serves a
  consistent subset of the contract, so the work can pause without leaving a half-changed interface.

## Alternatives

- **Design a new, cleaner interface.** It fails R1 and R2: every consumer and the interface must be
  rewritten, and the migration ends only when the last consumer moves.
- **Keep the old interface but allow undocumented "obvious" fixes.** It fails R3: each fix is a
  surprise for a client that depended on the old behaviour.
- **Run both implementations behind a router indefinitely.** It meets R1 but doubles operating
  cost and leaves the old system in place, which is what the migration exists to end.

## Tradeoffs

- **Positive:** consumers are untouched; the old system's behaviour is a free, executable
  specification; the migration can be paused at any increment boundary (R4).
- **Negative:** we inherit the old interface's design flaws and quirks, and improving them later
  is a versioned change, not a refactor.
- **Neutral / follow-ups:** the contract is verified by comparing behaviour with the reference
  implementation ([048](./048-behaviour-is-proven-against-the-reference-before-it-is-accepted.md)).
  Current implementation: the Apache Atlas 2.4.0 REST API (`/api/atlas/v2`, `/api/atlas/admin`)
  and its two user interfaces, `dashboardv2` and `dashboardv3`; deviations are listed in
  [Deviations from Apache Atlas](../conversion/deviations.md).
