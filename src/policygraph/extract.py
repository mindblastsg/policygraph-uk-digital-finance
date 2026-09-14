"""Document extraction adapters and deterministic claim extraction interface."""

from __future__ import annotations

import json
from datetime import date
from email.message import Message
from html.parser import HTMLParser
from typing import Protocol

from .fetch import FetchedContent
from .models import Claim, Document, EvidenceLocator, PolicyStatus, Source


class DocumentExtractor(Protocol):
    def extract(self, source: Source, content: FetchedContent) -> Document: ...


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def _decode(content: FetchedContent) -> str:
    message = Message()
    message["content-type"] = content.content_type
    charset = message.get_content_charset() or "utf-8"
    return content.body.decode(charset, errors="strict")


class GenericHTMLExtractor:
    def extract(self, source: Source, content: FetchedContent) -> Document:
        parser = _TextHTMLParser()
        if not content.content_type.casefold().startswith("text/html"):
            raise ValueError("generic HTML extractor requires text/html")
        parser.feed(_decode(content))
        return Document(
            f"doc-{source.id}",
            source.id,
            source.title,
            "\n".join(parser.parts),
            content.final_url,
            source.published_on,
            content.final_url.startswith("fixture://"),
        )


class GovUKContentExtractor:
    """Use documented Content API fields: title, public_updated_at, details.body."""

    def extract(self, source: Source, content: FetchedContent) -> Document:
        if not content.content_type.casefold().startswith("application/json"):
            raise ValueError("GOV.UK extractor requires application/json")
        payload = json.loads(_decode(content))
        details = payload.get("details") or {}
        parts = details.get("parts") or []
        body = details.get("body") or "\n".join(part.get("body", "") for part in parts if isinstance(part, dict))
        parser = _TextHTMLParser()
        parser.feed(body)
        updated = payload.get("public_updated_at")
        published = date.fromisoformat(updated[:10]) if updated else source.published_on
        return Document(
            f"doc-{source.id}",
            source.id,
            payload.get("title", source.title),
            "\n".join(parser.parts),
            content.final_url,
            published,
            content.final_url.startswith("fixture://"),
        )


class ClaimExtractor(Protocol):
    def extract(self, source: Source, document: Document) -> list[Claim]: ...


class DeterministicDemoClaimExtractor:
    """Fixture-driven baseline: explicit markers, no model or production-AI claim."""

    marker = "POLICYGRAPH_CLAIM:"

    @staticmethod
    def _topics(source: Source, subject: str, object_: str) -> tuple[str, ...]:
        text = f"{subject} {object_}".casefold()
        aliases = {
            "digital securities sandbox": ("digital securities sandbox", "dss"),
            "cryptoasset regulation": ("cryptoasset",),
            "stablecoins": ("stablecoin",),
        }
        return tuple(
            topic
            for topic in source.topics
            if any(term in text for term in aliases.get(topic.casefold(), (topic.casefold(),)))
        )

    def extract(self, source: Source, document: Document) -> list[Claim]:
        claims: list[Claim] = []
        for line_number, line in enumerate(document.text.splitlines(), start=1):
            if not line.startswith(self.marker):
                continue
            data = json.loads(line.removeprefix(self.marker).strip())
            quote = data["quote"]
            claims.append(
                Claim(
                    id=data["id"],
                    source_id=source.id,
                    subject=data["subject"],
                    predicate=data["predicate"],
                    object=data["object"],
                    status=PolicyStatus(data.get("status", source.status)),
                    status_as_of=source.status_as_of,
                    evidence=EvidenceLocator(document.id, f"line:{line_number}", quote),
                    topics=self._topics(source, data["subject"], data["object"]),
                )
            )
        return claims
