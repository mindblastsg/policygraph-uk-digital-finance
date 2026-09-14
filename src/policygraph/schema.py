"""Standards-compliant JSON Schema and graph provenance validation."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

SCHEMA_NAMES = frozenset({"claim", "document", "evaluation", "graph", "source-registry"})


def load_schema(name: str) -> dict[str, Any]:
    if name not in SCHEMA_NAMES:
        raise ValueError(f"unknown schema {name!r}; choose one of: {', '.join(sorted(SCHEMA_NAMES))}")
    value = json.loads(files("policygraph.schemas").joinpath(f"{name}.schema.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("schema root must be an object")
    return value


def _provenance_errors(graph: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = {item["id"] for item in graph.get("sources", [])}
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
                line_number = int(evidence["section"].removeprefix("line:"))
                lines = document["text"].splitlines()
                if line_number > len(lines):
                    errors.append(f"$/{collection}/{index}/evidence/section: line is outside the document")
                elif evidence["quote"] not in lines[line_number - 1]:
                    errors.append(f"$/{collection}/{index}/evidence/quote: quote is not present on the located line")
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
    return errors


def validation_errors(instance: Any, schema_name: str) -> list[str]:
    from jsonschema import Draft202012Validator, FormatChecker

    Draft202012Validator.check_schema(load_schema(schema_name))
    validator = Draft202012Validator(load_schema(schema_name), format_checker=FormatChecker())
    errors = [
        f"$/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    ]
    if not errors and schema_name == "graph" and isinstance(instance, dict):
        errors.extend(_provenance_errors(instance))
    return errors
