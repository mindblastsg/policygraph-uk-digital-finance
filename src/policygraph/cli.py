"""PolicyGraph command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import build_sample


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="policygraph")
    commands = root.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-sample", help="rebuild the committed offline sample graph")
    build.add_argument("--registry", type=Path, default=Path("data/registry/sources.json"))
    build.add_argument("--fixtures", type=Path, default=Path("data/sample/raw"))
    build.add_argument("--output", type=Path, default=Path("data/sample/graph.json"))
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "build-sample":
        build_sample(args.registry, args.fixtures, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
