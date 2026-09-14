# Building a source adapter

Adapters implement `policygraph.adapters.SourceAdapter`: a stable `name`, a non-empty tuple of `supported_hosts`, and `fetch(source)` / `extract(source, content)` methods. Use PolicyGraph `0.2.x` for this contract. While PolicyGraph is pre-1.0, breaking contract changes may increment the minor version; after 1.0 they will increment the major version.

## Setup and registration

Copy `examples/source-adapter`, create a Python 3.12 virtual environment, and install both repositories in editable mode. Register the class under the `policygraph.source_adapters` entry-point group in your `pyproject.toml`. The entry-point name and class `name` should match.

Run `policygraph adapters list` to inspect installed metadata. Discovery does not import plugins. Loading is explicit through `load_adapter(name)` and imports and validates the adapter class without instantiating it. The application remains responsible for constructing that class with any required configuration or credentials.

## Development and tests

Keep an offline, licensed fixture and call `assert_adapter_contract(adapter, source)`. If your deterministic test transport uses another non-network scheme, pass it explicitly with `allowed_final_url_schemes=("fixture", "your-test-scheme")`. This helper checks contract shape and deterministic fixture behaviour; it is not a network sandbox.

Validate registries with `policygraph validate-registry path.json` and generated graphs with `policygraph validate-graph path.json`. JSON Schema checks structure and formats; graph validation additionally checks unique IDs and source, document, claim, entity, and evidence references.

## Security and source rights

Imports and discovery must have no side effects. Never fetch during import, discovery, or contract tests. Validate redirects and content types, set timeouts and byte limits, treat remote content as untrusted, and keep credentials out of source registries and logs. Document fixture provenance and redistribution rights.

## Troubleshooting

- `adapter ... is not installed`: install the adapter into the active environment and verify its entry-point group.
- `adapter ... is ambiguous`: remove or rename duplicate entry points.
- `entry point must resolve to a class`: export the adapter class, not an instance or factory.
- Validation exit code `1`: the JSON is well formed but violates the schema or graph provenance rules.
- Validation exit code `2`: the file cannot be read or parsed.
