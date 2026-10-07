# 025. Data has a stated lifetime that the system enforces

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Every kind of data the system keeps has a stated lifetime, and expiry is
enforced by the system rather than left to defaults or to nobody. Data whose
lifetime has passed is removed by a mechanism, on schedule, without a person
deciding per record. A store with no stated lifetime is treated as a defect:
either its lifetime is named, or it is declared unbounded and the cost and
risk of that are owned in writing.

No lifetime is stated or enforced anywhere today — operational data sits at
library defaults, one signal's expiry is effectively switched off, and stored
business data has no declared lifetime at all. This record is Proposed
because the decision has not been made.

## Context

The system accumulates data in several kinds of place, and each grows on its
own schedule: operational signals from every part, business rows in databases,
events waiting in streams. Growth is not neutral. Storage has a cost that
arrives as a bill or a full disk; old operational data keeps answering
questions nobody asked anymore while burying the ones people do ask; and data
that can identify people or customers creates obligations that grow with the
time it is kept.

The system deliberately keeps all of this inside its own boundary — no
operational data is shipped to a hosted service — which means the
organisation that runs the system also owns the question of how long the data
lives inside that boundary. That decision was named as the owner's problem
when the boundary was drawn, and it has not been made since. Defaults are
currently making it by accident, and one default is "forever".

The question this record answers is not which tool expires what; it is who
says how long each kind of data is kept, what enforces the answer, and what
happens when the answer changes.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Every kind has a stated lifetime.** For each kind of data the system
  keeps, the period is written down where a person answering "why do you
  still have this?" can read it.
- **R2 — Expiry is automatic.** The stated lifetime is enforced by a
  mechanism on a schedule; it does not depend on anyone remembering to clean
  up.
- **R3 — Lifetimes differ by kind.** Operational signals, stored business
  data, and queued events are different kinds with different reasons to keep
  or drop; one global number is not an answer to three questions.
- **R4 — The statement is answerable.** "How long do we keep X?" has an
  answer from the system's own configuration, not from a person's memory.
- **R5 — Change is a recorded change.** Extending or shortening a lifetime is
  a deliberate, reviewable act, not a side effect of upgrading a tool.
- **R6 — Cheap to keep true.** A new store inherits a stated default lifetime
  rather than arriving with an undeclared one.

## Alternatives

- **Upstream defaults (the status quo).** Every tool keeps data for however
  long its documentation says. It fails R1 — the lifetime is whatever a
  vendor chose, which nobody read — and R4, because the answer requires
  auditing every tool's configuration. It fails R2 in one place today, where
  the default is effectively no expiry at all.
- **Keep everything forever.** The simplest policy to state and the most
  expensive to hold: it fails R1's purpose (a lifetime of infinity is the
  absence of a decision), grows cost without limit, and maximises the
  exposure of anything personal the system ever recorded.
- **Periodic manual cleanup.** A person prunes on a schedule. It fails R2 by
  definition, and R4, because what was pruned and when lives in their notes.
  Manual cleanup also fails R5 in practice: the cleanup that is skipped during
  a busy month is a silent policy change.
- **One global retention number.** Easy to state and audit. It fails R3:
  debug traces and customer records do not share a reason to exist, and a
  single number is always wrong for at least one kind — too long for the
  sensitive, too short for the useful.
- **Do nothing.** Costs nothing today and lets every tool's vendor make the
  decision per upgrade; it fails every requirement by leaving the question
  unasked, which is the current state described as a choice.

## Tradeoffs

- **Positive:** the organisation can answer retention questions about its own
  data without an audit (R1, R4); storage cost becomes bounded and predictable
  because growth is matched by enforced expiry (R2); the exposure that comes
  with keeping data is limited to a chosen period (R3); retention changes
  become visible decisions (R5).
- **Negative:** enforced expiry destroys data irreversibly, so a wrong
  lifetime is discovered after the fact — the failure mode is losing something
  that mattered, which argues for starting generous and tightening; every
  store's expiry is one more mechanism to operate and verify; and a stated
  lifetime invites the question of exceptions, which must be refused or
  recorded, not absorbed.
- **Neutral / follow-ups:** the boundary inside which these lifetimes apply is
  drawn by the observability record
  ([016](./016-the-system-observes-itself-internally.md)), which names
  retention as the operator's problem and hands it to this record; the
  lifetime of business rows in storage interacts with schema change
  ([023](./023-storage-schema-changes-by-recorded-migration.md)) — deleting
  old rows is easy, deleting old _shapes_ is a migration; queued events whose
  lifetime is shorter than the slowest consumer's recovery window turn
  retention into a delivery question owned by
  [027](./027-every-stream-carries-a-stated-delivery-guarantee.md); and the
  periods themselves — the actual numbers — belong to whoever owns each kind
  of data and must be named when this record is accepted, not later.
