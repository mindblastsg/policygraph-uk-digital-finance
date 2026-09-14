# Security policy

## Supported versions

PolicyGraph is a proof of concept. The latest `main` branch receives best-effort security fixes but no production support or response-time guarantee.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability or exposed secret. Use **Report a vulnerability** on the repository's [Security advisories page](https://github.com/mindblastsg/policygraph-uk-digital-finance/security/advisories/new). If that control is unavailable, open a public issue containing no sensitive details and ask a maintainer to enable a private channel.

Include the affected component/version, impact, reproduction steps, and any suggested mitigation. No response-time guarantee applies during the POC stage.

## Scope notes

The POC is read-only, uses public policy material, and does not require secrets in CI. Remote documents remain untrusted input. Please report injection paths, unsafe parsing, dependency vulnerabilities, data exposure, provenance bypasses, and routes that enable unintended writes.

The repository runs a deterministic credential-pattern scan in CI. It is a backstop, not a substitute for platform secret scanning or contributor review.

The supported standalone configuration runs the application as a non-root user
with a read-only filesystem, no added Linux capabilities and privilege escalation
disabled. Operators exposing it publicly remain responsible for HTTPS termination,
network access controls, image updates, dependency monitoring and log handling.
