"""Read-only, same-origin API and web application for the sample graph."""

from __future__ import annotations

import json
import os
import sysconfig
from datetime import date
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from policygraph import __version__
from policygraph.schema import validation_errors

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
INSTALLED_ROOT = Path(sysconfig.get_path("data")) / "share" / "policygraph"


def _runtime_path(relative: str) -> Path:
    """Prefer checkout assets, falling back to wheel-installed data files."""
    checkout_path = REPOSITORY_ROOT / relative
    return checkout_path if checkout_path.exists() else INSTALLED_ROOT / relative


DEFAULT_GRAPH_PATH = _runtime_path("data/sample/graph.json")
WEB_ROOT = _runtime_path("app")
POLICY_STATUSES = {"consultation", "proposal", "final_rule", "in_force"}
SOURCE_HOSTS = {"gov.uk", "fca.org.uk", "bankofengland.co.uk", "legislation.gov.uk", "parliament.uk"}


class HealthResponse(BaseModel):
    status: str
    graph_loaded: bool


class TopicResponse(BaseModel):
    name: str
    source_ids: list[str]
    entity_ids: list[str]
    event_ids: list[str]


def _graph_path() -> Path:
    override = os.environ.get("POLICYGRAPH_DATA_PATH")
    return Path(override) if override else DEFAULT_GRAPH_PATH


def load_graph() -> dict[str, Any]:
    try:
        payload = json.loads(_graph_path().read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("PolicyGraph sample data is unavailable") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("PolicyGraph sample data has an invalid root")
    errors = validate_graph_payload(payload)
    if errors:
        raise RuntimeError("PolicyGraph sample data failed validation: " + "; ".join(errors))
    return payload


def validate_graph_payload(payload: dict[str, Any]) -> list[str]:
    """Validate the read model before it crosses the API trust boundary."""
    errors = validation_errors(payload, "graph")
    if errors:
        return errors
    collections = ("sources", "documents", "claims", "entities", "events", "relationships")
    if payload.get("schema_version") != "1.0":
        errors.append("unsupported schema_version")
    for name in collections:
        records = payload.get(name)
        if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
            errors.append(f"{name} must be a list of objects")
            continue
        identifiers = [item.get("id") for item in records]
        if any(not isinstance(item, str) or not item for item in identifiers) or len(identifiers) != len(
            set(identifiers)
        ):
            errors.append(f"{name} must have unique non-empty ids")
    if errors:
        return errors
    source_map = {item["id"]: item for item in payload["sources"]}
    source_ids = set(source_map)
    document_map = {item["id"]: item for item in payload["documents"]}
    claim_ids = {item["id"] for item in payload["claims"]}
    entity_ids = {item["id"] for item in payload["entities"]}
    from urllib.parse import urlsplit

    def valid_iso_date(value: object) -> bool:
        if not isinstance(value, str):
            return False
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        return True

    for source in payload["sources"]:
        url = source.get("url", "")
        try:
            parsed = urlsplit(url) if isinstance(url, str) else None
        except ValueError:
            parsed = None
        hostname = parsed.hostname.casefold() if parsed and parsed.hostname else ""
        trusted = any(hostname == host or hostname.endswith(f".{host}") for host in SOURCE_HOSTS)
        if not parsed or parsed.scheme != "https" or not trusted or parsed.username or parsed.password:
            errors.append(f"source {source['id']} has an untrusted URL")
        if (
            source.get("status") not in POLICY_STATUSES
            or not isinstance(source.get("topics"), list)
            or any(not isinstance(topic, str) or not topic for topic in source.get("topics", []))
        ):
            errors.append(f"source {source['id']} has invalid status or topics")
        if not valid_iso_date(source.get("status_as_of")):
            errors.append(f"source {source['id']} has invalid status_as_of")
        if not all(isinstance(source.get(field), str) and source[field] for field in ("title", "publisher")):
            errors.append(f"source {source['id']} has invalid display fields")
    for entity in payload["entities"]:
        aliases = entity.get("aliases")
        if (
            not all(isinstance(entity.get(field), str) and entity[field] for field in ("name", "kind"))
            or not isinstance(aliases, list)
            or any(not isinstance(alias, str) or not alias for alias in aliases)
        ):
            errors.append(f"entity {entity['id']} has invalid display fields")
    for document in payload["documents"]:
        if not all(
            isinstance(document.get(field), str) and document[field]
            for field in ("source_id", "title", "text", "retrieved_from")
        ) or not isinstance(document.get("synthetic"), bool):
            errors.append(f"document {document['id']} has invalid display fields")
    for collection in ("claims", "events", "relationships"):
        for item in payload[collection]:
            evidence = item.get("evidence")
            document = document_map.get(evidence.get("document_id")) if isinstance(evidence, dict) else None
            if (
                item.get("source_id") not in source_ids
                or document is None
                or document.get("source_id") != item.get("source_id")
            ):
                errors.append(f"{collection} {item['id']} has orphaned provenance")
            if not isinstance(evidence, dict) or not evidence.get("section") or not evidence.get("quote"):
                errors.append(f"{collection} {item['id']} has invalid evidence")
            elif document:
                section = evidence["section"]
                try:
                    number = (
                        int(section.removeprefix("line:"))
                        if isinstance(section, str) and section.startswith("line:")
                        else 0
                    )
                    line = document.get("text", "").splitlines()[number - 1] if number > 0 else ""
                except (IndexError, ValueError):
                    line = ""
                if not isinstance(evidence["quote"], str) or evidence["quote"] not in line:
                    errors.append(f"{collection} {item['id']} evidence does not match its locator")
            topics = item.get("topics")
            status_invalid = collection != "relationships" and item.get("status") not in POLICY_STATUSES
            if (
                status_invalid
                or not isinstance(topics, list)
                or any(not isinstance(topic, str) or not topic for topic in topics)
            ):
                errors.append(f"{collection} {item['id']} has invalid status or topics")
            if collection != "relationships" and not valid_iso_date(item.get("status_as_of")):
                errors.append(f"{collection} {item['id']} has invalid status_as_of")
            display_fields = {
                "claims": ("subject", "predicate", "object"),
                "events": ("title",),
                "relationships": ("kind",),
            }[collection]
            if not all(isinstance(item.get(field), str) and item[field] for field in display_fields):
                errors.append(f"{collection} {item['id']} has invalid display fields")
    for item in payload["relationships"]:
        if (
            item.get("claim_id") not in claim_ids
            or item.get("source_entity_id") not in entity_ids
            or item.get("target_entity_id") not in entity_ids
        ):
            errors.append(f"relationship {item['id']} has orphaned graph references")
        claim = next((claim for claim in payload["claims"] if claim["id"] == item.get("claim_id")), None)
        if claim and (
            item.get("source_id") != claim.get("source_id")
            or item.get("evidence") != claim.get("evidence")
            or item.get("topics") != claim.get("topics")
        ):
            errors.append(f"relationship {item['id']} does not match its claim evidence")
    claim_map = {item["id"]: item for item in payload["claims"]}
    for claim in payload["claims"]:
        source = source_map.get(claim.get("source_id"))
        if source and (
            claim.get("status") != source.get("status") or claim.get("status_as_of") != source.get("status_as_of")
        ):
            errors.append(f"claim {claim['id']} status does not match its source document")
    for event in payload["events"]:
        claim = claim_map.get(event["id"].removeprefix("event-"))
        source = source_map.get(event.get("source_id"))
        if (
            claim is None
            or source is None
            or event.get("status") != claim.get("status")
            or event.get("status_as_of") != claim.get("status_as_of")
            or event.get("status") != source.get("status")
            or event.get("status_as_of") != source.get("status_as_of")
        ):
            errors.append(f"event {event['id']} status does not match its claim and source document")
    return errors


def _by_id(graph: dict[str, Any], collection: str, record_id: str) -> dict[str, Any]:
    record = next((item for item in graph.get(collection, []) if item.get("id") == record_id), None)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{collection.removesuffix('s').title()} not found")
    return cast(dict[str, Any], record)


def _topics(graph: dict[str, Any]) -> list[dict[str, Any]]:
    topics: dict[str, dict[str, Any]] = {}
    relationships = graph.get("relationships", [])
    events = graph.get("events", [])
    sources = {item["id"]: item for item in graph.get("sources", [])}
    for source in sources.values():
        for name in source.get("topics", []):
            entry = topics.setdefault(name, {"name": name, "source_ids": [], "entity_ids": [], "event_ids": []})
            entry["source_ids"].append(source["id"])
    for claim in graph.get("claims", []):
        for name in claim.get("topics", []):
            entry = topics.setdefault(name, {"name": name, "source_ids": [], "entity_ids": [], "event_ids": []})
            source = sources[claim["source_id"]]
            entry["source_ids"].append(source["id"])
            related = [
                item for item in relationships if item["claim_id"] == claim["id"] and name in item.get("topics", [])
            ]
            entry["entity_ids"].extend(
                entity_id for item in related for entity_id in (item["source_entity_id"], item["target_entity_id"])
            )
            entry["event_ids"].extend(
                item["id"] for item in events if item["source_id"] == source["id"] and name in item.get("topics", [])
            )
    for entry in topics.values():
        for field in ("source_ids", "entity_ids", "event_ids"):
            entry[field] = sorted(set(entry[field]))
    return sorted(topics.values(), key=lambda item: item["name"].casefold())


app = FastAPI(
    title="PolicyGraph API",
    description="Read-only access to a bounded, synthetic UK digital-finance policy graph sample.",
    version=__version__,
)
app.mount("/assets", StaticFiles(directory=WEB_ROOT / "assets"), name="assets")


@app.exception_handler(RuntimeError)
def graph_failure(_request: object, _exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": "PolicyGraph data is unavailable or invalid"})


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        load_graph()
    except RuntimeError:
        return HealthResponse(status="degraded", graph_loaded=False)
    return HealthResponse(status="ok", graph_loaded=True)


@app.get("/api/graph")
def graph() -> dict[str, Any]:
    return load_graph()


@app.get("/api/topics", response_model=list[TopicResponse])
def topics() -> list[dict[str, Any]]:
    return _topics(load_graph())


@app.get("/api/topics/{topic_name}", response_model=TopicResponse)
def topic(topic_name: str) -> dict[str, Any]:
    record = next((item for item in _topics(load_graph()) if item["name"].casefold() == topic_name.casefold()), None)
    if record is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return record


@app.get("/api/entities/{entity_id}")
def entity(entity_id: str) -> dict[str, Any]:
    graph_data = load_graph()
    record = dict(_by_id(graph_data, "entities", entity_id))
    record["relationships"] = [
        item
        for item in graph_data.get("relationships", [])
        if entity_id in (item["source_entity_id"], item["target_entity_id"])
    ]
    return record


@app.get("/api/events/{event_id}")
def event(event_id: str) -> dict[str, Any]:
    graph_data = load_graph()
    record = dict(_by_id(graph_data, "events", event_id))
    record["source"] = _by_id(graph_data, "sources", record["source_id"])
    return record


@app.get("/api/relationships/{relationship_id}")
def relationship(relationship_id: str) -> dict[str, Any]:
    graph_data = load_graph()
    record = dict(_by_id(graph_data, "relationships", relationship_id))
    record["source_entity"] = _by_id(graph_data, "entities", record["source_entity_id"])
    record["target_entity"] = _by_id(graph_data, "entities", record["target_entity_id"])
    record["source"] = _by_id(graph_data, "sources", record["source_id"])
    return record


@app.get("/api/sources/{source_id}")
def source(source_id: str) -> dict[str, Any]:
    graph_data = load_graph()
    record = dict(_by_id(graph_data, "sources", source_id))
    record["claims"] = [item for item in graph_data.get("claims", []) if item["source_id"] == source_id]
    record["events"] = [item for item in graph_data.get("events", []) if item["source_id"] == source_id]
    return record


def run() -> None:
    """Run the development server."""
    import uvicorn

    uvicorn.run("policygraph.api:app", host="127.0.0.1", port=8000)
