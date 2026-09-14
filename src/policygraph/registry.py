"""Load and validate the human-curated authoritative source registry."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import PolicyStatus, Source, SourceKind
from .schema import validation_errors


def load_registry(path: Path) -> list[Source]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = validation_errors(payload, "source-registry")
    if errors:
        raise ValueError("Invalid source registry: " + "; ".join(errors))
    sources: list[Source] = []
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
        sources.append(source)
    return sources
