# 006. The whole system runs on one machine

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

The whole system — every application, every service, and the infrastructure
they depend on — runs on a single machine: the machine of the person doing the
work. The same arrangement, brought up by automation rather than by
procedure, is what the pipeline validates on every change.

The rule constrains what may enter the system, not just where it runs: a
dependency that exists only as a service elsewhere needs a local equivalent
before the system may depend on it.

## Context

The behaviour of the business system lives in the interactions between its
parts, not inside any one part, so defects surface wherever the whole system
runs. Two places are candidates for that: infrastructure the organisation
operates, and the machine of the person doing the work. Operated
infrastructure brings scale and realism; the engineer's machine puts the whole
system directly in front of the person who has to understand it.

What either place is worth depends on how often the system is run there,
and how often it is run follows from what running it costs. Validation that
is expensive to run happens rarely, and validation that happens rarely lags
the code it is supposed to validate — the gap is found later, by someone
else, at higher cost.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The investigator reproduces the defect.** A defect observed anywhere
  can be brought up again, whole, by the person investigating it, quickly and
  repeatably, without depending on infrastructure the organisation operates
  or must keep available.
- **R2 — Validation covers the parts working together.** The system is
  validated as interacting parts, not part by part, on every change, and
  without waiting for a person — neither a colleague at a keyboard nor a
  manual step in a release.
- **R3 — Work needs no operated infrastructure.** Neither the everyday loop
  nor a validation run depends on services that must be reachable, on network
  access, or on accounts a human provisioned.
- **R4 — Running it is an everyday act.** A full-system run — bring-up, work,
  teardown — costs minutes, not hours, so it happens routinely rather than by
  arrangement. The moment a run costs hours, it has stopped being an everyday
  act and this record's premise no longer holds.
- **R5 — Cheap to keep true.** Adding a service, or changing what an
  application depends on, is a local edit to the environment definition by
  the person making the change, not a change request to whoever operates the
  infrastructure.

## Alternatives

- **A development environment the organisation operates.** One environment,
  run centrally, that everyone connects to. It fails R1: reproducing a defect
  means investigating through the platform — its state, its availability,
  access to it — rather than reproducing it independently; and it fails R4,
  because the everyday loop queues behind shared infrastructure.
- **Applications local, infrastructure cloud-hosted.** Developers run their
  own code but connect to shared hosted services. It fails R3 outright:
  every loop and every unattended run reaches services its owner does not
  control and needs network access and accounts a human provisioned; and it
  fails R1, because reproducing a defect means reproducing against services
  someone else operates.
- **One orchestration everywhere.** Run development, validation, and
  production on the same orchestration platform, so there is nothing to
  translate. It fails R3: the organisation now operates a platform alongside
  the system, and everyday work goes through platform machinery; it fails
  R4, because the everyday loop waits on a cluster a single application does
  not need; and it fails R5, because adding a service changes cluster
  definitions rather than one application's files.
- **Validation in the pipeline only.** Let the pipeline be the only place the
  system runs as a whole. It fails R1: a failure that no one can reproduce
  outside the platform becomes a second-class defect, debuggable only by
  whoever holds platform access.
- **Do nothing (each part runs wherever it happens to run).** Zero cost
  today. It fails R2 by default — the parts are validated, but the system
  runs as a whole nowhere until someone assembles it by hand — and R4,
  because every run is a planned assembly and every machine accumulates its
  own environment.

## Tradeoffs

- **Positive:** a production incident can be reproduced on a laptop without
  provisioning access to operated infrastructure; everyday work works
  offline, with no accounts and no access requests; and the pipeline
  validates the same arrangement a person can run on demand, so a green
  pipeline and a working local run are claims about the same arrangement.
- **Negative:** the rule constrains what may enter the system — every part
  must be startable by automation on one machine, so a dependency that
  exists only as a hosted service needs a local stand-in, and every stand-in
  is a maintained artifact
  ([012](./012-validation-runs-against-real-services.md)); validating
  the full stack unattended costs real minutes and real money per run; and
  the confidence a local or pipeline run gives stops at the environment
  boundary, whose named exceptions
  [010](./010-the-unit-validated-is-the-unit-that-ships.md) lists.
- **Neutral / follow-ups:** every application needs a run target that brings
  up what a run needs, which is the obligation
  [005](./005-dev-infra-starts-with-the-app.md) places on each
  application; the cost of validating the whole system on every change is
  bounded by validating the parts a change can reach, with the full
  arrangement reserved for changes whose reach cannot be bounded — where that
  line sits is a pipeline decision this record does not make.
