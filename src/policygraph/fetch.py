"""Fetch contracts and offline cache adapter; no live transport is shipped."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

from .models import Source


@dataclass(frozen=True)
class FetchedContent:
    body: bytes
    content_type: str
    final_url: str


class Fetcher(Protocol):
    def fetch(self, source: Source) -> FetchedContent: ...


class NetworkFetchUnavailable(RuntimeError):
    """The POC deliberately has no built-in live transport."""


class UnavailableNetworkFetcher:
    def fetch(self, source: Source) -> FetchedContent:
        raise NetworkFetchUnavailable(
            "PolicyGraph ships no live network transport; inject a separately audited Fetcher"
        )


SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,99}$")


class CachedFetcher:
    """Read validated cache entries; delegate cache misses only by explicit injection."""

    def __init__(self, delegate: Fetcher, cache_dir: Path, *, allow_delegate: bool = False) -> None:
        self.delegate, self.cache_dir, self.allow_delegate = delegate, cache_dir, allow_delegate

    def fetch(self, source: Source) -> FetchedContent:
        if not SAFE_ID.fullmatch(source.id):
            raise ValueError("source id is not cache-safe")
        body_path = self.cache_dir / f"{source.id}.body"
        metadata_path = self.cache_dir / f"{source.id}.metadata.json"
        if body_path.exists() and metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if set(metadata) != {"content_type", "final_url"} or not all(
                isinstance(metadata[key], str) for key in metadata
            ):
                raise ValueError("invalid cache metadata")
            final = urlparse(metadata["final_url"])
            if final.scheme not in {"https", "fixture"} or not (final.hostname or final.path):
                raise ValueError("invalid cached final URL")
            return FetchedContent(body_path.read_bytes(), metadata["content_type"], metadata["final_url"])
        if not self.allow_delegate:
            raise NetworkFetchUnavailable("cache miss; external fetch delegation is disabled")
        fetched = self.delegate.fetch(source)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(fetched.body)
        metadata_path.write_text(
            json.dumps({"content_type": fetched.content_type, "final_url": fetched.final_url}, sort_keys=True),
            encoding="utf-8",
        )
        return fetched
