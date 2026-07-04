"""Central config: paths, model, and reusable constants for JalRakshak."""
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CPCB_LIMITS_PATH = DATA_DIR / "cpcb_limits.json"
SECTOR_LIMITS_PATH = DATA_DIR / "sector_limits.json"
SAMPLE_DATA_PATH = DATA_DIR / "sample_data.csv"
DB_PATH = BASE_DIR / "jalrakshak.db"
REPORTS_DIR = BASE_DIR / "generated_reports"

# --- AI ---
# Current Sonnet. Do NOT downgrade to claude-sonnet-4-6 (retired id).
CLAUDE_MODEL = "claude-sonnet-5"

# --- Compliance thresholds ---
WARNING_FRACTION = 0.8      # "lower is better" params warn at 80% of the max limit
RANGE_WARN_FRACTION = 0.05  # range params (pH) warn within 5% of the span of a bound

# CSV column -> internal limit key
PARAM_MAP = {
    "ph": "ph",
    "bod_mg_l": "bod",
    "cod_mg_l": "cod",
    "tss_mg_l": "tss",
    "oil_grease_mg_l": "oil_grease",
    "tds_mg_l": "tds",
    "ammoniacal_nitrogen_mg_l": "ammoniacal_nitrogen",
    "temperature_c": "temperature",
}

# Human-friendly labels for reports/UI
PARAM_LABELS = {
    "ph": "pH",
    "bod": "BOD",
    "cod": "COD",
    "tss": "TSS",
    "oil_grease": "Oil & Grease",
    "tds": "TDS",
    "ammoniacal_nitrogen": "Ammoniacal N",
    "temperature": "Temperature",
}
