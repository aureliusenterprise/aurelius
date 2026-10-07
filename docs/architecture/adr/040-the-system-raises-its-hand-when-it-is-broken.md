# 040. The system raises its hand when it is broken

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

A condition that matters to the business has a named trigger and a named
destination: the system notices it and tells someone, without that person
watching a screen. Signals that are collected but never examined are treated
as a blind spot with extra steps, and a condition nobody is told about is a
defect of the arrangement, not bad luck.

## Context

The system already produces its own picture and gathers it in one place:
traces, metrics, and logs from every part meet at a collection point the
system runs itself
([016](./016-the-system-observes-itself-internally.md),
[034](./034-signals-meet-at-one-replaceable-collection-point.md)). That
arrangement was made so the picture is available wherever the system runs. It
says nothing about anyone looking.

Today nobody is told anything. The collection point holds the signals and a
person reads them when they already suspect something — which means the
system's failures are discovered by whoever notices a symptom, usually a
person outside the system, after the fact. The collection point's own storage
can fill, a part can stop emitting and the picture simply goes quiet, and
neither event announces itself. A picture nobody looks at is a log with extra
steps.

The tension is between noticing and noise. A trigger for everything trains
people to ignore triggers, and an ignored trigger is worse than none because
it carries a false promise. The tension is sharper here than in a typical
deployment because the boundary rule
([016](./016-the-system-observes-itself-internally.md)) keeps the whole
picture inside: there is no hosted service with alerting on by default, so
noticing is the organisation's own mechanism or nobody's. And the availability
posture ([037](./037-the-system-itself-promises-nothing-about-staying-up.md))
makes this record the system's only honest answer to "how would you know?" —
the system promises no prevention, so detection is what remains.

The decision to make is what the system must announce, to whom, by what
mechanism, and what keeps the announcements worth reading.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Conditions are named, not improvised.** The conditions worth
  announcing are written down where a reviewer can see them; a trigger exists
  because someone chose it.
- **R2 — Every trigger has a destination.** Each named condition says who is
  told and how; a trigger that reaches nobody is a log line with a siren on.
- **R3 — Silence is itself a condition.** A part that stops emitting, or a
  collection point that stops receiving, is a named trigger: the picture going
  quiet is an event, not an absence.
- **R4 — Triggers stay worth reading.** A condition that fires without action
  being needed is revised or removed; the arrangement is graded by whether its
  announcements still mean something.
- **R5 — The mechanism lives inside the boundary.** Noticing uses the signals
  the collection point already holds; it sends nothing outside that the
  boundary rule forbids.
- **R6 — The path is exercised where the system is validated.** A trigger can
  be demonstrated to fire in a local or pipeline run; a trigger nobody has
  seen fire is decoration.
- **R7 — Cheap to keep true.** A new part inherits the basic triggers — it is
  emitting, it is reachable — rather than arriving mute.

## Alternatives

- **Dashboards only (the status quo).** The picture exists for whoever looks.
  It fails R2 and R3 by definition: nothing is announced, and the picture
  going quiet is precisely what a dashboard cannot show you.
- **Alert on everything the tools can measure.** It fails R4: a stream nobody
  triages becomes wallpaper, and the wallpaper hides the one announcement that
  mattered.
- **Watch the platform, not the conditions.** Triggers on machine-level
  signals — disk, memory, process state. It fails R1 for the business: a
  service can be healthy on every gauge and wrong in every answer, and the
  conditions the business cares about are answers, not gauges.
- **Rely on users to report.** The cheapest detector ever built. It fails R2's
  purpose — the first informed person is the affected customer — and R3,
  because a system quiet enough to be broken quietly produces no complaints
  worth trusting.
- **A hosted alerting service.** Mature and low-upkeep. It fails R5: the raw
  material of noticing is the operational picture, and the boundary rule
  keeps that inside
  ([016](./016-the-system-observes-itself-internally.md)); a hosted alert
  would ship the evidence out to announce it.
- **Do nothing.** Costs nothing today; it fails every requirement above the
  way the status quo does, and it leaves the availability posture
  ([037](./037-the-system-itself-promises-nothing-about-staying-up.md)) with
  no detection to stand on.

## Tradeoffs

- **Positive:** failures announce themselves instead of being excavated (R1,
  R2); the blind spot of a quiet part or a full store closes (R3); the
  boundary holds — noticing happens on the picture the system already keeps
  (R5); and the incident path has something to start from, which the
  incident-response question needs before it can be answered at all.
- **Negative:** triggers are upkeep — each one is a condition to tune, a
  destination to keep current, and a false alarm to learn from; the first
  honest set of triggers will be wrong in both directions until it is
  exercised; and naming a destination for every trigger forces a question the
  organisation has not answered — who is told at what hour — which belongs to
  the incident record but cannot be dodged here.
- **Neutral / follow-ups:** this record is Proposed because the decision has
  not been made: the collection point holds the signals and no trigger reads
  them. The placeholder page on alerting under the architecture section
  remains a heading until this record is accepted and written from its answer;
  what a person does after the hand is raised — who owns the failure and along
  what path — is the incident record's question, and that record leans on
  this one for the moment the incident begins; the thresholds and numbers
  themselves belong to whoever accepts this record and must be named at
  acceptance, not deferred; and a part that emits nothing is a deviation the
  observability record already names
  ([016](./016-the-system-observes-itself-internally.md)) — an uninstrumented
  part cannot raise its hand, and this record inherits that blind spot until
  each part is instrumented or excused in writing.
