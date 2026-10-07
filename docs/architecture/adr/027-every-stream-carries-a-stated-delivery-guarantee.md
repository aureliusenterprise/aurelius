# 027. Every stream carries a stated delivery guarantee

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Every stream of business events has a stated delivery guarantee — what the
system promises about duplication and loss — and the parts that write and
read the stream are configured to honour that promise rather than to whatever
their libraries default to. Where a duplicate or a lost event would cost the
business, the guarantee is enforced by configuration a reviewer can see;
messages that cannot be delivered are parked somewhere named, not dropped in
silence.

Today no stream states a guarantee: producers run on library defaults, the
key that would give per-entity ordering is chosen in a way that defeats it,
and the one dead-letter path that exists is unconsumed. This record is
Proposed because the guarantees, and the enforcement, have not been decided.

## Context

Business facts move between parts as events: something happened here, and
everything downstream must learn about it. Once a fact travels over a network
to code the same team will write later, in another language, the possibilities
are not just "delivered" and "not delivered" — an event can arrive twice,
arrive out of order relative to its siblings, or arrive never. The business
does not get to skip this question; it can only answer it by default or by
decision.

The system carries events today with the default answer, which is roughly
"probably once, in no particular order, and good luck." That is harmless in a
demonstration and misleading as a taught example, because the example is what
a future reader copies. It is also invisible: nothing in the codebase states
what a consumer may assume, so every consumer silently assumes the friendliest
interpretation and discovers the truth during an incident.

Ordering deserves its own sentence because the system currently contradicts
itself: the design guidance tells producers to key events by entity so each
entity's history stays in order, while the shipped example keys every event
randomly, which spreads one entity's events across every partition. A consumer
that trusted the guidance would be wrong, and the guidance would not say so.

The question this record answers is what the system promises about events in
flight — per stream, in writing, enforced where it matters.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The promise is stated per stream.** For each stream, a reader can
  find what is guaranteed about duplication and loss, without asking a
  producer's author.
- **R2 — Configuration matches the promise.** The settings on writers and
  readers are the ones that make the promise true; a default that contradicts
  the promise is a defect, not a shortcut.
- **R3 — Duplication is survivable where it is allowed.** If a stream may
  duplicate, consumers can tell a repeat from a new fact; a duplicated event
  must not double-count in anything the business reads.
- **R4 — Order is promised where it matters.** Where an entity's events have
  a meaningful sequence, the arrangement keeps one entity's events in that
  sequence end to end; where it does not, the stream says so.
- **R5 — Undeliverable events land somewhere named.** A failure to deliver
  becomes a visible, inspectable pile with an owner, not a silent gap between
  what was sent and what arrived.
- **R6 — Cheap for the routine case.** A new stream inherits the stated
  defaults rather than a library's, and stating its guarantee is one line a
  reviewer sees.

## Alternatives

- **Library defaults (the status quo).** Every part inherits whatever its
  client library chose. It fails R1 — the promise is unwritten and differs
  per language — and R2, because nobody checked the defaults against any
  intent. As a taught example it is the worst option: it teaches the question
  away.
- **Exactly-once everywhere.** Strongest promise, and the libraries can
  deliver pieces of it. It fails R6: the machinery reaches into every writer,
  reader, and store, and it buys a guarantee the demonstration streams do not
  need — a promise the business cannot yet name a cost for. Strongest is not
  the same as correct.
- **At-least-once with idempotent consumers.** Deliver duplicates, make
  duplicates harmless. It satisfies R1, R2, R3, and R6 with modest machinery,
  and it is the honest shape of what the system's storage sinks already do by
  accident — upserting by identifier makes a redelivered event a no-op. It
  fails R4 unless keying is fixed, which is exactly the contradiction this
  record names.
- **Best-effort, declared.** Some streams genuinely do not care — a lost
  telemetry event is not a business loss. Declaring that is legitimate and
  passes R1; it fails R3 and R5 only if applied to streams that do care,
  which is the decision this record forces per stream.
- **Do nothing.** Costs nothing and leaves every consumer to assume the
  friendliest reading of an unwritten promise; it fails R1 by definition and
  teaches the gap to everyone who copies the example.

## Tradeoffs

- **Positive:** consumers can reason about what they will receive instead of
  hoping (R1, R2); duplicate-tolerance becomes a designed property of the
  sinks that need it rather than an accident of upserts (R3); the ordering
  guidance and the shipped example stop contradicting each other (R4);
  delivery failures become visible work rather than missing rows (R5).
- **Negative:** every guarantee has a price in throughput, latency, or
  machinery, and naming a guarantee per stream forces that price to be paid
  and argued rather than dodged; idempotent consumers must carry a notion of
  "already seen," which is state they did not need before; and a parked pile
  of undeliverable events (R5) is a queue with a human attached — someone
  owns reading it, or it becomes a landfill.
- **Neutral / follow-ups:** the shipped example currently keys events randomly
  while the design guidance prescribes keying by entity — closing that
  contradiction is this record's first act on acceptance, in whichever
  direction the guarantee for that stream turns out to be; the dead-letter
  path that exists today has no consumer and no replay procedure, and R5 is
  not satisfied until parked events can be inspected and returned; stream
  retention is a delivery question, not only a storage one — a lifetime
  shorter than the slowest consumer's recovery window silently breaks the
  guarantee, and lifetimes are owned by
  [025](./025-data-has-a-stated-lifetime.md); the compatibility of what the
  events _contain_ is decided elsewhere
  ([017](./017-shared-concepts-change-only-compatibly.md)) and this record
  covers only how the containing stream behaves; the name a stream — or a
  dead-letter stream — carries is set by the naming convention
  ([032](./032-shared-streams-are-named-by-a-declared-convention.md)); and
  authentication of the parts that speak to the stream belongs to
  [013](./013-services-prove-who-they-are-at-every-boundary.md).
