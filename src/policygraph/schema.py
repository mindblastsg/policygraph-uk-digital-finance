"""Standards-compliant JSON Schema and graph provenance validation."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from .canonicalise import stable_id

SCHEMA_NAMES = frozenset({"claim", "document", "evaluation", "graph", "source-registry"})


def load_schema(name: str) -> dict[str, Any]:
    if name not in SCHEMA_NAMES:
        raise ValueError(f"unknown schema {name!r}; choose one of: {', '.join(sorted(SCHEMA_NAMES))}")
    value = json.loads(files("policygraph.schemas").joinpath(f"{name}.schema.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("schema root must be an object")
    return value


def _source_errors(sources: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    identifiers = [source["id"] for source in sources]
    if len(identifiers) != len(set(identifiers)):
        errors.append("$/sources: ids must be unique")
    for index, source in enumerate(sources):
        if source["kind"] == "govuk_content" and not source.get("content_path"):
            errors.append(f"$/sources/{index}/content_path: GOV.UK source requires content_path")
    return errors


def _provenance_errors(graph: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = {item["id"]: item for item in graph.get("sources", [])}
    documents = {item["id"]: item for item in graph.get("documents", [])}
    claims = {item["id"]: item for item in graph.get("claims", [])}
    entities = {item["id"] for item in graph.get("entities", [])}
    for collection in ("sources", "documents", "claims", "entities", "events", "relationships"):
        values = [item.get("id") for item in graph.get(collection, []) if isinstance(item, dict)]
        if len(values) != len(set(values)):
            errors.append(f"$/{collection}: ids must be unique")
    for index, document in enumerate(graph.get("documents", [])):
        if document["source_id"] not in sources:
            errors.append(f"$/documents/{index}/source_id: unknown source")
    for collection in ("claims", "events", "relationships"):
        for index, item in enumerate(graph.get(collection, [])):
            if item["source_id"] not in sources:
                errors.append(f"$/{collection}/{index}/source_id: unknown source")
            evidence = item["evidence"]
            document = documents.get(evidence["document_id"])
            if document is None:
                errors.append(f"$/{collection}/{index}/evidence/document_id: unknown document")
            elif document["source_id"] != item["source_id"]:
                errors.append(f"$/{collection}/{index}/evidence: document belongs to another source")
            else:
                number = evidence["section"].removeprefix("line:")
                lines = document["text"].splitlines()
                # Compare digit count first: even a schema-valid enormous locator
                # must return a validation error, not exceed Python's int limit.
                if len(number) > len(str(len(lines))) or int(number) > len(lines):
                    errors.append(f"$/{collection}/{index}/evidence/section: line is outside the document")
                elif not evidence["quote"].strip() or evidence["quote"] not in lines[int(number) - 1]:
                    errors.append(f"$/{collection}/{index}/evidence/quote: quote is not present on the located line")
            if collection in {"claims", "events"} and (source := sources.get(item["source_id"])):
                if any(item[field] != source[field] for field in ("status", "status_as_of")):
                    errors.append(f"$/{collection}/{index}: status and status_as_of must match the source document")
    for index, relationship in enumerate(graph.get("relationships", [])):
        if relationship["source_entity_id"] not in entities or relationship["target_entity_id"] not in entities:
            errors.append(f"$/relationships/{index}: unknown entity reference")
        claim = claims.get(relationship["claim_id"])
        if claim is None:
            errors.append(f"$/relationships/{index}/claim_id: unknown claim")
        elif claim["source_id"] != relationship["source_id"]:
            errors.append(f"$/relationships/{index}/claim_id: claim belongs to another source")
        elif relationship["evidence"] != claim["evidence"]:
            errors.append(f"$/relationships/{index}/evidence: evidence must match the linked claim")
        if claim is not None and (
            relationship["kind"] != claim["predicate"]
            or relationship["topics"] != claim["topics"]
            or relationship["source_entity_id"] != stable_id(claim["subject"])
            or relationship["target_entity_id"] != stable_id(claim["object"])
        ):
            errors.append(f"$/relationships/{index}: relationship must match the linked claim projection")
    return errors


def validation_errors(instance: Any, schema_name: str) -> list[str]:
    from jsonschema import Draft202012Validator, FormatChecker

    schema = load_schema(schema_name)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"$/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    ]
    if not errors and isinstance(instance, dict):
        if schema_name == "source-registry":
            errors.extend(_source_errors(instance["sources"]))
        elif schema_name == "graph":
            errors.extend(_provenance_errors(instance))
    return errors
