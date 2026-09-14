# Deployment and standalone Docker runtime

The public research alpha is hosted by GitHub Pages at
<https://mindblastsg.github.io/policygraph-uk-digital-finance/>. It contains the
dependency-free explorer and bounded sample graph; it does not expose a Python
server or the FastAPI documentation.

## Static public-alpha path

The `pages` workflow runs on each push to `main` and can also be started
manually. It:

1. checks out the repository with persisted credentials disabled;
2. assembles only `app/index.html`, the browser assets and
   `data/sample/graph.json` into `_site`;
3. runs the static-bundle test;
4. uploads the Pages artifact; and
5. deploys through the protected `github-pages` environment.

The generated Pages bundle is explicitly marked as static and loads
`data/graph.json` directly. The FastAPI application uses the same client assets
and serves `/api/*` when run as a container. No secrets, database, payment method
or live source credentials are required.

## Standalone Docker path

Docker is the supported full-stack runtime. It packages the interface, bounded
graph and read-only FastAPI service into one provider-neutral image:

```bash
docker compose up --build
```

Open <http://127.0.0.1:8000>, inspect the API at
<http://127.0.0.1:8000/docs>, and verify health at
<http://127.0.0.1:8000/api/health>. Stop and remove the local container with:

```bash
docker compose down
```

The runtime image:

- installs the built PolicyGraph wheel rather than running from the source tree;
- runs as the unprivileged `policygraph` user;
- exposes only port 8000;
- includes an application-aware health check; and
- needs no writable application filesystem, external database or credentials.

Compose additionally enables a read-only root filesystem, a small temporary
filesystem, no Linux capabilities and no-new-privileges. TLS and public network
exposure remain the operator's responsibility; the application should sit behind
a trusted HTTPS reverse proxy if exposed beyond a local machine.

### Run without Compose

```bash
docker build --tag policygraph:local .
docker run --rm --publish 8000:8000 --read-only --tmpfs /tmp:rw,size=16m \
  --cap-drop ALL --security-opt no-new-privileges policygraph:local
```

### Supply a reviewed graph

The bundled synthetic graph is the safe default. A reviewed graph can be mounted
read-only and selected with `POLICYGRAPH_DATA_PATH`:

```bash
docker run --rm --publish 8000:8000 \
  --mount type=bind,source=/absolute/path/graph.json,target=/data/graph.json,readonly \
  --env POLICYGRAPH_DATA_PATH=/data/graph.json policygraph:local
```

The API validates the mounted payload before serving it and reports degraded
health when the file is missing or invalid.

## Verification checklist

- `/` loads over HTTPS without authentication.
- All five topic controls appear and can be selected by keyboard.
- DSS, stablecoin and cryptoasset topics show evidence-linked sample records.
- DLT and tokenisation show their explicit sample-coverage limitation.
- Primary-source links pass the browser allowlist and open separately.
- The feedback link opens the structured GitHub issue form.
- A 390-pixel viewport has no horizontal overflow.
- The browser console has no errors after a topic selection.
- `docker inspect` reports the standalone container as healthy.
- `/api/health` returns `{"status":"ok","graph_loaded":true}`.
- The container process runs with UID 10001 and without root filesystem writes.

## Initial-insight protocol

Ask each participant to choose a topic, identify one policy relationship, open
its evidence, and explain whether they would trust it in a briefing. Record
task completion, time to evidence, source opens, misunderstandings, and missing
coverage. Participants can use the structured public feedback form, but must
not include personal, confidential, privileged, or legally sensitive
information.

Both distributions remain a research demonstration. They do not make the synthetic
sample complete, current, legally authoritative, or representative of a
production semantic-research service.
