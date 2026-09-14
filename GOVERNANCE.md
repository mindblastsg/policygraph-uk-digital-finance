# Governance

PolicyGraph is currently a maintainer-led proof of concept.

## Roles

- **Maintainers** set scope, merge changes, manage releases, and enforce quality and safety gates.
- **Contributors** propose issues, documentation, code, data metadata, tests, and evaluations.
- **Domain reviewers** advise on policy interpretation and evidence but do not replace legal review.

## Decision process

Routine changes are decided through pull-request review. Changes to ontology, corpus inclusion rules, evaluation gates, safety boundaries, licensing, or governance require a documented decision in the [decision log](docs/product/decision-log.md). Maintainers seek consensus; where consensus is not possible, the responsible maintainer records the decision and trade-offs publicly.

## Data and policy corrections

Evidence or status corrections receive priority. A contested record should be labelled or removed from the published sample until support is established. Correction discussions must cite the relevant primary source and locator.

## Releases

A release must meet the phase exit criteria in the [roadmap](docs/product/roadmap.md), disclose known limitations, and not describe unrun targets as results.

Release approval requires a maintainer to review CI results, golden-set changes, source/provenance changes, dependency changes, security reports, and the changelog. A contributor must not both change golden expectations and solely approve the extraction behaviour those expectations assess. The current POC has no formal steering body or funded support commitment.

## Conduct and security

Community behaviour is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). Report vulnerabilities through [SECURITY.md](SECURITY.md), not a public issue.
