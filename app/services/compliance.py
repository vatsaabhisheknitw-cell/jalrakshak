"""Check ETP readings against CPCB / factory-CTO limits.

Key correctness note (the bug the plan originally had):
  A flat "warn at 80% of max" rule is WRONG for *range* parameters like pH.
  pH sits in a band (5.5-9.0); 0.8 * 9.0 = 7.2, so a healthy pH of 7.3 would
  be flagged as a warning. Here, range params (those with a `min`) warn only
  when the value creeps toward *either* bound, while "lower is better" params
  (BOD, COD, TSS, ...) keep the 80%-of-max rule.
"""
from __future__ import annotations

import json

import pandas as pd

from app.config import (
    CPCB_LIMITS_PATH,
    PARAM_MAP,
    RANGE_WARN_FRACTION,
    SECTOR_LIMITS_PATH,
    WARNING_FRACTION,
)


def load_limits(discharge_destination: str, custom_limits: dict | None = None) -> dict:
    """Load CPCB limits for the destination, overlay factory-CTO overrides."""
    with open(CPCB_LIMITS_PATH, encoding="utf-8") as f:
        all_limits = json.load(f)

    limits = dict(all_limits.get(discharge_destination, all_limits["inland_surface_water"]))
    limits.pop("_note", None)

    if custom_limits:
        for param, values in custom_limits.items():
            limits[param] = values
    return limits


def load_sector_limits() -> dict:
    """All sector-specific effluent standards (data/sector_limits.json)."""
    with open(SECTOR_LIMITS_PATH, encoding="utf-8") as f:
        return json.load(f)


def sector_names() -> list:
    """Sector keys available as overrides (excludes metadata keys)."""
    return sorted(k for k in load_sector_limits() if not k.startswith("_"))


def sector_overrides(sector: str) -> dict:
    """Return {param: {min?, max, unit}} limits for a sector; drops _metadata."""
    data = load_sector_limits().get(sector, {})
    out = {}
    for key, val in data.items():
        if key.startswith("_"):
            continue
        if isinstance(val, dict) and ("max" in val or "min" in val):
            out[key] = val
    return out


def check_compliance(df: pd.DataFrame, limits: dict) -> dict:
    """Compare each reading against limits; return violations, warnings, score."""
    violations: list[dict] = []
    warnings: list[dict] = []

    for _, row in df.iterrows():
        for csv_col, key in PARAM_MAP.items():
            if csv_col not in df.columns or pd.isna(row.get(csv_col)):
                continue

            value = float(row[csv_col])
            limit = limits.get(key)
            if not limit:
                continue

            has_min = "min" in limit and limit["min"] is not None
            has_max = "max" in limit and limit["max"] is not None
            date = str(pd.to_datetime(row["date"]).date())
            unit = limit.get("unit", "")

            over_max = has_max and value > limit["max"]
            under_min = has_min and value < limit["min"]

            if over_max:
                violations.append({
                    "date": date, "parameter": key, "value": value,
                    "limit": limit["max"], "unit": unit, "severity": "critical",
                    "exceedance_pct": round(((value - limit["max"]) / limit["max"]) * 100, 1),
                })
            if under_min:
                violations.append({
                    "date": date, "parameter": key, "value": value,
                    "limit": limit["min"], "unit": unit, "severity": "critical",
                    "note": f"Below minimum {limit['min']}",
                })

            # Warning only if not already a violation this reading.
            if not (over_max or under_min):
                if has_min:
                    # RANGE parameter (e.g. pH): warn near either bound.
                    band = (limit["max"] - limit["min"]) * RANGE_WARN_FRACTION
                    if value >= limit["max"] - band or value <= limit["min"] + band:
                        warnings.append({
                            "date": date, "parameter": key, "value": value,
                            "min": limit["min"], "max": limit["max"], "unit": unit,
                            "severity": "warning", "note": "Approaching range bound",
                        })
                elif has_max and value > limit["max"] * WARNING_FRACTION:
                    warnings.append({
                        "date": date, "parameter": key, "value": value,
                        "limit": limit["max"], "unit": unit, "severity": "warning",
                        "usage_pct": round((value / limit["max"]) * 100, 1),
                    })

    checked_cols = [c for c in PARAM_MAP if c in df.columns]
    total_checks = len(df) * len(checked_cols)
    violation_count = len(violations)
    score = round(((total_checks - violation_count) / total_checks) * 100, 1) if total_checks else 100.0

    return {
        "compliance_score": score,
        "total_readings": len(df),
        "total_checks": total_checks,
        "parameters_checked": [PARAM_MAP[c] for c in checked_cols],
        "violations": violations,
        "warnings": warnings,
        "violation_count": violation_count,
        "warning_count": len(warnings),
    }


def parameter_summary(df: pd.DataFrame, limits: dict) -> list[dict]:
    """Per-parameter avg/min/max vs limit + status, for the report table."""
    rows: list[dict] = []
    for csv_col, key in PARAM_MAP.items():
        if csv_col not in df.columns:
            continue
        series = pd.to_numeric(df[csv_col], errors="coerce").dropna()
        if series.empty:
            continue
        limit = limits.get(key, {})
        lo, hi = limit.get("min"), limit.get("max")

        breached = False
        warned = False
        if hi is not None:
            breached = bool((series > hi).any())
            warned = bool((series > hi * WARNING_FRACTION).any()) if lo is None else warned
        if lo is not None:
            breached = breached or bool((series < lo).any())

        status = "violation" if breached else ("warning" if warned else "ok")
        rows.append({
            "parameter": key,
            "avg": round(series.mean(), 2),
            "min": round(series.min(), 2),
            "max": round(series.max(), 2),
            "limit": (f"{lo}-{hi}" if lo is not None else f"<= {hi}") if hi is not None else "-",
            "unit": limit.get("unit", ""),
            "status": status,
        })
    return rows
