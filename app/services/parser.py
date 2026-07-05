"""Parse and validate uploaded ETP monitoring files (CSV/Excel)."""
from __future__ import annotations

import pandas as pd

from app.services.dates import fmt_date

REQUIRED_COLUMNS = ["date", "ph"]
OPTIONAL_COLUMNS = [
    "bod_mg_l", "cod_mg_l", "tss_mg_l", "oil_grease_mg_l", "tds_mg_l",
    "ammoniacal_nitrogen_mg_l", "temperature_c", "flow_intake_kld",
    "flow_discharge_kld", "flow_recycled_kld", "lab_name", "operator_name",
    "sample_point",
]

# Canonical columns that should be numeric (coerced; bad values -> NaN, skipped)
NUMERIC_COLUMNS = [
    "ph", "bod_mg_l", "cod_mg_l", "tss_mg_l", "oil_grease_mg_l", "tds_mg_l",
    "ammoniacal_nitrogen_mg_l", "temperature_c", "flow_intake_kld",
    "flow_discharge_kld", "flow_recycled_kld",
]


def read_file(file_path: str) -> pd.DataFrame:
    """Read a CSV/Excel with its ORIGINAL column names (for the mapping UI)."""
    if str(file_path).lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def finalize(df: pd.DataFrame) -> dict:
    """Validate + clean a DataFrame whose columns are already the canonical names
    (after column mapping). Coerces numerics so real-world junk (e.g. 'BDL',
    'Below Detection Limit', blanks) becomes NaN and is skipped, not crashed on."""
    df = df.copy()
    if "date" not in df.columns:
        return {"success": False, "error": "Please map the Date column."}
    if "ph" not in df.columns:
        return {"success": False, "error": "Please map the pH column."}

    warnings: list[str] = []

    df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True, errors="coerce")
    bad_dates = int(df["date"].isna().sum())
    if bad_dates:
        warnings.append(f"{bad_dates} row(s) had unreadable dates and were skipped.")
    df = df[df["date"].notna()]

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            before = int(df[col].notna().sum())
            df[col] = pd.to_numeric(df[col], errors="coerce")
            lost = before - int(df[col].notna().sum())
            if lost:
                warnings.append(f"{lost} non-numeric value(s) in '{col}' ignored (e.g. 'BDL').")

    if "ph" in df.columns:
        bad_ph = df[(df["ph"] < 0) | (df["ph"] > 14)]
        if len(bad_ph):
            warnings.append(f"{len(bad_ph)} row(s) have pH outside 0-14.")

    if df.empty:
        return {"success": False, "error": "No valid rows remained after cleaning."}

    df = df.sort_values("date").reset_index(drop=True)
    return {
        "success": True,
        "data": df,
        "row_count": len(df),
        "date_range": f"{fmt_date(df['date'].min())} to {fmt_date(df['date'].max())}",
        "period_start": str(df["date"].min().date()),  # ISO, for storage/sorting
        "period_end": str(df["date"].max().date()),
        "warnings": warnings,
    }


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
        "date_range": f"{fmt_date(df['date'].min())} to {fmt_date(df['date'].max())}",
        "columns_found": list(df.columns),
        "warnings": warnings,
    }
