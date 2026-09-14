"""Public adapter contract and side-effect-free plugin discovery."""

from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points
from pathlib import Path
from typing import Protocol, cast, runtime_checkable

from .extract import GenericHTMLExtractor, GovUKContentExtractor
from .fetch import FetchedContent
from .models import Document, Source, SourceKind

ENTRY_POINT_GROUP = "policygraph.source_adapters"


@runtime_checkable
class SourceAdapter(Protocol):
    name: str
    supported_hosts: tuple[str, ...]

    def fetch(self, source: Source) -> FetchedContent: ...
    def extract(self, source: Source, content: FetchedContent) -> Document: ...


def discover_adapters() -> tuple[EntryPoint, ...]:
    """Return metadata only; deliberately does not import or instantiate plugins."""
    return tuple(entry_points(group=ENTRY_POINT_GROUP))


def load_adapter(name: str) -> type[SourceAdapter]:
    """Import and validate one adapter class without instantiating it."""
    matches = [item for item in discover_adapters() if item.name == name]
    if not matches:
        raise LookupError(f"adapter {name!r} is not installed")
    if len(matches) > 1:
        providers = ", ".join(sorted(item.value for item in matches))
        raise LookupError(f"adapter {name!r} is ambiguous; providers: {providers}")
    loaded = matches[0].load()
    if not isinstance(loaded, type):
        raise TypeError(f"adapter {name!r} entry point must resolve to a class")
    if getattr(loaded, "name", None) != name:
        raise TypeError(f"adapter entry point {name!r} does not match class name {getattr(loaded, 'name', None)!r}")
    hosts = getattr(loaded, "supported_hosts", None)
    if not isinstance(hosts, tuple) or not hosts or not all(isinstance(host, str) and host.strip() for host in hosts):
        raise TypeError(f"adapter {name!r} must define a non-empty tuple[str, ...] supported_hosts")
    if not callable(getattr(loaded, "fetch", None)) or not callable(getattr(loaded, "extract", None)):
        raise TypeError(f"adapter {name!r} must define callable fetch and extract methods")
    return cast(type[SourceAdapter], loaded)


class LocalFixtureAdapter:
    """Reference adapter restricted to explicitly supplied local fixture roots."""

    name = "local_fixture"
    supported_hosts = ("fixture",)

    max_fixture_bytes = 5 * 1024 * 1024
    content_types = {
        ".html": "text/html; charset=utf-8",
        ".htm": "text/html; charset=utf-8",
        ".json": "application/json",
    }

    def __init__(self, fixture_root: Path = Path("data/sample/raw")) -> None:
        self.fixture_root = fixture_root.resolve()

    def fetch(self, source: Source) -> FetchedContent:
        if not source.content_path:
            raise ValueError("local fixture source requires content_path")
        relative = Path(source.content_path)
        if relative.is_absolute() or len(relative.parts) != 1 or relative.name in {".", ".."}:
            raise ValueError("fixture content_path must be a single relative filename")
        path = self.fixture_root / relative
        resolved = path.resolve(strict=True)
        if resolved.parent != self.fixture_root or not resolved.is_file():
            raise ValueError("fixture must be a regular file contained by the configured root")
        content_type = self.content_types.get(resolved.suffix.casefold())
        if content_type is None:
            raise ValueError("fixture must use an explicit .html, .htm, or .json content type")
        if resolved.stat().st_size > self.max_fixture_bytes:
            raise ValueError(f"fixture exceeds {self.max_fixture_bytes} byte limit")
        return FetchedContent(resolved.read_bytes(), content_type, f"fixture://{resolved.name}")

    def extract(self, source: Source, content: FetchedContent) -> Document:
        extractor = GovUKContentExtractor() if source.kind == SourceKind.GOVUK_CONTENT else GenericHTMLExtractor()
        return extractor.extract(source, content)
