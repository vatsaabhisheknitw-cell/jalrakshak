"""Generate a compliance report PDF with ReportLab (Python-native, no browser)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)

from app.config import PARAM_LABELS, REPORTS_DIR
from app.services.dates import now_ist_str

_STATUS_COLOR = {
    "ok": colors.HexColor("#1a7f37"),
    "warning": colors.HexColor("#9a6700"),
    "violation": colors.HexColor("#cf222e"),
}


def _score_color(score: float):
    if score >= 98:
        return colors.HexColor("#1a7f37")
    if score >= 90:
        return colors.HexColor("#9a6700")
    return colors.HexColor("#cf222e")


def generate_report_pdf(
    factory: dict,
    period: str,
    compliance_result: dict,
    param_summary: list[dict],
    ai: dict,
    out_dir: Path = REPORTS_DIR,
) -> str:
    """Build the PDF and return its path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in factory.get("name", "factory"))
    path = out_dir / f"{safe_name}_{stamp}.pdf"

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=colors.grey))
    story = []

    # --- Cover ---
    story.append(Paragraph("JalRakshak Compliance Report", styles["Title"]))
    story.append(Spacer(1, 6 * mm))
    meta = [
        ["Factory", factory.get("name", "-")],
        ["Industry / Category", f"{factory.get('industry_type', '-')} / {factory.get('cpcb_category', '-')}"],
        ["CTO Number", factory.get("cto_number", "-")],
        ["Discharge", factory.get("discharge_destination", "-")],
        ["Reporting Period", period],
        ["Generated", now_ist_str()],
    ]
    t = Table(meta, colWidths=[45 * mm, 110 * mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8 * mm))

    score = compliance_result["compliance_score"]
    score_style = ParagraphStyle(
        "Score", parent=styles["Title"], fontSize=40, textColor=_score_color(score))
    story.append(Paragraph(f"{score}%", score_style))
    story.append(Paragraph("Compliance Score", styles["Normal"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        f"{compliance_result['violation_count']} violation(s) &nbsp; | &nbsp; "
        f"{compliance_result['warning_count']} warning(s) &nbsp; | &nbsp; "
        f"{compliance_result['total_readings']} reading(s)", styles["Normal"]))
    story.append(Spacer(1, 8 * mm))

    # --- Executive summary ---
    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    story.append(Paragraph(ai.get("summary", "-"), styles["Normal"]))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f"<b>Risk level:</b> {ai.get('risk_level', 'unknown')} — {ai.get('risk_explanation', '')}",
        styles["Normal"]))
    story.append(Spacer(1, 6 * mm))

    # --- Parameter table ---
    story.append(Paragraph("Parameter-wise Analysis", styles["Heading2"]))
    head = ["Parameter", "Avg", "Min", "Max", "Limit", "Unit", "Status"]
    data = [head]
    status_rows = []
    for i, r in enumerate(param_summary, start=1):
        data.append([
            PARAM_LABELS.get(r["parameter"], r["parameter"]),
            r["avg"], r["min"], r["max"], r["limit"], r["unit"], r["status"].upper(),
        ])
        status_rows.append((i, r["status"]))
    pt = Table(data, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f4c81")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d7de")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
    ]
    for i, st in status_rows:
        style.append(("TEXTCOLOR", (6, i), (6, i), _STATUS_COLOR.get(st, colors.black)))
    pt.setStyle(TableStyle(style))
    story.append(pt)
    story.append(Spacer(1, 6 * mm))

    # --- Violation log ---
    story.append(Paragraph("Violation Log", styles["Heading2"]))
    v = compliance_result["violations"]
    if not v:
        story.append(Paragraph("No violations in this period.", styles["Normal"]))
    else:
        vdata = [["Date", "Parameter", "Value", "Limit", "Exceedance %"]]
        for row in sorted(v, key=lambda r: r.get("exceedance_pct", 0), reverse=True)[:40]:
            vdata.append([
                row["date"], PARAM_LABELS.get(row["parameter"], row["parameter"]),
                row["value"], row["limit"], row.get("exceedance_pct", row.get("note", "-")),
            ])
        vt = Table(vdata, repeatRows=1)
        vt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#cf222e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d7de")),
        ]))
        story.append(vt)
    story.append(Spacer(1, 6 * mm))

    # --- Recommendations ---
    story.append(Paragraph("Recommendations", styles["Heading2"]))
    for rec in ai.get("recommendations", []):
        story.append(Paragraph(f"• {rec}", styles["Normal"]))
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph(
        "Generated by JalRakshak | jalrakshak.in — This report is for internal "
        "compliance tracking. Official submissions must be signed by an authorized "
        "signatory.", styles["Small"]))

    SimpleDocTemplate(str(path), pagesize=A4,
                      leftMargin=18 * mm, rightMargin=18 * mm,
                      topMargin=16 * mm, bottomMargin=16 * mm).build(story)
    return str(path)
