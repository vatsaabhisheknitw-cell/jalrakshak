"""Parse and validate uploaded ETP monitoring files (CSV/Excel)."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ["date", "ph"]
OPTIONAL_COLUMNS = [
    "bod_mg_l", "cod_mg_l", "tss_mg_l", "oil_grease_mg_l", "tds_mg_l",
    "ammoniacal_nitrogen_mg_l", "temperature_c", "flow_intake_kld",
    "flow_discharge_kld", "flow_recycled_kld", "lab_name", "operator_name",
    "sample_point",
]


def parse_upload(file_path: str) -> dict:
    """Parse a CSV/Excel upload; return validated DataFrame + diagnostics.

    Returns {"success": False, "error": ...} on hard failures, or
    {"success": True, "data": df, ...warnings...} on success.
    """
    try:
        if str(file_path).lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:  # noqa: BLE001 - surface parse errors to the user
        return {"success": False, "error": f"Could not read file: {e}"}

    # Normalize column names: strip, lowercase, spaces -> underscores
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return {"success": False, "error": f"Missing required columns: {missing}"}

    # Parse dates (accept mixed formats, prefer day-first for Indian data)
    try:
        df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True)
    except Exception as e:  # noqa: BLE001
        return {"success": False, "error": f"Could not parse 'date' column: {e}"}

    warnings: list[str] = []

    # Sanity checks
    if "ph" in df.columns:
        bad_ph = df[(df["ph"] < 0) | (df["ph"] > 14)]
        if len(bad_ph):
            warnings.append(f"{len(bad_ph)} row(s) have invalid pH (must be 0-14)")

    if "temperature_c" in df.columns:
        bad_temp = df[df["temperature_c"] > 100]
        if len(bad_temp):
            warnings.append(f"{len(bad_temp)} row(s) have unrealistic temperature >100 C")

    # Null checks on required columns
    for col, count in df[REQUIRED_COLUMNS].isnull().sum().items():
        if count > 0:
            warnings.append(f"{count} null value(s) in required column '{col}'")

    df = df.sort_values("date").reset_index(drop=True)

    return {
        "success": True,
        "data": df,
        "row_count": len(df),
        "date_range": f"{df['date'].min().date()} to {df['date'].max().date()}",
        "columns_found": list(df.columns),
        "warnings": warnings,
    }
