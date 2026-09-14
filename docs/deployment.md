# Public alpha deployment

The public research alpha is hosted by GitHub Pages at
<https://mindblastsg.github.io/policygraph-uk-digital-finance/>. It contains the
dependency-free explorer and bounded sample graph; it does not expose a Python
server or the FastAPI documentation.

## Deployment path

The `pages` workflow runs on each push to `main` and can also be started
manually. It:

1. checks out the repository with persisted credentials disabled;
2. assembles only `app/index.html`, the browser assets and
   `data/sample/graph.json` into `_site`;
3. runs the static-bundle test;
4. uploads the Pages artifact; and
5. deploys through the protected `github-pages` environment.

The browser first attempts the same-origin API used in local development, then
falls back to `data/graph.json` when hosted statically. This preserves one UI
implementation while keeping the contributor-facing FastAPI service testable.
No secrets, database, payment method or live source credentials are required.

## Verification checklist

- `/` loads over HTTPS without authentication.
- All five topic controls appear and can be selected by keyboard.
- DSS, stablecoin and cryptoasset topics show evidence-linked sample records.
- DLT and tokenisation show their explicit sample-coverage limitation.
- Primary-source links pass the browser allowlist and open separately.
- The feedback link opens the structured GitHub issue form.
- A 390-pixel viewport has no horizontal overflow.
- The browser console has no errors after a topic selection.

## Initial-insight protocol

Ask each participant to choose a topic, identify one policy relationship, open
its evidence, and explain whether they would trust it in a briefing. Record
task completion, time to evidence, source opens, misunderstandings, and missing
coverage. Participants can use the structured public feedback form, but must
not include personal, confidential, privileged, or legally sensitive
information.

The deployment remains a research demonstration. It does not make the synthetic
sample complete, current, legally authoritative, or representative of a
production semantic-research service.

## Dynamic-service option

`render.yaml` remains available for contributors who want the FastAPI interface
and `/api/*` routes on a dynamic host. It is not used by the public alpha and a
hosting provider may require separate account or billing verification.
