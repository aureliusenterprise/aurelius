# 041. A failure of the running system has an owner and a rehearsed path

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

When the running system fails, the response follows a named path with a named
owner: someone is answerable for deciding, someone is answerable for acting,
and the steps — who is told, what is tried, when it escalates, what is written
down afterwards — are written and rehearsed rather than improvised by whoever
is nearest. Until this record is accepted, the system has no incident path at
all, and whoever happens to notice becomes the owner by default.

## Context

The system is built to be handed over: the records explain the decisions, the
examples teach the shape, the development arrangement runs the whole thing on
one machine. A failure response is the same kind of asset. When something
breaks in an environment that matters, the cost of the failure is dominated by
the hours around it — who was told, who decided, what was tried in what order,
what was learned afterwards — and those hours are cheap only when the path was
walked before.

The organisation has already conceded this principle once, for credentials:
secret handling has a named owner and a rehearsed path, because a lost key at
midnight is not the moment to invent a process
([028](./028-operational-secret-handling-has-a-named-owner.md)). The running
system has no equivalent. Today the implicit path is: whoever notices acts,
whoever acts is answerable, and the lessons leave with the person who learned
them. That path has a name in every post-incident review ever written.

Two properties of this system sharpen the question. The boundary rule
([016](./016-the-system-observes-itself-internally.md)) means the evidence for
any investigation lives inside the system, so the responder must know the
system's own picture — an incident path that assumes a vendor's support line
would be a fiction here. And the availability posture
([037](./037-the-system-itself-promises-nothing-about-staying-up.md)) says the
system prevents nothing on its own: failures will happen, and the honest
answer to "what then?" is the path this record would decide. The detection
half — how anyone learns something is wrong — is owned by the alerting record
([040](./040-the-system-raises-its-hand-when-it-is-broken.md)); this record
starts where that one ends.

The decision to make is who owns a failure of the running system, what the
path from noticing to closing looks like, and what makes the path real before
it is needed.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — An owner exists before the incident.** One named role answers for the
  response: deciding, escalating, and closing. "Whoever is available" is the
  absence of an owner, not a kind of one.
- **R2 — The path is written.** From the first signal to the all-clear: who is
  told, in what order, what may be tried without asking, when it escalates,
  and who says it is over.
- **R3 — The path is rehearsed.** A path nobody has walked is a paragraph. The
  arrangement includes practising it, on the schedule the rehearsal decays at
  at worst.
- **R4 — The evidence is reachable by the responder.** The responder can read
  the system's own picture — the signals the collection point holds — without
  provisioning anything the boundary rule forbids.
- **R5 — Every incident leaves a record.** What happened, what was done, and
  what changes: written where a future responder, or the next audit, can read
  it.
- **R6 — Learning closes the loop.** A recorded lesson that should become a
  rule or a trigger becomes one — into the alerting arrangement, the recovery
  path, or a new record — rather than resting in a file.
- **R7 — Cheap enough to survive.** The path fits one small organisation:
  rehearsing it is hours per year, not a department.

## Alternatives

- **Whoever notices owns it (the status quo).** It fails R1 by definition and
  R2 by leaving the path to be invented at the worst moment; it fails R5
  because the record of the incident is the chat log of whoever was paged.
- **A formal incident-management process, imported whole.** ITIL-scale roles,
  severity matrices, war rooms. It fails R7 at this scale: a process sized for
  a department goes unused by a team, and an unused process is a paragraph
  that teaches the team to ignore process.
- **Ad-hoc escalation by seniority.** Everyone knows who to call. It fails R1
  — the owner is a person, not a role, and people leave — and R3, because a
  path carried in heads is unrehearsed by definition.
- **Defer until the first real incident.** It fails R3 outright: the first
  walk of an unrehearsed path is the incident itself, paid for by the people
  affected; it also fails R6, because the lessons of that first incident are
  gathered by the exhausted people who lived it, if at all.
- **Do nothing.** Costs nothing today; every requirement above is failed by
  the same silence, which is the current state described as a choice.

## Tradeoffs

- **Positive:** a failure has an address before it happens (R1); the hours
  around an incident shrink because the path is known and walked (R2, R3); the
  organisation accumulates a written memory of its own failures (R5); and each
  incident makes the arrangement better instead than just over (R6).
- **Negative:** naming an owner makes that role a single point unless backup
  is named too — the same hazard the secret-handling record accepts and
  manages; rehearsal is real time spent on a disaster hoped against; and a
  written path invites mechanical following when the incident does not match
  it, which the owner's judgement must be trusted to override.
- **Neutral / follow-ups:** this record is Proposed because the decision has
  not been made: no role is named, no path is written, no rehearsal exists. It
  leans on the alerting record
  ([040](./040-the-system-raises-its-hand-when-it-is-broken.md)) for the
  moment an incident begins — that record is itself Proposed, so today the
  system neither raises its hand nor answers when one is raised; the
  recovery half of a severe incident — bringing the system back from a named
  snapshot — is owned by the recovery record
  ([026](./026-the-system-can-be-brought-back-from-a-named-snapshot.md)), and
  this record is the path that invokes it; the owner role this record names
  and the secret-handling owner
  ([028](./028-operational-secret-handling-has-a-named-owner.md)) may be the
  same role or must at least know each other, and that pairing is decided at
  acceptance of both; the placeholder pages on incident management under the
  architecture section remain headings until this record is accepted and
  written from its answer; and the numbers — rehearsal cadence, escalation
  times — belong to whoever accepts this record and must be named then, not
  deferred.
