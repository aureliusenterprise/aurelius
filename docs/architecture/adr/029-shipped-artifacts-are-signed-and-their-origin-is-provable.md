# 029. What ships is signed, and its origin can be proven

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Every deployable part of a release is signed at publication, its build origin
is recorded alongside it, and its inventory of contents is attached to it —
and the release is not considered delivered until the signature has been
verified against the identity that was supposed to produce it. Anyone holding
a released artifact can prove which pipeline run produced it and what it
contains, without trusting a copy of the artifact or the word of whoever
delivered it.

This decision was already in force before it was written down: publication
signs each artifact without holding a secret of its own, attaches the build's
provenance and its contents inventory as attestations, and ends with a
verification step pinned to the exact identity allowed to have produced the
release. This record exists because a mechanism this load-bearing should not
be folklore.

## Context

A released artifact travels: it is pushed to a registry, pulled by
environments, copied by pipelines, sometimes mirrored to places the
organisation does not operate. At every hop, the receiving side has a
question — _is this the thing we published, or a copy of it, or something
wearing its name?_ — and an artifact with no answer to that question is
trusted only as far as the last person who touched it.

The system releases as one versioned whole
([019](./019-the-system-releases-as-one-versioned-whole.md)), and the unit
that ships is the unit that was validated
([010](./010-the-unit-validated-is-the-unit-that-ships.md)). Both properties
depend on the artifact a consumer runs being the artifact the pipeline
produced. Without signatures and provenance, that identity is an assumption
renewed at every pull; with them, it is a check. The supply chain that the
artifacts themselves are built from is scanned and reported on elsewhere
([015](./015-a-change-answers-for-what-it-caused.md)); this record covers the
other half — the trustworthiness of what the organisation itself publishes.

There is also a teaching obligation: the examples in this codebase are how
the organisation teaches
([009](./009-examples-must-run-and-be-tested.md)). Publication without proof
would teach that shipping an artifact ends at uploading bytes.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Every released part is covered.** Signing and origin proof apply to
  every deployable part of a release, automatically; a part cannot be
  released without them because the mechanism is triggered by being a part.
- **R2 — No secret to steal.** The proof of who published does not depend on
  the organisation custodying a signing key that, if leaked, lets anyone
  publish a trusted forgery.
- **R3 — Contents travel with the artifact.** What a released part is built
  from is attached to it, so answering "what is in what we ran?" at incident
  time is a lookup, not a reconstruction.
- **R4 — Verification is part of delivery.** The release event includes
  checking the signature against a pinned identity; delivery without
  verification is incomplete, not merely unchecked.
- **R5 — The check needs no insider.** A consumer with no special access can
  verify an artifact's signature and read its provenance and contents
  inventory.
- **R6 — Cheap to keep true.** Adding a new deployable part adds the whole
  chain by convention, with no per-part ceremony.

## Alternatives

- **Publish unsigned (the arrangement before the mechanism).** Simplest, and
  the norm for internal systems. It fails R1's purpose — consumers cannot
  tell the published artifact from a forgery — and R3, because contents
  knowledge exists only in build logs that expire. It leaves R4 impossible:
  there is nothing to verify.
- **A long-lived signing key held by the organisation.** Classical and
  portable. It fails R2: the key becomes a crown jewel with a custody
  problem attached — the very class of problem handled by
  [028](./028-operational-secret-handling-has-a-named-owner.md) — and a
  leaked key forges trust retroactively, since old verification still
  accepts it. Keyless publication removes the asset instead of guarding it.
- **Sign only, without provenance or contents.** A signature answers "who"
  but not "how" or "what." It fails R3 and weakens R5: a consumer can confirm
  the publisher yet still cannot say what the artifact contains without
  re-running the build.
- **Verify at the deployment site only.** Push verification downstream to
  whoever runs the artifact. It keeps R4's spirit but fails its letter — the
  release event would complete unverified — and fails R5 in practice, since
  verification rules known only to deployers are not usable by other
  consumers.
- **Do nothing (keep the mechanism undocumented).** The state this record
  corrects. It fails no requirement of the mechanism itself and fails the
  organisation's: an unrecorded load-bearing decision is silently dropped by
  the next person who rewrites the pipeline, and its absence would not fail
  any check.

## Tradeoffs

- **Positive:** artifact identity survives every copy and mirror (R1, R5);
  there is no signing key to guard, leak, or rotate (R2); incident response
  can ask what a running part contains and get an attached answer (R3); the
  release is self-certifying — delivery includes its own proof (R4).
- **Negative:** the proof depends on external parties — the identity issuer
  and the public record — so a release cannot be signed where they are
  unreachable, which puts a network dependency on the one step that must
  never be improvised; keyless signatures age differently from keys, so
  long-term verification of old releases relies on those parties' history
  staying intact; and signature and provenance say _who_ and _how_, not
  _whether it is safe_ — a signed artifact is a truthful one, not a clean
  one, and the scanning question stays separate
  ([015](./015-a-change-answers-for-what-it-caused.md)).
- **Neutral / follow-ups:** signing runs only at release, so an artifact
  built outside a release event is unsigned by design and must not be
  confused with a release; the verification identity is pinned to the release
  workflow itself, which means a change to that workflow's path or name is a
  change to the trust anchor and deserves the review weight of a security
  boundary; promotion of a verified artifact into environments is where this
  record stops and the promotion question begins
  ([024](./024-a-validated-release-is-promoted-by-a-declared-path.md)); the
  contents inventory is assembled from two sources — the runtime image and
  the built application, merged into one document — for the one part whose
  build already produces an application inventory, while every other part's
  inventory comes from its image alone, and any new kind of deployable part
  must name how its inventory is produced; R5's no-insider check also
  assumes the registry serves signatures, provenance, and inventories to
  anyone, which is a setting of the registry itself and is not yet declared
  anywhere alongside it.
