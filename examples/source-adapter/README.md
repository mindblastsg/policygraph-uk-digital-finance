# PolicyGraph source adapter starter

This minimal Python 3.12 package demonstrates the PolicyGraph `0.2.x` adapter contract. Copy it, rename the distribution, module, class, and entry point, then install it beside PolicyGraph with `python -m pip install -e ".[test]"`.

Install PolicyGraph from the parent repository into the same environment first; the SDK is distributed through this repository, not PyPI. The `example_adapter/fixtures/sample.html` file is synthetic and included in both source and wheel distributions, so the example also works after a regular package installation.

The entry point in `pyproject.toml` makes metadata visible through `policygraph adapters list`; discovery does not import adapter code. Run `python -m pytest` from this directory to exercise the deterministic offline fixture contract. The helper checks interface shape and output consistency, not network isolation.

Before publishing, document source ownership and fixture redistribution rights. Production adapters must validate redirects and content types, impose timeouts and response-size limits, avoid import-time work, and never place credentials in registries or logs. See the [adapter guide](../../docs/contributors/building-an-adapter.md) for compatibility, validation, and troubleshooting guidance.
