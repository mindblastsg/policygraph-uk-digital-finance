# Product brief

## Product statement

PolicyGraph helps UK digital-finance policy analysts trace how policy develops by connecting topics, organisations, events, claims, and primary-source evidence in linked, filterable cards.

## Problem

Evidence about DLT, tokenisation, the Digital Securities Sandbox, stablecoins, and cryptoasset regulation is fragmented across institutions and document types. Analysts spend substantial time finding, sequencing, and reconciling sources. Conventional search encourages document-by-document reading and can obscure policy status. Generative summaries can accelerate synthesis but introduce unacceptable provenance and hallucination risks.

## Users

- **Primary:** policy and regulatory analysts producing evidence-backed briefings.
- **Secondary:** fintech product/compliance leads assessing implications; researchers learning the policy landscape.
- **Not an MVP user:** retail consumers seeking personalised legal, financial, or investment advice.

See [personas and journeys](personas-and-journeys.md).

## Jobs to be done

- When investigating a policy topic, show me the relevant actors, events, and changes so I can form a coherent view quickly.
- When I encounter a graph relationship, show me the source and evidence passage so I can verify it.
- When policy status changes, preserve the distinction between consultation, proposal, final rule, and in-force law.

## MVP scope

- A curated, explicitly bounded set of public UK sources.
- Entities, policy events, claims, and typed relationships.
- Topic exploration with linked entity, event, relationship, source, and evidence cards.
- Source and locator metadata for all material policy claims and relationships.
- Deterministic offline demo data and a reproducible build.
- Golden-set quality evaluation and visible coverage/caveat messaging.

## Non-goals

- Legal advice, compliance determination, or investment guidance.
- Exhaustive UK policy coverage or real-time monitoring.
- Autonomous publication of AI-generated claims.
- Prediction of regulatory outcomes or political intent.
- User accounts, collaboration, alerts, or enterprise integrations in the MVP.
- Replacing primary-source reading or expert judgement.

## Hypotheses and success measures

| Hypothesis | Validation measure | Threshold |
|---|---|---|
| A graph reduces synthesis effort | Median time to answer a benchmark policy-history question | <10 minutes |
| Evidence links increase trust | Material policy claims and relationships with a valid source and locator | 100% |
| Structured extraction is usable | Citation correctness on the golden set | >=90% |
| Status modelling prevents misreading | Unsupported relationships and status-critical errors | 0 |
| Users find the workflow usable | Task completion across 5 moderated sessions | >=4/5 |

These are validation targets, not achieved results. Measurement is defined in the [evaluation plan](evaluation-plan.md).

## Constraints

The POC must run without secrets or live model access in CI; preserve source rights; distinguish derived data from original content; and make uncertainty, dates, coverage, and evidence inspectable. Source material is treated as untrusted input.

## Product status

Version 0.2.0 is a functional POC: the deterministic fixture pipeline, reusable ingestion SDK, graph, API, UI, and bounded golden evaluation work offline. It is AI-ready through a replaceable extraction interface, but does not ship a working AI/LLM extractor. “Validated MVP” remains reserved for meeting the real-corpus and moderated-user gates in the [evaluation plan](evaluation-plan.md).

Status values describe what a historical document represented on `status_as_of`; they are not current-law determinations. Users must inspect current primary sources before relying on regulatory status.
