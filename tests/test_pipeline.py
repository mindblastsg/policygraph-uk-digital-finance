from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from policygraph.canonicalise import canonical_name, stable_id
from policygraph.cli import main
from policygraph.extract import GenericHTMLExtractor, GovUKContentExtractor
from policygraph.fetch import CachedFetcher, FetchedContent, NetworkFetchUnavailable, UnavailableNetworkFetcher
from policygraph.models import EvidenceLocator, PolicyStatus, Source, SourceKind
from policygraph.pipeline import build_sample
from policygraph.registry import load_registry
from policygraph.validate import validate_graph

ROOT = Path(__file__).parents[1]
REGISTRY = ROOT / "data/registry/sources.json"
FIXTURES = ROOT / "data/sample/raw"


class RegistryTests(unittest.TestCase):
    def test_registry_is_curated_and_unique(self) -> None:
        sources = load_registry(REGISTRY)
        self.assertEqual(4, len(sources))
        self.assertEqual(len(sources), len({source.id for source in sources}))
        self.assertTrue(all(source.publisher == "HM Treasury" for source in sources))

    def test_registry_rejects_path_traversal_id(self) -> None:
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
        payload["sources"][0]["id"] = "../escape"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid source registry"):
                load_registry(path)


class AdapterTests(unittest.TestCase):
    def test_govuk_fixture_contract(self) -> None:
        source = load_registry(REGISTRY)[0]
        fetched = FetchedContent((FIXTURES / f"{source.id}.json").read_bytes(), "application/json", source.url)
        document = GovUKContentExtractor().extract(source, fetched)
        self.assertEqual("Digital Securities Sandbox", document.title)
        self.assertIn("POLICYGRAPH_CLAIM:", document.text)

    def test_generic_html_adapter(self) -> None:
        source = Source(
            "web",
            "Web",
            "Publisher",
            "https://example.test",
            SourceKind.WEB_PAGE,
            ("DLT",),
            PolicyStatus.PROPOSAL,
            date(2026, 1, 1),
        )
        document = GenericHTMLExtractor().extract(
            source, FetchedContent(b"<h1>Hello</h1><p>World</p>", "text/html", source.url)
        )
        self.assertEqual("Hello\nWorld", document.text)

    def test_network_fetch_requires_explicit_opt_in(self) -> None:
        source = load_registry(REGISTRY)[0]

        class UnusedFetcher:
            def fetch(self, source: Source) -> FetchedContent:
                raise AssertionError("delegate must not be called")

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(NetworkFetchUnavailable, "cache miss"):
                CachedFetcher(UnusedFetcher(), Path(directory)).fetch(source)

    def test_builtin_network_transport_is_unavailable(self) -> None:
        with self.assertRaisesRegex(NetworkFetchUnavailable, "no live network transport"):
            UnavailableNetworkFetcher().fetch(load_registry(REGISTRY)[0])

    def test_invalid_cache_metadata_is_rejected(self) -> None:
        source = load_registry(REGISTRY)[0]

        class UnusedFetcher:
            def fetch(self, source: Source) -> FetchedContent:
                raise AssertionError

        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            (cache / f"{source.id}.body").write_bytes(b"x")
            (cache / f"{source.id}.metadata.json").write_text('{"final_url":"file:///x","content_type":"x"}')
            with self.assertRaises(ValueError):
                CachedFetcher(UnusedFetcher(), cache).fetch(source)

    def test_cache_rejects_unsafe_id_before_path_construction(self) -> None:
        source = Source(
            "../escape",
            "x",
            "x",
            "https://www.gov.uk/x",
            SourceKind.WEB_PAGE,
            (),
            PolicyStatus.PROPOSAL,
            date(2026, 1, 1),
        )

        class UnusedFetcher:
            def fetch(self, source: Source) -> FetchedContent:
                raise AssertionError

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "cache-safe"):
                CachedFetcher(UnusedFetcher(), Path(directory)).fetch(source)

    def test_empty_and_multipart_govuk_bodies(self) -> None:
        source = load_registry(REGISTRY)[0]
        empty = FetchedContent(
            b'{"title":"Empty","details":{"parts":[]}}', "application/json; charset=utf-8", "fixture://empty"
        )
        self.assertEqual("", GovUKContentExtractor().extract(source, empty).text)
        multi = FetchedContent(
            b'{"title":"Parts","details":{"parts":[{"body":"<p>One</p>"},{"body":"<p>Two</p>"}]}}',
            "application/json",
            "fixture://parts",
        )
        self.assertEqual("One\nTwo", GovUKContentExtractor().extract(source, multi).text)


class GraphTests(unittest.TestCase):
    def test_canonicalisation(self) -> None:
        self.assertEqual("HM Treasury", canonical_name(" hmt "))
        self.assertEqual("digital-securities-sandbox", stable_id("DSS"))

    def test_graph_has_complete_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "graph.json"
            build_sample(REGISTRY, FIXTURES, output)
            graph = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(graph["claims"])
            self.assertTrue(all(item["source_id"] and item["evidence"]["quote"] for item in graph["claims"]))
            self.assertTrue(all(item["source_id"] and item["evidence"]["quote"] for item in graph["relationships"]))
            self.assertTrue(
                all(
                    item["synthetic"] and item["retrieved_from"].startswith("fixture://") for item in graph["documents"]
                )
            )
            self.assertTrue(all(item["date"] is None for item in graph["events"]))
            self.assertRegex(graph["fixture_set_sha256"], r"^[0-9a-f]{64}$")

    def test_validator_accepts_built_graph(self) -> None:
        from policygraph.extract import DeterministicDemoClaimExtractor
        from policygraph.graph import build_graph

        source = load_registry(REGISTRY)[0]
        fetched = FetchedContent((FIXTURES / f"{source.id}.json").read_bytes(), "application/json", source.url)
        document = GovUKContentExtractor().extract(source, fetched)
        claims = DeterministicDemoClaimExtractor().extract(source, document)
        self.assertEqual([], validate_graph(build_graph([source], [document], claims)))

    def test_validator_rejects_duplicate_and_mismatched_evidence(self) -> None:
        from dataclasses import replace

        from policygraph.extract import DeterministicDemoClaimExtractor
        from policygraph.graph import build_graph

        source = load_registry(REGISTRY)[0]
        fetched = FetchedContent((FIXTURES / f"{source.id}.json").read_bytes(), "application/json", "fixture://test")
        document = GovUKContentExtractor().extract(source, fetched)
        claims = DeterministicDemoClaimExtractor().extract(source, document)
        graph = build_graph([source], [document], claims)
        graph.entities.append(graph.entities[0])
        graph.relationships[0] = replace(
            graph.relationships[0], evidence=EvidenceLocator(document.id, "line:2", "absent quote")
        )
        errors = validate_graph(graph)
        self.assertTrue(any("duplicate" in item for item in errors))
        self.assertTrue(any("does not match" in item for item in errors))
        self.assertTrue(any("absent" in item for item in errors))

    def test_validator_rejects_zero_line_locator(self) -> None:
        from dataclasses import replace

        from policygraph.extract import DeterministicDemoClaimExtractor
        from policygraph.graph import build_graph

        source = load_registry(REGISTRY)[0]
        fetched = FetchedContent((FIXTURES / f"{source.id}.json").read_bytes(), "application/json", "fixture://test")
        document = GovUKContentExtractor().extract(source, fetched)
        claim = DeterministicDemoClaimExtractor().extract(source, document)[0]
        claim = replace(claim, evidence=replace(claim.evidence, section="line:0"))
        errors = validate_graph(build_graph([source], [document], [claim]))
        self.assertTrue(any("invalid locator" in item for item in errors))

    def test_cli_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "a.json", Path(directory) / "b.json"
            args = ["build-sample", "--registry", str(REGISTRY), "--fixtures", str(FIXTURES)]
            self.assertEqual(0, main([*args, "--output", str(first)]))
            self.assertEqual(0, main([*args, "--output", str(second)]))
            self.assertEqual(first.read_bytes(), second.read_bytes())


if __name__ == "__main__":
    unittest.main()
