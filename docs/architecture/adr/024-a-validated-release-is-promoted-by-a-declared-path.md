# 024. A validated release is promoted by a declared path

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The system names the environments it operates: **development**, which is one
person's machine, and **test**, which is the pipeline. A change becomes a
release candidate by passing test. What happens to a released version after
that is the adopting deployment's decision — acceptance and production exist
only as customer- or project-specific arrangements, and this record says so
out loud rather than leaving them to oral tradition.

The system's obligation to those further environments is to hand over an
artifact complete enough to promote: signed, versioned, and configured only
by the settings an environment supplies. Where a deployment wants promotion
to be a declared, repeatable path with a one-move rollback, it writes that
path against the released artifact; the system neither operates it nor
invents one on the deployment's behalf.

The two named environments exist and are exercised today: development is the
versioned container the whole system runs in, and test is the pipeline that
validates every change against real services. The decision this record makes
is the boundary between what the system operates and what it hands over, and
the mechanisms for the named environments already exist — which is why this
record is Accepted rather than a proposal.

## Context

The system releases as one versioned whole, and a release produces a complete
set of deployable artifacts, validated together and signed so their origin is
provable ([029](./029-shipped-artifacts-are-signed-and-their-origin-is-provable.md)).
Two environments are the system's own: development, where the whole system
runs on one machine, and test, where the pipeline validates every change
before it can become a release. Beyond test the picture changes shape —
acceptance and production are where a customer's or project's requirements
live, and they are not the same arrangement twice. The one part whose runtime
is a cloud provider's reaches neither named environment today: it runs only
in a local emulator, so its first real deployment will be unexercised.

This is not an accident of laziness; it is the honest shape of a system meant
to be adopted rather than operated by the people who build it. But the
boundary still has to be drawn, because a reader who finds no statement will
assume the missing environments are an oversight and build on them, and a
reader who finds a promotion path in the documentation will assume the system
operates one. The cost of the ambiguity is paid at the worst moment: the
first deployment that matters, by the person with the least room for error.

The question this record answers is what happens to a released version after
it is published: which environments exist, what moving a version into one
means, and who or what performs the move.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The set of environments is stated.** Where the system runs is
  written down, including which environments the system operates and which it
  hands over; "where does version N run?" has an answer that is not a
  question back.
- **R2 — Promotion is repeatable where the system operates.** Moving a
  version into an environment the system runs is one declared action that
  produces the same result every time, performable by whoever is allowed to
  perform it, not only by whoever invented it.
- **R3 — The artifact does not change.** What is promoted is the released,
  signed artifact itself; an environment contributes settings, never a
  rebuild.
- **R4 — Position is knowable.** Any environment can state which version it
  runs, and the statement is trustworthy because promotion is what updates it.
- **R5 — Rollback is one move where the system operates.** Returning an
  environment the system runs to a previous version is the same kind of
  action as promotion, not a reconstruction.
- **R6 — The operated path is exercised.** Promotion in the environments the
  system runs happens routinely enough that its first use in anger is not its
  first use.
- **R7 — The hand-over is complete.** What the system gives an environment
  it does not operate is enough to promote from without the system's help:
  the artifact, its provenance, and the settings channel — no oral tradition
  about extra steps only the builders know.

## Alternatives

- **Name the operated environments; delegate the rest.** Development and test
  are named because the system operates them and exercises them daily;
  acceptance and production are declared the deployment's, because their
  shape is the engagement's requirement, not the system's. It satisfies every
  requirement: R2, R5, and R6 speak only of the environments the system runs,
  and R7 is the contract it keeps toward the ones it does not.
- **Hand deployment (the status quo).** Whoever deploys knows how, and does it
  by hand. It fails R1 — the set of environments is never written down — and
  R7, because the hand-over is oral tradition: the extra steps live in the
  heads of whoever built them.
- **Per-environment build pipelines.** Each environment builds the code it
  runs. It fails R3: the artifact in the environment was never the artifact
  that was validated, which quietly undoes the confidence the release was
  built to carry. It fails R5 as a side effect, since rollback means waiting
  on a rebuild.
- **Declare every environment out of scope.** Publish artifacts and let each
  environment write its own path, naming nothing. It fails R1 even for the
  environments the system does operate: development and test exist and are
  exercised daily, and leaving them unnamed makes the taught path a secret.
  The chosen decision takes this alternative's honest half — the further
  environments are not the spine's to operate — and refuses its dishonest
  half, which is silence about the two that are.
- **Adopt a platform's native deployment model wholesale.** It answers R2 and
  R4 for one environment shape and fails R3's neutrality by binding promotion
  to that platform, which narrows where the system may run at all.
- **Do nothing.** Costs nothing today and leaves every requirement to oral
  tradition; it is the current state described as a choice, which is what
  this record exists to prevent.

## Tradeoffs

- **Positive:** the boundary between what the system operates and what it
  hands over is written down, so neither a reader nor a reviewer has to guess
  (R1, R4); the two operated environments are exercised daily rather than
  hoped for (R6); and the hand-over contract is small and checkable — a
  signed, versioned artifact configured only by settings (R3).
- **Negative:** the system cannot promise a deployment how its release will
  be promoted, and a customer who expects one must be told the answer is
  theirs to build; naming the operated environments constrains future
  flexibility, which is the point but will be felt as one; and the delegation
  is honest only while the handed-over artifact is truly complete, so any
  property a deployment needs that the artifact lacks silently pulls the
  environment back into the spine's scope.
- **Neutral / follow-ups:** promotion of a _released_ artifact beyond test
  has no mechanism here by design — a deployment that wants one writes it
  against the signed artifact, and the first such deployment is this record's
  first real test; the image the pipeline validates and the image the release
  publishes are built by different steps, so R3 does not yet hold even for
  the named environments, and closing that gap is a standing obligation of
  this record; the
  cloud-provider runtime reaches neither named environment and runs today
  only in a local emulator, so its first real deployment will be unexercised;
  rollback beyond test is the deployment's move, named as a deploy-time act
  by the release record
  ([019](./019-the-system-releases-as-one-versioned-whole.md)); settings are
  what an environment contributes to an artifact, and the channel that
  delivers them is already decided elsewhere
  ([018](./018-settings-arrive-at-startup-through-one-channel.md)); and every
  environment must be reachable by the same identity rules that govern every
  other boundary
  ([013](./013-services-prove-who-they-are-at-every-boundary.md)).
