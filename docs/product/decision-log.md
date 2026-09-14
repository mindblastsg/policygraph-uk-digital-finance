# Decision log

Decisions are lightweight architecture/product decision records. “Accepted” means chosen for the POC, not permanently fixed.

## ADR-001 — Evidence-first graph

- **Status:** Accepted
- **Decision:** All material policy claims and relationships must carry a source ID and evidence locator; invalid records fail validation.
- **Why:** The core user risk is an attractive but unverifiable synthesis.
- **Trade-off:** Smaller coverage and more curation work.

## ADR-002 — Curated primary-source corpus

- **Status:** Accepted
- **Decision:** Start with a bounded registry of authoritative UK public sources; do not crawl broadly.
- **Why:** Coverage can be explained and evaluated, while licensing and relevance remain reviewable.
- **Trade-off:** The POC cannot claim completeness.

## ADR-003 — JSON graph before a graph database

- **Status:** Accepted
- **Decision:** Build a deterministic, typed JSON dataset for the POC rather than operating Neo4j or another graph database.
- **Why:** The riskiest assumptions concern usefulness and trust, not database scalability.
- **Trade-off:** Complex traversal and scale testing are deferred.

## ADR-004 — Replaceable AI extraction interface

- **Status:** Accepted
- **Decision:** Separate extraction from validation and provide a deterministic demo implementation. Live LLM access is optional and absent from CI.
- **Why:** Reproducibility and evaluation must not depend on secrets or model availability.
- **Trade-off:** The sample may underrepresent production extraction complexity.

## ADR-005 — Same-origin API and UI

- **Status:** Accepted
- **Decision:** Serve the full interface and API from one FastAPI application, while building a static-data edition of the same client for public research sessions.
- **Why:** The container avoids unnecessary CORS and multi-service complexity; the static edition remains usable without operating a public API.
- **Trade-off:** The static edition cannot expose API routes or accept runtime data changes.

## ADR-006 — Status is a domain field, not prose

- **Status:** Accepted
- **Decision:** Model document states with a required `status_as_of` date; never present historical labels as current-law determinations.
- **Why:** Status ambiguity can materially mislead users.
- **Trade-off:** Some documents remain “uncertain” until reviewed.

## ADR-007 — Repository-safe source boundary

- **Status:** Accepted
- **Decision:** Do not copy upstream workspace reference directories. Store only curated metadata, rights-reviewed fixtures, and derived demo records intended for publication.
- **Why:** Prevent accidental publication of workspace-only or third-party material.
- **Trade-off:** Reproduction may fetch original sources separately.

## ADR-008 — Provider-neutral container runtime

- **Status:** Accepted
- **Decision:** Distribute the full application as a single non-root OCI image with a hardened local Compose configuration and no provider-specific deployment manifest.
- **Why:** Contributors can reproduce and operate the same artefact on a laptop, server or container platform without adopting a particular hosting vendor.
- **Trade-off:** Operators own TLS termination, public routing, updates and capacity management.
