# 031. Language and runtime versions have a declared support window

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

For every language and runtime the system runs on, the organisation declares
a support window — the versions it undertakes to build, test, and keep
working — and every place a version is written agrees with that declaration.
Moving a runtime's major version is a planned, recorded act, not something
that happens to the machine that upgraded first.

Today there are pins but no window: versions are written in several places
that are not kept in step, some tools are pinned only to "latest", and no
document states a floor, a ceiling, or who decides a bump. This record is
Proposed because the declaration, and the mechanism that keeps the pins
honest, do not exist.

## Context

The system spans several languages, and each one's version is a business
fact, not a technicality. The version determines which libraries can be used,
which security fixes arrive, what a new joiner must install, and how long the
organisation has before it is running something the wider ecosystem has
stopped maintaining. A runtime that reaches end of support is a compliance
conversation and an emergency upgrade, in that order.

Because the whole system releases as one versioned whole
([019](./019-the-system-releases-as-one-versioned-whole.md)), a runtime
version is a property of the system, not of a part — which means it needs one
answer. It currently has several. The same runtime's version appears in the
build definition, the development environment, the shipped image, and the
compiler configuration, and those places are not kept in step: the
development environment asks for the Node "lts" release while the build and
the shipped image pin a specific major, some tools are pinned only to
"latest", and two compiler targets disagree with each other. Nothing catches
the disagreement, because nothing states what the answer is supposed to be.

Dependency currency is already decided elsewhere
([020](./020-dependencies-stay-current-by-default.md)) and covers the
libraries inside a runtime. This record is about the runtime itself, which
that record does not speak to: a language major version is not a dependency
bump, because it can change what correct code is. Where the two meet — a
runtime minor release is arguably a dependency update — neither record yet
says who owns that bump. The development
environment is also already a versioned artifact
([011](./011-the-development-environment-is-a-versioned-artifact.md)) — that
record decides that the environment is reproducible; this one decides what
version it is allowed to contain and who says so.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The window is written.** For each runtime, the supported range is
  stated where a person choosing a dependency, or onboarding, can read it
  without inspecting five configuration files.
- **R2 — One answer everywhere.** Every place a version is declared agrees
  with the window, and a disagreement is caught by a check rather than by an
  incident.
- **R3 — Nothing floats.** No runtime, tool, or compiler target is left
  unpinned or implicitly chosen, because an unpinned thing changes without a
  decision.
- **R4 — Bumps are planned.** Moving a major version is scheduled work with
  an owner and an end date for the old version, not a surprise delivered by
  an upgrade or an image refresh.
- **R5 — Support status is visible.** The organisation can see, without
  research, how close each runtime is to losing upstream maintenance.
- **R6 — Cheap for the routine case.** A patch or minor bump inside the
  window is automatic; only a window change costs a decision.

## Alternatives

- **Pins without a window (the status quo).** Versions are written wherever
  they are needed and never reconciled. It fails R1 — the window exists only
  as an archaeology result — and R2, which is precisely the disagreement
  observed today. It fails R3 wherever a tool is pinned only to "latest".
- **Track the newest of everything.** Aggressive currency. It fails R4:
  "always newest" is a policy of never planning, and every major becomes an
  emergency when it lands. It also quietly narrows where the system can run,
  since consumers and hosts on older supported versions are excluded by
  choice nobody made.
- **Freeze versions with long support windows.** Maximum stability. It fails
  R5's purpose — a long window with no plan for its end is how an organisation
  ends up two majors behind with a deadline — and it collides with the
  dependency-currency decision, which commits the organisation to staying
  near the front.
- **Let each part choose its runtime version.** It fails R1 and R2 at the
  level that matters: the system would have as many answers as parts, and a
  release would no longer be describable. It is the shape that per-part
  packaging encourages and per-part release was written to prevent.
- **Do nothing.** Costs nothing today; the observed drift continues, and the
  first end-of-support date arrives as news. It fails every requirement by
  leaving the window unwritten, which is the current state described as a
  choice.

## Tradeoffs

- **Positive:** "what version do we support?" has one written answer (R1) and
  every configuration file is accountable to it (R2); runtime upgrades become
  scheduled work with a visible deadline (R4); the end-of-support risk stops
  being something discovered by an auditor (R5).
- **Negative:** a declared window is a commitment that costs effort at its
  edges — supporting the floor of a window is real work that a single pinned
  version would dodge; reconciling the places versions are written means
  touching build, environment, image, and compiler configuration together,
  which is exactly the kind of cross-stack coordination this system usually
  keeps to a minimum; and a window that is written but not reviewed is worse
  than none, because it will be trusted.
- **Neutral / follow-ups:** the disagreement between the base compiler target
  and the per-project targets, and between the development environment's
  Node "lts" request and the pinned major the build and the shipped image
  use, are the first two items this record's check must catch on acceptance;
  the tools pinned only to "latest" — one in the development environment,
  one in the local event-platform tooling — are R3 violations to close at
  the same time; the cadence review that keeps the
  decision set current
  ([015](./015-a-change-answers-for-what-it-caused.md)) is where a window is
  revisited, since no separate review should be invented for it; and the
  window's actual numbers — floor, ceiling, and how long an old major is kept
  alive — belong to whoever accepts this record and must be named at
  acceptance rather than deferred.
