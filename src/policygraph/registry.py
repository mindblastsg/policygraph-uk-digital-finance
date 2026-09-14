"""Load and validate the human-curated authoritative source registry."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .models import PolicyStatus, Source, SourceKind

SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,99}$")


def load_registry(path: Path) -> list[Source]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("Unsupported source registry schema_version")
    sources: list[Source] = []
    seen: set[str] = set()
    for item in payload.get("sources", []):
        source = Source(
            id=item["id"],
            title=item["title"],
            publisher=item["publisher"],
            url=item["url"],
            kind=SourceKind(item["kind"]),
            topics=tuple(item["topics"]),
            status=PolicyStatus(item["status"]),
            status_as_of=date.fromisoformat(item["status_as_of"]),
            published_on=date.fromisoformat(item["published_on"]) if item.get("published_on") else None,
            content_path=item.get("content_path"),
        )
        if not SAFE_ID.fullmatch(source.id):
            raise ValueError(f"Unsafe source id: {source.id}")
        if source.id in seen:
            raise ValueError(f"Duplicate source id: {source.id}")
        if source.kind == SourceKind.GOVUK_CONTENT and not source.content_path:
            raise ValueError(f"GOV.UK source requires content_path: {source.id}")
        seen.add(source.id)
        sources.append(source)
    return sources
