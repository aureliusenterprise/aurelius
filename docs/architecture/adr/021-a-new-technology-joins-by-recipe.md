# 021. A new technology joins the system by recipe

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

When a technology the system did not previously use takes root — a new
language, a new kind of artifact, a new class of service — it does not arrive
with hand-wired plumbing. It arrives by recipe: a repeatable, written
procedure that makes the new technology a first-class citizen of the
workspace in one pass.

A complete recipe does four things. It teaches the workspace to recognise
projects written in the technology, by the markers they carry, so they are
discovered automatically rather than registered by hand. It gives them the
same standard lifecycle as everything else — build, validate, package, run —
expressed through the same task runner, so the pipeline, the pre-commit
hooks, and the person debugging at speed see one way to do things rather than
one per language. It wires their development infrastructure to start with
the application, as every other kind of project already does
([005](./005-dev-infra-starts-with-the-app.md)). And it records the removal
checklist at the same time: what to unwire, where, in which files — a
technology whose wiring nobody can enumerate is a technology nobody dares
remove, so the recipe makes it leave as cleanly as it arrived.

The recipes live in the repository, beside the directories they govern, and
are followed by whoever adds the project — human or automated agent. The
workspace-level recognition logic is shared, not per-project: one place
decides how a technology is detected and what its projects can do.

This record decides how a technology is admitted; what the repository says to
whoever works in an admitted directory afterwards is governed elsewhere
([022](./022-the-codebase-explains-itself-to-its-agents.md)).

## Context

The system is deliberately polyglot — a browser application, services in
several languages, functions, connectors, pipelines, documentation — and
polyglot is another word for "many kinds of thing must be built, run, and
released". The workspace's task runner is the single entry point for all of
that: one command shape that works for every project, so the workspace-wide
flows — the gate, the release — reach every project without per-project
wiring.

The pressure point is the moment a new kind of thing arrives. Without a
recipe, that moment produces bespoke wiring: a task definition copied from a
neighbouring project and adapted, a pipeline step added by hand, a compose
file with no owner, a discovery list someone must remember to append to. Each
bespoke choice is small and defensible; together they are how a workspace
silently becomes N ways of doing the same thing, and how a technology becomes
unremovable — nobody knows everything that was wired for it, so nobody dares
take it out.

With a recipe, the same moment is routine: follow the procedure, and the new
technology is discovered, buildable, validatable, releasable, and — equally
importantly — removable on its first day. The recipe also captures the
knowledge once, where the next person (or agent) adding the second project in
that technology does not have to rediscover it. This matters more than in a
typical organisation because the people doing the adding are not always
people: automated agents make changes in this repository, and a written
recipe is something an agent can actually follow.

The recognition mechanism itself is a workspace-level program keyed to
marker files — the files a technology's projects inherently carry — so
projects need no registration and cannot be forgotten. That mechanism already
exists for the languages and artifact kinds in use; this record decides that
it is the permanent way in, for every future technology too.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — New kinds of thing are discovered, not registered.** A project in an
  admitted technology is picked up automatically by what it contains;
  forgetting to announce it is impossible.
- **R2 — One command shape covers every technology.** Build, test, lint,
  serve, and release run the same way regardless of what language the project
  is written in, so tooling, pipeline, and people learn one interface.
- **R3 — Admission is a written, repeatable procedure.** Adding the second
  project of a kind costs less than the first, because the procedure exists
  and is kept current; it is followable by any competent person or agent
  without oral tradition.
- **R4 — The gate and the release include new technologies for free.** A
  project admitted by recipe is automatically covered by the workspace-wide
  flows; opting in to validation and release is not a separate manual step
  that can be skipped.
- **R5 — Every admitted technology is removable.** The recipe includes the
  removal checklist, and keeping it current is part of keeping the technology
  admitted; "we can't get rid of it, we don't know what it's wired to" is
  ruled out by construction.
- **R6 — Recognition logic is shared, not per-project.** The rules for
  detecting a technology and giving its projects their lifecycle live in one
  place per technology, where they can be reviewed and changed once.

## Alternatives

- **Hand-wire each new project from a neighbour's example.** The common
  organic approach. It fails R3 — the knowledge lives in whoever copied what
  — and R5, because removal knowledge is never captured when wiring
  knowledge was never written. It passes R2 only as long as everyone copies
  faithfully, which is exactly what drift prevents.
- **Per-project registration lists.** The workspace keeps an explicit list of
  projects and technologies. It fails R1 — forgetting the list is the default
  failure — and spends the budget of R3 on bookkeeping the marker-based
  mechanism makes unnecessary. It is the arrangement the current
  recognition mechanism already replaced.
- **One language, one framework, no new technologies.** The maximal
  consistency option: admit nothing new and every recipe problem disappears.
  It fails the premise — the system's shape (a browser application, several
  service runtimes, functions, connectors) is settled, and the right tool per
  job is the point — so this alternative is really a rejection of the system,
  not an arrangement within it.
- **Let each technology bring its own native tooling, orchestrated outside
  the workspace.** Makefiles, shell scripts, or a second orchestrator beside
  the task runner. It fails R2 — the command shape fragments by language —
  and R4, because workspace-wide flows (gate, release) must then learn about
  each technology twice: once to run it, once to keep the external flow in
  sync. It also fails R5: external wiring is precisely the wiring nobody can
  enumerate for removal.
- **Do nothing (no recipe, no shared recognition).** Zero cost until the
  second technology arrives, then pays per project: bespoke wiring, bespoke
  removal risk, and a command shape that fragments with each admission. It
  fails R1–R5 by drift rather than by decision, which is the worst way to
  acquire them.

## Tradeoffs

- **Positive:** a new technology is buildable, gated, releasable, and
  removable on day one (R2, R4, R5); the knowledge of "how does a thing of
  this kind join us?" is written once and followable by agents as well as
  people (R3); recognition is a property of the project's own files, so
  nothing depends on memory (R1); the shared logic means a fix or extension
  to a technology's handling applies to all its projects at once (R6).
- **Negative:** the recipe layer is itself software that must be maintained —
  recognition logic, lifecycle defaults, and the written procedures all age,
  and a stale recipe is worse than none because it will be followed; recipes
  have a granularity problem in both directions (too coarse and they don't
  fit the project, too fine and they're copies), which needs judgement to
  keep right; and a recipe can lag the platform it targets, so an admission
  done by an outdated recipe produces exactly the bespoke drift the record
  exists to prevent.
- **Neutral / follow-ups:** a recipe is documentation, and documentation that
  contradicts reality is a defect: a recipe that no longer works is a defect
  to be fixed, not a draft to be tolerated; when a technology is eventually
  removed, the removal checklist executed and closed is this record's claim
  to removability tested for real; and the boundary between "a new
  technology" (recipe applies) and "a new version of an existing one"
  (dependency policy applies,
  [020](./020-dependencies-stay-current-by-default.md)) is a judgement call
  the recipes themselves should make explicit as they grow.
