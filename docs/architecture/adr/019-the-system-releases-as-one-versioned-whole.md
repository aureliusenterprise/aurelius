# 019. The system releases as one versioned whole

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The whole system is versioned and released as a single unit: one version
number, one changelog, one release event that publishes every deployable part
together. A released version is a complete, mutually consistent snapshot of
the system — every part in it is known to have been built and validated
against the same everything.

Individual parts are not independently versioned or independently released.
When a part changes, the system's version moves; the changelog records which
parts moved and how. This is the delivery face of two older decisions: the
single repository makes one version meaningful
([001](./001-single-monorepo.md)), and the unit that
ships is the unit that was validated
([010](./010-the-unit-validated-is-the-unit-that-ships.md)) — lockstep release
is what keeps those two true at the moment of delivery rather than only at
the moment of commit.

## Context

The repository holds many deployable things — services, frontends, functions,
connectors — and they are useful only in combination: a frontend that speaks
to a service that reads a topic a producer writes. The question this record
answers is what gets a version number and a release: each part separately, or
the system as a whole.

Independent per-part versioning is the instinct that per-part packaging
encourages, and it is the arrangement most organisations drift into. It buys
fine-grained choice about what to ship and pays for it in compatibility
knowledge: once parts move independently, the question "does this combination
work?" has no cheap answer, and someone — usually the person deploying, usually
late — becomes the source of truth about which versions of which parts belong
together. The matrix of tested combinations grows faster than the team that
must reason about it.

The alternative is to release the whole system at once, under one number. That
is only affordable because of how the repository is arranged: everything lives
together and is validated together
([001](./001-single-monorepo.md)), so every commit
already represents a consistent whole, and the pipeline builds and validates
every deployable part as one flow
([010](./010-the-unit-validated-is-the-unit-that-ships.md)). Given that,
per-part release adds a choice the organisation has no evidence to make
wisely — it did not test the combination that a partial release creates.

The team is one multi-disciplinary group; there is no second team whose
release cadence the system must accommodate, and no consumer who consumes one
part without the rest. The cost of lockstep — releasing a changed part only
when the whole does — is a cost this organisation does not currently pay,
because the whole always moves anyway.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — One identifier for a state of the system.** A version number names a
  complete, consistent state, so "deploy 4.4.0" is a whole instruction and
  "which parts?" is not a follow-up question.
- **R2 — What ships was validated as a whole.** The set of parts deployed
  together is a set the pipeline built and tested together: no release
  creates a combination that was never validated, so nobody has to carry
  knowledge of which combinations work.
- **R3 — History is one story.** The changelog is a single chronological
  account of what the system gained and fixed, readable by whoever needs to
  know what changed between two versions, without cross-referencing per-part
  ledgers.
- **R4 — Rollback is one move.** Returning to a previous version of the
  system means deploying a previous snapshot, not reconstructing a compatible
  set of part versions.
- **R5 — Delivery is one event.** Releasing publishes every deployable part
  under the same event, so a version is either fully available or not
  released — no half-released state to reason about.
- **R6 — Cheap to keep true.** Releasing is one action by the release owner,
  not a per-part ceremony; the version is derived from recorded change
  history rather than hand-set.

## Alternatives

- **Independent per-part versions and releases.** Each part moves on its own
  number and cadence. It fails R2 — every combination becomes a candidate,
  most untested — and R3/R4, because "what changed" and "roll back" become
  matrix questions. It is the right shape for a platform with unrelated
  consumers of individual parts; this system has none, and the cost lands on
  the deployer regardless.
- **Train releases (parts move independently; bundles ship on a schedule).**
  A middle path: parts version separately, and a periodic "train" bundles a
  tested set. It restores R2 and R4 at the bundle level but fails R1 as long
  as two identifiers (part versions and train version) both claim to describe
  what is deployed, and it fails R6 — the train needs a curator to decide
  membership, which is the compatibility judgement lockstep avoids making.
  It earns its keep when independent teams have independent cadences; here it
  would be ceremony around a train that leaves whenever anything changes.
- **Release only changed parts per event.** One version number, but each
  release publishes only the parts whose files changed. It keeps R1 and R3 and
  tempts with shorter pipelines, but it fails R5: a version becomes a partial
  publication, and "deploy 4.4.0" quietly means "4.4.0 plus whatever the
  unchanged parts were last time" — a combination defined by deployment
  history rather than by the release.
- **Do nothing (keep hand-tagging and ad-hoc publishing).** No setup cost.
  It fails R6 — every release is manual and each missed step is a
  half-released state (R5) — and R3, because a changelog written by hand at
  release time drifts from what actually changed.

## Tradeoffs

- **Positive:** one number answers "what is deployed?" and "what changed?"
  (R1, R3); every shipped combination was built and validated as one flow
  (R2), extending the confidence transfer [010](./010-the-unit-validated-is-the-unit-that-ships.md)
  to the whole system; rollback is a single move (R4); releasing is one action
  (R6).
- **Negative:** an unchanged part still gets a new version number, which reads
  as noise to anyone who expects a part's version to track its own change
  history — the changelog has to carry that meaning instead; a release waits
  on the slowest part to clear the gate, so one struggling part delays the
  whole system's delivery; and the version number itself becomes coarse —
  "4.4.0 to 4.5.0" says the system moved, not which parts did, which is a
  real loss for anyone consuming one part's history.
- **Neutral / follow-ups:** the changelog is the one place the per-part story
  must live, so release notes that name affected parts are a standing
  obligation of this record rather than a courtesy; a release event that
  fails partway — parts published but not yet signed, say — is exactly the
  half-released state R5 rules out, so a version counts as released only when
  the whole event has completed, and a failed event is re-run to completion or
  abandoned, never partially claimed; R4's rollback is a deploy-time move onto
  a previous snapshot, which today means deploying a previous release by hand
  until a mechanism exists to make it one move; if a part ever gains a
  consumer outside the system — a library published for general use — that
  part's versioning is a decision this record does not cover and would need
  its own; and the environment side of "deploy one version" — how a snapshot
  is promoted between environments — is where this record stops: the
  settings record
  ([018](./018-settings-arrive-at-startup-through-one-channel.md)) carries
  on from here, and the boundary between the environments the system operates
  and the ones it hands over is recorded elsewhere
  ([024](./024-a-validated-release-is-promoted-by-a-declared-path.md)).
