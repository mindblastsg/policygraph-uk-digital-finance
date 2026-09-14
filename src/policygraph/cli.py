"""PolicyGraph command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .adapters import discover_adapters
from .pipeline import build_sample
from .schema import validation_errors


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="policygraph")
    commands = root.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-sample", help="rebuild the committed offline sample graph")
    build.add_argument("--registry", type=Path, default=Path("data/registry/sources.json"))
    build.add_argument("--fixtures", type=Path, default=Path("data/sample/raw"))
    build.add_argument("--output", type=Path, default=Path("data/sample/graph.json"))
    commands.add_parser("adapters", help="list installed adapter metadata").add_argument("action", choices=["list"])
    for command, schema in (("validate-registry", "source-registry"), ("validate-graph", "graph")):
        validate = commands.add_parser(command, help=f"validate a {schema} JSON file")
        validate.add_argument("path", type=Path)
    return root


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        if args.command == "build-sample":
            build_sample(args.registry, args.fixtures, args.output)
        elif args.command == "adapters":
            for item in discover_adapters():
                print(f"{item.name}\t{item.value}")
        elif args.command.startswith("validate-"):
            schema = "source-registry" if args.command == "validate-registry" else "graph"
            errors = validation_errors(json.loads(args.path.read_text(encoding="utf-8")), schema)
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print(f"valid {schema} schema")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, LookupError) as error:
        print(f"policygraph: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
