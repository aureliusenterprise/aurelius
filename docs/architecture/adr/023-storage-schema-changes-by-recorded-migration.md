# 023. A storage schema changes only by recorded migration

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Every change to the structure of stored business data is a recorded, ordered
migration that is applied the same way in every environment, and a database
can always state which migrations it has applied. A release that needs a
storage change ships that change as a reviewable artifact; nothing creates or
evolves a schema as a side effect of starting up.

The mechanism that makes this true does not exist yet — today a schema is
created automatically only where none exists, and an existing database is
never moved. This record is Proposed for exactly that reason: the decision is
that schema change becomes a recorded artifact, and the mechanism is the work
this record commissions.

## Context

Business data outlives the release that wrote it. The concepts stored in
databases keep changing — a field added, a meaning split, a table divided —
and each change has to meet data that already exists. That meeting is where
storage differs from every other artifact in the system: code can be replaced,
but rows persist, and the rows in one environment are not the rows in another.

The system releases as one versioned whole, so every release implicitly
answers the question "what does the database behind this version look like?"
Today that question is answered by a startup routine that creates tables where
they are missing and does nothing where they exist. That answer is correct
exactly once, on an empty database. The de-facto procedure for a schema change
since then is to drop the data and recreate it — acceptable while every
database is a throwaway development database, and unacceptable the first time
a database holds anything the business wants to keep.

A migration tool is already wired into the build but has never been switched
on, because no project has activated it. So the organisation holds the intent
without the decision: whether schema change is a recorded artifact, who
reviews it, and how two environments running different versions are reconciled
is re-answered by omission in every release.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Existing data is moved, not replaced.** A database holding real
  data reaches the schema a release expects without anyone deleting anything.
- **R2 — One ordered path.** Every environment reaches a given version's
  schema through the same sequence of changes, so two databases on the same
  version are structurally identical.
- **R3 — Position is knowable.** Any database can state how far along that
  path it has reached, without a person remembering.
- **R4 — The change is reviewable.** A schema change is authored, reviewed,
  and released like any other change, and can be refused before it runs.
- **R5 — Schema and concepts move together.** A change to what is stored and
  a change to the concept it stores land as one release, not as two changes
  that must be coordinated by hand.
- **R6 — Cheap for the routine case.** Adding an optional field costs a
  small recorded step, not a ceremony; a throwaway development database may
  still be created from scratch.

## Alternatives

- **Create-only startup (the status quo).** Zero cost while every database is
  disposable. It fails R1 by construction — it cannot move existing data —
  and R2, because two databases that were dropped and recreated at different
  times have no guaranteed relationship. It is a mechanism for first runs
  mistaken for a mechanism for change.
- **Hand-run SQL per environment.** A person applies statements where needed.
  It fails R2 — environments drift the first time one is patched and another
  is not — and R3, because position lives in that person's memory. It fails
  R4: statements run against a live database cannot be reviewed after.
- **Treat every database as disposable.** Honest, and true of the current
  deployment. It fails R1 the moment data is worth keeping, and R5, because
  "drop and recreate" is not a way of moving with a concept — it is a way of
  losing what the concept accumulated.
- **Do nothing (keep the dormant tooling).** The wiring suggests the decision
  was made when it was not: an unused tool is not an arrangement. It fails
  every requirement by leaving them to the next incident.

## Tradeoffs

- **Positive:** a release carries a complete answer to "what happens to the
  data" (R1, R5); environments are comparable because they share one path
  (R2, R3); schema change becomes reviewable work rather than an operational
  surprise (R4).
- **Negative:** every storage change gains a step it does not pay today, and
  in a system whose databases are all disposable that step is pure overhead
  until a real database exists; migrations are ordered artifacts, so parallel
  changes must be reconciled with each other, a cost the create-only approach
  never charges; and the team operates a migration mechanism, including its
  testing, which the startup routine got for free.
- **Neutral / follow-ups:** the dormant migration tooling in the build is
  evidence of intent, not of a decision — activating it, or replacing it with
  a mechanism that fits the stacks actually in use, is this record's first
  act on acceptance; the drop-and-recreate shortcut remains legitimate for
  throwaway development databases and must be named as such wherever it is
  documented, so it is visibly the exception and not the mechanism; and
  migrating stored data to match a changed concept — backfills, dual writes,
  the period where two shapes coexist — is a change-management question this
  record makes possible but does not answer; and the schema this record
  protects is what the retention rule ([025](./025-data-has-a-stated-lifetime.md))
  and the recovery rule
  ([026](./026-the-system-can-be-brought-back-from-a-named-snapshot.md))
  later land on — a recorded migration path is a precondition for both.
