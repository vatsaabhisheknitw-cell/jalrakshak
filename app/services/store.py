"""Persistence layer over the SQLite schema (app/database.py).

Single-org for now (no auth yet) — everything hangs off a default org. Callers
should treat every function as best-effort: on any DB error they return a safe
empty value rather than raising, so persistence can never break the compliance
flow (important because Streamlit Cloud's disk is ephemeral).
"""
from __future__ import annotations

import json

import pandas as pd

from app.config import PARAM_MAP
from app.database import get_connection, init_db

DEFAULT_ORG = 1


def _ensure_org(conn) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO orgs (id, name, plan) VALUES (?, 'Default', 'basic')",
        (DEFAULT_ORG,),
    )


def bootstrap() -> bool:
    """Create tables + default org. Returns True if the DB is usable."""
    try:
        init_db()
        conn = get_connection()
        try:
            _ensure_org(conn)
            conn.commit()
        finally:
            conn.close()
        return True
    except Exception:  # noqa: BLE001
        return False


def upsert_factory(f: dict):
    """Insert or update a factory by name (within the default org). Returns id or None."""
    try:
        conn = get_connection()
        try:
            _ensure_org(conn)
            row = conn.execute(
                "SELECT id FROM factories WHERE org_id=? AND name=?",
                (DEFAULT_ORG, f["name"]),
            ).fetchone()
            if row:
                fid = row["id"]
                conn.execute(
                    "UPDATE factories SET industry_type=?, cpcb_category=?, "
                    "discharge_destination=?, cto_number=? WHERE id=?",
                    (f["industry_type"], f["cpcb_category"],
                     f["discharge_destination"], f.get("cto_number"), fid),
                )
            else:
                cur = conn.execute(
                    "INSERT INTO factories (org_id, name, industry_type, cpcb_category, "
                    "discharge_destination, state, district, cto_number) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (DEFAULT_ORG, f["name"], f["industry_type"], f["cpcb_category"],
                     f["discharge_destination"], f.get("state", "-"),
                     f.get("district", "-"), f.get("cto_number")),
                )
                fid = cur.lastrowid
            conn.commit()
            return fid
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        return None


def list_factories() -> list:
    try:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT id, name, industry_type, cpcb_category, discharge_destination, "
                "cto_number FROM factories WHERE org_id=? ORDER BY name", (DEFAULT_ORG,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        return []


def save_mapping(factory_id, mapping: dict) -> None:
    if not factory_id:
        return
    try:
        conn = get_connection()
        try:
            conn.execute("DELETE FROM column_mappings WHERE factory_id=?", (factory_id,))
            conn.execute(
                "INSERT INTO column_mappings (factory_id, mapping_json) VALUES (?, ?)",
                (factory_id, json.dumps(mapping)),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        pass


def get_mapping(factory_id) -> dict:
    if not factory_id:
        return {}
    try:
        conn = get_connection()
        try:
            r = conn.execute(
                "SELECT mapping_json FROM column_mappings WHERE factory_id=? "
                "ORDER BY updated_at DESC LIMIT 1", (factory_id,),
            ).fetchone()
            return json.loads(r["mapping_json"]) if r else {}
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        return {}


def save_readings(factory_id, df: pd.DataFrame) -> int:
    """Persist mapped readings (long format). Idempotent via ux_readings index."""
    if not factory_id:
        return 0
    n = 0
    try:
        conn = get_connection()
        try:
            for _, row in df.iterrows():
                date = str(pd.to_datetime(row["date"]).date())
                sp = str(row["sample_point"]) if "sample_point" in df.columns and pd.notna(
                    row.get("sample_point")) else "etp_outlet"
                for csv_col, key in PARAM_MAP.items():
                    if csv_col in df.columns and pd.notna(row.get(csv_col)):
                        conn.execute(
                            "INSERT OR IGNORE INTO readings "
                            "(factory_id, reading_date, parameter, value, unit, sample_point) "
                            "VALUES (?,?,?,?,?,?)",
                            (factory_id, date, key, float(row[csv_col]), "mg/L", sp),
                        )
                        n += conn.total_changes and 1 or 0
            conn.commit()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        return 0
    return n


def save_report(factory_id, period: str, result: dict, pdf_path: str, ai: dict) -> None:
    if not factory_id:
        return
    parts = period.split(" to ")
    start, end = parts[0], parts[-1]
    try:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO reports (factory_id, report_type, period_start, period_end, "
                "total_readings, total_violations, compliance_score, ai_summary, pdf_path) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (factory_id, "adhoc", start, end, result["total_readings"],
                 result["violation_count"], result["compliance_score"],
                 ai.get("summary", ""), pdf_path),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        pass


def factory_history(factory_id):
    """Return (total_readings, [recent report dicts])."""
    if not factory_id:
        return 0, []
    try:
        conn = get_connection()
        try:
            rc = conn.execute(
                "SELECT COUNT(*) AS c FROM readings WHERE factory_id=?", (factory_id,),
            ).fetchone()["c"]
            reports = conn.execute(
                "SELECT created_at, period_start, period_end, compliance_score, "
                "total_violations FROM reports WHERE factory_id=? "
                "ORDER BY created_at DESC LIMIT 10", (factory_id,),
            ).fetchall()
            return rc, [dict(r) for r in reports]
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        return 0, []
