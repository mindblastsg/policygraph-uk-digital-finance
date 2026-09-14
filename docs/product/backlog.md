# Product backlog

Priorities: P0 is required for the first usable POC; P1 supports validation; P2 is exploratory.

| ID | Priority | User story | Acceptance signal |
|---|---|---|---|
| PG-01 | P0 | As an analyst, I can see corpus scope and freshness | Fixture digest/generator metadata and per-record `status_as_of` are exposed; no live freshness claim |
| PG-02 | P0 | As a maintainer, I can register a curated public source | Schema validates ID, publisher, URL, topic, date |
| PG-03 | P0 | As a maintainer, I can supply fetched content explicitly | Offline adapters and a guarded fetcher injection seam exist; no live transport ships |
| PG-04 | P0 | As a reviewer, I can inspect extracted claims | Each claim includes source ID and locator |
| PG-05 | P0 | As an analyst, I can distinguish policy states | Consultation/proposal/final/in-force are explicit |
| PG-06 | P0 | As a maintainer, I can rebuild demo data offline | Fixture build is deterministic |
| PG-07 | P0 | As an analyst, I can explore a topic graph | Linked entity and typed relationship cards render |
| PG-08 | P0 | As a keyboard user, I can navigate the evidence view | Topic controls are native buttons and evidence is statically inline in cards |
| PG-09 | P0 | As an analyst, I can inspect evidence from an edge | Evidence view is one action away |
| PG-10 | P0 | As a maintainer, I can reject invalid graphs | Orphaned provenance and invalid status fail validation |
| PG-11 | P1 | As a product team, we can run a golden-set evaluation | Metrics and failures are reproducible offline |
| PG-12 | P1 | As a contributor, I receive automated quality feedback | Read-only CI runs lint, types, tests, evals, build |
| PG-13 | P1 | As a researcher, I can understand ontology decisions | Schema and ADRs are published |
| PG-14 | P1 | As an analyst, I can answer a benchmark task | Median completion is measured against <10 min target |
| PG-15 | P1 | As a user, I see useful empty and failure states | Missing coverage is never presented as “no activity” |
| PG-16 | P2 | As an analyst, I can export an evidence trail | Export preserves citations and status labels |
| PG-17 | P2 | As a maintainer, I can compare extractor versions | Versioned eval results show regressions |
| PG-18 | P2 | As a team, we can assess broader coverage | Expansion experiment measures marginal value and cost |

Implementation ordering follows the [roadmap](roadmap.md); definitions of success are in the [evaluation plan](evaluation-plan.md).
