# Ingestion pipeline

The executable implementation lives in `src/policygraph`. Its boundary is deliberate:

```text
curated registry -> Fetcher -> DocumentExtractor -> ClaimExtractor
                 -> canonicalise -> build_graph -> validate_graph -> graph.json
```

- `Fetcher`, `DocumentExtractor`, and `ClaimExtractor` are typed interfaces.
- The POC ships no live network transport. `UnavailableNetworkFetcher` fails explicitly; a future adapter requires a separate security review.
- `CachedFetcher` reads validated entries and has a disabled-by-default dependency-injection seam; `.cache/` is excluded from version control.
- The committed demo never contacts a network. Its fixtures mimic the documented GOV.UK `title`, `public_updated_at`, and `details.body` fields.
- Fixture-backed documents use `fixture://` retrieval URIs and `synthetic: true`; authoritative registry URLs remain citations, never alleged retrieval locations.
- `DeterministicDemoClaimExtractor` reads visible fixture markers. It demonstrates the extraction boundary; it is not an AI model or an accuracy claim.
- Claims and projected relationships cannot pass validation without a source and evidence locator.
- Publication dates describe documents, not policy events. Demo event dates remain `null` until a cited event-date extractor exists.
- Output ordering, generator version, fixture-set SHA-256, and JSON formatting are deterministic.

Run from an installed package, or during development with `src` on the Python path:

```console
policygraph build-sample
python -m unittest discover -s tests -v
```
