# 037. The system itself promises nothing about staying up

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Availability is not a property the system carries; it is a property the
adopting deployment builds around it. The system promises no uptime of its
own, and the rule has two halves: the system must not fake availability — no
page, guide, or example may claim resilience the arrangement does not provide
— and it must not prevent availability — a part holds no private state that
would pin it to one instance, and state that must exist lives in named stores
a deployment can protect. What the system does promise about loss and
downtime is the recovery promise, owned by the snapshot record
([026](./026-the-system-can-be-brought-back-from-a-named-snapshot.md)), not a
prevention promise.

This decision was already in force before it was written down: every part runs
as an instance a deployment can multiply, the state the system keeps sits in
stores a deployment can name and protect, and nothing in the system claims an
uptime no mechanism backs. What this record adds is the posture in words, so
that the absence of a cluster reads as a decision rather than an omission.

## Context

People who meet the system ask, directly or by implication, how safe it is to
depend on: what happens when a machine fails, whether a service can be lost
for an hour, whether data survives. The honest answer today is that the
system, as built, provides no protection of its own — every part runs as a
single instance, and the arrangement is deliberately small. That answer is
reasonable for what the system is: an arrangement validated whole on one
machine, meant to be deployed by an organisation that will place it inside
infrastructure it already operates.

The risk is not the smallness; it is the ambiguity around it. A reader who
finds guidance about replicating streams can mistake advice to a future
deployment for a property of the system. A reader who finds no statement at
all can assume protection exists and build on it. And a reviewer of the next
design can read the missing cluster as an oversight and add machinery nobody
asked for. Each of these costs more than the missing sentence.

The forces pull in two directions. Stating "no availability promise" plainly
is honest but can be read as permission to ignore resilience entirely.
Promising resilience the system does not have is worse: it moves the failure
from the machine to the trust. The decision to make is who owns availability,
and what the system owes the deployment either way.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The posture is stated, not inferred.** A reader asking "is this
  resilient?" finds an answer in a record, not in the silence between a
  single-instance arrangement and a replication tip.
- **R2 — No claim without a mechanism.** No document, guide, or example
  presents protection the system does not provide.
- **R3 — Nothing quietly prevents protection.** A part can be run in more than
  one instance, or replaced while down, without losing the thread — it holds
  no private state only it can recover.
- **R4 — State is enumerable.** The state the system keeps lives in stores a
  person can list, which is what makes a deployment's protection decisions —
  and the recovery record's promises — possible at all.
- **R5 — The development arrangement stays honest about itself.** Running one
  instance of everything on one machine is a decision about where the system
  is built and validated, not a statement that the system cannot run other-
  wise.
- **R6 — Advice to a deployment is marked as advice.** Guidance about
  replicating or protecting services reads as what it is: a recommendation to
  whoever deploys, not a property of what is deployed.

## Alternatives

- **Promise availability now: cluster everything.** Replication and failover
  built into the spine. It fails R5 and the arrangement the whole-system
  record requires
  ([006](./006-the-whole-system-runs-on-one-machine.md)) — a cluster cannot be
  the daily development environment — and it buys prevention the organisation
  has not asked for at a price every run pays.
- **Say nothing (the status quo).** It fails R1 by definition, and R2 by
  omission: silence is where an unbacked claim gets read in, and where the
  missing cluster gets "fixed" by someone who never saw the decision.
- **Per-part availability tiers.** Each part declares its own protection
  level. It fails R6's purpose at this scale: with one team and one
  arrangement, a catalogue of tiers is upkeep that answers a question nobody
  in the organisation has yet asked differently for two parts.
- **Fold the question into recovery alone.** "We don't prevent, we recover" is
  half the answer already recorded elsewhere
  ([026](./026-the-system-can-be-brought-back-from-a-named-snapshot.md)). It
  fails R3: recovery of a store says nothing about whether a part can be
  multiplied or replaced, which is the prevention half of the question.
- **Do nothing.** Costs nothing today; it fails every requirement above the
  way the status quo does, by leaving the posture to be guessed.

## Tradeoffs

- **Positive:** the missing cluster is a recorded decision, so reviewers
  protect it instead of "fixing" it (R1, R2); the deployment team gets an
  honest starting point — the list of stores to protect, and the knowledge
  that parts can be multiplied (R3, R4); and the development arrangement is
  freed from being read as a production topology (R5).
- **Negative:** the system cannot win a requirement that demands built-in
  uptime, and the record says so plainly; "the deployment owns it" transfers
  risk to a decision the adopting organisation has not always made yet, which
  makes this record a prerequisite for the promotion record to answer well;
  and R3 is a standing constraint on every future part, cheap per part but
  real in aggregate.
- **Neutral / follow-ups:** the placeholder page on high availability under the
  architecture section remains a heading until written from this answer — as
  advice to a deployment, per R6; the replication advice in the design
  guidance is exactly such advice and should be marked as it under this
  record; the recovery promise this record points at is itself Proposed
  ([026](./026-the-system-can-be-brought-back-from-a-named-snapshot.md)), so
  until it is accepted the system promises neither prevention nor recovery,
  and that gap is stated here rather than papered over; and a part that begins
  holding private state a restart cannot recover is a deviation from R3 that
  belongs in this record's follow-ups until it is removed.
