# Roadmap

This is an outcome-led delivery roadmap; dates are intentionally unset until ownership and capacity are confirmed.

Version 0.1.0 is the functional alpha described in the delivered rows below. It is not a validated MVP and does not contain a live AI extractor.

| Horizon | Outcome | Deliverables | Exit evidence |
|---|---|---|---|
| Now — Foundation | Make the product thesis and trust contract reviewable | Product artefacts, architecture, governance, repository skeleton | Internal-link check; scope/metric consistency review |
| Next — Reproducible data | Demonstrate a traceable source-to-graph transformation | Typed models, curated registry, adapters, deterministic fixtures, graph validation, CLI | Clean offline rebuild; every edge has provenance |
| Delivered — Functional alpha | Let users explore and verify the sample | FastAPI service, accessible web UI, linked topic/entity/event/relationship/source cards | API tests; structural keyboard and empty/error-state checks |
| Delivered — Engineering validation | Make the bounded POC reproducible and release-checkable | Golden-set evals, quality gates, relocatable package, least-privilege CI | Automated fixture gates and distribution checks pass |
| Then — Validate the MVP | Determine whether the functional alpha solves the user problem | Five moderated sessions and real-corpus evaluation | All mandatory thresholds in the evaluation plan pass and are reported honestly |
| Later — Learn and decide | Choose expand, pivot, or stop | Coverage experiments, workflow export research, operating-cost model | Decision memo based on observed evidence |

## Release boundary

The functional alpha is complete only when the deterministic sample can be regenerated, the app can display it, automated evaluations run offline, caveats are visible, and CI passes. It is a validated MVP only after the moderated product evaluation and mandatory quality gates pass. Repository publication alone is not a product validation result.
