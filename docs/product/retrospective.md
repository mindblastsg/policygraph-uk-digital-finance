# Delivery retrospective

## What was established

- A coherent product contract centred on fast, evidence-backed policy understanding.
- Shared target users, intended MVP scope, non-goals, hypotheses, and validation gates.
- A source-to-interface architecture with provenance and status as hard constraints.
- Open-source governance and a repository boundary that excludes protected workspace sources.

## What went well

Starting with user risk clarified that citation correctness, unsupported relationships, and policy status are release gates—not optional model metrics. The documentation makes planned work distinguishable from working software and keeps the product narrative testable.

## What remains uncertain

- Whether the selected corpus supports representative benchmark questions.
- Whether users prefer linked-card exploration to a future visual graph or timeline.
- The effort required for reliable locators across heterogeneous public documents.
- Whether the proposed thresholds are feasible without excessive human review.

## What we would change with more time

Interview analysts before fixing the ontology; validate accessible graph patterns with assistive-technology users; and conduct a source-rights review before expanding fixtures.

## Phase 3 update

The functional alpha now turns the deterministic graph into an inspectable product experience. Topic filters lead to typed relationships, quoted evidence, explicit status, and primary-source links; the read-only API also exposes entity, event, relationship, source, and full-graph views. Keeping API and static UI in one service reduced deployment surface and avoided CORS configuration. Structural accessibility checks cover keyboard-native controls and empty/error copy, but assistive-technology testing and the benchmark user task remain unvalidated.

## Phase 4 update

The release-candidate engineering layer turns trust claims into executable gates. A reviewer-authored golden set blocks status errors and unsupported relationships instead of averaging them into a headline score. CI has read-only repository permission, persists no checkout credentials, installs declared dependencies, names both API and evaluation suites explicitly, scans common credential patterns, and inspects wheel contents. Runtime app and graph assets now work from a built installation as well as a checkout.

This phase also exposed and corrected an API-boundary validation mismatch: relationships intentionally derive status from their supporting claim and do not carry a duplicate status field. The validator now checks relationship provenance and claim alignment without requiring that nonexistent field.

## Version 0.2.0: contribution and completion review

The ingestion boundary is now reusable: a versioned adapter protocol, plugin registration, public JSON Schemas, a fixture-backed starter package and contributor guides make the next integration concrete. Discovery reads metadata; explicit loading imports a class; the consuming application controls construction and configuration. This keeps ownership and failure handling visible to contributors.

The completion review found that an archive-only package check could miss a broken installed experience. Distribution verification now installs into a fresh environment and loads the API, graph, schemas and adapter from that installation. The starter's fixture is packaged too. A committed-graph regression checks the exact output of a rebuild, with consistent line endings across platforms.

The browser review also exposed missing topic choices and cramped section links. All five scoped topics now appear. DLT and tokenisation have source coverage without extracted claims; the UI explains that distinction instead of silently hiding them. Event labels use readable words and counts use singular/plural forms.

These are engineering and contribution outcomes. No analyst interviews, moderated sessions or real-corpus extraction results are claimed.

## Next product experiment

Run the planned moderated sessions and evaluate a held-back real-document corpus. The bounded synthetic golden result is an engineering regression result, not evidence that the user or production-quality hypotheses are met.
