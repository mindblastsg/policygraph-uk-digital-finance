"""Assert the built wheel contains every runtime asset."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile


def main() -> int:
    wheels = sorted(Path("dist").glob("*.whl"))
    if len(wheels) != 1:
        raise SystemExit(f"Expected one wheel in dist, found {len(wheels)}")
    with ZipFile(wheels[0]) as archive:
        names = set(archive.namelist())
    required_suffixes = {
        "share/policygraph/app/index.html",
        "share/policygraph/app/assets/app.js",
        "share/policygraph/app/assets/styles.css",
        "share/policygraph/app/assets/accessibility.css",
        "share/policygraph/data/sample/graph.json",
    }
    missing = [suffix for suffix in required_suffixes if not any(name.endswith(suffix) for name in names)]
    if missing:
        raise SystemExit("Wheel is missing runtime files: " + ", ".join(missing))
    print(f"Wheel runtime assets passed: {wheels[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
