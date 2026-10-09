# 047. One search store is the only system of record for metadata

- **Status:** Proposed (becomes Accepted when increment 0.2 provides the store in the spine)
- **Date:** 2026-10-09
- **Deciders:** Aurelius Enterprise

## Decision

We will keep all catalogue data — type definitions, entities, relationships, classifications,
glossaries, audit events — in a single search store, which is both the system of record and the
search index. There is no separate graph database, relational database or index to keep in step
with it.

The sharp edge: the store has no multi-record transactions and no native graph traversal. Where
the catalogue needs either, the application provides it, and each such place is recorded as a
design decision.

## Context

The current catalogue keeps its data in a graph database, which itself runs on a wide-column
store, plus a separate full-text index, plus a coordination service. Each is a system to deploy,
secure, back up, upgrade and understand. Most of the catalogue's daily use is search and
retrieval of individual records; graph traversal matters for lineage and for propagating
classifications, but on graphs that are shallow compared with what a graph database is built for.

The team must be able to run the whole system on one machine for development
([006](./006-the-whole-system-runs-on-one-machine.md)), and operations must stay affordable
for small installations.

## Requirements

- **R1 — One thing to operate.** A deployment has one stateful data service to run, back up and
  restore.
- **R2 — Search is first-class.** Full-text and attribute search, facets and suggestions perform
  well without a second copy of the data.
- **R3 — No drift between copies.** There is no second store that can disagree with the first.
- **R4 — Graph questions remain answerable.** Lineage and classification propagation are
  computed correctly for the depths the catalogue supports.

## Alternatives

- **Keep a graph database plus a search index (the current design).** Meets R4 natively but fails
  R1 and R3: two or more stores to operate and keep consistent.
- **Relational database plus a search index.** Meets R4 with recursive queries but fails R1 and R3
  in the same way.
- **Relational database only.** Meets R1, R3, R4 but weakens R2: full-text relevance, facets and
  suggestions are the catalogue's most used features.

## Tradeoffs

- **Positive:** one store to operate, back up and secure; search is native; no copies to reconcile.
- **Negative:** consistency across records and multi-hop traversal become application concerns,
  with their own tests and failure modes; very deep lineage is slower than in a graph database.
- **Neutral / follow-ups:** the storage layout, identifier strategy, consistency model and
  traversal strategy are design-log entries in [the conversion ledger](../conversion/design-log.md).
  Current implementation: Elasticsearch 9.
