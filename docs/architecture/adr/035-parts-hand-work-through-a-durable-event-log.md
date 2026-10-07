# 035. Parts hand work to each other through a durable event log

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Business events — the record of what happened — flow between parts through a
durable, replayable event log, and that log is the default way one part makes a
fact available to others. A part may still answer a caller directly when a
person is waiting; the log is where the shared record lives, not a copy of
every request. A new part that needs an existing fact subscribes to the log
rather than asking the part that produced it.

This decision was already in force before it was written down: the development
arrangement starts the platform, the examples produce events to it and consume
them from it, and a sink carries those events into storage. What this record
adds is the rule itself — that the log is the default integration substrate and
that joining the system is a subscription, not a new bridge between two parts.

## Context

The system is made of parts that were built separately and must keep working
together as they are added and removed. When one part learns something the
business cares about, that fact has to reach the parts that act on it and the
places that keep it. The question is how the fact travels.

The cheapest answer — the caller calls the next part directly — binds the two
together: the caller must know the callee, reach it now, and be changed again
when a new reader appears. As parts come and go, that binding becomes the cost
of every change. A shared table is another answer, but it shows only the state
right now, not the ordered record of what happened, so a part that starts late
cannot catch up on what it missed.

The system is also meant to run whole on one machine and be validated against
real services, so whatever carries the facts must run there too, not only in a
hosted deployment. And because the examples are how the organisation teaches,
the way facts move in an example is the way the next system will move them.

The decision to make is what carries the shared record of what happened, and
what a part must do to make a fact available or to consume one.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Producer and consumer are not tied together in time or knowledge.** A
  part can make a fact available without knowing which parts will use it or
  whether they are running now.
- **R2 — The record is durable and replayable.** A part that starts later, or
  recovers from a stop, can catch up on what it missed rather than seeing only
  the state that remains.
- **R3 — One fact can reach many users without the producer changing.** Adding
  a reader does not rewrite the writer.
- **R4 — Joining the system is a subscription, not a bridge.** A new part that
  needs an existing fact consumes it rather than forcing new wiring into the
  part that produced it.
- **R5 — The arrangement runs where the system is built and validated.** The
  event path is live on one machine and in the pipeline, not only in a hosted
  deployment.
- **R6 — Removing a part does not strand what it produced or consumed.** The
  record outlives the parts that used it.
- **R7 — A person waiting is served directly.** The log carries the shared
  record of what happened; it does not replace the immediate answer an
  interactive surface needs.

## Alternatives

- **Direct calls between parts only.** Each part calls the next by name. It
  fails R1 — the caller must know and reach the callee now — R3, because a new
  reader means changing the writer, and R4, because every new consumer is new
  wiring in an existing part.
- **A shared store as the medium.** Parts meet by reading and writing common
  tables. It fails R2: a table shows the current state, not the ordered record
  of what happened, so a late or recovered part cannot replay what it missed;
  and it ties every reader to one shape at once.
- **Ad hoc integration per pair.** Each connection is built when a need
  appears. It fails R4 and R6 — the wiring is bespoke and the record is
  whatever the pair privately agreed, so removing a part can strand it.
- **Do nothing (each part chooses).** It costs nothing today and lets the
  cheapest local answer win; it fails R1 and R4 by default, because the default
  becomes a direct call and joining the system means touching parts that
  already work.

## Tradeoffs

- **Positive:** parts are decoupled in time and in what they must know of each
  other (R1, R4); one fact serves many users without rework (R3); a late or
  recovered part can catch up rather than guess (R2); a part removed leaves the
  record intact (R6).
- **Negative:** the log is infrastructure to run and to understand, and it
  joins what a new joiner must learn; a fact reaches a reader a moment after it
  happens rather than instantly, so parts must tolerate brief lag; debugging
  "the fact has not arrived yet" is harder than debugging a call that failed
  loudly; and an example that skips the platform teaches the wrong shape.
- **Neutral / follow-ups:** the guarantee a single stream gives is owned by the
  delivery-guarantee record
  ([027](./027-every-stream-carries-a-stated-delivery-guarantee.md)), the
  naming of streams by the naming record
  ([032](./032-shared-streams-are-named-by-a-declared-convention.md)), the
  compatibility of the events themselves by the shared-concept record
  ([017](./017-shared-concepts-change-only-compatibly.md)), and the canonical
  shape of the concept an event carries by the domain-model record
  ([004](./004-one-shared-domain-model.md)); the platform running on one
  machine and in the pipeline is the arrangement the whole-system record
  already requires
  ([006](./006-the-whole-system-runs-on-one-machine.md)). The placeholder pages
  on data pipelines and on integration methods under the architecture section
  remain headings until written from this answer; where a part integrates by a
  direct call today rather than joining the log, that is a named deviation to
  be either justified or brought in line.
