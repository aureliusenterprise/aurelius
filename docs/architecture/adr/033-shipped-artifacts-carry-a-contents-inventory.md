# 033. Shipped artifacts carry a contents inventory

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Every deployable part of a release carries a machine-readable inventory of
what it contains, attached to the artifact at publication in the same
attestation step that carries its provenance
([029](./029-shipped-artifacts-are-signed-and-their-origin-is-provable.md)).
Answering "what is in what we ran?" — at an incident, during a recall of a
flawed dependency, or for a customer question — is a lookup against the
released artifact, not a reconstruction from build logs.

This decision was already in force before it was written down: publication
assembles each part's contents inventory and attaches it to the signed
artifact, and the advisory scans over released parts
([015](./015-a-change-answers-for-what-it-caused.md)) consume it. This record
exists because the inventory is what makes those scans answerable for a
specific release, and that role should not be implicit.

## Context

A release is a set of artifacts that travel
([019](./019-the-system-releases-as-one-versioned-whole.md)), and the unit
that ships is the unit that was validated
([010](./010-the-unit-validated-is-the-unit-that-ships.md)). When something
goes wrong with a running part, the first question is not who built it — that
is provenance, decided in
[029](./029-shipped-artifacts-are-signed-and-their-origin-is-provable.md) —
but what is inside it: which dependencies, which versions, which layers. A
part whose contents can only be re-derived by re-running an old build, if the
build inputs still exist at all, turns an urgent question into slow
reconstruction work.

The organisation already answers dependency questions continuously for the
codebase ([015](./015-a-change-answers-for-what-it-caused.md)); the inventory
is what makes the same answer specific to a released artifact rather than to
the current branch. Separating the two decisions — origin here, contents
there — keeps each checkable on its own: an artifact can have perfect
provenance and no inventory, and the gap should be visible as exactly that.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Every released part is covered.** A contents inventory is produced
  and attached for every deployable part of a release, automatically; a part
  cannot be released without one because the mechanism is triggered by being
  a part.
- **R2 — The inventory travels with the artifact.** It is attached at
  publication, not stored beside it or left in build output, so it survives
  every copy and mirror the artifact survives.
- **R3 — Machines can read it.** The inventory is in a standard
  machine-readable form, so consumer tooling — scanners, report builders, a
  customer's own tooling — can read it without this organisation's
  cooperation.
- **R4 — Incident-time lookup.** For any released part, its contents can be
  read at the moment the question is asked, however old the release, without
  re-running its build.
- **R5 — Cheap to keep true.** Adding a new deployable part adds the
  inventory by convention, with no per-part ceremony.

## Alternatives

- **Contents live only in build logs.** Free today. It fails R2 and R4 —
  logs expire, are not attached, and are written for humans — and fails R3
  because there is no standard form to read. This is the arrangement the
  record replaces.
- **Reconstruct contents on demand at incident time.** Re-running the build
  for a released version and listing what came out. It fails R4 under
  pressure — the worst moment to discover the old build inputs are gone —
  and it answers about today's toolchain, not about what the release
  actually contained.
- **Ship the inventory as a separate downloadable document.** It fails R2 in
  substance: a document beside the artifact is copied at some hops and not
  others, and nothing binds it to the artifact it describes.
- **Rely on the registry's own metadata about the artifact.** The registry
  knows the storage-level facts, not the application-level contents, and
  those facts are readable only through that registry. It fails R3 and
  leaves the answer stranded where the artifact was mirrored from.
- **Do nothing (keep the inventory implicit in the scan pipeline).** The
  state this record corrects. It fails no requirement of the mechanism
  itself and fails the organisation's: the next person to wire a new part
  would not know the inventory is required, and its absence would not fail
  any check.

## Tradeoffs

- **Positive:** an incident question about a running part is answered by
  reading the artifact (R2, R4); dependency advisories can be answered per
  release rather than per branch, which is what
  [015](./015-a-change-answers-for-what-it-caused.md) needs to be precise;
  and consumers can run their own tooling over what they received (R3).
- **Negative:** assembling an inventory adds real time to every publication,
  and for the one part whose build already produces its own application
  inventory the two sources must be merged into one document, which is a
  maintained mechanism; and an inventory is a claim about contents, not about
  safety — it says what is in the artifact, and the judgement of whether any
  of it is a problem stays with the scanning record
  ([015](./015-a-change-answers-for-what-it-caused.md)).
- **Neutral / follow-ups:** the two-source merge (runtime image plus built
  application) exists for the one part whose build produces an application
  inventory; every other part's inventory comes from its image alone, and any
  new kind of deployable part must name how its inventory is produced rather
  than assume the image covers it; reading an inventory with no special
  access depends on the registry serving attached attestations to anyone, the
  same undeclared registry setting
  [029](./029-shipped-artifacts-are-signed-and-their-origin-is-provable.md)
  waits on, and must be confirmed before R2's no-insider reading can be
  called met; and an inventory assembled at publication is silent about
  contents added later at run time — configuration, downloads, mounted code —
  which remain outside what any inventory can claim.
