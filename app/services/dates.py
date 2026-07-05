"""Date/time formatting helpers — dd-mmm-yyyy everywhere, timestamps in IST.

SQLite CURRENT_TIMESTAMP is stored in UTC; the app serves Indian users, so all
displayed timestamps are converted to IST (UTC+5:30).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

IST = timezone(timedelta(hours=5, minutes=30))
DATE_FMT = "%d-%b-%Y"          # e.g. 05-Jul-2026
DATETIME_FMT = "%d-%b-%Y %H:%M"  # e.g. 05-Jul-2026 20:55


def fmt_date(value) -> str:
    """Format a date/datetime/ISO-string as dd-mmm-yyyy. Blank on missing."""
    if value is None or value == "" or (isinstance(value, float) and pd.isna(value)):
        return ""
    try:
        return pd.to_datetime(value).strftime(DATE_FMT)
    except Exception:  # noqa: BLE001
        return str(value)


def now_ist_str() -> str:
    """Current IST timestamp as 'dd-mmm-yyyy HH:MM'."""
    return datetime.now(IST).strftime(DATETIME_FMT)


def fmt_datetime_ist(value) -> str:
    """Format a stored (naive-UTC) timestamp as IST 'dd-mmm-yyyy HH:MM'."""
    if not value:
        return ""
    try:
        dt = pd.to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.tz_localize("UTC")
        return dt.tz_convert(IST).strftime(DATETIME_FMT)
    except Exception:  # noqa: BLE001
        return str(value)
