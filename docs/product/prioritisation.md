# Prioritisation

The planned MVP uses a lightweight RICE comparison. **Reach** is the estimated share of 10 benchmark user tasks affected (1–10). **Impact** is 0.5 minimal, 1 moderate, 2 high, or 3 massive. **Confidence** is the probability that the estimates are directionally right. **Effort** is relative person-weeks. `RICE = reach × impact × confidence ÷ effort`. Scores guide sequencing, not business-case precision; rows are sorted from highest to lowest score.

| Capability | Reach | Impact | Confidence | Effort | RICE | Decision |
|---|---:|---:|---:|---:|---:|---|
| Provenance on every claim/edge | 10 | 3.0 | 0.9 | 3 | 9.0 | Must |
| Typed events and policy status | 9 | 3.0 | 0.8 | 3 | 7.2 | Must |
| Curated source registry + reproducible build | 8 | 3.0 | 0.9 | 4 | 5.4 | Must |
| Golden-set evaluation | 7 | 3.0 | 0.9 | 4 | 4.7 | Must |
| Timeline and graph exploration | 9 | 2.0 | 0.8 | 4 | 3.6 | Must |
| Full-text semantic search | 7 | 1.5 | 0.6 | 5 | 1.3 | Later |
| Alerts and continuous monitoring | 5 | 2.0 | 0.5 | 7 | 0.7 | Later |
| Accounts and collaboration | 4 | 1.0 | 0.5 | 6 | 0.3 | Later |
| Regulatory prediction | 2 | 1.0 | 0.2 | 9 | 0.04 | Not planned |

## Principles behind the cut

1. Trust controls are product features, not cleanup work.
2. The POC proves one end-to-end evidence trail before expanding coverage.
3. Deterministic, offline evaluation takes precedence over live-model spectacle.
4. Features that imply legal or predictive authority are excluded.

“Must” means required for the functional alpha or its validation; “Later” is outside that release; “Not planned” conflicts with the product’s responsible-use boundary. See the [product brief](product-brief.md) for the agreed scope.
