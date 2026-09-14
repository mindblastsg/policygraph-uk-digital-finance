# Frontend demo roadmap — policy-official research journey

## Objective

Advance PolicyGraph from a single evidence explorer into a guided demonstration
that a UK policy official can understand on the first screen and use to complete
the documented journey: frame a question, find milestones, understand connections,
verify evidence and assemble a defensible answer.

This roadmap improves the evidence-first POC. It does not commit the project to a
general policy platform, live AI answers, complete UK coverage, accounts, alerts or
regulatory prediction.

## Page map

| Surface | User purpose | Delivery point |
| --- | --- | --- |
| Welcome and guided start | Understand who the product is for, what it helps with and its limits | Phase 1 |
| Topic workspace | Follow milestones, organisations, connections and sources for one topic | Phase 2 |
| Evidence detail | Verify why a connection is shown and open its primary source | Phase 3 |
| Methodology and evaluation | Understand how records are produced, what was tested and what remains unknown | Phase 4 |
| Optional visual map | Explore network structure with an equivalent list/table route | Phase 6, only after research |
| Briefing workspace | Assemble and export a cited evidence trail | Post-MVP, after real-corpus validation |

## Phase 0 — Documentation discovery and delivery constraints

### What was established

- The primary user is a policy analyst preparing an evidence-backed briefing;
  their failure anxiety is confusing a proposal with settled policy or repeating an
  untraceable claim (`docs/product/personas-and-journeys.md`, “Primary persona”).
- The required journey is Frame → Discover → Connect → Verify → Synthesize
  (`docs/product/personas-and-journeys.md`, “Journey: evidence-backed policy
  history”).
- Provenance, policy status and event exploration outrank semantic search, alerts
  and collaboration (`docs/product/prioritisation.md`, RICE table).
- The current implementation is one dependency-free page using native browser APIs
  and a validated JSON graph (`app/index.html`; `app/assets/app.js`).
- The same client must continue to work in the static GitHub Pages edition and the
  same-origin Docker/FastAPI edition (`app/README.md`; `docs/architecture.md`,
  “Runtime distribution”).
- New HTML pages must be included deliberately in the Pages builder, Python package,
  FastAPI routes and installed-wheel verification (`scripts/build_pages.py`;
  `pyproject.toml`; `src/policygraph/api.py`; `scripts/verify_wheel.py`).

### Allowed implementation patterns

- Native semantic HTML, CSS and browser DOM APIs.
- `URL`, `URLSearchParams` and `history.replaceState` for stable demo state.
- Same-origin `fetch('/api/...')` in the Docker edition and relative
  `fetch('data/graph.json')` in the static edition.
- Existing read-only graph, topic, entity, event, relationship and source endpoints
  in `src/policygraph/api.py`.
- `escapeHtml`, `safeSourceUrl`, evidence locators, visible `status_as_of` labels,
  native buttons, landmarks, anchors, `aria-pressed`, `aria-live` and `role="alert"`
  from the current client.
- Progressive enhancement: cards, lists and tables remain the canonical accessible
  representation even if a visual map is later added.

### Anti-pattern guards

- Do not introduce a second frontend service, framework, router or CORS dependency
  without a new architecture decision.
- Do not lead with knowledge-graph terminology, ingestion architecture or AI.
- Do not use absolute asset paths that break the GitHub Pages project subpath.
- Do not render graph strings without escaping or source URLs without the HTTPS host
  allowlist.
- Do not infer an event date from `status_as_of`; use an asserted event date or label
  a source-publication date explicitly.
- Do not make status colour-only, a network graph the only route, or an empty sample
  look like no real-world activity.
- Do not present concept artwork, synthetic evaluation results or polished screens
  as proof of real-corpus accuracy or user value.

### Phase 0 verification

- Confirm the current files and routes listed above still exist before each phase.
- Re-read the product brief, persona journey, decision log and evaluation plan when
  a phase begins; do not implement from this roadmap alone.
- Stop and update the plan if the dual static/container distribution contract has
  changed.

## Phase 1 — Make the first screen self-explanatory

### Outcome

A policy official can identify the audience, task, evidence basis, limitation and
next action without facilitator explanation.

### What to implement

1. Replace the current mechanism-led eyebrow with “For UK policy professionals.”
2. Retain the evidence-first headline but name briefing preparation and the three
   user questions: what changed, who acted and what supports the finding.
3. Add a primary “Explore a policy topic” link to `#explorer` and a secondary “How
   evidence is verified” link to the trust section.
4. Add three task cards using the existing `.principles` pattern:
   “What changed?”, “Who was involved?” and “What supports this finding?”.
5. Add a compact trust strip: primary sources, evidence on each material connection,
   historical status shown with a date, and explicit coverage gaps.
6. Reframe the limitation as a useful scope statement: a bounded synthetic research
   prototype, not a complete or current-law record or legal advice.
7. Rename “Choose a topic” to “What are you researching?” and mark Digital
   Securities Sandbox as the recommended walkthrough while it remains the richest
   sample.

### Documentation references

- Copy the jobs and responsible-use boundary from `docs/product/product-brief.md`,
  “Jobs to be done” and “Non-goals”.
- Copy the policy-official framing from `docs/product/personas-and-journeys.md`,
  “Primary persona”.
- Reuse the hero, notice and principles structures in `app/index.html` and the
  matching classes in `app/assets/styles.css`.
- Preserve the direct `#explorer` entry and query-selected topic pattern in
  `app/assets/app.js`.

### Verification checklist

- In a five-person first-impression test, at least 4/5 correctly state who it is
  for, what question it helps answer, where evidence comes from and what it cannot
  establish after ten seconds on the first screen.
- Both calls to action work by keyboard and visible focus is retained.
- The five topic controls remain present and the recommended walkthrough is text,
  not colour alone.
- At 390 CSS pixels there is no horizontal overflow.
- Automated UI assertions cover the audience, task cards, scope wording and CTA
  targets.

### Anti-pattern guards

- Do not put “AI”, “knowledge graph”, “entity” or “edge” ahead of the user task.
- Do not hide the scope notice below the explorer.
- Do not add navigation links to unimplemented pages.

## Phase 2 — Turn topic results into a guided policy-history workspace

### Outcome

An official can move from a topic to a pivotal milestone, involved organisation and
supporting source without learning the graph data model.

### What to implement

1. Keep the existing `?topic=` deep link and single data-loading path.
2. Replace user-facing section names with “Policy milestones”, “Organisations and
   policies”, “Connections and evidence”, and “Primary sources”.
3. Add a topic summary that explains exactly what the bounded dataset contains,
   including source, milestone and supported-connection counts.
4. Add journey wayfinding: Frame the question → Find milestones → Understand
   connections → Verify evidence.
5. Present milestones chronologically only when a date is explicitly asserted. If
   only a publication date exists, label it “Source published” rather than implying
   the represented event happened that day.
6. Keep coverage/freshness and empty-state explanations adjacent to each view.
7. Preserve current linked-card sections as the canonical non-visual experience.

### Documentation references

- Copy the stage names and measures from `docs/product/personas-and-journeys.md`,
  journey table.
- Reuse `renderTopic`, `section`, `countLabel`, `escapeHtml`, `safeSourceUrl` and
  the coverage-note pattern from `app/assets/app.js`.
- Reuse the status, evidence, grid, empty and focus styles from
  `app/assets/styles.css` and `app/assets/accessibility.css`.
- Follow ADR-006 in `docs/product/decision-log.md` for historical status wording.

### Verification checklist

- A participant finds a relevant milestone within two minutes.
- A participant correctly explains one directed connection.
- Selecting every topic updates the URL, results heading, counts and focus.
- Proposal, consultation, final and in-force wording never relies on colour alone.
- DLT/tokenisation continue to say “no extracted claims in this sample,” not “no
  policy activity.”
- API, Pages and installed-wheel tests still exercise the same client.

### Anti-pattern guards

- Do not invent chronology from missing event dates.
- Do not collapse proposals and rules into a generic “active” state.
- Do not duplicate a second topic data model in the browser.

## Phase 3 — Add a stable evidence-detail page

### Outcome

Every material connection can be opened as a focused, shareable explanation of why
it appears in PolicyGraph.

### What to implement

1. Add `app/evidence.html?relationship=<id>` with a clear “Why is this connection
   shown?” heading.
2. Show the two connected records, relationship type, supporting passage, source
   title, publisher, historical status, status date and exact source location.
3. Keep “Open primary source” as the dominant action and return users to their
   selected topic without losing context.
4. Add explicit copy explaining that the passage supports the displayed connection
   but does not establish broader legal effect or current-law status.
5. Fail closed for missing, malformed or orphaned relationship IDs.
6. Update every delivery surface: Pages builder, FastAPI HTML route, package data,
   installed-wheel verification, Docker image and automated tests.

### Documentation references

- Copy the evidence hierarchy from `docs/product/service-blueprint.md`, “Verify”,
  and concept placement `docs/assets/screenshots/02-evidence-inspection-concept.png`.
- Reuse `record`, `escapeHtml`, `evidenceLabel`, `safeSourceUrl` and `sourceLink`
  from `app/assets/app.js`; extract shared helpers rather than creating looser copies.
- Copy the static-mode marker and relative-path transformation pattern from
  `scripts/build_pages.py`.
- Copy the FileResponse route pattern from `src/policygraph/api.py` and package-file
  assertions from `scripts/verify_wheel.py`.

### Verification checklist

- Evidence detail is one action from every displayed connection.
- A copied evidence URL reopens the same relationship in Pages and Docker editions.
- Invalid IDs produce a plain-language error without rendering untrusted data.
- Primary-source URLs still pass the browser and API allowlists.
- Keyboard focus lands on the evidence heading; the back route preserves topic.
- Pages, API, wheel and container CI jobs all pass with the new page included.

### Anti-pattern guards

- Do not use a modal as the only evidence route; it cannot satisfy stable sharing.
- Do not expose raw HTML, arbitrary URLs or unvalidated query content.
- Do not describe an evidence passage as a legal conclusion.

## Phase 4 — Explain methodology, coverage and evaluation

### Outcome

Officials and contributors can judge how the dataset was made and what the demo has
and has not demonstrated.

### What to implement

1. Add a “How PolicyGraph works” page covering register → retrieve → locate text →
   propose structure → review/validate → publish graph.
2. Add an evaluation/limitations section or page generated from the committed
   evaluation result and corpus/build metadata.
3. Separate “engineering checks passed” from “user value not yet validated.”
4. Show current corpus size, synthetic/real label, included topics, known gaps and
   the date/version of the displayed dataset.
5. Link methodology and limitations from the first screen, topic workspace and
   evidence page.

### Documentation references

- Copy the pipeline sequence from `docs/architecture.md`, “Product and data flow”,
  and `docs/assets/screenshots/04-ingestion-pipeline-concept.png`.
- Copy evaluation definitions and caveats from
  `docs/product/evaluation-plan.md`, not from the concept image.
- Copy coverage language from `docs/product/initial-data-acquisition-scope.md` and
  the existing empty-state wording in `app/assets/app.js`.

### Verification checklist

- All displayed figures can be traced to committed graph/evaluation metadata.
- Synthetic metrics are labelled next to the metric, not only in a footer.
- A policy official can explain the human-review boundary after reading the page.
- Local links, Pages bundle, package contents and container smoke tests pass.
- No page claims real-corpus accuracy or a validated MVP.

### Anti-pattern guards

- Do not hand-author impressive dashboard numbers.
- Do not present the ingestion pipeline as autonomous AI publication.
- Do not reproduce third-party source text beyond the rights-reviewed evidence need.

## Phase 5 — Validate the guided demo before adding visual complexity

### Outcome

Choose the next interface investment using observed policy-official behaviour.

### What to implement

1. Run five moderated sessions using the same bounded benchmark task.
2. Record first-screen comprehension, milestone discovery time, status
   interpretation, evidence opens, task completion and qualitative friction.
3. Include participants with varied graph literacy and at least one
   assistive-technology or non-visual navigation session where recruitment permits.
4. Publish aggregate findings and a continue/iterate/stop decision without personal
   or sensitive participant data.

### Documentation references

- Use the thresholds and reporting rules in `docs/product/evaluation-plan.md`.
- Use the task stages in `docs/product/personas-and-journeys.md`.
- Use the structured feedback boundary in `docs/deployment.md`, “Initial-insight
  protocol”.

### Verification checklist

- At least 4/5 complete without facilitator correction.
- Median completion is under ten minutes.
- Every successful answer includes an inspected primary source.
- No participant reports a proposal as in force after viewing status.
- Findings identify whether cards, a timeline or a visual map best address the next
  observed friction.

### Anti-pattern guards

- Do not count targets as results before sessions occur.
- Do not optimise completion time at the expense of source inspection.
- Do not collect unnecessary personal, confidential or legally sensitive data.

## Phase 6 — Conditional enhancements after the validation checkpoint

### Visual map and timeline

Build an optional focused topic map only if research shows it improves connection
interpretation. It must have an equivalent list/table, keyboard selection, a
direction legend, visible evidence access and no causal implication. Test it against
the existing linked-card baseline rather than assuming the concept visual is better.

### Real-corpus briefing workflow

After the 60–100-document corpus passes provenance, rights, citation and status
gates, prototype pinning evidence and exporting a compact briefing trail. Every
export must preserve source title, URL, locator, historical status/date and coverage
caveat, and must distinguish user notes from PolicyGraph records.

### Semantic retrieval

Keep this as a separate experiment after the accepted corpus and held-back evidence
keys exist. Compare keyword, embedding and hybrid retrieval. Do not expose open-ended
generated answers until exact locators and the zero-unsupported-relationship gate
pass.

### Explicitly outside this frontend roadmap

- Full UK legislation mirroring or cross-domain crawling.
- Autonomous publication or general-purpose policy chat.
- Accounts, saved workspaces, collaboration and alerts.
- Regulatory prediction, compliance conclusions or personalised advice.
- The human-review console and wider domain-general platform in the epic mind-map.

## Recommended delivery cut

Deliver Phases 1–4 as the next frontend demonstration increment, then pause for
Phase 5. Treat Phase 6 as a set of evidence-triggered options, not a committed
feature queue. This keeps the demo portfolio-ready while preserving the distinction
between a convincing interface, a trustworthy corpus and a validated product.
