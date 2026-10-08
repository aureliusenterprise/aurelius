# 045. Conventions are borrowed before they are invented

- **Status:** Accepted
- **Date:** 2026-10-08
- **Deciders:** Aurelius Enterprise

## Decision

Every convention the organisation could write is borrowed first, along a
ladder of three rungs:

1. **The framework's conventions.** When a technology slot is filled — a web
   framework, a frontend framework, a validation library — the default is the
   mainstream option whose conventions do the most work: the framework decides
   where code goes, how it is wired, and what is valid, so the organisation
   writes rules only where the framework is silent.
2. **The community's conventions.** Where the framework is silent, the
   organisation adopts the settled habits of its ecosystem — naming, test
   layout, commit titles — rather than inventing its own.
3. **A local rule.** Invention is permitted only where no framework or
   community convention covers the gap, and each rung must be shown empty
   before the next may be used.

A new technology joins by recipe
([021](./021-a-new-technology-joins-by-recipe.md)), and the recipe's first
question is "which existing convention already covers this?", not "what shall
we invent?". In-house frameworks and private style guides are not the default:
an organisation this size does not write a framework, or a dialect, to make a
choice it can borrow.

The borrowed conventions are treated as load-bearing, not decorative:
framework majors are planned events, not routine updates
([020](./020-dependencies-stay-current-by-default.md)), and a framework's
defaults are adopted through the declared channel rather than trusted silently
([018](./018-settings-arrive-at-startup-through-one-channel.md)).

## Context

The repository spans several stacks maintained by one small,
multi-disciplinary team, and it is changed routinely by automated agents as
well as by people ([022](./022-the-codebase-explains-itself-to-its-agents.md)).
Every convention the organisation invents for itself is a rule that must be
written down, taught to every new joiner, restated in the machine-facing
instructions, checked in review, and re-learned by every agent session —
forever, and per stack. Every convention a mainstream framework or its
community brings is known by every new joiner who has worked in that
ecosystem, and is the shape an assistant produces when nobody tells it
otherwise.

The cost of inventing instead is visible in the fate of similar teams: a
feature-first or lightweight choice leaves the framework's job half-done, and
the team finishes it privately — a directory layout, a wiring style, a
settings story — and then maintains a small framework nobody outside can read.
That private dialect is the most expensive kind of knowledge in a codebase: it
exists only in the heads of the people who wrote it, and it is exactly the
knowledge an agent cannot absorb by osmosis.

The same arithmetic runs below the framework level. A framework cannot settle
every habit — how commits are titled, how tests are named and placed — and
those gaps are where teams grow a house style. But most gaps already have a
settled community answer: conventional commits, test naming idioms, project
layout customs. A borrowed community convention carries the same assets as a
borrowed framework convention — a joiner arrives knowing it, an assistant
produces it unprompted, a reviewer recognizes it — while an invented one
carries only maintenance. The ladder therefore covers every convention the
organisation might write, not only the framework choices above it.

The choice also has a durability question. The decision log holds that
frameworks and libraries change while the business reasoning does not; a record
that outlives its implementation must therefore not name a brand. The decision
to make is the _preference_ that governs how conventions are acquired — the
property that should hold every time a slot is filled or a habit is written —
not which framework fills which slot today.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Structure arrives borrowed.** The framework, then the community,
  supply the default answers for layout, wiring, validation, and everyday
  habits, so the written rule set stays small and covers only genuine local
  decisions.
- **R2 — Strangers read the code.** A competent outsider — new joiner,
  reviewer, or assistant — who knows the stack reads the code without
  learning a private dialect; understanding is a hiring and onboarding asset
  ([003](./003-every-project-documents-itself.md)).
- **R3 — The convention is load-bearing on purpose.** Adopting a framework's
  or community's conventions is a commitment: upgrades are planned, defaults
  are validated through the declared channel, and the convention is not
  quietly worked around.
- **R4 — The choice stays replaceable.** The preference is about properties,
  not brands; replacing a framework is a planned migration under
  [020](./020-dependencies-stay-current-by-default.md), not a decision
  reversal.
- **R5 — New stacks join through the same gate.** A technology that genuinely
  needs new ground enters by recipe
  ([021](./021-a-new-technology-joins-by-recipe.md)) with its conventions
  documented beside it, so the preference survives the arrival of new
  technology.
- **R6 — Invention is the last resort.** A locally invented convention is
  permitted only where no framework or community convention covers the gap,
  and it names the empty rung it stands on — an invented rule that could have
  been borrowed is a defect of the same kind as a private dialect.

## Alternatives

- **Feature-first selection.** Choose the framework with the best per-feature
  benchmarks or the most capabilities. It fails R1: capability-first choices
  are typically the least opinionated, and the unopinionated space is filled
  by an invented in-house dialect — the cost R1 exists to avoid.
- **In-house framework.** Build the shared abstractions ourselves. It fails R2
  by construction — the dialect is private — and R3, because the team that
  builds a framework also has to operate, document, and staff it, which a
  small team pays for twice.
- **Private house style.** Accept the frameworks but invent the habits the
  framework leaves open — our commit format, our test layout, our naming —
  when the community already settled them. It fails R6 where a borrowed
  answer exists and R2 where the invented answer diverges from what joiners
  and assistants arrive knowing; the invented habits are a dialect with a
  style guide, and a style guide is still a rule re-learned by every session.
- **Maximal minimalism.** One language, one framework, nothing new
  ([021](./021-a-new-technology-joins-by-recipe.md) rejects this variant). It
  passes R1 and R2 for the stacks it keeps but fails R5: it freezes the
  stack rather than expressing a preference about how new parts join.
- **No stated preference.** Decide each slot and each habit ad hoc, on
  whoever's instincts. It fails R4 — the absence of a rule is itself decided
  differently every time — and R1, because ad hoc selection drifts toward the
  familiar-but-thin option and the invented conventions return.
- **Do nothing.** Keep the current stack without recording why. It fails R3:
  an unrecorded preference is argued again at every upgrade, and the first
  "just this once" lightweight exception starts the drift back to the private
  dialect.

## Tradeoffs

- **Positive:** the written rule set stays small because the framework and its
  community carry the structure and the habits (R1, R6); onboarding and
  assistant-authored changes start from the stack's conventions instead of a
  local dialect (R2), which lightens the instruction layer
  ([022](./022-the-codebase-explains-itself-to-its-agents.md)); review spends
  attention on meaning because form is typical of the stack; and the
  preference is brand-independent, so it survives every migration (R4).
- **Negative:** mainstream conventions are not always the best conventions —
  the team inherits decisions it did not make and must live inside them, and
  escaping one (a framework fighting a requirement) costs more than never
  adopting it; community conventions are softer than framework ones — they
  shift with the ecosystem and two communities can disagree, so R6's "no
  convention covers this" needs judgement at the edges, and a settled habit
  the team dislikes must be swallowed or consciously opted out of, not
  silently diverged from; the commitment is real, since planned majors
  ([020](./020-dependencies-stay-current-by-default.md)) and declared-channel
  settings ([018](./018-settings-arrive-at-startup-through-one-channel.md))
  are obligations, not decorations; and "mainstream" narrows the field in a
  way that must be re-examined when a genuinely better convention matures.
- **Neutral / follow-ups:** which framework fills which slot today is an
  implementation note and deliberately absent from this record — it belongs in
  the project documentation that describes each stack
  ([003](./003-every-project-documents-itself.md)). The recipe machinery
  ([021](./021-a-new-technology-joins-by-recipe.md)) is where this preference
  is applied when a new technology joins; the record is Accepted because the
  preference is the operating practice across every stack in the repository,
  and the enforcement point is the recipe review that every new technology
  passes through.
