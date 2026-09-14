"""Deterministic, offline release evaluation against the reviewed golden set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[1]


def evaluate(graph: dict[str, Any], golden: dict[str, Any]) -> dict[str, float | int]:
    claims = {item["id"]: item for item in graph["claims"]}
    entities = {item["id"] for item in graph["entities"]}
    relationships = {item["id"]: item for item in graph["relationships"]}
    expected_claims = golden["claims"]
    expected_relationships = golden["relationships"]
    evidence_records = [*graph["claims"], *graph["relationships"]]

    def evidence_present(item: dict[str, Any]) -> bool:
        evidence = item.get("evidence", {})
        return bool(
            item.get("source_id") and evidence.get("document_id") and evidence.get("section") and evidence.get("quote")
        )

    def expected_fields_match(actual: dict[str, Any], expected: dict[str, Any], fields: tuple[str, ...]) -> bool:
        return all(actual.get(field) == expected[field] for field in fields)

    matched_relationships = sum(
        relationship_id in relationships
        and expected_fields_match(
            relationships[relationship_id],
            expected,
            ("claim_id", "source_entity_id", "target_entity_id", "source_id", "evidence"),
        )
        for relationship_id, expected in expected_relationships.items()
    )
    citation_matches = sum(
        claim_id in claims and expected_fields_match(claims[claim_id], expected, ("source_id", "evidence"))
        for claim_id, expected in expected_claims.items()
    ) + sum(
        relationship_id in relationships
        and expected_fields_match(relationships[relationship_id], expected, ("source_id", "evidence"))
        for relationship_id, expected in expected_relationships.items()
    )
    expected_entities = {
        expected[field]
        for expected in expected_relationships.values()
        for field in ("source_entity_id", "target_entity_id")
    }
    expected_evidence_count = len(expected_claims) + len(expected_relationships)
    matched_claims = sum(
        claim_id in claims
        and expected_fields_match(claims[claim_id], expected, ("status", "status_as_of", "source_id", "evidence"))
        for claim_id, expected in expected_claims.items()
    )
    return {
        "citation_correctness": citation_matches / expected_evidence_count,
        "claim_precision": matched_claims / len(claims),
        "entity_precision": len(expected_entities & entities) / len(entities),
        "provenance_completeness": sum(evidence_present(item) for item in evidence_records) / len(evidence_records),
        "relationship_precision": matched_relationships / len(relationships),
        "relationship_recall": matched_relationships / len(expected_relationships),
        "status_critical_errors": sum(
            claims.get(claim_id, {}).get("status") != expected["status"]
            or claims.get(claim_id, {}).get("status_as_of") != expected["status_as_of"]
            for claim_id, expected in expected_claims.items()
        ),
        "unsupported_claims": len(claims) - matched_claims,
        "unsupported_relationships": len(relationships) - matched_relationships,
    }


def assert_gates(metrics: dict[str, float | int], thresholds: dict[str, float | int]) -> None:
    blockers = []
    for name, threshold in thresholds.items():
        passed = (
            metrics[name] <= threshold
            if name.endswith("errors") or name.startswith("unsupported")
            else metrics[name] >= threshold
        )
        if not passed:
            blockers.append(f"{name}={metrics[name]} (gate {threshold})")
    if blockers:
        raise ValueError("Evaluation gates failed: " + "; ".join(blockers))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=ROOT / "data/sample/graph.json")
    parser.add_argument("--golden", type=Path, default=ROOT / "evals/golden.json")
    args = parser.parse_args()
    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    golden = json.loads(args.golden.read_text(encoding="utf-8"))
    metrics = evaluate(graph, golden)
    assert_gates(metrics, golden["thresholds"])
    print(json.dumps({"status": "pass", "metrics": metrics}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
