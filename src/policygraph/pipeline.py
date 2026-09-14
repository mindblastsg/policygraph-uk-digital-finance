"""Offline sample orchestration and deterministic JSON serialization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .extract import DeterministicDemoClaimExtractor, GovUKContentExtractor
from .fetch import FetchedContent
from .graph import build_graph
from .models import Claim, Document
from .registry import load_registry
from .validate import validate_graph


def build_sample(registry_path: Path, fixtures_dir: Path, output_path: Path) -> None:
    sources = load_registry(registry_path)
    documents: list[Document] = []
    claims: list[Claim] = []
    extractor, claim_extractor = GovUKContentExtractor(), DeterministicDemoClaimExtractor()
    for source in sources:
        fixture_path = fixtures_dir / f"{source.id}.json"
        content = FetchedContent(
            fixture_path.read_bytes(), "application/json; charset=utf-8", f"fixture://{fixture_path.name}"
        )
        document = extractor.extract(source, content)
        documents.append(document)
        claims.extend(claim_extractor.extract(source, document))
    graph = build_graph(sources, documents, claims)
    digest = hashlib.sha256()
    for name, digest_content in [
        ("registry", registry_path.read_bytes()),
        *[(path.name, path.read_bytes()) for path in sorted(fixtures_dir.glob("*.json"), key=lambda item: item.name)],
    ]:
        digest.update(len(name.encode()).to_bytes(4, "big"))
        digest.update(name.encode())
        digest.update(len(digest_content).to_bytes(8, "big"))
        digest.update(digest_content)
    digest.update(graph.schema_version.encode())
    digest.update(graph.generator_version.encode())
    graph.fixture_set_sha256 = digest.hexdigest()
    errors = validate_graph(graph)
    if errors:
        raise ValueError("Invalid graph: " + "; ".join(errors))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(graph.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
