# Risk register

Likelihood and impact use Low/Medium/High planning estimates. Owners are roles until a team is assigned.

| ID | Risk | Likelihood | Impact | Mitigation/control | Trigger/indicator | Owner |
|---|---|---|---|---|---|---|
| R1 | AI invents or distorts a claim | M | H | Golden set; provenance-required validation; human review | Unsupported or contradicted output | Data/ML lead |
| R2 | Proposal is presented as in-force policy | M | H | Typed status; status-critical eval; visible labels | Status mismatch | Policy lead |
| R3 | Corpus gaps imply false completeness | H | H | Bounded registry; coverage notice; empty states | User assumes exhaustive coverage | Product lead |
| R4 | Source changes or disappears | M | M | Retrieval metadata, timestamps, stable identifiers, cache policy | Broken URL/content hash change | Data lead |
| R5 | Third-party rights are mishandled | L | H | Prefer metadata; include limited fixtures only after documented rights review; preserve source rights | Takedown or licence concern | Maintainer |
| R6 | Political/institutional framing bias | M | H | Transparent inclusion criteria; diverse review; publisher breakdown | Skewed source mix | Policy lead |
| R7 | Graph visualisation overstates certainty | M | H | Evidence panel, uncertainty fields, non-visual list | Users infer causation from association | Design lead |
| R8 | Users treat POC as legal advice | M | H | Persistent disclaimer; no personalised recommendations | Compliance decision attributed to tool | Product lead |
| R9 | Model/provider cost or availability blocks use | M | M | Replaceable interface; deterministic fallback; offline CI | Failed live extraction/cost spike | Engineering lead |
| R10 | Sensitive values enter repository | L | H | No secrets in CI; pre-release scan; least privilege | Secret-pattern detection | Maintainer |
| R11 | Accessibility blocks graph use | M | H | Keyboard support; list alternative; user testing | Task failure with assistive workflow | Design lead |
| R12 | Metric targets encourage shallow coverage | M | M | Pair speed with provenance/status gates | Faster tasks but trust errors | Product lead |

Risks are reviewed at each phase exit and after any evaluation failure. A High-impact risk cannot be accepted implicitly; the decision and owner must be recorded.
