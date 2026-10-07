# ADR Template

Copy the template below into `docs/architecture/adr/NNN-short-slug.md` (next
free number, kebab-case slug), fill it in, and add the new file to the `nav`
section of `mkdocs.yaml`. Delete the guidance comments when you are done.

Keep the record business-focused: describe the decision's drivers and
consequences, not implementation detail. If replacing every technology in the
stack would make the record wrong, it needs rewriting. See
[Architecture Decisions](./index.md) for the full practice.

```markdown
# NNN. Decision Title

<!--
    Title the decision as an action or a property that now holds, not a topic:
    "Adopt a single shared domain model", not "Domain model".
-->

- **Status:** Proposed | Accepted | Superseded by [NNN](./NNN-slug.md) |
  Deprecated
- **Date:** YYYY-MM-DD (date of last status change)
- **Deciders:** names or roles who own this decision

## Decision

<!--
    The decision itself, in one or two sentences, active voice: "We will ...".
    State what is now true and what the organisation may and may not do
    because of it.
    If the decision has sharp edges, name them here rather than hiding them.
    The decision comes first on purpose: the sections below justify it, they
    do not build up to it. Draft them first, though — a decision written
    before the requirements is a solution looking for a problem.
-->

## Context

<!--
    The business situation that makes a decision necessary: the goal, the
    constraints, and the forces in tension (cost, risk, delivery speed, team
    autonomy, compliance, portability). Describe the problem as it would be
    described to a non-technical stakeholder, and keep it neutral: do not
    argue for the decision here, and do not phrase the situation in terms
    only the chosen option could solve. Technologies may appear as evidence,
    but the drivers must stand without them.
-->

## Requirements

<!--
    What any acceptable solution must deliver, independent of the chosen one:
    short "must" statements (R1, R2, ...) that a reader can grade the
    alternatives against. Every rejected alternative should fail at least one
    requirement; the decision should satisfy all of them.
-->

## Alternatives

<!--
    The realistic alternatives to the decision (including "do nothing"), each
    described fairly and graded against the requirements, with the reason it
    lost. One short paragraph per option. This section is the main thing
    future readers mine — they need to know the alternatives were weighed,
    not that the chosen option was perfect.
-->

## Tradeoffs

<!--
    What follows from the decision — both directions, honestly. If a
    consequence is "this must be revisited when X", say so explicitly.
-->

- **Positive:** capabilities, guarantees, or costs avoided.
- **Negative:** new costs, constraints, or risks accepted.
- **Neutral / follow-ups:** things this decision makes necessary but does not
  itself deliver.

Reference related records inline, where they are relevant, rather than in a
trailing links section.
```
