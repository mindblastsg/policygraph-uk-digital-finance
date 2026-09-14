# Public alpha deployment

PolicyGraph's interface and read-only API run as one FastAPI web service. The
repository's `render.yaml` is the deployment source of truth for the public
alpha: Python 3.12, the Frankfurt region, a free web-service instance, a
graph-aware health check, and deployment only after GitHub checks pass.

## Deploy on Render

1. In Render, choose **New > Blueprint** and connect this GitHub repository.
2. Select the `main` branch and leave the Blueprint path as `render.yaml`.
3. Review the proposed `policygraph-uk-digital-finance` web service.
4. Deploy the Blueprint and wait for `/api/health` to report
   `{"status":"ok","graph_loaded":true}`.
5. Verify `/`, `/api/topics`, `/api/graph`, and `/docs` on the issued HTTPS
   address before inviting research participants.

No secrets, database, persistent disk, or live source credentials are required
for the bounded synthetic alpha. Render's free service can sleep while idle, so
the first request after inactivity may take longer. Use a paid always-on plan
only if that delay materially affects research sessions.

## Initial-insight protocol

Ask each participant to choose a topic, identify one policy relationship, open
its evidence, and explain whether they would trust it in a briefing. Record
task completion, time to evidence, source opens, misunderstandings, and missing
coverage. The interface links to a structured public feedback form; participants
must not include personal, confidential, or legally sensitive information.

The deployment remains a research demonstration. It does not make the synthetic
sample complete, current, legally authoritative, or representative of a
production semantic-research service.
