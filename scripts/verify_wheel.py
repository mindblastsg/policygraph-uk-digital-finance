"""Assert the built wheel contains every runtime asset."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile


def main() -> int:
    version_match = re.search(
        r'^version = "([^"]+)"$', Path("pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE
    )
    if version_match is None:
        raise SystemExit("Could not read project version")
    wheel = Path("dist") / f"policygraph-{version_match.group(1)}-py3-none-any.whl"
    if not wheel.is_file():
        raise SystemExit(f"Current wheel does not exist: {wheel}")
    with ZipFile(wheel) as archive:
        names = set(archive.namelist())
    required_suffixes = {
        "share/policygraph/app/index.html",
        "share/policygraph/app/assets/app.js",
        "share/policygraph/app/assets/styles.css",
        "share/policygraph/app/assets/accessibility.css",
        "share/policygraph/data/sample/graph.json",
        "policygraph/py.typed",
        "policygraph/schemas/claim.schema.json",
        "policygraph/schemas/document.schema.json",
        "policygraph/schemas/evaluation.schema.json",
        "policygraph/schemas/graph.schema.json",
        "policygraph/schemas/source-registry.schema.json",
        f"policygraph-{version_match.group(1)}.dist-info/entry_points.txt",
    }
    missing = [suffix for suffix in required_suffixes if not any(name.endswith(suffix) for name in names)]
    if missing:
        raise SystemExit("Wheel is missing runtime files: " + ", ".join(missing))
    with ZipFile(wheel) as archive:
        entry_points = archive.read(f"policygraph-{version_match.group(1)}.dist-info/entry_points.txt").decode()
        if "policygraph.source_adapters" not in entry_points or "local_fixture" not in entry_points:
            raise SystemExit("Wheel is missing the source adapter entry point")
        metadata = archive.read(f"policygraph-{version_match.group(1)}.dist-info/METADATA").decode()
        if "Requires-Dist: jsonschema[format]" not in metadata:
            raise SystemExit("Wheel metadata is missing the JSON Schema runtime dependency")
        schema = archive.read("policygraph/schemas/source-registry.schema.json")
        if b'"$schema"' not in schema:
            raise SystemExit("Packaged schema is invalid")
    verify_root = Path(".verify-tmp")
    verify_root.mkdir(exist_ok=True)
    temp_root = Path(tempfile.mkdtemp(prefix="policygraph-wheel-", dir=verify_root)).resolve()
    try:
        subprocess.run([sys.executable, "-m", "venv", str(temp_root / "venv")], check=True)
        python = temp_root / "venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheel.resolve())],
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-I",
                "-c",
                "import policygraph, sys; from pathlib import Path; "
                "from policygraph.adapters import discover_adapters, load_adapter; "
                "from policygraph.schema import load_schema, validation_errors; "
                "from policygraph.api import app, load_graph, WEB_ROOT, DEFAULT_GRAPH_PATH; "
                "assert Path(policygraph.__file__).is_relative_to(sys.prefix); "
                "assert WEB_ROOT.is_relative_to(sys.prefix); "
                "assert DEFAULT_GRAPH_PATH.is_relative_to(sys.prefix); "
                "assert (WEB_ROOT / 'index.html').is_file(); "
                "assert (WEB_ROOT / 'assets/app.js').is_file(); "
                "assert not validation_errors(load_graph(), 'graph'); "
                "assert app.version == policygraph.__version__; "
                "assert policygraph.__version__; "
                "assert load_schema('source-registry')['$schema']; "
                "assert validation_errors({'schema_version': '1.0', 'sources': [], 'extra': True}, "
                "'source-registry'); "
                "assert any(item.name == 'local_fixture' for item in discover_adapters()); "
                "assert load_adapter('local_fixture').name == 'local_fixture'",
            ],
            check=True,
            cwd=temp_root,
        )
        example_dist = temp_root / "example-dist"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "build",
                "--no-isolation",
                "--wheel",
                "--outdir",
                str(example_dist),
                "examples/source-adapter",
            ],
            check=True,
        )
        example_wheel = next(example_dist.glob("*.whl"))
        subprocess.run([str(python), "-m", "pip", "install", "--no-deps", str(example_wheel)], check=True)
        subprocess.run(
            [
                str(python),
                "-I",
                "-c",
                "from datetime import date; "
                "from policygraph.adapters import load_adapter; "
                "from policygraph.models import Source, SourceKind, PolicyStatus; "
                "from policygraph.testing import assert_adapter_contract; "
                "adapter = load_adapter('example_regulator')(); "
                "source = Source('example', 'Example', 'Example', 'https://example.invalid/policy', "
                "SourceKind.WEB_PAGE, (), PolicyStatus.PROPOSAL, date(2026, 1, 1), content_path='sample.html'); "
                "assert_adapter_contract(adapter, source); "
                "assert 'Fixture-only evidence.' in adapter.extract(source, adapter.fetch(source)).text",
            ],
            check=True,
            cwd=temp_root,
        )
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        try:
            verify_root.rmdir()
        except OSError:
            pass
    print(f"Wheel archive, isolated API/runtime and installed adapter contract checks passed: {wheel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
