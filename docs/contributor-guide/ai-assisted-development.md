# AI-Assisted Development

Automated agents write a routine share of the changes in this repository —
alongside bot-authored dependency updates, which have been routine for years.
The rule that makes this safe is short: **an assistant is a generator, not a
signatory.** It cannot approve, own, or operate what it wrote, so the gate and
the human signatures a change needs are exactly the same as if a person had
typed every line. This page describes how we work with assistants under that
rule: what counts as done, who signs off, and where the guardrails live. It is
written for people reading the system; the machine-facing instructions that
agents read are a separate layer, and this page deliberately stands without
them.

## The premise: same discipline, faster generator

An assistant changes the speed at which code appears, not the obligations that
come with it. A change is judged as a change: whoever — or whatever — produced
a diff, it passes the same gate, the same review, and the same release rules
as any other. The reasoning behind that rule is recorded in
[ADR 022](../architecture/adr/022-the-codebase-explains-itself-to-its-agents.md);
the gate itself is defined once and runs everywhere
([ADR 014](../architecture/adr/014-the-gate-is-defined-once-and-runs-everywhere.md)),
and a change answers only for what it caused
([ADR 015](../architecture/adr/015-a-change-answers-for-what-it-caused.md)).

Because the assistant cannot sign, the responsibility for a change rests with
the person who asked for it. What that person is agreeing to is defined next.

## The guarantee

A merged change always gives the same guarantee, whoever produced it: the
gate runs the full ladder on every pull request — the commit checks
(formatting, lint, types, secret scanning), the unit tests, and the end-to-end
tests against real services — and all of it must pass before the change is
accepted.

This is the standard both signatures below are given against. It is stated
here, before them, so that "I verified it" has a fixed meaning: it means the
change meets this guarantee, not that its author liked the prompt.

## Two people sign off

Every change carries two human signatures before it merges:

1. **The task owner** — the person who triggered the assistant and who can
   explain the change line by line. Their signature means _I understand this
   and I verified it against the guarantee above_. In practice, verifying a
   generated diff means running the gate locally and reading the diff itself —
   the prompt is not evidence of anything.
2. **A reviewer** — a second pair of eyes, who confirms independent
   understanding and, in doing so, spreads knowledge of the area beyond its
   author.

The second signature is not new: the [version control
guide](./version-control.md#code-review) has always required at least one
other team member to review every pull request. What changes when code is
generated quickly is how load-bearing that rule becomes. A diff you wrote
yourself carries its understanding for free; a diff you prompted into
existence does not, and the review is where understanding is either built or
silently skipped. The debt from skipping it has a name.

## Cognitive debt

Technical debt accrues in the code, and the tests feel it. **Cognitive debt**
accrues in the team: code that works but that nobody but its author
understands. It is felt later — at the next review, the next incident, the
next handover — and the delay is what makes it debt.

Two habits keep it down, and both predate assistants:

- **The code explains itself.** Every project documents itself
  ([ADR 003](../architecture/adr/003-every-project-documents-itself.md)), and
  ownership of shared data is a stated answer, never an absence
  ([ADR 042](../architecture/adr/042-every-dataset-has-an-owner-who-answers-for-it.md)).
  A reviewer or a new joiner who knows the stack should be able to read this
  repository without a local dialect.
- **Knowledge spreads through review.** The reviewer is chosen to be someone
  who should learn the area, not merely someone who is free.

Accountability is carried by the team and cannot be offloaded to a single person
or an assistant. A team that cannot explain a change it shipped owns a change it
does not have.
