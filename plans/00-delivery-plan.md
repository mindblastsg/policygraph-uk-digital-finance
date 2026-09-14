# PolicyGraph delivery plan

## Phase 0 — Documentation discovery

### Allowed APIs and patterns

- Use a Python 3.12 `src/` package configured through `pyproject.toml`, following the PyPA packaging guide: <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>.
- Use FastAPI route decorators, Pydantic response models, `StaticFiles`, and `FileResponse` following the official tutorials: <https://fastapi.tiangolo.com/tutorial/first-steps/>, <https://fastapi.tiangolo.com/tutorial/response-model/>, and <https://fastapi.tiangolo.com/tutorial/static-files/>.
- Test the app with `fastapi.testclient.TestClient` following <https://fastapi.tiangolo.com/tutorial/testing/>.
- Fetch GOV.UK content through `GET https://www.gov.uk/api/content/{path}` and use Search API only for discovery, following <https://content-api.publishing.service.gov.uk/reference.html> and <https://docs.publishing.service.gov.uk/repos/search-api/using-the-search-api.html>.
- Run CI with read-only permissions, `actions/checkout@v6`, and `actions/setup-python@v5`, following <https://docs.github.com/en/actions/tutorials/build-and-test-code/python>.

### Discovery findings

No reusable implementation was identified during discovery. The publishable repository is isolated from upstream workspace reference material, which will not be copied. Remote creation requires the publisher to provide a verified GitHub session and commit identity outside the repository.

### Guards

- No invented or undocumented service APIs.
- No broad crawling, committed third-party PDFs, or live network/LLM dependency in CI.
- No graph claim without source and locator metadata.
- No conflation of consultation, policy proposal, final rule, and in-force legislation.
- No GET bodies, permissive credentialed CORS, secrets, or write-enabled CI.

## Phase 1 — Product foundation and repository structure

Implement the repository skeleton, product brief, personas and journeys, opportunity-solution tree, service blueprint, prioritisation, roadmap, backlog, decision log, risk register, evaluation plan, retrospective, governance files, and diagrams. Establish the AI Product Manager narrative: user problem, choices, evidence, product risks, measurable hypotheses, and explicit non-goals.

References: the Phase 0 sources above and the project brief.

Verification:

- All internal links resolve.
- Artefacts agree on target users, MVP scope, metrics, and product status.
- README distinguishes working functionality, scaffolding, samples, and future work.

## Phase 2 — Reproducible ingestion and graph pipeline

Implement typed source/document/claim/entity/event/relationship models; a curated UK source registry; fetch/extract interfaces; GOV.UK and generic web adapters; deterministic sample fixtures; canonicalisation; graph building; validation; and CLI commands. Network ingestion must be explicit and cached outside version control. AI extraction is an interface with a deterministic demo implementation, not an unverified production claim.

References: copy the Content API URL and response-field contracts from the official GOV.UK reference; copy packaging and CLI layout from PyPA.

Verification:

- Unit tests cover registry parsing, adapters with fixtures, canonicalisation, provenance, graph validation, and CLI build.
- A clean offline run regenerates the committed sample graph deterministically.
- Every claim and relationship has a source ID and evidence locator.

## Phase 3 — API and app scaffold

Implement a FastAPI service and accessible, responsive vanilla web UI for exploring topics, entities, events, relationships, sources, evidence, and product caveats. Serve the UI from the same origin.

References: copy route, response-model, `StaticFiles`, `FileResponse`, and `TestClient` patterns from the FastAPI documentation listed above.

Verification:

- Health, graph, entity, event, and source endpoints pass API tests.
- The UI loads from `/`, supports keyboard use, and presents empty/error states.
- No separate-origin CORS configuration is added.

## Phase 4 — Executable evaluation, quality, and automation

Implement deterministic golden-set evals, quality gates, lint/type/test/build commands, CI, and a changelog. Review and complete the Phase 1 governance, issue/PR templates, security policy, contributing guide, code of conduct, citation metadata, and licence against the implemented system; ensure all reporting guidance links to actionable public channels.

References: copy pytest configuration and GitHub Actions patterns from Phase 0 documentation.

Verification:

- Formatting, linting, type checking, tests, evals, package build, and secret-pattern scan pass locally.
- CI uses least privilege and has no network or secret dependency for tests.
- Package and app start instructions work from a clean environment.

## Phase 5 — Release verification and publication

Review repository contents, provenance, licensing notes, sample-data labels, and staged files. Initialise Git, configure an author identity supplied by the publisher, commit only after all checks pass, then use a verified GitHub session, confirm the slug is available, create a public repository without auto-push, inspect the remote, and push `main`.

Verification:

- `git diff --cached --check` and a sensitive-value scan pass before commit.
- The remote contains only this child directory.
- GitHub Actions passes and the public README renders correctly.

Publication credentials and commit identity must be supplied outside the repository; local delivery and verification remain independent of that publication step.
