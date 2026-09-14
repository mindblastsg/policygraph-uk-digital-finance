"""Assemble the dependency-free PolicyGraph research alpha for GitHub Pages."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(output: Path) -> None:
    """Copy only the public client and bounded graph into a clean site directory."""
    output = output.resolve()
    if output == ROOT or ROOT not in output.parents:
        raise ValueError("Pages output must be a child of the repository")
    if output.exists():
        shutil.rmtree(output)
    (output / "assets").mkdir(parents=True)
    (output / "data").mkdir()

    graph_source = ROOT / "data" / "sample" / "graph.json"
    graph = json.loads(graph_source.read_text(encoding="utf-8"))
    required = {"sources", "documents", "claims", "entities", "events", "relationships"}
    if not isinstance(graph, dict) or not required.issubset(graph):
        raise ValueError("The committed graph is not a publishable PolicyGraph payload")

    index_source = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    marker = '<meta charset="utf-8">'
    if marker not in index_source:
        raise ValueError("The application index is missing its expected charset marker")
    static_index = index_source.replace(
        marker,
        f'{marker}\n  <meta name="policygraph-data-mode" content="static">',
        1,
    )
    (output / "index.html").write_text(static_index, encoding="utf-8")
    for asset in (ROOT / "app" / "assets").iterdir():
        if asset.is_file():
            shutil.copy2(asset, output / "assets" / asset.name)
    shutil.copy2(graph_source, output / "data" / "graph.json")
    (output / ".nojekyll").write_text("", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    build(args.output)
    print(f"GitHub Pages site assembled at {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
