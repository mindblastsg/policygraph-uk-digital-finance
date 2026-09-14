# Contributing to PolicyGraph

Thanks for helping make UK digital-finance policy easier to examine responsibly.

## Before contributing

Read the [product brief](docs/product/product-brief.md), [architecture](docs/architecture.md), [decision log](docs/product/decision-log.md), and [Code of Conduct](CODE_OF_CONDUCT.md). Open an issue before large changes so scope, evidence, and accessibility expectations can be agreed.

## Contribution principles

- Use authoritative primary sources where available.
- Never add material policy claims or relationships without a source ID and precise locator.
- Preserve the difference between consultation, proposal, final rule, and in-force law.
- Do not commit secrets, private data, bulk third-party documents, or files from upstream workspace reference directories.
- Keep automated tests deterministic and independent of live networks or model credentials.
- Include non-visual and keyboard-accessible paths for graph interactions.
- State uncertainty and coverage limits rather than filling gaps with inference.

## Change workflow

1. Link the change to a backlog item or issue and state the user outcome.
2. Add or update tests/evaluations and documentation with the implementation.
3. Install `.[dev]`, then run the repository quality checks below.
4. Submit a focused pull request using the template, including evidence and risk changes.

By contributing, you agree that your contribution is licensed under the repository’s [MIT License](LICENSE). Third-party content remains subject to its original terms.

## Quality checks

Run these from the repository root before opening a pull request:

```bash
python -m ruff format .
python -m ruff check .
python -m mypy
python -m pytest tests evals
python -m evals.evaluate
python scripts/check_links.py
python scripts/check_secrets.py
node --check app/assets/app.js
python -m build
python scripts/verify_wheel.py
```

The test command names both suites explicitly: missing API tests cannot be treated as an optional discovery result. Tests and evaluations are offline and require no credentials.
