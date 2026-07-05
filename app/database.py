"""SQLite schema + connection for JalRakshak.

Multi-tenant from day one: every domain row is reachable from an `org` so a
consultant managing many factories can't see another org's data. Enforce
org scoping in every query (row-level isolation) — not just in the UI.
"""
import sqlite3
from pathlib import Path

from app.config import DB_PATH

SCHEMA = """
-- Tenancy: an org is a paying account (a single factory, or a consultant
-- managing many). plan drives feature gating.
CREATE TABLE IF NOT EXISTS orgs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    plan TEXT NOT NULL DEFAULT 'basic',  -- basic, pro, enterprise, consultant
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,  -- bcrypt/argon2; never store plaintext
    role TEXT NOT NULL DEFAULT 'member',  -- owner, admin, member
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES orgs(id)
);

CREATE TABLE IF NOT EXISTS factories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    industry_type TEXT NOT NULL,
    cpcb_category TEXT NOT NULL,
    discharge_destination TEXT NOT NULL,
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    cto_number TEXT,
    cto_expiry DATE,
    contact_name TEXT,
    contact_phone TEXT,
    contact_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES orgs(id)
);

CREATE TABLE IF NOT EXISTS factory_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    parameter TEXT NOT NULL,
    min_value REAL,
    max_value REAL NOT NULL,
    unit TEXT NOT NULL,
    source TEXT DEFAULT 'cpcb_general',
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    reading_date DATE NOT NULL,
    parameter TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    sample_point TEXT DEFAULT 'etp_outlet',
    lab_name TEXT,
    is_violation INTEGER DEFAULT 0,
    violation_severity TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

CREATE TABLE IF NOT EXISTS flow_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    reading_date DATE NOT NULL,
    water_intake_kld REAL,
    water_discharge_kld REAL,
    water_recycled_kld REAL,
    etp_chemical_consumption_kg REAL,
    etp_power_consumption_kwh REAL,
    operator_name TEXT,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    report_type TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_readings INTEGER,
    total_violations INTEGER,
    compliance_score REAL,
    ai_summary TEXT,
    ai_recommendations TEXT,
    pdf_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,
    parameter TEXT,
    current_value REAL,
    limit_value REAL,
    message TEXT NOT NULL,
    sent_via TEXT DEFAULT 'whatsapp',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

-- Remembered column mapping per factory (see services/column_mapping.py)
CREATE TABLE IF NOT EXISTS column_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    mapping_json TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

-- Idempotent reading history (repeat uploads of the same day don't duplicate)
CREATE UNIQUE INDEX IF NOT EXISTS ux_readings
    ON readings(factory_id, reading_date, parameter, sample_point);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    """Create all tables if they don't exist."""
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Initialized database at {DB_PATH}")
