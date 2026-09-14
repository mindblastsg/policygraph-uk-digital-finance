"""Typed domain contracts for evidence-bearing policy graph records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date as Date
from enum import StrEnum
from typing import Any, cast

from . import GENERATOR_VERSION


class SourceKind(StrEnum):
    GOVUK_CONTENT = "govuk_content"
    WEB_PAGE = "web_page"


class PolicyStatus(StrEnum):
    CONSULTATION = "consultation"
    PROPOSAL = "proposal"
    FINAL_RULE = "final_rule"
    IN_FORCE = "in_force"


class EntityKind(StrEnum):
    ORGANISATION = "organisation"
    POLICY = "policy"
    TOPIC = "topic"


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    publisher: str
    url: str
    kind: SourceKind
    topics: tuple[str, ...]
    status: PolicyStatus
    status_as_of: Date
    published_on: Date | None = None
    content_path: str | None = None


@dataclass(frozen=True)
class Document:
    id: str
    source_id: str
    title: str
    text: str
    retrieved_from: str
    published_on: Date | None = None
    synthetic: bool = False


@dataclass(frozen=True)
class EvidenceLocator:
    document_id: str
    section: str
    quote: str


@dataclass(frozen=True)
class Claim:
    id: str
    source_id: str
    subject: str
    predicate: str
    object: str
    status: PolicyStatus
    status_as_of: Date
    evidence: EvidenceLocator
    topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class Entity:
    id: str
    name: str
    kind: EntityKind
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class Event:
    id: str
    title: str
    date: Date | None
    status: PolicyStatus
    status_as_of: Date
    source_id: str
    evidence: EvidenceLocator
    topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class Relationship:
    id: str
    source_entity_id: str
    target_entity_id: str
    kind: str
    source_id: str
    claim_id: str
    evidence: EvidenceLocator
    topics: tuple[str, ...] = ()


@dataclass
class Graph:
    schema_version: str = "1.0"
    generator_version: str = GENERATOR_VERSION
    fixture_set_sha256: str = ""
    sources: list[Source] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        def convert(value: Any) -> Any:
            if isinstance(value, (Date, StrEnum)):
                return str(value)
            if isinstance(value, tuple):
                return [convert(item) for item in value]
            if isinstance(value, list):
                return [convert(item) for item in value]
            if isinstance(value, dict):
                return {key: convert(item) for key, item in value.items()}
            return value

        return cast(dict[str, Any], convert(asdict(self)))
