# 016. The system observes itself; its operational data never leaves it

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The running picture of the system — its traces, metrics, and logs — is
produced and consumed inside the system. Every part exports the same three
signals to one collection point that is part of the system, and the tools that
read the picture run beside it. No operational data is shipped to a vendor or
a hosted service: understanding the system requires nothing outside it.

The collection point itself — that parts hand their signals to one seam over
a standard protocol, and that the tools behind it can be changed without
touching the parts — is a separate decision
([034](./034-signals-meet-at-one-replaceable-collection-point.md)); this
record covers where the picture lives. The rule follows the data wherever it
is generated: a part that runs inside a user's browser — the frontend — sends
its signals to the collection point its deployment names, so a customer's
deployment keeps that picture inside the same boundary as the rest. A part
that emits nothing is a blind spot this record treats as a defect, not a
simplification.

## Context

The behaviour of the business system lives in the conversations between its
parts, so when something misbehaves, the evidence needed is spread across
them: which request entered where, how long each hop took, what each part
decided. Assembling that picture is what observability is for, and the
organisation has to decide where the picture is produced and who can see the
raw material.

The conventional answer — a hosted observability service — is cheap to operate
and powerful, and it moves the raw material outside the organisation.
Operational data is not neutral: traces carry request data, logs carry
identifiers, and what they reveal about customers and operations grows as the
system grows. Once that data flows to a vendor, every environment that runs
the system needs an account, a network path, and a data-processing agreement,
and an environment that cannot grant them — an offline machine, a restricted
site, a demonstration — runs blind.

The system is also meant to be understood wherever it runs: on the machine of
the person doing the work, in the pipeline, in a customer's environment
([006](./006-the-whole-system-runs-on-one-machine.md)). An arrangement where
the picture exists only where a vendor is reachable makes the system legible
in only one place. And because the examples in the codebase are how the
organisation teaches ([009](./009-examples-must-run-and-be-tested.md)), the
debugging path is part of what is taught: if observing the system required an
external account, the taught path would be one the learner cannot walk.

The decision to make is where the running picture is assembled, and who
outside the system is allowed to hold its raw material.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The picture is assembled inside.** Traces, metrics, and logs from
  every part come together somewhere the system itself runs, and reading them
  needs nothing the system does not already carry.
- **R2 — The system runs where data may not leave.** Some environments
  forbid operational data from crossing their boundary; the system must run
  unchanged in every one of them, so running it can never depend on a
  third-party data agreement.
- **R3 — Observing needs no accounts or network.** A person on their own
  machine, and an unattended run, get the same picture without provisioning
  access to anything outside.
- **R4 — The path is exercised where the system is validated.** The debugging
  path is live in local runs and pipeline runs, so it is exercised routinely
  rather than discovered under pressure.
- **R5 — Cheap to keep true.** Instrumenting a new part, or adding the
  observability stack to a new environment, is a local change by the person
  making it.

## Alternatives

- **A hosted observability service.** The industry default: rich tooling, no
  stack to operate. It fails R2 — the raw material leaves the boundary — and
  with it R3, because every environment needs an account and a network path;
  an offline or restricted run loses the picture entirely, which contradicts
  the arrangement in
  [006](./006-the-whole-system-runs-on-one-machine.md). It also fails R4: the
  debugging path exists only where the vendor is reachable, so the taught
  path and the shipped path diverge.
- **A self-hosted stack that is not part of the system.** An observability
  deployment the organisation runs, but outside the system it observes. It
  answers R2 — the data stays the organisation's — and fails R1 and R3: the
  picture is assembled where the system does not run, so an environment
  needs the stack provisioning beside it, which is the account-and-network
  dependency again with a different owner. It fails R5 for the same reason:
  every new environment now installs two things instead of one.
- **The cloud platform's monitoring services.** Use the monitoring built into
  whichever platform runs production. It fails R2 — the data leaves the
  boundary, to the platform's owner rather than a vendor's — and it
  fails R3 for every environment that does not run on that platform.
- **Logs only, no traces or metrics.** The minimal arrangement: every part
  writes logs, a person reads them. It passes R2 and R3 but fails R1: the
  picture of a request crossing several parts cannot be reassembled from
  uncorrelated text, which is precisely the failure mode the system's shape
  makes common.
- **Each part exports to whichever backend it needs.** No collection point;
  parts point at their own storage. It fails R1 in practice, because a
  picture spread over unlinked backends is not one picture — and the seam
  those backends would sit behind is what
  [034](./034-signals-meet-at-one-replaceable-collection-point.md) decides.
- **Do nothing (debug with prints and local reproduction).** It costs nothing
  to keep. It fails R1 by default — the evidence of a production incident is
  whatever the logs happened to catch — and R4, because the debugging path is
  invented per incident rather than exercised daily.

## Tradeoffs

- **Positive:** the system is legible wherever it runs, including offline and
  in a customer's environment, with no account to provision (R1, R3); no
  operational data crosses the boundary, so running the system never requires
  a data-processing agreement (R2); the debugging path is live in every
  validation run, so it is trusted before it is needed (R4).
- **Negative:** the organisation operates its own observation stack — its
  availability, retention, and dashboards are its problem, and a hosted
  service's polish is paid for in upkeep; the picture is bounded by what a
  self-hosted stack at the scale of the run can hold, so long retention and
  fleet-wide aggregation are not what this arrangement provides; and every
  part that ships without instrumentation is a blind spot its owner has to
  close, because the picture is only as complete as its least-instrumented
  part.
- **Neutral / follow-ups:** parts that currently emit nothing are deviations
  this record names rather than tolerates, and each needs its instrumentation
  or a stated reason not to have it; a part that emits only some of the three
  signals is a partial blind spot treated the same way; the collection point
  speaks a standard protocol
  ([034](./034-signals-meet-at-one-replaceable-collection-point.md)) so that
  a future production arrangement may export elsewhere — whether production
  ships its operational data out is a decision this record does not make, and
  no export may begin without a new record superseding this one; sampling
  rates that keep runs affordable are a tuning decision per part, owned by
  the part; and how long the signals the collection point holds are kept is a
  lifetime question owned by
  [025](./025-data-has-a-stated-lifetime.md), not by this record.
