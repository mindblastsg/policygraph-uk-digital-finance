"""Deterministic canonical names and stable identifiers."""

import re
import unicodedata

ALIASES = {
    "fca": "Financial Conduct Authority",
    "hm treasury": "HM Treasury",
    "hmt": "HM Treasury",
    "bank of england": "Bank of England",
    "dss": "Digital Securities Sandbox",
    "digital securities sandbox": "Digital Securities Sandbox",
    "dlt": "Distributed Ledger Technology",
}


def canonical_name(value: str) -> str:
    clean = " ".join(value.strip().split())
    return ALIASES.get(clean.casefold(), clean)


def stable_id(value: str) -> str:
    normal = unicodedata.normalize("NFKD", canonical_name(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", normal.casefold()).strip("-")
