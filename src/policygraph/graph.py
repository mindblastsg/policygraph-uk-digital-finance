"""Convert evidence-bearing claims into the graph projection."""

from __future__ import annotations

from .canonicalise import canonical_name, stable_id
from .models import Claim, Document, Entity, EntityKind, Event, Graph, Relationship, Source


def build_graph(sources: list[Source], documents: list[Document], claims: list[Claim]) -> Graph:
    entity_map: dict[str, Entity] = {}
    relationships: list[Relationship] = []
    for claim in claims:
        subject_name, object_name = canonical_name(claim.subject), canonical_name(claim.object)
        subject_id, object_id = stable_id(subject_name), stable_id(object_name)
        entity_map.setdefault(subject_id, Entity(subject_id, subject_name, EntityKind.ORGANISATION))
        entity_map.setdefault(object_id, Entity(object_id, object_name, EntityKind.POLICY))
        relationships.append(
            Relationship(
                f"rel-{claim.id}",
                subject_id,
                object_id,
                claim.predicate,
                claim.source_id,
                claim.id,
                claim.evidence,
                claim.topics,
            )
        )
    events = [
        Event(
            f"event-{claim.id}",
            f"{canonical_name(claim.subject)} {claim.predicate} {canonical_name(claim.object)}",
            None,  # claim extraction does not establish when the described event occurred
            claim.status,
            claim.status_as_of,
            claim.source_id,
            claim.evidence,
            claim.topics,
        )
        for claim in claims
    ]
    return Graph(
        sources=sorted(sources, key=lambda item: item.id),
        documents=sorted(documents, key=lambda item: item.id),
        claims=sorted(claims, key=lambda item: item.id),
        entities=sorted(entity_map.values(), key=lambda item: item.id),
        events=sorted(events, key=lambda item: item.id),
        relationships=sorted(relationships, key=lambda item: item.id),
    )
