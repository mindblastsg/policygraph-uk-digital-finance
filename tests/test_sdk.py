import json
from copy import deepcopy
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from policygraph import GENERATOR_VERSION, __version__
from policygraph.adapters import LocalFixtureAdapter, discover_adapters, load_adapter
from policygraph.cli import main
from policygraph.models import PolicyStatus, Source, SourceKind
from policygraph.schema import validation_errors
from policygraph.testing import assert_adapter_contract


def test_discovery_does_not_load_plugins() -> None:
    entry = Mock()
    with patch("policygraph.adapters.entry_points", return_value=(entry,)) as metadata:
        assert discover_adapters() == (entry,)
        metadata.assert_called_once_with(group="policygraph.source_adapters")
        entry.load.assert_not_called()


def test_loading_class_does_not_construct_configured_plugin() -> None:
    class ConfiguredAdapter(LocalFixtureAdapter):
        name = "configured"

        def __init__(self, credential: str) -> None:
            raise AssertionError("Only the consuming application may construct the plugin")

    entry = Mock()
    entry.name = "configured"
    entry.value = "example:ConfiguredAdapter"
    entry.load.return_value = ConfiguredAdapter
    with patch("policygraph.adapters.discover_adapters", return_value=(entry,)):
        assert load_adapter("configured") is ConfiguredAdapter
        entry.load.assert_called_once_with()
    with patch("policygraph.adapters.discover_adapters", return_value=(entry, entry)):
        with pytest.raises(LookupError, match="ambiguous"):
            load_adapter("configured")
    with patch("policygraph.adapters.discover_adapters", return_value=()):
        with pytest.raises(LookupError, match="not installed"):
            load_adapter("configured")


@pytest.mark.parametrize("value", [object(), type("Broken", (), {"name": "broken"})])
def test_loader_rejects_malformed_entry_points(value: object) -> None:
    entry = Mock()
    entry.name = "broken"
    entry.load.return_value = value
    with patch("policygraph.adapters.discover_adapters", return_value=(entry,)):
        with pytest.raises(TypeError):
            load_adapter("broken")


def test_runtime_version_is_aligned() -> None:
    assert __version__ == "0.2.0"
    assert GENERATOR_VERSION == "policygraph-0.2.0"


def test_local_adapter_contract(tmp_path: Path) -> None:
    (tmp_path / "sample.html").write_text("<h1>Evidence</h1>", encoding="utf-8")
    source = Source(
        "example",
        "Example",
        "Publisher",
        "https://example.invalid",
        SourceKind.WEB_PAGE,
        (),
        PolicyStatus.PROPOSAL,
        date(2026, 1, 1),
        content_path="sample.html",
    )
    assert_adapter_contract(LocalFixtureAdapter(tmp_path), source)


def test_registry_schema_rejects_unknown_fields() -> None:
    assert validation_errors({"schema_version": "1.0", "sources": [], "secret": True}, "source-registry")


def test_registry_schema_enforces_formats_and_uniqueness() -> None:
    source = {
        "id": "example",
        "title": "",
        "publisher": "Publisher",
        "url": "not a URI",
        "kind": "web_page",
        "topics": ["DLT", "DLT"],
        "status": "proposal",
        "status_as_of": "not-a-date",
    }
    errors = validation_errors({"schema_version": "1.0", "sources": [source]}, "source-registry")
    assert len(errors) >= 4


def test_validation_cli(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema_version": "1.0", "sources": []}), encoding="utf-8")
    assert main(["validate-registry", str(path)]) == 0


def test_graph_rejects_fabricated_quote_and_out_of_range_line() -> None:
    graph = json.loads(Path("data/sample/graph.json").read_text(encoding="utf-8"))
    fabricated = deepcopy(graph)
    fabricated["claims"][0]["evidence"]["quote"] = "fabricated evidence"
    assert any("quote is not present" in error for error in validation_errors(fabricated, "graph"))
    out_of_range = deepcopy(graph)
    out_of_range["events"][0]["evidence"]["section"] = "line:999999"
    assert any("outside the document" in error for error in validation_errors(out_of_range, "graph"))


def test_graph_rejects_huge_locator_and_changed_relationship_meaning() -> None:
    graph = json.loads(Path("data/sample/graph.json").read_text(encoding="utf-8"))
    huge = deepcopy(graph)
    huge["claims"][0]["evidence"]["section"] = "line:" + "9" * 5000
    assert any("outside the document" in error for error in validation_errors(huge, "graph"))
    altered = deepcopy(graph)
    altered["relationships"][0]["kind"] = "proposed"
    assert validation_errors(altered, "graph")


def test_committed_graph_matches_rebuild(tmp_path: Path) -> None:
    from policygraph.pipeline import build_sample

    output = tmp_path / "graph.json"
    build_sample(Path("data/registry/sources.json"), Path("data/sample/raw"), output)
    assert output.read_bytes() == Path("data/sample/graph.json").read_bytes()
