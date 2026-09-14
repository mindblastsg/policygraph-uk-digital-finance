# Functional POC completion evidence

Release: 0.2.0. Review date: 2026-09-14. Scope: the working proof of concept described in the [delivery plan](../plans/00-delivery-plan.md) and [product brief](product/product-brief.md), including the reusable ingestion SDK and portfolio visuals.

## Requirement-to-evidence map

| Requirement | Implementation and evidence |
|---|---|
| Public open-source repository | [PolicyGraph on GitHub](https://github.com/mindblastsg/policygraph-uk-digital-finance); MIT licence, contributing guide, governance, security policy, conduct policy, issue and PR templates, citation metadata |
| AI Product Manager narrative | Product brief, personas/journeys, RICE prioritisation, opportunity-solution tree, service blueprint, backlog, decision log, risk register, evaluation plan, roadmap and retrospective in [product documentation](product/) |
| Reproducible ingestion and graph | Registry → local adapter → text/located lines → deterministic claim extraction → canonicalisation → graph validation. `policygraph build-sample` reproduces the committed graph; `test_committed_graph_matches_rebuild` compares exact bytes. Fixtures and outputs use LF line endings across platforms. |
| Reusable pipeline for contributors | Typed `SourceAdapter`, metadata-only discovery, explicit class loading, five bundled JSON Schemas, validation CLI, adapter test helper, example package and seven [contributor guides](contributors/) |
| Evidence and status integrity | Tests reject missing/forged evidence, invalid locators, duplicate IDs, wrong source ownership, changed relationship meaning and status mismatches. Invalid API data yields a stable 503 response and degraded health. |
| Working app and API | Same-origin FastAPI service serves the explorer, graph, topics, entity/event/relationship/source details and API documentation. Five topics are exposed; DLT/tokenisation display their registered sources and explicit claim-coverage gaps. |
| Browser experience | Live browser verification covers topic switching, DSS proposal/consultation labels and evidence, DLT coverage gap, keyboard activation and focus transfer. At a 390-pixel mobile viewport the page fits without horizontal overflow and section links wrap with spacing. |
| Evaluations and CI | 50 tests pass locally; the four-record synthetic golden set passes all thresholds. CI runs formatting, lint, types, tests, evaluation, links, secret-pattern checks, JavaScript syntax and package verification. [Authoritative CI runs](https://github.com/mindblastsg/policygraph-uk-digital-finance/actions/workflows/ci.yml) must be checked for the release commit. |
| Installable distribution | `scripts/verify_wheel.py` creates a fresh environment, installs declared dependencies and the wheel, checks that API/assets/data resolve inside that installation, validates the graph and schemas, then installs and exercises the example adapter with its bundled fixture. |
| Portfolio visuals | Nine labelled AI concept images: welcome, explorer, evidence, topic graph/timeline, ingestion, analyst journey, human review, evaluation and larger-project epic. They are placed in the README and corresponding product documents. |
| Long-term project mindmap | The [roadmap](product/roadmap.md) includes the broader policy-intelligence platform and future domains. The original v0.1.0 image label is historical; those ambitions remain outside this POC. |

## Verification limits

The four fixtures are authored synthetic examples. The deterministic claim extractor reads visible markers; it is an executable baseline behind a replaceable interface. Live crawling, an LLM extractor, semantic search, interactive graph/timeline views, a review console, exports, accounts and alerts remain future work. The repository does not claim a deployed hosted service or a PyPI publication.

The evaluation demonstrates regression resistance on this bounded sample. Real-corpus accuracy, five moderated analyst sessions, assistive-technology research and operating-cost measurements are the next product-validation experiments. They are not reported as completed or required to call this engineering POC functional.
