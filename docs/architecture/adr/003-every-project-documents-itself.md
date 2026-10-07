# 003. Every project documents itself

- **Status:** Accepted
- **Date:** 2026-10-06
- **Deciders:** Aurelius Enterprise

## Decision

Knowledge about a part of the system lives with the thing it describes: every
project carries its own documentation — what it is, how to run it, and the
rules that govern it — and the repository maintains no hand-edited central
catalogue of projects or capabilities.

The repository tree is the index: to find out what exists, read the tree; to
learn about a part, read what sits beside it. Derived artifacts — generated
API reference, navigation derived from the tree — are not catalogues in the
sense this rule forbids, because they cannot disagree with the code.

The site's navigation file is the one hand-edited list this rule tolerates. It
enumerates documents rather than describing projects, and the documentation
build reports every entry that no longer resolves and every document the list
omits, so its drift is loud at build time rather than quiet at read time —
which is the property R2 asks of everything else.

## Context

The system is made of many parts: applications, shared libraries, backing
services, and development infrastructure. People constantly need to learn
about parts they did not build — what a part is for, how to run it, what
constraints it operates under, and what breaks if it is removed.

The team is small and multi-disciplinary, and the same people change many
different parts. The person who changes a project today is often not the
person who needs to understand it next, so what the system does cannot live
in anyone's head.

Where documentation lives decides how fast it decays. Knowledge kept in a
place that changes only when someone remembers to update it drifts from the
code, and readers eventually learn to distrust it. Knowledge kept beside the
code changes in the same review, is reviewed together with it, and is deleted
with it.

The decision to make is where knowledge about a part of the system belongs,
and what has to be updated when that part changes.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Knowledge travels with the part.** When a project changes, its
  documentation changes in the same review, as one reviewed piece of work.
- **R2 — Drift is structurally impossible.** No hand-edited central artifact
  exists that quietly goes out of date when a project changes.
- **R3 — Local discovery is enough.** Someone working on a part can learn
  what it is for, how to run it, and what governs it without leaving it.
- **R4 — Removal takes the knowledge with it.** Deleting a project deletes
  its documentation, leaving no stale description behind.
- **R5 — Cheap to keep true.** Honouring the rule costs a small team nothing
  beyond the change they were already making.

## Alternatives

- **A curated catalogue: one page listing every project and capability.** The
  best possible discovery — a single page answers "what does the system
  contain?" It fails R2: a hand-edited central page is updated only when the
  person making a change happens to remember it, which is precisely how
  catalogues come to be disbelieved. It fails R1 too, since every project
  change becomes a two-place edit in two different reviews, and R3, because
  answering a question about a part means leaving it for the catalogue.
- **The project wiki as the home of project knowledge.** Familiar tooling,
  easy to write. It fails R1: the wiki is edited by whoever
  remembers it, not by whoever makes the change, so its review is separate
  from the change and it drifts; R3 fails as well, because the answer to a
  question about a part lives somewhere else, and R4, because deleting a
  project leaves its wiki page standing.
- **No rule: knowledge lives in people and commit history.** Zero cost today.
  It fails R3 by default — every question about an unfamiliar part becomes a
  question to a person — and R1, because nothing connects what changed to any
  written account of it.
- **Documentation generated from code only.** Drift is impossible, since the
  text is derived: R2 holds trivially. It fails R1: code can state what a
  project does, but not why it is shaped the way it is or what rules constrain
  it — the reasoning has to be written down by a person, somewhere, and
  generation cannot supply that.

## Tradeoffs

- **Positive:** documentation is reviewed together with the change it
  describes, so it is current exactly where people are working (R1); drift is
  not merely discouraged but impossible, because there is nothing central to
  forget (R2); removal leaves no stale text behind (R4), which is what makes
  whole-slice removal trustworthy.
- **Negative:** no single page answers "what does the system contain?" —
  discovery means browsing the tree, which is slower for a newcomer who does
  not yet know what to look for; the shape of each project's documentation is
  a convention, and keeping twenty documents consistent without a tool
  enforcing the shape takes deliberate effort.
- **Neutral / follow-ups:** "documents itself" needs a shared shape — what
  every project's documentation must contain — or the rule degrades into
  twenty unrelated files; directory-level recipes for adding new projects are
  the mechanism that carries that shape, and keeping them current is ongoing
  work. The removal rule in [002](./002-modules-are-removable-slices.md)
  depends on this record: a capability is only fully removable when its
  documentation is part of the slice.
