"""Reusable contract assertions for third-party adapters."""

from __future__ import annotations

from urllib.parse import urlparse

from .adapters import SourceAdapter
from .models import Source


def assert_adapter_contract(
    adapter: SourceAdapter, source: Source, *, allowed_final_url_schemes: tuple[str, ...] = ("fixture",)
) -> None:
    assert adapter.name.strip(), "adapter name must not be empty"
    assert adapter.supported_hosts and all(host.strip() for host in adapter.supported_hosts)
    first = adapter.fetch(source)
    second = adapter.fetch(source)
    assert first == second, "contract fixture fetch must be deterministic"
    assert first.body and first.content_type.strip()
    parsed = urlparse(first.final_url)
    assert parsed.scheme in allowed_final_url_schemes, "final URL scheme is not allowed by this contract test"
    document = adapter.extract(source, first)
    assert document.id.strip()
    assert document.source_id == source.id
    assert document.retrieved_from == first.final_url
    assert document.text.strip()
