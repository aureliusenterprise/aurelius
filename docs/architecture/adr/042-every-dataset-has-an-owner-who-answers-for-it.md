# 042. Every dataset has an owner who answers for it

- **Status:** Proposed
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

Every dataset the system keeps — a table, a stream, a store of operational
signals — has an owner: a named role that answers for its shape, its
lifetime, and its quality, and whose approval a change to those needs. A
dataset may be declared shared, but sharing is itself the ownership answer,
recorded with a named custodian — not the absence of one. Until this record is
accepted, the datasets with more than one writer have no answer at all, and
disagreements about them are settled by whoever edits first.

## Context

The system keeps data in places with different lives: business rows in a
database, events in streams, operational signals in their own stores. Each
raises the same quiet question — who answers for this? — and today the answer
is nowhere written.

The question stopped being theoretical the moment one store grew a second
hand. The database the API writes is the same database the event sink writes:
one store, two writers, each shaped by a different part's needs. A change to
what a row means is now a change to what the other writer stores, and neither
part's tests can see the other's assumption. The schema-change record
([023](./023-storage-schema-changes-by-recorded-migration.md)) decides how a
schema changes; it cannot decide who says yes. The shared-concept record
([004](./004-one-shared-domain-model.md)) decides that a concept has one
canonical definition; it does not decide who answers when two parts want the
definition to bend.

The same absence has softer but real costs. A person asking "can we trust
this number?" has no one to ask. A dataset nobody owns is a dataset nobody
notices decaying, and its lifetime question — owned in principle by the
data-lifetime record ([025](./025-data-has-a-stated-lifetime.md)) — has no one
to answer for it in practice. And when a dataset is finally retired, nobody
can say what still reads it.

The force is not team size. Even one team needs the answer, because the team
hands over: new joiners, agents working from the codebase, and future
reviewers all ask "who cares about this table?" and today the codebase does
not say.

The decision to make is what ownership of a dataset means, what the owner may
decide alone, and how a shared dataset states its sharing.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — Every dataset has a name beside it.** For each dataset the system
  keeps, a named role answers for it; the list of datasets and owners is
  small enough to stay true.
- **R2 — Sharing is a stated answer.** A dataset with several writers is
  declared shared, with a named custodian who arbitrates its shape; "several
  writers, no answer" is not a permitted state.
- **R3 — The owner's say is defined.** Changing a dataset's shape, lifetime,
  or meaning requires the owner's approval; the owner is named in the change,
  not consulted by folklore.
- **R4 — Ownership survives people.** The owner is a role, not a person's
  memory; when the person changes, the answer does not.
- **R5 — The answer is findable.** A person asking "who owns this?" finds it
  beside the dataset or in one short list, not by asking around.
- **R6 — Cheap to keep true.** A new dataset arrives with an owner named in
  the change that creates it; ownership is one line, not a ceremony.

## Alternatives

- **Ownership by writer (the status quo).** Whoever writes a dataset owns it.
  It fails R2 the moment a second writer appears — which has already happened
  — and R3, because two writers means two answers, and the one that wins is
  whoever ships first.
- **Ownership by the whole team.** Everyone cares, so no one answers. It fails
  R1 in practice: a question about the data has no address, and the approval
  R3 needs is a meeting instead of a decision.
- **A data governance board.** A standing committee arbitrates every dataset.
  It fails R6 at this scale: a board for a handful of datasets is ceremony
  that the first urgent change routes around, and a routed-around process is
  worse than none.
- **Ownership by the schema's source of truth.** The part whose model defines
  the table owns it. It fails R2 directly: the shared store is precisely the
  case where two models meet, and it fails R5 because the answer is a
  deduction from code, not a stated fact.
- **Do nothing.** Costs nothing today; it fails R1 by leaving the question
  unasked, and every later record that needs an owner — lifetime, quality,
  lineage, compliance — inherits the silence.

## Tradeoffs

- **Positive:** questions about data have an address (R1, R5); the shared
  store's two-writer problem gets an arbiter instead of a race (R2); the
  lifetime and quality questions finally have someone to answer them, which
  the lifetime record assumes and this one supplies
  ([025](./025-data-has-a-stated-lifetime.md)); and a new joiner or agent can
  learn who cares about a table without asking (R4, R5).
- **Negative:** ownership lines are upkeep — a dataset whose owner left is a
  lie waiting to be read, so R4 needs a real hand-over habit; naming an owner
  invites ownership to expand into style review and veto over everything,
  which R3 must bound to shape, lifetime, and meaning; and declaring a dataset
  shared with a custodian still concentrates arbitration in one role, which
  must be exercised visibly or it decays into the status quo with extra
  paperwork.
- **Neutral / follow-ups:** this record is Proposed because the decision has
  not been made: the shared store has two writers and no stated answer. The
  migration record decides how a schema changes and this record decides who
  says yes
  ([023](./023-storage-schema-changes-by-recorded-migration.md)); the
  canonical-concept record decides what a concept means and this record
  supplies the role that answers when meanings are contested
  ([004](./004-one-shared-domain-model.md)); the lifetime record needs an
  owner per kind of data to state its numbers
  ([025](./025-data-has-a-stated-lifetime.md)), and this record is where that
  owner comes from. The placeholder pages on data-governance roles and the
  data dictionary under the architecture section remain headings until this
  record is accepted and written from its answer; the questions of lineage and
  compliance under the same section lean on this record's substrate and should
  not be framed before it; and the mechanism — where the dataset-and-owner
  list lives and how a change proves the owner's approval — must be named at
  acceptance, not deferred.
