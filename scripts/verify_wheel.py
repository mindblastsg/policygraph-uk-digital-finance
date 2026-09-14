"""Assert the built wheel contains every runtime asset."""

from __future__ import annotations

import os
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
    temp_root = Path(tempfile.mkdtemp(prefix="policygraph-wheel-", dir=verify_root))
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(temp_root), str(wheel.resolve())],
            check=True,
        )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(temp_root.resolve())
        subprocess.run(
            [
                sys.executable,
                "-c",
                "import policygraph; "
                "from policygraph.adapters import discover_adapters, load_adapter; "
                "from policygraph.schema import load_schema, validation_errors; "
                "assert policygraph.__version__; "
                "assert load_schema('source-registry')['$schema']; "
                "assert validation_errors({'schema_version': '1.0', 'sources': [], 'extra': True}, "
                "'source-registry'); "
                "assert any(item.name == 'local_fixture' for item in discover_adapters()); "
                "assert load_adapter('local_fixture').name == 'local_fixture'",
            ],
            check=True,
            cwd=temp_root,
            env=environment,
        )
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        try:
            verify_root.rmdir()
        except OSError:
            pass
    print(f"Wheel archive and isolated runtime smoke tests passed: {wheel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
