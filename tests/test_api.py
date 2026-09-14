from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from policygraph import __version__
from policygraph.api import app

ROOT = Path(__file__).parents[1]
GRAPH = json.loads((ROOT / "data/sample/graph.json").read_text(encoding="utf-8"))
CLIENT = TestClient(app)


class ApiTests(unittest.TestCase):
    def test_openapi_reports_installed_package_version(self) -> None:
        self.assertEqual(__version__, CLIENT.get("/openapi.json").json()["info"]["version"])

    def test_health_and_graph(self) -> None:
        self.assertEqual({"status": "ok", "graph_loaded": True}, CLIENT.get("/api/health").json())
        response = CLIENT.get("/api/graph")
        self.assertEqual(200, response.status_code)
        self.assertEqual(GRAPH["fixture_set_sha256"], response.json()["fixture_set_sha256"])

    def test_entity_includes_relationships(self) -> None:
        response = CLIENT.get("/api/entities/hm-treasury")
        self.assertEqual(200, response.status_code)
        self.assertEqual("HM Treasury", response.json()["name"])
        self.assertEqual(4, len(response.json()["relationships"]))

    def test_event_includes_source(self) -> None:
        response = CLIENT.get(f"/api/events/{GRAPH['events'][0]['id']}")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json()["source_id"], response.json()["source"]["id"])

    def test_source_includes_evidence_bearing_records(self) -> None:
        response = CLIENT.get(f"/api/sources/{GRAPH['sources'][0]['id']}")
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json()["claims"][0]["evidence"]["quote"])
        self.assertTrue(response.json()["events"])
        self.assertRegex(response.json()["status_as_of"], r"^20\d\d-\d\d-\d\d$")

    def test_topics_and_relationship_evidence(self) -> None:
        topic_data = CLIENT.get("/api/topics").json()
        self.assertEqual(
            {"DLT", "tokenisation", "Digital Securities Sandbox", "stablecoins", "cryptoasset regulation"},
            {item["name"] for item in topic_data},
        )
        for name in ("DLT", "tokenisation"):
            record = next(item for item in topic_data if item["name"] == name)
            self.assertTrue(record["source_ids"])
            self.assertEqual([], record["entity_ids"])
            self.assertEqual([], record["event_ids"])
        detail = CLIENT.get("/api/topics/Digital%20Securities%20Sandbox")
        self.assertEqual(200, detail.status_code)
        self.assertTrue(detail.json()["source_ids"])
        response = CLIENT.get(f"/api/relationships/{GRAPH['relationships'][0]['id']}")
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json()["evidence"]["quote"])

    def test_unknown_records_are_404s(self) -> None:
        self.assertEqual(404, CLIENT.get("/api/entities/not-present").status_code)
        self.assertEqual(404, CLIENT.get("/api/events/not-present").status_code)
        self.assertEqual(404, CLIENT.get("/api/relationships/not-present").status_code)
        self.assertEqual(404, CLIENT.get("/api/sources/not-present").status_code)
        self.assertEqual(404, CLIENT.get("/api/topics/not-present").status_code)

    def test_health_reports_missing_graph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"POLICYGRAPH_DATA_PATH": str(Path(directory) / "missing.json")}):
                self.assertEqual({"status": "degraded", "graph_loaded": False}, CLIENT.get("/api/health").json())

    def test_health_rejects_malformed_orphaned_and_unsafe_graphs(self) -> None:
        malformed = {"schema_version": "wrong"}
        orphaned = json.loads(json.dumps(GRAPH))
        orphaned["events"][0]["source_id"] = "missing-source"
        unsafe_url = json.loads(json.dumps(GRAPH))
        unsafe_url["sources"][0]["url"] = "javascript:alert(1)"
        for payload in (malformed, orphaned, unsafe_url):
            with self.subTest(payload=payload.get("schema_version")):
                with tempfile.TemporaryDirectory() as directory:
                    graph_path = Path(directory) / "graph.json"
                    graph_path.write_text(json.dumps(payload), encoding="utf-8")
                    with patch.dict(os.environ, {"POLICYGRAPH_DATA_PATH": str(graph_path)}):
                        self.assertEqual(
                            {"status": "degraded", "graph_loaded": False}, CLIENT.get("/api/health").json()
                        )

    def test_invalid_graph_endpoint_fails_with_stable_503(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph_path = Path(directory) / "graph.json"
            graph_path.write_text('{"schema_version":"wrong"}', encoding="utf-8")
            with patch.dict(os.environ, {"POLICYGRAPH_DATA_PATH": str(graph_path)}):
                response = CLIENT.get("/api/graph")
                self.assertEqual(503, response.status_code)
                self.assertEqual({"detail": "PolicyGraph data is unavailable or invalid"}, response.json())

    def test_malformed_evidence_and_field_types_fail_closed(self) -> None:
        mutations = (
            (
                "claims",
                "evidence",
                {"document_id": GRAPH["claims"][0]["evidence"]["document_id"], "section": "line:abc", "quote": "test"},
            ),
            ("claims", "evidence", {"document_id": [], "section": "line:1", "quote": "test"}),
            ("claims", "source_id", []),
            ("sources", "status", {}),
            ("documents", "text", []),
            ("entities", "id", {}),
            ("relationships", "claim_id", []),
            ("sources", "url", "https://[malformed"),
        )
        endpoints = (
            "/api/graph",
            "/api/topics",
            "/api/entities/hm-treasury",
            f"/api/events/{GRAPH['events'][0]['id']}",
            f"/api/relationships/{GRAPH['relationships'][0]['id']}",
            f"/api/sources/{GRAPH['sources'][0]['id']}",
        )
        for collection, field, value in mutations:
            with self.subTest(collection=collection, field=field, value=value):
                payload = json.loads(json.dumps(GRAPH))
                payload[collection][0][field] = value
                with tempfile.TemporaryDirectory() as directory:
                    graph_path = Path(directory) / "graph.json"
                    graph_path.write_text(json.dumps(payload), encoding="utf-8")
                    with patch.dict(os.environ, {"POLICYGRAPH_DATA_PATH": str(graph_path)}):
                        self.assertEqual(
                            {"status": "degraded", "graph_loaded": False}, CLIENT.get("/api/health").json()
                        )
                        for endpoint in endpoints:
                            response = CLIENT.get(endpoint)
                            self.assertEqual(503, response.status_code, endpoint)
                            self.assertEqual({"detail": "PolicyGraph data is unavailable or invalid"}, response.json())

    def test_invalid_utf8_graph_fails_with_stable_503(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph_path = Path(directory) / "graph.json"
            graph_path.write_bytes(b"\xff\xfe")
            with patch.dict(os.environ, {"POLICYGRAPH_DATA_PATH": str(graph_path)}):
                self.assertEqual(503, CLIENT.get("/api/graph").status_code)
                self.assertEqual({"status": "degraded", "graph_loaded": False}, CLIENT.get("/api/health").json())

    def test_strict_validation_rejects_duplicate_ids_and_claim_mismatch(self) -> None:
        duplicate = json.loads(json.dumps(GRAPH))
        duplicate["entities"].append(duplicate["entities"][0])
        mismatch = json.loads(json.dumps(GRAPH))
        mismatch["relationships"][0]["topics"] = ["fabricated-topic"]
        for payload in (duplicate, mismatch):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    graph_path = Path(directory) / "graph.json"
                    graph_path.write_text(json.dumps(payload), encoding="utf-8")
                    with patch.dict(os.environ, {"POLICYGRAPH_DATA_PATH": str(graph_path)}):
                        self.assertEqual(503, CLIENT.get("/api/graph").status_code)

    def test_missing_status_date_is_rejected(self) -> None:
        payload = json.loads(json.dumps(GRAPH))
        payload["claims"][0].pop("status_as_of")
        with tempfile.TemporaryDirectory() as directory:
            graph_path = Path(directory) / "graph.json"
            graph_path.write_text(json.dumps(payload), encoding="utf-8")
            with patch.dict(os.environ, {"POLICYGRAPH_DATA_PATH": str(graph_path)}):
                self.assertEqual(503, CLIENT.get("/api/graph").status_code)

    def test_status_must_match_source_claim_and_event(self) -> None:
        mismatched_claim = json.loads(json.dumps(GRAPH))
        mismatched_claim["claims"][0]["status"] = "in_force"
        mismatched_event = json.loads(json.dumps(GRAPH))
        mismatched_event["events"][0]["status_as_of"] = "2026-09-14"
        for payload in (mismatched_claim, mismatched_event):
            with tempfile.TemporaryDirectory() as directory:
                graph_path = Path(directory) / "graph.json"
                graph_path.write_text(json.dumps(payload), encoding="utf-8")
                with patch.dict(os.environ, {"POLICYGRAPH_DATA_PATH": str(graph_path)}):
                    self.assertEqual(503, CLIENT.get("/api/graph").status_code)


class UiTests(unittest.TestCase):
    def test_ui_and_assets_load_from_same_origin(self) -> None:
        response = CLIENT.get("/")
        self.assertEqual(200, response.status_code)
        self.assertIn('href="#explorer"', response.text)
        self.assertIn("Know the limits", response.text)
        self.assertIn("No result means", response.text)
        self.assertIn("Share feedback", response.text)
        self.assertIn("research_feedback.yml", response.text)
        self.assertEqual(200, CLIENT.get("/assets/app.js").status_code)

    def test_ui_has_keyboard_controls_and_empty_error_states(self) -> None:
        script = CLIENT.get("/assets/app.js").text
        self.assertIn("document.createElement('button')", script)
        self.assertIn("aria-pressed", script)
        self.assertIn("No topics are covered", script)
        self.assertIn('role="alert"', script)
        self.assertIn("url.protocol === 'https:'", script)
        self.assertIn("bankofengland.co.uk", script)
        self.assertNotIn('href="${escapeHtml(source.url)}"', script)
        self.assertIn("Synthetic fixture excerpt", script)
        self.assertIn("history.replaceState", script)


if __name__ == "__main__":
    unittest.main()
