"""Graph integrity and provenance quality gates."""

from .models import Document, EvidenceLocator, Graph


def validate_graph(graph: Graph) -> list[str]:
    errors: list[str] = []
    collections = (graph.sources, graph.documents, graph.claims, graph.entities, graph.events, graph.relationships)
    for collection in collections:
        ids = [item.id for item in collection]
        if len(ids) != len(set(ids)):
            errors.append("duplicate ids in graph collection")
    source_ids = {item.id for item in graph.sources}
    documents = {item.id: item for item in graph.documents}
    claim_ids = {item.id for item in graph.claims}
    entity_ids = {item.id for item in graph.entities}
    for document in graph.documents:
        if document.source_id not in source_ids:
            errors.append(f"document {document.id}: unknown source {document.source_id}")

    def locator_valid(document: Document, evidence: EvidenceLocator) -> bool:
        if not evidence.section.startswith("line:") or not evidence.quote.strip():
            return False
        try:
            line_number = int(evidence.section.removeprefix("line:"))
            if line_number < 1:
                return False
            line = document.text.splitlines()[line_number - 1]
        except (ValueError, IndexError):
            return False
        return evidence.quote in line

    for claim in graph.claims:
        if claim.source_id not in source_ids:
            errors.append(f"claim {claim.id}: unknown source {claim.source_id}")
        claim_document = documents.get(claim.evidence.document_id)
        if claim_document is None or claim_document.source_id != claim.source_id:
            errors.append(f"claim {claim.id}: evidence document ownership mismatch")
        if claim_document and not locator_valid(claim_document, claim.evidence):
            errors.append(f"claim {claim.id}: invalid locator or evidence quote absent from section")
    for relationship in graph.relationships:
        if relationship.source_id not in source_ids or relationship.claim_id not in claim_ids:
            errors.append(f"relationship {relationship.id}: invalid provenance")
        if relationship.source_entity_id not in entity_ids or relationship.target_entity_id not in entity_ids:
            errors.append(f"relationship {relationship.id}: unknown entity")
        supporting_claim = next((item for item in graph.claims if item.id == relationship.claim_id), None)
        if supporting_claim and (
            relationship.source_id != supporting_claim.source_id or relationship.evidence != supporting_claim.evidence
        ):
            errors.append(f"relationship {relationship.id}: evidence does not match claim")
        relationship_document = documents.get(relationship.evidence.document_id)
        if relationship_document is None or relationship_document.source_id != relationship.source_id:
            errors.append(f"relationship {relationship.id}: evidence document ownership mismatch")
        if relationship_document and not locator_valid(relationship_document, relationship.evidence):
            errors.append(f"relationship {relationship.id}: invalid locator or evidence quote absent from section")
    for event in graph.events:
        event_document = documents.get(event.evidence.document_id)
        if event.source_id not in source_ids or event_document is None or event_document.source_id != event.source_id:
            errors.append(f"event {event.id}: invalid provenance")
        elif not locator_valid(event_document, event.evidence):
            errors.append(f"event {event.id}: invalid evidence locator")
    return errors
