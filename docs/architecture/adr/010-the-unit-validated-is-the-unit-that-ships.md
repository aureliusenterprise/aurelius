# 010. The unit validated is the unit that ships

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

Every part of the system ships as one packaged unit: the same unit that is
built and validated on an engineer's machine and in the pipeline is the unit
deployed to production. Environments may differ in configuration and in the
orchestration that runs the unit — production is deployed by the orchestration
the organisation operates for it, which need not be how the system runs in
development or CI — but not in artifact.

A run that passes on a unit is evidence about that unit, and a deployment is
only ever of that same unit. Where a difference between places is unavoidable
in configuration, it is expressed as configuration of the unit, never as a
differently built unit.

## Context

The system is validated in several places: on an engineer's machine, in the
pipeline, and in production. Each validation produces a claim — the system
behaves this way — and the claims are only worth acting on if they are about
the same thing.

If the artifact validated differs from the artifact deployed, then a passing
run and a healthy deployment are claims about two different objects, and
confidence does not transfer from one to the other. The organisation is then
left reasoning about the gap between them: which failures belong to the
packaging step, which to the environment, which to the code — a question that
exists only because two builds happened where one could have.

The decision to make is what the unit of validation and delivery is, and what
must be true of it for validation performed in one place to count in all
others.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One build, everywhere used.** Each part of the system is packaged
  once per change, and every place that runs or validates it consumes that
  package rather than rebuilding or reassembling from source.
- **R2 — Validation transfers to production.** A passing run against the unit
  is evidence about what will be deployed, because they are the same artifact;
  differences between places are configuration, not artifact.
- **R3 — The unit is self-contained.** The unit carries everything needed to
  run it; where it depends on services outside itself, those dependencies are
  declared, not assumed from the surrounding machine.
- **R4 — Deploy is a selection, not a transformation.** Releasing means
  pointing the operating environment at an already-validated unit, not
  rebuilding, repackaging, or patching it on the way.
- **R5 — Cheap to keep true.** Packaging a new part, or changing how it is
  packaged, is a local edit to that part's definition by the person making
  the change, not a change request to whoever owns the delivery path.

## Alternatives

- **Build per environment.** Each environment builds or assembles its own copy
  from source at deploy time, the traditional per-server pattern. It fails
  R1 by construction, and with it the transfer of confidence this record
  exists to secure: the unit tested and the unit serving users are produced by
  different builds at different times, and every difference between the two
  builds is an unvalidated difference. R4 then fails too — deploying means
  running the build, so the release path contains a step no validation
  covered.
- **Patch the validated unit at release.** Validate a package, then modify it
  on its way to production — inject configuration by rewriting contents, patch
  a dependency, tune a setting inside the artifact. It fails R4 directly: the
  deployed unit is the validated unit plus an unvalidated edit, and the
  pipeline's claim ends where the edit begins.
- **Deploy source, build in place.** Skip packaging and let each environment
  run from source it checks out and assembles itself. It fails R1: every
  environment's copy is assembled by that environment's toolchain, so two
  environments can produce two different running things from one commit; and
  R4, because the running thing has no identity to roll back to.
- **Do nothing (each place takes what it takes).** Zero cost today. It fails
  R1 by default — machine, pipeline, and production each assemble their own
  copy — and R2 by default: green locally and green in production become
  claims about different things, and the gap is investigated only when they
  disagree.

## Tradeoffs

- **Positive:** a passing run means the same thing on a machine, in the
  pipeline, and production, because they all ran the same unit (R1, R2);
  releasing is a selection, so rollback is a selection too — pointing back at
  the previously validated unit (R4); the running unit has an identity, so an
  incident can be tied to exactly the code that is running.
- **Negative:** every part must be packageable, which rules out arrangements
  that only work in place, and the packaging step becomes part of every
  delivery path — packaging bugs become release bugs; configuration that
  differs per environment must live outside the unit, which means a stated
  place for it and a habit of keeping secrets and environment values out of
  the package.
- **Neutral / follow-ups:** the confidence claim stops at the environment
  boundary — scale, live traffic, third-party behaviour, and the production
  orchestration itself are not proven by validating the unit, and remain named
  exceptions; parts whose packaging is not yet uniform (an application run
  from source rather than from its package) deviate from this record until
  they ship the unit that was tested. The image that developers and the
  pipeline work in is not a deliverable and is not the unit this record
  governs: it is a tool for producing and validating the unit, and a change to
  it is not a release.
