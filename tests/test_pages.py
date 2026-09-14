from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_pages import ROOT, build


class PagesBuildTests(unittest.TestCase):
    def test_static_bundle_contains_safe_explorer_and_graph(self) -> None:
        temporary_root = ROOT / ".pytest-tmp"
        temporary_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            output = Path(directory) / "site"
            build(output)
            index = (output / "index.html").read_text(encoding="utf-8")
            script = (output / "assets" / "app.js").read_text(encoding="utf-8")
            graph = json.loads((output / "data" / "graph.json").read_text(encoding="utf-8"))

            self.assertIn('href="assets/styles.css"', index)
            self.assertIn('src="assets/app.js"', index)
            self.assertIn('class="brand" href="./"', index)
            self.assertIn('name="policygraph-data-mode" content="static"', index)
            self.assertIn("data/graph.json", script)
            self.assertIn("topicsFromGraph", script)
            self.assertIn("Project documentation", script)
            self.assertTrue(graph["sources"])
            self.assertTrue((output / ".nojekyll").exists())

    def test_builder_refuses_repository_root(self) -> None:
        with self.assertRaises(ValueError):
            build(ROOT)


if __name__ == "__main__":
    unittest.main()
