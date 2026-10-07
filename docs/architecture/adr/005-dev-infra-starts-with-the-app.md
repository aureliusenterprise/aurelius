# 005. Development infrastructure starts with the app that needs it

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

The development infrastructure an application needs — its database, identity
provider, event platform, observability backends — starts when the application
is run and stops with that run. There is no always-on shared development
environment, and no application depends on infrastructure somebody else
started.

The application's run command is the entry point: it brings up the services
the application declares it depends on, then starts the application itself.
From a fresh checkout, one command per application is enough to see the system
work.

This record settles who owns development infrastructure and when it exists;
which machine the whole system runs on is a separate decision, made separately
([006](./006-the-whole-system-runs-on-one-machine.md)).

## Context

The business runs a system made of several small applications rather than one
large one, and each application depends on services to do its work: a
database, an identity provider, an event platform, metrics and dashboards.
Every developer therefore faces the same question before any feature work can
begin: how do I get a running system in front of me?

Two arrangements answer it conventionally. A shared development environment —
one always-on set of services everyone connects to — front-loads the work with
access requests and setup instructions, and its state is shared: what one
person changes is visible in everyone else's results. A documented manual
setup — a list of services to install and start — puts the system in front of
the developer only as reliably as the list is current, and lists go stale
quietly.

Both arrangements share a slower cost: the cost of trying the system decides
how often it is run, and a system that is rarely run is rarely observed.
Where the codebase's examples are its demonstration, an example nobody runs
is an example nobody can vouch for.

The decision to make is who owns development infrastructure, and when it
exists.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One command to a running system.** A fresh checkout reaches a running
  application with a single documented command; no manual prerequisite steps.
- **R2 — Runs do not interfere.** Two applications, or two developers, can run
  at the same time without sharing mutable state: one run cannot change
  another's results.
- **R3 — Dependencies are declared where they are used.** The services an
  application needs are listed in the application's own definition, not in a
  central inventory, so the list travels with the application.
- **R4 — Reproducible everywhere.** The same command works for a new
  developer, on a fresh machine, and in CI, without knowledge that lives only
  with whoever set it up last.
- **R5 — Nothing accumulates.** When the run ends, its infrastructure ends
  with it; no state accumulates between runs.
- **R6 — Cheap to keep true.** Adding an application, or changing what it
  depends on, is a local edit to that application's definition by the person
  making the change; a small team cannot fund a central inventory that someone
  has to remember to update.

## Alternatives

- **A shared always-on development environment.** One always-on set of services
  everyone connects to. It fails R2 structurally: the state is shared, so one
  person's run changes everyone else's results, and debugging becomes a
  question of who else is connected. It fails R5 as well — the environment
  outlives every run and accumulates state no one owns — and it fails R1 at
  the front door, because access provisioning is a prerequisite step.
- **One root compose file that starts the whole world.** One central file
  starts every service at once, for everyone. It passes R1 — the command
  exists — but fails R3: what starts is the full list, not what any one
  application uses, so the list and reality drift apart; and it fails R6,
  because adding or removing an application is an edit to a global file
  rather than a local one.
- **A documented manual setup.** A README listing the services to install and
  start before running anything. It fails R1 — the list is the prerequisite —
  and R4: the setup works on the machine of whoever last wrote it down, and
  nowhere else.
- **Do nothing (each developer wires up their own stack).** Zero cost to
  organise. It fails R1 by default — every run is bespoke — and R2 by
  default, because every stack is configured slightly differently and every
  mismatch is debugged as an application bug.

## Tradeoffs

- **Positive:** clone-to-running is one command with no prerequisites (R1);
  runs are isolated, so a broken run is the developer's own to fix (R2); the
  dependency list lives with the application, so removing a module removes its
  infrastructure with it (R3); a new developer, a colleague, and the CI
  pipeline all take the same path (R4); changing what an application needs is
  a local edit (R6).
- **Negative:** startup cost is paid per run rather than amortised over a
  shared environment, so bring-up has to stay fast — images kept current,
  services started in parallel — and running several applications at once
  means several stacks whose ports and resource use must be coordinated.
- **Neutral / follow-ups:** every application needs a run command that brings
  up the infrastructure it declares, and an application whose run target is a
  build tool or an emulator rather than a container deviates from this record
  until it has one; the convention that keeps parallel stacks from colliding
  on ports is a convention, not a check, and remains so until a collision has
  happened once.
