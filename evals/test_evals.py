from __future__ import annotations

import json
import unittest
from pathlib import Path

from evals.evaluate import assert_gates, evaluate

ROOT = Path(__file__).parents[1]


class GoldenEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = json.loads((ROOT / "data/sample/graph.json").read_text(encoding="utf-8"))
        self.golden = json.loads((ROOT / "evals/golden.json").read_text(encoding="utf-8"))

    def test_committed_sample_passes_release_gates(self) -> None:
        assert_gates(evaluate(self.graph, self.golden), self.golden["thresholds"])

    def test_unsupported_relationship_is_a_hard_failure(self) -> None:
        self.graph["relationships"][0]["target_entity_id"] = "unsupported"
        with self.assertRaisesRegex(ValueError, "relationship_precision|unsupported_relationships"):
            assert_gates(evaluate(self.graph, self.golden), self.golden["thresholds"])

    def test_status_error_is_a_hard_failure(self) -> None:
        self.graph["claims"][0]["status"] = "in_force"
        with self.assertRaisesRegex(ValueError, "status_critical_errors"):
            assert_gates(evaluate(self.graph, self.golden), self.golden["thresholds"])

    def test_changed_evidence_is_a_hard_failure(self) -> None:
        self.graph["claims"][0]["evidence"]["quote"] = "Plausible but not reviewer-approved"
        with self.assertRaisesRegex(ValueError, "citation_correctness"):
            assert_gates(evaluate(self.graph, self.golden), self.golden["thresholds"])

    def test_missing_relationship_is_a_hard_failure(self) -> None:
        self.graph["relationships"].pop()
        with self.assertRaisesRegex(ValueError, "relationship_recall"):
            assert_gates(evaluate(self.graph, self.golden), self.golden["thresholds"])

    def test_unexpected_provenance_valid_claim_is_a_hard_failure(self) -> None:
        unexpected = json.loads(json.dumps(self.graph["claims"][0]))
        unexpected["id"] = "claim-unreviewed"
        self.graph["claims"].append(unexpected)
        with self.assertRaisesRegex(ValueError, "claim_precision|unsupported_claims"):
            assert_gates(evaluate(self.graph, self.golden), self.golden["thresholds"])


if __name__ == "__main__":
    unittest.main()
