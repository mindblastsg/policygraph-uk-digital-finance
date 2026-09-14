# Roadmap

## Long-term product epic

![Concept mind-map of the larger PolicyGraph platform, spanning source intelligence, temporal knowledge graphs, AI capabilities, trust and governance, user experiences, platform workflows and future policy domains](../assets/screenshots/08-epic-roadmap-concept.png)

> **Concept visual:** AI-generated map of the larger, domain-general PolicyGraph ambition. With the exception of the small UK digital-finance proving ground, these capabilities and domains are explicitly outside the v0.1.0 POC and are not delivery commitments.

The image retains its original v0.1.0 design label. Its platform ambitions also remain outside the v0.2.0 ingestion-SDK release.

The longer-term epic is a traceable public-policy intelligence platform: continuously updated primary sources become temporal entities, events and relationships; AI supports structured extraction and evidence-linked synthesis; and users can ask, explore, compare and monitor policy change while inspecting the system's workings. Potential domains include AI regulation, payments, financial stability, climate finance, competition, sovereign debt, a wider World Factbook and financial-crisis archives.

## Frontend demonstration roadmap

The next interface increment is organised around the policy-official journey rather
than the underlying graph model. The detailed, implementation-ready sequence is in
the [frontend demo roadmap](../../plans/01-frontend-demo-roadmap.md).

| Phase | User outcome | Demonstration surfaces | Exit evidence |
| --- | --- | --- | --- |
| 1 — First-screen orientation | Understand the audience, use case, evidence basis, limitation and next action immediately | Policy-official hero, three task cards, trust strip, guided topic start | At least 4/5 first-impression participants correctly explain all four concepts |
| 2 — Guided topic workspace | Find milestones, organisations, connections and sources without graph vocabulary | Topic summary, journey wayfinding, explicit chronology/status, accessible linked cards | Relevant milestone within two minutes; correct connection and status interpretation |
| 3 — Evidence detail | Verify and share why a connection is shown | Stable evidence page with passage, locator, source metadata and primary-source action | Evidence and primary source each reachable in one action; stable deep link works in Pages and Docker |
| 4 — Method and limitations | Judge how the graph was produced and what has actually been tested | Methodology, corpus coverage and bounded evaluation pages | All figures trace to committed metadata; synthetic and unvalidated claims remain explicit |
| 5 — Moderated validation | Decide what interface investment is justified next | Five policy-official sessions and published aggregate findings | 4/5 completion, median under ten minutes, source inspected, zero status-critical interpretation errors |
| 6 — Conditional expansion | Address observed friction without weakening trust | Optional visual map/table, real-corpus briefing trail, retrieval experiment | Built only when research and real-corpus gates justify the relevant option |

Phases 1–4 are the recommended next demonstration cut. Phase 5 is a mandatory
decision checkpoint. A visual graph, briefing export and semantic retrieval are not
default next steps merely because they appear in concept artwork.

## POC delivery roadmap

This is an outcome-led delivery roadmap; dates are intentionally unset until ownership and capacity are confirmed.

Version 0.2.0 is the functional POC described in the delivered rows below. It is not a validated MVP and does not contain a live AI extractor.

| Horizon | Outcome | Deliverables | Exit evidence |
|---|---|---|---|
| Delivered — Foundation | Make the product thesis and trust contract reviewable | Product artefacts, architecture, governance, repository skeleton | Internal-link check; scope/metric consistency review |
| Delivered — Reproducible data | Demonstrate a traceable source-to-graph transformation | Typed models, curated registry, adapters, deterministic fixtures, graph validation, CLI | Clean offline rebuild; every edge has provenance |
| Delivered — Functional alpha | Let users explore and verify the sample | FastAPI service, accessible web UI, linked topic/entity/event/relationship/source cards | API tests; structural keyboard and empty/error-state checks |
| Delivered — Engineering validation | Make the bounded POC reproducible and release-checkable | Golden-set evals, quality gates, relocatable package, least-privilege CI | Automated fixture gates and distribution checks pass |
| Delivered — Reusable ingestion SDK | Enable external contributions and reuse | Adapter protocol, plugin discovery, schemas, starter package, contribution guides | Contract tests, packaged fixture and installed-wheel validation |
| Delivered — Public research alpha | Put the bounded explorer in front of users | GitHub Pages deployment, static graph fallback, structured feedback route | Public HTTPS checks and responsive interaction verification pass |
| Next — Acquire the first real corpus | Test source adapters and provenance on authoritative material | 60–100 accepted documents under the bounded [initial acquisition scope](initial-data-acquisition-scope.md) | Corpus, rights, repeatability and citation gates pass |
| Then — Validate the MVP | Determine whether the functional alpha solves the user problem | Five moderated sessions and real-corpus evaluation | All mandatory thresholds in the evaluation plan pass and are reported honestly |
| Later — Learn and decide | Choose expand, pivot, or stop | Coverage experiments, workflow export research, operating-cost model | Decision memo based on observed evidence |

## Release boundary

The functional alpha is complete only when the deterministic sample can be regenerated, the app can display it, automated evaluations run offline, caveats are visible, and CI passes. It is a validated MVP only after the moderated product evaluation and mandatory quality gates pass. Repository publication alone is not a product validation result.
