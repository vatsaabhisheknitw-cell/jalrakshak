"""End-to-end smoke test: parser -> compliance -> AI(fallback) -> PDF + DB init."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import SAMPLE_DATA_PATH
from app.services import parser, compliance
from app.services.ai_summary import generate_compliance_summary
from app.services.pdf_generator import generate_report_pdf
from app.database import init_db

factory = {
    "name": "Demo Pharma Pvt Ltd", "industry_type": "pharma",
    "cpcb_category": "red", "discharge_destination": "inland_surface_water",
    "cto_number": "APSPCB/CTO/2026/1234",
}

parsed = parser.parse_upload(str(SAMPLE_DATA_PATH))
assert parsed["success"], parsed
df = parsed["data"]
print("parsed rows:", parsed["row_count"], "|", parsed["date_range"])

limits = compliance.load_limits(factory["discharge_destination"])
result = compliance.check_compliance(df, limits)
psum = compliance.parameter_summary(df, limits)
print("score:", result["compliance_score"], "| violations:", result["violation_count"],
      "| warnings:", result["warning_count"])

# pH correctness: no pH VIOLATIONS (all in 5.5-9.0), but pH WARNINGS expected
# on the near-bound days (8.85 and 5.6). A healthy 7.x must NOT warn.
ph_viol = [v for v in result["violations"] if v["parameter"] == "ph"]
ph_warn = [w for w in result["warnings"] if w["parameter"] == "ph"]
print("pH violations:", len(ph_viol), "| pH warnings:", len(ph_warn),
      "on", [w["date"] for w in ph_warn])
assert len(ph_viol) == 0, "pH should have no violations in sample"
assert len(ph_warn) == 2, f"expected 2 pH near-bound warnings, got {len(ph_warn)}"

ai = generate_compliance_summary(factory["name"], result, parsed["date_range"])
print("ai risk:", ai["risk_level"])

pdf = generate_report_pdf(factory, parsed["date_range"], result, psum, ai)
print("pdf:", pdf, "exists:", Path(pdf).exists(), "bytes:", Path(pdf).stat().st_size)

init_db()
print("db initialized OK")
print("\nSMOKE TEST PASSED")
