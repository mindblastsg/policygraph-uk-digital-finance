# Deterministic sample data

The files in `raw/` are synthetic, minimal Content API-shaped fixtures. They are not downloaded government documents and their short evidence text is a demonstration, not a substitute for the linked authoritative source. The `POLICYGRAPH_CLAIM` markers make the demo extraction deterministic and auditable.

Rebuild `graph.json` offline from the repository root:

```console
python -m policygraph.cli build-sample
```

Network-fetched content belongs in `.cache/`, which is ignored by Git.
