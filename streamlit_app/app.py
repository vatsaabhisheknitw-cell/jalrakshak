"""JalRakshak — Streamlit MVP.

Upload ETP data -> validate -> check compliance -> AI summary -> PDF report.
Calls the `app.services` modules directly (no FastAPI needed for the MVP).

Run:  streamlit run streamlit_app/app.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Make the project root importable when run via `streamlit run`
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.config import PARAM_LABELS, PARAM_MAP, SAMPLE_DATA_PATH
from app.services import column_mapping, compliance, parser
from app.services.ai_summary import generate_compliance_summary
from app.services.pdf_generator import generate_report_pdf

st.set_page_config(page_title="JalRakshak — Water Compliance", page_icon="💧", layout="wide")

# --- Sidebar: factory config ---
st.sidebar.title("💧 JalRakshak")
st.sidebar.caption("Water compliance for Indian industries")
GENERAL = "(General standards only)"


def _sector_label(key: str) -> str:
    return "General standards only" if key == GENERAL else key.replace("_", " ").title()


_sector_keys = [GENERAL] + compliance.sector_names()
_name = st.sidebar.text_input("Factory name", "Demo Pharma Pvt Ltd")
sector_choice = st.sidebar.selectbox(
    "Industry / sector", _sector_keys, format_func=_sector_label,
    help="Applies that sector's CPCB effluent standard on top of the general standards.")

# Auto-fill CPCB category from the selected sector (CPCB Jan-2025 classification).
# Keyed per sector so switching sector resets to that sector's category; still overridable.
_CATS = ["red", "orange", "green", "white", "blue"]
_sec_meta = {} if sector_choice == GENERAL else compliance.load_sector_limits().get(sector_choice, {})
_auto_cat = _sec_meta.get("cpcb_category", "red")
_cat_index = _CATS.index(_auto_cat) if _auto_cat in _CATS else 0

factory = {
    "name": _name,
    "industry_type": _sector_label(sector_choice),
    "cpcb_category": st.sidebar.selectbox(
        "CPCB category", _CATS, index=_cat_index, format_func=str.title,
        key=f"cat_{sector_choice}",
        help="Auto-set from the selected sector (CPCB classification, Jan 2025). Override if needed."),
    "discharge_destination": st.sidebar.selectbox(
        "Discharge to", ["inland_surface_water", "public_sewer"]),
    "cto_number": st.sidebar.text_input("CTO number", "APSPCB/CTO/2026/XXXX"),
}
if factory["cpcb_category"] == "red":
    st.sidebar.warning(
        "Red category: JalRakshak is a supplementary reporting layer, not a "
        "replacement for mandatory real-time OCEMS transmission.")

st.title("Compliance Analysis")

# --- Data source ---
col_a, col_b = st.columns([3, 1])
uploaded = col_a.file_uploader("Upload ETP data (CSV / Excel)", type=["csv", "xlsx", "xls"])
use_sample = col_b.button("Use sample data", use_container_width=True)

# Persist the chosen source in session_state — otherwise a later button click
# (e.g. "Generate report") reruns the script, the transient button flags reset,
# and the analysis vanishes before the generate branch runs.
if uploaded is not None:
    suffix = Path(uploaded.name).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getbuffer())
    tmp.close()
    st.session_state["source_path"] = tmp.name
    st.session_state.pop("pdf_path", None)  # invalidate any old report
elif use_sample:
    st.session_state["source_path"] = str(SAMPLE_DATA_PATH)
    st.session_state.pop("pdf_path", None)

source_path = st.session_state.get("source_path")
if source_path is None:
    st.info("Upload a file or click **Use sample data** to see a demo analysis.")
    st.stop()

# --- Read raw file + column mapping ---
try:
    raw = parser.read_file(source_path)
except Exception as e:  # noqa: BLE001
    st.error(f"Could not read file: {e}")
    st.stop()
raw_cols = list(raw.columns)
suggested = column_mapping.suggest_mapping(raw_cols)
_sig = abs(hash(tuple(raw_cols)))  # fresh mapping widgets when the file's columns change

with st.expander("① Map your columns  —  auto-detected, confirm or correct", expanded=True):
    st.caption("Your lab sheet can use any column names/order. Match each parameter "
               "to a column in your file (or leave as *not in file*). Date & pH are required.")
    mapping = {}
    _ui = st.columns(3)
    for _i, (field, label, required) in enumerate(column_mapping.CANONICAL_FIELDS):
        options = ["(not in file)"] + raw_cols
        default = suggested.get(field)
        idx = options.index(default) if default in options else 0
        sel = _ui[_i % 3].selectbox(
            f"{label}{' *' if required else ''}", options, index=idx,
            key=f"map_{_sig}_{field}")
        if sel != "(not in file)":
            mapping[field] = sel
    st.caption(f"Auto-detected {len(suggested)} of {len(raw_cols)} columns.")

_missing = [lbl for f, lbl, req in column_mapping.CANONICAL_FIELDS if req and f not in mapping]
if _missing:
    st.warning(f"Map the required field(s) to continue: **{', '.join(_missing)}**")
    st.stop()

# --- Validate + clean the mapped data ---
parsed = parser.finalize(column_mapping.apply_mapping(raw, mapping))
if not parsed["success"]:
    st.error(parsed["error"])
    st.stop()

df = parsed["data"]
for w in parsed["warnings"]:
    st.warning(w)
st.caption(f"Parsed {parsed['row_count']} rows · {parsed['date_range']} · "
           f"{len(mapping)} column(s) mapped")

# --- Compliance ---
overrides = {} if sector_choice == GENERAL else compliance.sector_overrides(sector_choice)
limits = compliance.load_limits(factory["discharge_destination"], overrides or None)
result = compliance.check_compliance(df, limits)
param_summary = compliance.parameter_summary(df, limits)

if overrides:
    _sec = compliance.load_sector_limits().get(sector_choice, {})
    st.caption(f"Applying **{_sector_label(sector_choice)}** sector limits over CPCB "
               f"general standards · source: {_sec.get('_source', '—')}")
    if _sec.get("_note"):
        st.info(_sec["_note"])
else:
    st.caption("Applying **CPCB general standards** (no sector selected).")
period = parsed["date_range"]

# --- Scoreboard ---
c1, c2, c3, c4 = st.columns(4)
score = result["compliance_score"]
c1.metric("Compliance score", f"{score}%")
c2.metric("Violations", result["violation_count"])
c3.metric("Warnings", result["warning_count"])
c4.metric("Readings", result["total_readings"])

if score >= 98:
    st.success("Strong compliance for this period.")
elif score >= 90:
    st.warning("Mostly compliant — some parameters need attention.")
else:
    st.error("Significant violations — corrective action required.")

# --- Parameter table ---
st.subheader("Parameter-wise analysis")
ps_df = pd.DataFrame(param_summary)
if not ps_df.empty:
    ps_df["parameter"] = ps_df["parameter"].map(lambda k: PARAM_LABELS.get(k, k))
    st.dataframe(ps_df, use_container_width=True, hide_index=True)

# --- Trend charts with limit lines ---
st.subheader("Trends")
plot_cols = [c for c in PARAM_MAP if c in df.columns]
chart_cols = st.columns(2)
for i, csv_col in enumerate(plot_cols):
    key = PARAM_MAP[csv_col]
    limit = limits.get(key, {})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df[csv_col], mode="lines+markers",
                             name=PARAM_LABELS.get(key, key)))
    if limit.get("max") is not None:
        fig.add_hline(y=limit["max"], line_dash="dash", line_color="red",
                      annotation_text="max limit")
    if limit.get("min") is not None:
        fig.add_hline(y=limit["min"], line_dash="dash", line_color="orange",
                      annotation_text="min limit")
    fig.update_layout(title=PARAM_LABELS.get(key, key), height=280,
                      margin=dict(l=10, r=10, t=40, b=10))
    chart_cols[i % 2].plotly_chart(fig, use_container_width=True)

# --- Violations ---
if result["violations"]:
    st.subheader("Violation log")
    st.dataframe(pd.DataFrame(result["violations"]), use_container_width=True, hide_index=True)

# --- AI summary + PDF ---
st.subheader("AI summary & report")
if st.button("Generate AI summary + PDF report", type="primary"):
    with st.spinner("Analyzing..."):
        ai = generate_compliance_summary(factory["name"], result, period)
        pdf_path = generate_report_pdf(factory, period, result, param_summary, ai)
    # Stash results so the download button survives the rerun a download click triggers.
    st.session_state["ai"] = ai
    st.session_state["pdf_path"] = pdf_path

# Render the last generated report (persists across reruns until data changes).
if st.session_state.get("pdf_path") and Path(st.session_state["pdf_path"]).exists():
    ai = st.session_state["ai"]
    st.write(f"**Risk level:** {ai.get('risk_level', 'unknown')}")
    st.write(ai.get("summary", ""))
    if ai.get("recommendations"):
        st.markdown("**Recommendations**")
        for rec in ai["recommendations"]:
            st.markdown(f"- {rec}")
    with open(st.session_state["pdf_path"], "rb") as f:
        st.download_button("⬇️ Download PDF report", f.read(),
                           file_name=Path(st.session_state["pdf_path"]).name,
                           mime="application/pdf")
