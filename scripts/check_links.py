"""Check repository-relative Markdown links without requiring a network."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).parents[1]
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def main() -> int:
    missing: list[str] = []
    for path in ROOT.rglob("*.md"):
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            clean = target.strip("<>").split("#", 1)[0]
            if not clean or "://" in clean or clean.startswith("mailto:"):
                continue
            resolved = (path.parent / unquote(clean)).resolve()
            if not resolved.is_relative_to(ROOT.resolve()) or not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    if missing:
        print("Broken local links:\n" + "\n".join(missing))
        return 1
    print("Local Markdown links passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
