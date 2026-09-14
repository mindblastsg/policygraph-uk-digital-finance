# Changelog

All notable changes are documented here following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) conventions. This project uses semantic versioning.

## [0.1.0] - 2026-09-14

### Added

- Deterministic, reviewer-authored golden evaluation with explicit release thresholds.
- Read-only same-origin API and accessible evidence explorer.
- Offline fixture-to-graph pipeline with strict provenance validation.
- Least-privilege CI covering formatting, linting, typing, tests, evaluations, links, secret patterns, JavaScript syntax, and distribution builds.
- Relocatable wheel runtime assets with an archive-content verification gate.
- Explicit historical document-status dates so stale labels are not presented as current law.

### Security

- Trusted-source URL validation, untrusted graph validation at the API boundary, no built-in live network transport, and automated credential-pattern scanning.
