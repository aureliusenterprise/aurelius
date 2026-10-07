# 036. The delivery plane is a named exception to the data boundary

- **Status:** Accepted
- **Date:** 2026-10-07
- **Deciders:** Aurelius Enterprise

## Decision

The rule that the system's data never leaves it is a rule about the system:
the running system and its operational picture stay inside the boundary
without exception. The delivery plane — the pipeline that validates and
releases the system — may use outside services, and each such service is a
named entry: the tool, the kind of data it receives, and why the system's own
tools do not answer. A delivery tool not on the list may not receive data from
the pipeline, and a new entry is a new record, not a pipeline edit.

This decision was already in force before it was written down: the pipeline
sends interface snapshots of the user interface to a visual-review service and
source metadata to a hosted code-analysis service, while the running system
and its traces, metrics, and logs have never left. What this record adds is
the principle that makes those two uses deliberate rather than contradictory:
the boundary protects the running system, and the delivery plane crosses it
only at named, recorded points.

## Context

The system keeps its operational picture inside its own boundary: no trace,
metric, or log reaches an outside service, so the system runs and is legible
wherever it runs, including offline and where data may not leave. That rule
was written as a rule about the system, and it still holds without exception.

The pipeline that validates and releases the system is a different activity.
It answers questions about the code and interface before they ship — does this
change alter a screen a customer relies on, does this source introduce a known
flaw — and for those questions the organisation has chosen hosted services,
because the comparison they provide (against every previous screen, against a
continuously updated catalogue of known flaws) is not something the system's
own tools maintain. Those services receive data: pictures of interfaces,
metadata about source.

The two arrangements sit close enough to be confused for each other. A reader
of the boundary rule alone would expect the pipeline to send nothing anywhere;
a reader of the pipeline alone would expect the boundary to be a preference.
Neither is true, and the ambiguity is the risk: the next delivery tool can be
added by anyone, and without a stated rule there is no way to tell a
considered exception from a leak.

The decision to make is what the boundary actually protects, and what it takes
to cross it deliberately.

## Requirements

Any acceptable arrangement must deliver:

- **R1 — The boundary is stated by data class, not by tool.** It is clear from
  the rule itself which data may never leave and which data the delivery plane
  may send, without consulting a tool list.
- **R2 — The running system is never the exception.** No part of the deployed
  system sends anything outside the boundary; the exception belongs to the
  pipeline alone.
- **R3 — Operational data is never the exception.** Traces, metrics, and logs
  stay inside in every activity, delivery included.
- **R4 — Every crossing is named.** For each outside service: the tool, the
  kind of data it receives, and the reason the system's own tools do not
  suffice.
- **R5 — Crossing is a recorded act.** Adding a delivery service that receives
  data means a new record; a pipeline change alone cannot open a new exit.
- **R6 — The system still runs and is legible offline.** The exception must
  not create a dependency that a machine without network access would miss;
  running and observing the system never consult the delivery plane.

## Alternatives

- **No exceptions: the boundary covers every activity.** Clean and absolute.
  It fails R4's purpose in the other direction — the pipeline already uses
  hosted comparison services, so the rule is either false on paper or forces
  removing tools whose comparison value the organisation has chosen to keep; a
  rule that the working pipeline quietly violates teaches readers to ignore it.
- **Treat the boundary as a preference, decided per tool.** It fails R1 and
  R5: with no stated principle, every addition is a judgement call, and the
  difference between a considered exception and an accident is whoever notices.
- **Supersede the boundary entirely.** It fails R2 and R3 outright: the reason
  the system runs offline and in restricted environments is that the boundary
  holds for the running system; dissolving it to legitimise two pipeline
  services trades the system's portability for the pipeline's convenience.
- **Self-host replacements for both services.** Keeps every byte inside. It
  fails the reason the services are used: the value is the comparison against
  history and against a maintained external catalogue, and a self-hosted copy
  of that standing is upkeep the organisation has not chosen to operate.
- **Do nothing (leave the ambiguity).** Costs nothing today; it fails R1 and
  R5 by leaving the boundary readable two ways, which is the state in which an
  unlisted exit gets added without anyone deciding anything.

## Tradeoffs

- **Positive:** the boundary rule can be stated without asterisks because the
  exception is a separate, smaller rule (R1); the running system keeps every
  benefit of the boundary — offline, restricted, customer environments (R2,
  R3, R6); and the next exit is a decision with a paper trail rather than a
  pull request nobody read (R5).
- **Negative:** there are now two rules where a reader hoped for one, and the
  line between "delivery plane" and "system" must be held in every future
  review; each named service is a dependency the pipeline can fail on and a
  recipient the organisation must trust with the data class it receives; and
  the exception invites pressure to widen it, which R5 exists to slow down.
- **Neutral / follow-ups:** the current entries are the visual-review service,
  which receives interface snapshots, and the hosted code-analysis service,
  which receives source metadata; each entry's data kind is a standing
  obligation — a tool that begins receiving more than its entry states has
  opened an unrecorded exit; whether the findings those services return should
  be treated as findings the gate answers for is owned by the gate and
  causation records
  ([014](./014-the-gate-is-defined-once-and-runs-everywhere.md),
  [015](./015-a-change-answers-for-what-it-caused.md)); and this record
  narrows nothing about the boundary itself — the rule it scopes
  ([016](./016-the-system-observes-itself-internally.md)) stands as written,
  and any change to it is a supersession, not an edit.
