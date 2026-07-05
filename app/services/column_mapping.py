"""Deterministic column mapping for arbitrary lab sheets.

Real ETP data is never uniform (every lab/state names columns differently), so we
never assume a fixed header. Instead: read whatever columns the file has, SUGGEST a
mapping to our canonical fields via an alias table, let the user confirm/correct it
(in the UI), then apply the confirmed mapping deterministically. Human-confirmed +
reproducible = safe for compliance.
"""
from __future__ import annotations

import re

import pandas as pd

# (canonical_field, display_label, required) — canonical names match what the
# parser/compliance layers expect (PARAM_MAP keys), so no downstream changes.
CANONICAL_FIELDS = [
    ("date", "Date", True),
    ("ph", "pH", True),
    ("bod_mg_l", "BOD (mg/L)", False),
    ("cod_mg_l", "COD (mg/L)", False),
    ("tss_mg_l", "TSS / Suspended Solids (mg/L)", False),
    ("oil_grease_mg_l", "Oil & Grease (mg/L)", False),
    ("tds_mg_l", "TDS (mg/L)", False),
    ("ammoniacal_nitrogen_mg_l", "Ammoniacal N (mg/L)", False),
    ("temperature_c", "Temperature (°C)", False),
    ("sample_point", "Sample point", False),
    ("lab_name", "Lab name", False),
    ("operator_name", "Operator", False),
]

# Alias tokens (normalized form) matched as whole tokens against each column.
ALIASES = {
    "date": ["date", "sampling date", "sample date", "test date",
             "date of sampling", "monitoring date", "dt"],
    "ph": ["ph", "ph value"],
    "bod_mg_l": ["bod", "bod3", "bod 3", "bod5", "b o d",
                 "biochemical oxygen demand", "bio chemical oxygen demand"],
    "cod_mg_l": ["cod", "c o d", "chemical oxygen demand"],
    "tss_mg_l": ["tss", "suspended solids", "total suspended solids",
                 "suspended solid", "ss"],
    "oil_grease_mg_l": ["oil and grease", "oil grease", "o g", "grease", "oil"],
    "tds_mg_l": ["tds", "dissolved solids", "total dissolved solids"],
    "ammoniacal_nitrogen_mg_l": ["ammoniacal nitrogen", "ammonical nitrogen",
                                 "ammoniacal n", "ammonia as n", "nh3 n", "nh4 n",
                                 "ammonia", "ammoniacal"],
    "temperature_c": ["temperature", "temp", "temp c"],
    "sample_point": ["sample point", "sampling point", "sampling location",
                     "location", "source"],
    "lab_name": ["lab name", "laboratory", "lab", "tested by"],
    "operator_name": ["operator name", "operator", "analyst", "sampled by"],
}

# Priority order for greedy assignment (specific/leftmost first)
_ORDER = [f for f, _, _ in CANONICAL_FIELDS]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def _token_match(col_norm: str, alias: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])",
                     col_norm) is not None


def suggest_mapping(raw_columns: list) -> dict:
    """Best-effort {canonical_field: raw_column}. Correctness is guaranteed by the
    user confirming this in the UI, so 'good enough' is fine here."""
    norms = {c: _norm(c) for c in raw_columns}
    taken: set = set()
    mapping: dict = {}
    for field in _ORDER:
        aliases = sorted(ALIASES.get(field, []), key=len, reverse=True)
        for alias in aliases:
            hit = next((c for c in raw_columns
                        if c not in taken and _token_match(norms[c], alias)), None)
            if hit:
                mapping[field] = hit
                taken.add(hit)
                break
    return mapping


def apply_mapping(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Rename the user's columns to canonical names and keep only those."""
    rename = {raw: field for field, raw in mapping.items()}
    out = df.rename(columns=rename)
    keep = [f for f in mapping if f in out.columns]
    return out[keep].copy()
