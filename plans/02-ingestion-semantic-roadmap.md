# Data ingestion and semantic mapping roadmap

## Objective

Build a bounded, reproducible and reviewable UK digital-finance corpus, then test
whether semantic mapping and retrieval help policy officials find evidence without
weakening provenance, historical-status accuracy or source rights.

This roadmap deliberately separates three claims that are often blurred:

1. **Ingestion** retrieves and normalises a known source reproducibly.
2. **Semantic mapping** proposes reviewed entities, events, claims and typed
   connections with exact evidence.
3. **Semantic retrieval and synthesis** find or explain relevant evidence for a
   question.

Passing one layer does not validate the next. The first release remains capped at
250 discovered candidates and 60–100 accepted documents across the five launch
topics.

## Delivery map

| Layer | Product question | Delivery point |
| --- | --- | --- |
| Source governance | Which authoritative records may enter the corpus, and why? | Phase 1 |
| Controlled acquisition | Can an accepted record be fetched safely and repeated? | Phase 2 |
| Structural normalisation | Can a reviewer recover the exact provision or passage? | Phase 3 |
| Semantic mapping | Can proposed meaning be reviewed without losing source context? | Phase 4 |
| Corpus release | Does the first real corpus meet coverage, rights and trust gates? | Phase 5 |
| Lexical retrieval | What can a transparent keyword baseline already recover? | Phase 6 |
| Embedding and hybrid retrieval | Does semantic retrieval add measurable recall? | Phase 7 |
| Evidence-linked synthesis | Can an answer remain decomposable into supported claims? | Phase 8 |
| Verification and expansion decision | Should the project expand, iterate or stop? | Phase 9 |

## Phase 0 — Documentation discovery and current contract

### Current implementation

- `SourceAdapter` exposes `fetch(source) -> FetchedContent` and
  `extract(source, content) -> Document`; plugin metadata is discovered without
  import side effects (`src/policygraph/adapters.py`).
- `Fetcher`, `DocumentExtractor` and `ClaimExtractor` are Python protocols
  (`src/policygraph/fetch.py`; `src/policygraph/extract.py`).
- `CachedFetcher` is cache-first and permits delegated fetching only through
  explicit dependency injection. The shipped `UnavailableNetworkFetcher` proves
  that no live transport is silently enabled.
- `GovUKContentExtractor` reads the documented `title`, `public_updated_at`,
  `details.body` and `details.parts` fields. `GenericHTMLExtractor` is a basic text
  baseline, not a production policy-document parser.
- The current graph contracts cover sources, flat documents, line locators, claims,
  organisations/policies/topics, events and directed relationships
  (`src/policygraph/models.py`; `src/policygraph/schemas/`).
- `build_graph` preserves evidence but currently assumes the claim subject is an
  organisation, the object is a policy and no event date has been established
  (`src/policygraph/graph.py`).
- `validate_graph` rejects duplicate identifiers, orphaned provenance, mismatched
  evidence, fabricated line locators and status mismatches
  (`src/policygraph/validate.py`).
- The four-record fixture and golden set prove deterministic plumbing only. There
  is no live fetcher, structural legislation parser, review queue, embedding model,
  vector index, retrieval engine or generated-answer path.

### Verified external interfaces

- GOV.UK Content API: `GET https://www.gov.uk/api/content/{path}` returns published
  GOV.UK content and metadata as JSON, requires no authentication and documents a
  maximum of ten requests per second. PolicyGraph retains its stricter two-request-
  per-second budget. See <https://content-api.publishing.service.gov.uk/> and
  <https://content-api.publishing.service.gov.uk/reference.html>.
- legislation.gov.uk provides stable legislation URIs and structured data formats;
  use the official developer guidance at
  <https://www.legislation.gov.uk/developer> and treat enacted/revised
  representations as distinct versioned acquisitions.
- The FCA Handbook API now provides structured machine-readable Handbook content.
  It requires a free registered account, is subject to its terms and rate limits,
  and does not provide historic Handbook versions. See
  <https://handbook.fca.org.uk/latest-news/news-details/8e0653c7-1376-44b8-8bf1-9b41130dc50c>.
- UK Parliament publishes versioned public APIs, including Bills and their stages,
  publications and documents. See <https://developer.parliament.uk/> and
  <https://bills-api.parliament.uk/>.
- No general Bank of England/PRA publication API is assumed. Those records remain a
  reviewed seed-list integration until an authoritative supported interface is
  documented.

### Allowed implementation patterns

- Extend the current typed protocols and public adapter entry-point group rather
  than adding publisher logic to graph construction.
- Use deterministic, rights-cleared fixtures for every network adapter and keep
  live network access outside pull-request CI.
- Store immutable response bytes in a content-addressed cache outside Git, with a
  versioned manifest and fetch ledger inside the reproducibility boundary.
- Use conditional HTTP requests, strict HTTPS host allowlists, bounded redirects,
  timeouts, response-size/content-type limits, conservative rate budgets and
  explicit retry/backoff policies.
- Preserve source-native identifiers and hierarchy before generating search chunks
  or graph records.
- Add replaceable `Chunker`, `SemanticMapper`, `EmbeddingProvider` and `Retriever`
  protocols only when their phase begins; each requires deterministic fixture
  implementations and contract tests.
- Keep the bounded corpus and indices file-backed inside the standalone Docker
  project until measurement demonstrates a database service is necessary.

### Anti-pattern guards

- Do not turn search terms into automatic inclusion decisions.
- Do not run live discovery, fetching, model calls or authenticated APIs in CI.
- Do not commit credentials, unrestricted source dumps, copyrighted attachments or
  the local acquisition cache.
- Do not flatten legislation or policy documents before preserving provision,
  section, paragraph, heading and attachment boundaries.
- Do not use a vector match as evidence, a similarity score as confidence, or a
  generated summary as a graph fact.
- Do not infer commencement, legal effect, current-law status, causation or event
  dates from proximity or model output.
- Do not choose a managed vector database before the bounded benchmark proves a
  local index insufficient.

### Phase 0 verification

- Re-read the official interface documentation immediately before implementing each
  publisher adapter; beta and authenticated APIs may change.
- Confirm all new contracts preserve the installed-wheel, Docker and offline-CI
  boundaries.
- Record a decision before changing a public schema or adapter protocol.

## Phase 1 — Source governance and reviewed discovery

### Outcome

Produce a defensible candidate set without treating keyword hits as publishable
policy evidence.

### What to implement

1. Add versioned candidate, rights-decision and acquisition-manifest schemas.
2. Model candidate state explicitly: discovered, accepted, rejected, deferred and
   withdrawn, each with a stable reason code and reviewer/timestamp.
3. Record canonical/source-native ID, URL, publisher, document type, topic match,
   publication/made date, status evidence, rights basis, acquisition route and
   expected content format.
4. Build metadata-only discovery commands for reviewed GOV.UK paths,
   legislation.gov.uk searches/feeds and Parliament Bills queries.
5. Treat FCA Handbook access as a separately configured authenticated adapter;
   retain reviewed web seed lists for FCA consultations and policy statements that
   are not Handbook API content.
6. Keep Bank of England/PRA discovery seed-led until a supported publication API is
   verified.
7. Enforce the 250-candidate ceiling and publish a candidate coverage report by
   source, topic, year, format and decision state.

### Documentation references

- Copy the inclusion terms, source tiers and exclusions from
  `docs/product/initial-data-acquisition-scope.md`.
- Copy source validation and unknown-field rejection from
  `src/policygraph/schemas/source-registry.schema.json` and
  `src/policygraph/registry.py`.
- Copy metadata-only plugin discovery from `discover_adapters()` in
  `src/policygraph/adapters.py`.
- Copy documented external endpoint shapes only from the official sources in Phase
  0; do not infer query parameters from third-party examples.

### Verification checklist

- Candidate output is deterministic for a frozen discovery fixture.
- No discovery result becomes accepted without a review decision.
- Every rejection/deferment has a stable reason; there are no silent drops.
- Candidate count is at most 250 and all five topics are represented before
  sampling decisions.
- Registry, manifest and decisions validate against versioned schemas.
- Credentials and response bodies are absent from candidate metadata and logs.

### Anti-pattern guards

- Do not build a general web crawler or mirror the statute book.
- Do not use publisher name alone as a rights decision.
- Do not accept a source because it ranks highly for a keyword.

## Phase 2 — Guarded, repeatable acquisition

### Outcome

Fetch accepted records through publisher-specific adapters while producing a
complete audit trail and repeatable cache result.

### What to implement

1. Extend `FetchedContent` with retrieval timestamp, status code, response size,
   content SHA-256, ETag/Last-Modified where provided and redirect chain.
2. Add an audited HTTPS fetcher that accepts only the adapter's declared hosts and
   explicit content types, sizes, redirect count, timeout and rate budget.
3. Upgrade `CachedFetcher` to content-addressed immutable bodies plus a fetch ledger;
   never overwrite prior bytes when content changes.
4. Add conditional requests and explicit outcomes: fetched, not modified,
   redirected, withdrawn/gone, rejected content type, oversized, retry exhausted and
   operator review required.
5. Implement the GOV.UK Content API adapter first, then legislation.gov.uk. Add
   Parliament only for bills/publications linked to accepted policy chronologies.
6. Keep authenticated FCA configuration outside registries and logs; do not add it
   until account terms and secret handling are reviewed.
7. Run live acquisition only through an explicit operator command/profile, never at
   import, application startup or pull-request test time.

### Documentation references

- Copy the cache-first/delegate pattern and safe-ID check from
  `src/policygraph/fetch.py`.
- Copy adapter host declarations and explicit loading from
  `src/policygraph/adapters.py` and
  `docs/contributors/building-an-adapter.md`.
- Copy GOV.UK canonical redirect handling from the official Content API getting-
  started guide at
  <https://content-api.publishing.service.gov.uk/getting-started.html>.
- Copy the fetch ledger requirements from
  `docs/product/initial-data-acquisition-scope.md`, “Deliverables”.

### Verification checklist

- Offline contract fixtures cover success, redirect, 304, 404/410, timeout, invalid
  TLS/host, wrong type, excessive size and changed content.
- A cache hit performs no network call and reproduces identical body/hash metadata.
- At least 95% of unchanged reviewed URLs refetch or resolve from cache.
- GOV.UK stays at or below two requests per second; all other sources stay at or
  below one unless a reviewed source policy is stricter.
- Secrets and authorisation headers never enter logs, manifests or exceptions.
- Network integration tests are manual/scheduled and clearly separate from offline
  CI.

### Anti-pattern guards

- Do not create a generic fetch-any-URL command.
- Do not follow redirects outside approved hosts or retry indefinitely.
- Do not mutate cached content in place or treat the latest response as history.

## Phase 3 — Structural parsing and stable evidence locators

### Outcome

Normalise heterogeneous material while retaining enough source structure for a
reviewer to recover the exact passage and version.

### What to implement

1. Introduce a versioned normalised-document schema with source-native version ID,
   document type, retrieved representation, hierarchy and ordered text blocks.
2. Define stable block locators for legislation parts/chapters/sections/regulations,
   GOV.UK parts/headings/paragraphs and attachment/page coordinates when explicitly
   supported.
3. Preserve raw bytes and the source-native representation outside Git; generate
   normalised JSON and rights-cleared fixture slices for the repository.
4. Add GOV.UK JSON and legislation structured-data parsers. Use generic HTML only as
   a quarantined fallback with lower locator quality and mandatory review.
5. Chunk on structural boundaries with controlled overlap; every chunk inherits
   source ID, version, block IDs, ordering and character offsets.
6. Separate publication/made dates, asserted policy-event dates, effective dates and
   `status_as_of`; do not collapse them into one timeline field.
7. Report parsing coverage, skipped elements, attachment decisions and locator
   round-trip failures.

### Documentation references

- Copy the GOV.UK body/parts extraction branches from
  `GovUKContentExtractor` in `src/policygraph/extract.py`.
- Copy strict decoding and explicit content-type checks from the current extractors.
- Copy line-locator round-trip validation from
  `validate_graph()` in `src/policygraph/validate.py`, then extend it to block/span
  locators through a versioned schema rather than weakening the current rule.
- Follow official legislation format/URI guidance from
  <https://www.legislation.gov.uk/developer>.

### Verification checklist

- Every published chunk maps back to one immutable source hash and exact block/span.
- Locator round trips recover the supporting text byte-for-byte after normalisation.
- Parser fixtures cover nested provisions, multipage GOV.UK content, missing bodies,
  redirections and unsupported attachments.
- No source element is silently dropped; skipped material has a reason code.
- Event dates remain null unless a cited passage explicitly supports the date.

### Anti-pattern guards

- Do not make line numbers the permanent locator for structured legislation.
- Do not strip headings, numbering or amendment/version context before chunking.
- Do not OCR or parse unsupported attachments silently in the first increment.

## Phase 4 — Reviewed semantic mapping and ontology v2

### Outcome

Convert normalised passages into a controlled policy map whose meaning and evidence
can be reviewed independently of any model.

### What to implement

1. Publish ontology v2 before extraction: entity types, event types, relationship
   vocabulary, direction, temporal fields, status semantics and forbidden
   inferences.
2. Add a canonical-entity registry with preferred label, aliases, type, source-native
   identifiers, merge/split history and reviewer decision.
3. Replace subject-is-organisation/object-is-policy assumptions with schema-checked
   entity typing and allowed relationship-domain/range rules.
4. Represent extracted records as proposals carrying extractor/model version,
   prompt/rule version, input chunk IDs, evidence spans and review state.
5. Implement a deterministic baseline mapper first; an optional AI mapper may
   propose records but cannot publish them.
6. Add a file-backed review queue and decision log for accept, edit, reject, merge,
   split and insufficient-evidence outcomes.
7. Project only accepted claims/events/relationships into the public graph and retain
   the evidence-span identity through projection.
8. Create a held-back reviewer-authored mapping set across all five topics and at
   least three publishers.

### Documentation references

- Copy the immutable domain record style from `src/policygraph/models.py`.
- Copy `canonical_name`/`stable_id` as a deterministic baseline from
  `src/policygraph/canonicalise.py`; do not treat that simple normalisation as entity
  resolution.
- Copy claim-to-relationship evidence alignment from `src/policygraph/graph.py` and
  the failure conditions in `src/policygraph/validate.py`.
- Copy mandatory metrics and blockers from
  `docs/product/evaluation-plan.md` and `evals/golden.json`.

### Verification checklist

- 100% of accepted semantic records have a source, immutable version, chunk/block
  locator and exact evidence span.
- Citation agreement is at least 90%; entity and relationship precision are at least
  90%; expected relationship recall is 100% on the held-back set.
- Unsupported material relationships and status-critical errors are zero.
- Alias decisions are reproducible and merge/split history never changes an old
  identifier silently.
- A model version change produces a comparable proposal set rather than overwriting
  prior review decisions.

### Anti-pattern guards

- Do not auto-publish because model confidence exceeds a threshold.
- Do not infer causal/influenced-by connections from co-occurrence.
- Do not let a canonical label overwrite the source's original wording.
- Do not combine historical document status with current legal effect.

## Phase 5 — Release the first real corpus

### Outcome

Publish a useful but explicitly bounded real-data evidence graph and its coverage
report.

### What to implement

1. Run the reviewed discovery, acquisition, parsing and semantic-mapping workflow.
2. Accept 60–100 documents spanning all five topics and at least three publishers.
3. Publish registry/manifest metadata, hashes, rights decisions, derived normalised
   records where permitted, accepted semantic records and graph outputs.
4. Keep restricted raw bodies in the content-addressed cache; publish only
   rights-approved fixture excerpts.
5. Generate coverage, failure, duplicate and review-effort reports.
6. Feed real corpus metadata and evidence into the frontend methodology, limitations
   and topic surfaces without implying completeness.

### Documentation references

- Use every release gate in
  `docs/product/initial-data-acquisition-scope.md`, “Release gates”.
- Use the public/restricted source boundary in `SECURITY.md`, `CONTRIBUTING.md` and
  ADR-007 in `docs/product/decision-log.md`.
- Reuse deterministic graph serialization from `src/policygraph/pipeline.py`.

### Verification checklist

- 60–100 accepted documents, three publishers and all five topics.
- 100% provenance/rights/locator completeness, at least 95% retrieval repeatability,
  under 2% duplicate rate, at least 90% citation agreement, zero unsupported
  material relationships and zero status-critical errors.
- Every failure and rejection is counted; there are no silent drops.
- Public repository contents pass rights, secret, link and reproducibility reviews.
- Synthetic and real records are distinguishable in data and interface.

### Anti-pattern guards

- Do not publish the full cache as an open-data dump.
- Do not expand past 100 documents to conceal weak topic coverage.
- Do not call corpus gates proof of user value.

## Phase 6 — Establish the transparent lexical baseline

### Outcome

Measure how well provision-level keyword retrieval answers the policy-official
benchmark before adding semantic complexity.

### What to implement

1. Author 25 held-back questions across the five topics, each with reviewer-approved
   relevant chunk IDs and source/evidence keys.
2. Build a local keyword/BM25-style index over the same provision-level chunks that
   later semantic approaches will use.
3. Support explicit topic, publisher, document type, status and date filters.
4. Return ranked evidence passages with source title, locator, historical status and
   corpus version; do not generate an answer.
5. Record recall at 10, reciprocal-rank/first-relevant position, citation agreement,
   zero-result rate and latency by question category.
6. Version questions, judgments, index configuration and corpus hash.

### Documentation references

- Copy benchmark and held-back-set rules from
  `docs/product/evaluation-plan.md`, “Benchmark design”.
- Copy the 25-question comparison contract from
  `docs/product/initial-data-acquisition-scope.md`, “Semantic-research handoff”.
- Reuse the golden-set structure and blocker reporting pattern from
  `evals/golden.json` and `evals/evaluate.py`.

### Verification checklist

- The same frozen questions and relevant-chunk judgments are used for every method.
- Index construction is deterministic for the same corpus snapshot.
- Results always include exact source locators and never invent snippets.
- Baseline metrics are reported by topic and question type, not only as an average.
- Latency is measured inside the standalone Docker runtime.

### Anti-pattern guards

- Do not tune on the held-back questions and report them as independent results.
- Do not call lexical matches semantic understanding.
- Do not optimise recall by returning the entire corpus.

## Phase 7 — Evaluate embeddings and hybrid retrieval

### Outcome

Determine whether meaning-based retrieval adds material value over the lexical
baseline for this bounded policy corpus.

### What to implement

1. Introduce an `EmbeddingProvider` protocol returning vectors plus provider/model,
   revision, dimension and normalisation metadata.
2. Ship a deterministic fixture provider for offline contract tests. Keep real model
   calls in an explicit, separately configured indexing command.
3. Store an immutable local embedding/index artefact keyed by corpus hash, chunking
   version and model revision; do not require a hosted vector service.
4. Implement exact similarity search for the bounded corpus, then a documented
   hybrid fusion method over lexical and embedding ranks.
5. Evaluate lexical, embedding and hybrid retrieval on the identical 25-question
   set with identical filters and top-k.
6. Analyse gains and failures by terminology mismatch, acronym, cross-document
   connection, status and date sensitivity.
7. Select the simplest method that materially improves recall without degrading
   citation agreement, latency, repeatability or operator cost.

### Documentation references

- Copy the replaceable protocol/fixture pattern from `Fetcher`, `ClaimExtractor` and
  `SourceAdapter` in `src/policygraph/`.
- Copy version/hash metadata patterns from `Graph` and `build_sample()` in
  `src/policygraph/models.py` and `src/policygraph/pipeline.py`.
- Use the comparison metrics defined in the initial acquisition scope and evaluation
  plan; document any new metric before running the benchmark.

### Verification checklist

- No model secret or network call is required by CI.
- Every vector maps to one immutable chunk and corpus/model version.
- Re-indexing the same snapshot with the same model/configuration produces the same
  ordered chunk identities within documented numerical tolerance.
- All three methods publish recall@10, citation agreement, latency and failure cases.
- The selected method beats the lexical baseline on a predeclared threshold; if it
  does not, retain lexical retrieval.

### Anti-pattern guards

- Do not treat cosine similarity as factual confidence.
- Do not compare methods using different chunks, filters, questions or top-k.
- Do not introduce a hosted vector database merely to make the architecture look
  production-scale.

## Phase 8 — Evidence-linked synthesis experiment

### Outcome

Test whether constrained synthesis reduces briefing effort while every answer
statement remains reviewable and unsupported questions produce an abstention.

### What to implement

1. Define an answer schema made of atomic statements, each linked to one or more
   retrieved chunk IDs and exact evidence spans.
2. Require the generator to separate source-supported statements, user framing and
   explicit uncertainty; status and dates must be copied from validated records.
3. Add an abstention/no-answer outcome when retrieved evidence is insufficient or
   conflicting.
4. Evaluate retrieval and synthesis separately: retrieval recall, statement-level
   citation agreement, unsupported synthesis, status-critical errors and latency.
5. Keep synthesis behind an experimental operator flag until all blockers pass and
   policy-official sessions show a benefit over evidence-only retrieval.
6. Preserve the evidence-only route as the default and allow users to inspect every
   cited passage before using a summary.

### Documentation references

- Copy the no-public-answer gate from
  `docs/product/initial-data-acquisition-scope.md`, “Semantic-research handoff”.
- Copy zero-tolerance blockers from `docs/product/evaluation-plan.md`.
- Copy responsible-use and non-goals from `docs/product/product-brief.md`.

### Verification checklist

- 100% of material answer statements have inspectable citations.
- Unsupported synthesis and status-critical errors are zero on the held-back set.
- Citation agreement remains at least 90%, with disagreements published by category.
- Adversarial questions outside the corpus produce an explicit no-answer result.
- Five moderated comparisons test whether synthesis improves the briefing task
  without reducing primary-source inspection.

### Anti-pattern guards

- Do not use one citation at paragraph end to support multiple untraceable claims.
- Do not answer beyond the retrieved corpus or hide contradictory evidence.
- Do not expose open-ended chat, compliance advice or regulatory prediction.

## Phase 9 — Final verification and expansion decision

### What to verify

1. Re-read every official publisher/API document used by implemented adapters and
   confirm endpoint, authentication, rate and reuse assumptions remain current.
2. Validate all public schemas, manifests, acquisition ledgers, review decisions,
   normalised documents, indices and graph artefacts.
3. Run formatting, linting, typing, unit/integration fixtures, graph validation,
   held-back mapping evaluation, retrieval comparisons, link/secret scans, package
   verification and hardened Docker smoke tests.
4. Rebuild the corpus and every derived artefact from immutable cache content and
   compare hashes.
5. Search for forbidden paths: unreviewed publication, missing locators, unversioned
   vectors, secrets, silent drops, unsupported current-law language and uncited
   generated statements.
6. Publish a decision memo: continue, iterate, narrow or stop, with observed quality,
   user value, rights burden, refresh effort, latency and operating cost.

### Expansion rule

A wider legislation mirror, continuous update service, cross-domain semantic index,
managed database or multi-user workflow is a separate epic. Start it only when the
bounded corpus and retrieval/synthesis experiments identify a specific user-relevant
gap that cannot be solved within this standalone architecture.

## Recommended delivery cut

Deliver Phases 1–5 as the next data increment. That creates a real, reviewable
corpus and unlocks the frontend validation checkpoint. Run Phases 6–7 as a separate
semantic-research increment. Treat Phase 8 as conditional, and do not make it part
of the public experience until its evidence and user-value gates pass.
