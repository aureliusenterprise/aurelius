# 026. The system can be brought back from a named snapshot

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The durable data of the system is protected against loss by backups taken on
a stated schedule, and recovery is a rehearsed path: the system can be brought
back to a named point in time by a declared procedure, not by improvisation.
Data that is deliberately not backed up is declared disposable in writing, so
"we would lose that" is a decision rather than a discovery.

Nothing is backed up today, and no restore path exists. The only protection
in the system is that storage volumes survive a container being recreated —
an accident of tooling, not a decision. This record is Proposed because the
decision, and the mechanism, do not yet exist.

## Context

The system stores things that took time to accumulate: business rows, the
configuration that makes it run, the identity data that lets people in. None
of it is reproducible from the codebase — the codebase reproduces the
machinery, never the data. A lost database today is not an outage with a
recovery; it is a permanent loss whose size nobody has measured, because
nobody has been asked what would be lost.

The system is deliberately runnable in many places — one machine, the
pipeline, eventually a customer's environment — and every one of those places
raises the same question in a different form: when the storage behind it is
lost, what comes back, how much is missing, and who performs the return. A
host failure, a bad migration, a deleted volume: none of these require
malice, and the system currently answers all three the same way — it does not
come back.

Recovery is also a trust question for anyone the system runs for. "What
happens to our data if the worst happens?" is a question every operator and
many customers will ask, and an honest answer requires that someone has
decided what is backed up, how often, and how it comes back — and has
practised the coming-back part, because an unrehearsed restore is a hope.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Every durable store is covered or declared.** Each store holding
  data that cannot be recreated is either backed up on a stated schedule or
  explicitly declared disposable; there is no third, unexamined category.
- **R2 — A restore produces a working system.** Restoring the backups into a
  clean environment yields a system that runs and whose data is consistent —
  demonstrated, not assumed.
- **R3 — Loss is bounded and stated.** The maximum amount of data a failure
  can cost is a named number, chosen rather than discovered.
- **R4 — Recovery stays inside the boundary.** Backups are operational data
  and obey the same rule as the rest: they live inside the system's own
  boundary, not a third party's convenience.
- **R5 — The path is written where it can be found.** The procedure to
  recover is documented beside the system it recovers, in the language of the
  system, not in one person's memory.
- **R6 — Cheap enough to actually run.** Backups are automatic; the schedule
  and the check that they succeeded are the system's job, not a person's.
- **R7 — Recovery time is bounded and stated.** How long it takes to bring
  the system back after a failure is a named number, measured by rehearsal,
  not estimated during the incident.

## Alternatives

- **Nothing (the status quo).** Zero cost today; the loss is discovered at
  the worst possible moment. It fails R1 — the unexamined category is
  everything — and R2, because there is nothing to rehearse. It is the
  current arrangement, described as an option.
- **Volume snapshots treated as backups.** Storage-level snapshots are easy
  and automatic. They fail R2 as usually practised: a snapshot of a running
  database is not a consistent database, and a snapshot set nobody has
  restored is untested until it is needed. They also fail R4's intent when
  the snapshot lives wherever the hosting platform puts it.
- **Backups without rehearsed restore.** Take dumps on a schedule and trust
  them. It fails R2 — the gap between "we have files" and "the system comes
  back" is exactly the gap rehearsals find — and usually fails R5, because
  the restore procedure, unpractised, stays unwritten.
- **Full disaster-recovery infrastructure** — a standby environment kept warm
  elsewhere. It answers R2 and shrinks R3's number dramatically at the cost
  of operating the system twice. For a system whose current recovery point is
  "everything", the cheap win is backups and a rehearsed restore; a warm
  standby is a different decision with a different price tag, and this record
  does not require it.
- **Do nothing, honestly labelled.** Declaring the data disposable is a
  legitimate decision while every database is a development database — but it
  must be recorded as the decision it is, with R1's written declaration, and
  revisited the first time real data arrives.

## Tradeoffs

- **Positive:** loss stops being unbounded and starts being a chosen number
  (R3), and so does the time to recover (R7); recovery becomes a procedure
  with a known duration instead of an incident with an unknown one (R2, R5);
  the trust question can be answered honestly to anyone who asks (R1, R4).
- **Negative:** backups are a standing cost that buys nothing visibly on
  every day they are not needed, which is exactly why they decay — R6 and
  rehearsal are the defence, and they are the parts people skip; a backup is
  a copy of the data, so the boundary rule (R4) now applies to the backup
  too, including who may read it; and rehearsing recovery is real time spent
  on a path the system hopes not to walk.
- **Neutral / follow-ups:** the recovery point and recovery time numbers
  belong to whoever accepts this record and must be named at acceptance, not
  deferred; backups of operational signals interact with their stated
  lifetimes ([025](./025-data-has-a-stated-lifetime.md)) — a backup older
  than a retention period is a contradiction waiting to be found; a restore
  lands on a schema version, which makes this record a consumer of the
  migration path ([023](./023-storage-schema-changes-by-recorded-migration.md));
  and the placeholder pages on backup and disaster recovery under the
  architecture section remain headings until this record is accepted and they
  are written from its answer.
