# 022. The codebase explains itself to the agents that change it

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Automated agents are regular authors of changes in this repository, and the
codebase is arranged so that an agent can work correctly in any area without
oral tradition. Every project directory and every technology grouping carries
a short, colocated instruction file written for machine readers: how to build,
test, and run what lives here; which local conventions apply; what the
surrounding wiring is; and what to update elsewhere when something here
changes.

The files follow a nearest-first rule: whoever — or whatever — is editing a
file reads the instruction files from the workspace root down to the file's
own directory, and the nearest one wins on conflicts. Each is small and
scoped to its directory; the root file holds only workspace-wide rules. It
holds no catalogue of projects — each project's purpose, build steps, and
wiring are described only in that project's own file — because a catalogue
duplicates what the directory-level files already say and is the first thing
to drift.
The root file may hold a removal map
([002](./002-modules-are-removable-slices.md)): which slices exist and which
are optional is a workspace-wide removal rule, not a project description.
The practice is held to the same
standard as documentation
([003](./003-every-project-documents-itself.md)): an instruction that no
longer matches reality is a defect to be fixed in the same change that broke
it, and the human-facing documentation never cites the machine-facing
instructions — each addresses its own audience.

This is not a courtesy to tooling. It is the mechanism that lets a
multi-disciplinary team of people and agents share one codebase without a
shared memory of its conventions.

## Context

The team is one small multi-disciplinary group, and the repository is
polyglot, deeply wired (every project has tasks, pipeline steps, environment
keys, and documentation that reference each other), and explicitly designed
for removal — a slice that leaves must take its wiring with it
([002](./002-modules-are-removable-slices.md)). The knowledge of how a change
here ripples to there is the scarcest resource in the repository, and it
currently lives in two places: the documentation, which serves humans reading
the system, and the heads of the people who have been here longest.

Automated agents now make changes here routinely — the claim is checkable in
the commit history, which already carries agent co-authorship trailers
alongside the bot-authored updates that have been routine for years — and
they change the economics of that scarce resource. An agent has no osmosis:
it cannot absorb conventions by being around, has no memory between tasks,
and will confidently make a locally-correct change that violates a wiring
rule nobody told it about — updating a schema but not its registration,
adding a dependency but not its license entry, running a test suite in watch
mode and hanging the pipeline. New humans make the same mistakes at first; an
agent makes all of them, every time, until told. And an agent will follow a
written rule exactly, every time, once it is written where the agent will
read it.

That is what this record decides: the rules move into the repository, next to
the code they govern, in the form agents actually consume. The decision
complements the documentation rule ([003](./003-every-project-documents-itself.md))
rather than repeating it — that record serves the human reader trying to
understand the system; this one serves the automated reader trying to change
it correctly. The two audiences read differently: a person builds a mental
model and benefits from narrative; an agent executes instructions and
benefits from short, local, unambiguous rules placed exactly where its work
begins. Keeping the two layers separate, each addressing its own audience,
keeps both honest — neither layer can hide the other's drift.

The safety net is unchanged: an agent-authored change passes the same gate as
a human-authored one ([014](./014-the-gate-is-defined-once-and-runs-everywhere.md)).
The instruction layer exists so agents arrive with the right context, not so
they can be trusted without evidence.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Correct work is possible from the repository alone.** A competent
  agent with no prior knowledge of this system can make a correct change in
  any area using only what the repository tells it; oral tradition is not a
  dependency.
- **R2 — Instructions are nearest-first and small.** The rules governing a
  file are found by walking from the root to that file; each file is short
  enough to hold in working context, and the nearest instruction wins.
- **R3 — Wiring obligations travel with the code they govern.** When a change
  in one place requires updates in another, that obligation is written in the
  directory where the first change is made — not in a central list someone
  must remember to consult.
- **R4 — The two reader layers stay separate.** Human documentation never
  cites the machine-facing files: a person must be able to learn the system
  from documentation alone, without machine scaffolding. The instruction
  layer may point at human documentation where a wiring obligation leads
  there — an agent following a documentation path is not a human depending
  on machine scaffolding — but each layer must stand alone for its own
  audience.
- **R5 — Instructions are held true like tests.** An instruction that
  contradicts the code is a defect, and keeping instructions current is part
  of the change that could break them: the repair lands in the same review
  as the break, not in a later cleanup.
- **R6 — No privileged path for agents.** Agent-authored changes face the
  same gate, review, and release rules as human-authored ones; the
  instruction layer informs, it does not authorize.

## Alternatives

- **One central instruction document.** A single file at the workspace root
  holding every convention. It fails R2 — a central file grows until it
  exceeds the context it was meant to fit in — and R3, because conventions
  written far from their code are the ones that drift; it also fails R5 in
  practice, since nobody editing one project reads (or can maintain) a
  document about all of them.
- **No instruction layer; rely on the gate.** Let agents work blind and catch
  violations in CI. It keeps R6 intact and passes nothing else: the gate
  catches violations it knows about, but the wiring obligations (R3) are
  precisely the ones no check encodes — a missing registration, a stale
  removal checklist, an un-updated sibling file. It also pays the full review
  cost on every avoidable miss, which is the scarcest resource here.
- **Instructions embedded in human documentation.** One set of files serving
  both audiences. It fails R4 and then R2: documents written for both readers
  satisfy neither — the agent's rules drown in narrative, the human's
  narrative accretes machine boilerplate — and the drift of one layer becomes
  invisible inside the other.
- **Per-tool configuration only.** Rely on each agent tool's own settings
  (editor rules, prompt templates) and keep nothing in the repository. It
  fails R1 — the knowledge is bound to one vendor's tool and one developer's
  machine — and R5, because the rules then live outside the repository where
  no change can update them.
- **Do nothing (agents work from the code alone).** The current default in
  most repositories. It fails R1 for anything the code does not literally
  show — wiring, removal, cross-file obligations — and R3 entirely; agents
  produce locally-correct, globally-wrong changes at machine speed, and the
  review burden lands on the few humans who remember the wiring.

## Tradeoffs

- **Positive:** the scarcest resource — wiring knowledge — becomes a
  repository asset instead of a memory (R1, R3); agents and newcomers alike
  start every task with the same local truth (R2); the discipline of keeping
  instructions current surfaces documentation drift early, because a broken
  instruction is noticed the next time anything works in that directory
  (R5); and the separation keeps human documentation clean of machine
  scaffolding (R4).
- **Negative:** every directory now carries a maintenance artifact — the
  instruction files are themselves codebase surface that ages, and a stale
  one actively misleads an agent that follows it faithfully; the nearest-first
  rule needs judgement about what belongs at which level, and a rule written
  at the wrong level is either ignored or over-applied; and there is no gate
  that can check an instruction's truth, so R5 rests on review discipline —
  the same obligation [003](./003-every-project-documents-itself.md) already
  carries, now with a second, less forgiving reader.
- **Neutral / follow-ups:** the instruction layer is where the recipes for
  admitting new technologies ([021](./021-a-new-technology-joins-by-recipe.md))
  naturally live, so the two practices should be kept consistent as they
  grow; if agents ever author changes at materially higher volume than
  people, the review burden shifts toward the gate and the standing
  obligation becomes encoding more wiring rules as checks rather than prose;
  and the root-level file should stay small by design — growth there is a
  signal that a rule belongs one level down, which is a review judgement
  worth watching rather than automating.
