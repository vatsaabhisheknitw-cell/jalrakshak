# JalRakshak — Water Compliance SaaS for Indian Industries
## Complete Technical Build Plan

---

## Product Name Suggestion: **JalRakshak** (जलरक्षक — Water Protector)

---

## What You're Building

A web app where factory ETP operators upload their daily effluent monitoring data (CSV/Excel), and the system:
1. Validates data against CPCB 2026 discharge limits
2. Flags violations and anomalies
3. Generates a compliance report PDF (ready for SPCB submission)
4. Sends WhatsApp alerts when parameters approach breach thresholds
5. Uses Claude AI to generate plain-language summaries and recommendations

---

## Regulatory Context (What You Must Know)

### Key Laws
- **Water (Prevention & Control of Pollution) Act, 1974** — primary legislation
- **Environment (Protection) Act, 1986** — sets discharge standards
- **EP Rules, 1986 — Rule 14, Form V** — annual environmental statement every industry must submit

### Key Bodies
- **CPCB** — sets national discharge limits
- **SPCB (e.g., APSPCB)** — enforces locally, issues CTE/CTO consents
- **APSPCB portal** — https://apocmms.nic.in/ (AP-specific)

### Industry Categories (CPCB classification)
- **Red (61 sectors)** — highly polluting, OCEMS mandatory, strictest limits
- **Orange (90 sectors)** — moderate pollution, regular monitoring
- **Green (65 sectors)** — low pollution, lighter requirements
- **White (38 sectors)** — non-polluting, minimal compliance

### CPCB General Standards — Discharge of Environmental Pollutants (EP Rules 1986, Schedule VI)

> ✅ **Verified 2026-07** against the official CPCB general standards ([cpcb.nic.in/generalstandards.pdf](https://cpcb.nic.in/generalstandards.pdf), cross-checked on independent mirrors). Corrections from the earlier draft: **BOD basis is 3 days @ 27°C** (not 5 days @ 20°C); **Temperature is a delta rule**, not a flat cap; **TDS is NOT a general standard** (sector/CTO-specific); **Fecal coliform is not a general effluent standard** (IS:2296 / STP norms). Factory CTO / SPCB limits override these and may be stricter.

| Parameter | Inland Surface Water | Public Sewer | Unit |
|---|---|---|---|
| pH | 5.5 – 9.0 | 5.5 – 9.0 | — |
| BOD (3 days @ 27°C) | ≤ 30 | ≤ 350 | mg/L |
| COD | ≤ 250 | — | mg/L |
| Suspended Solids (TSS) | ≤ 100 | ≤ 600 | mg/L |
| Oil & Grease | ≤ 10 | ≤ 20 | mg/L |
| Temperature | ≤ 5°C above receiving-water temp | ≤ 5°C above receiving-water temp | °C |
| Ammoniacal Nitrogen (as N) | ≤ 50 | ≤ 50 | mg/L |
| Free Ammonia (as NH₃) | ≤ 5.0 | — | mg/L |
| Total Kjeldahl Nitrogen | ≤ 100 | — | mg/L |
| Total Residual Chlorine | ≤ 1.0 | — | mg/L |
| Total Chromium | ≤ 2.0 | ≤ 2.0 | mg/L |
| Hexavalent Chromium | ≤ 0.1 | ≤ 2.0 | mg/L |
| Lead | ≤ 0.1 | ≤ 1.0 | mg/L |
| Mercury | ≤ 0.01 | ≤ 0.01 | mg/L |
| Arsenic | ≤ 0.2 | ≤ 0.2 | mg/L |
| Cyanide | ≤ 0.2 | ≤ 2.0 | mg/L |
| Fluoride | ≤ 2.0 | ≤ 15 | mg/L |
| Phenolic Compounds | ≤ 1.0 | ≤ 5.0 | mg/L |
| Sulphide | ≤ 2.0 | — | mg/L |

**Not general standards (never hard-code these as CPCB):** *TDS* — sector/CTO-specific (distillery, pharma, etc.); the app treats it as a CTO-configurable limit with a flagged placeholder default. *Fecal coliform* — from IS:2296 / STP norms, not industrial general effluent. For **Temperature**, the app screens with a pragmatic absolute cap (40°C inland / 45°C sewer) because the true delta rule needs the receiving-water temperature — set the real absolute limit from the CTO.

**Note:** SPCBs can impose STRICTER limits than CPCB. Each factory's CTO document specifies their exact limits. Your app must allow custom limit configuration per factory.

### Sector-Specific Standards (important — limits vary by industry)
- **Textile:** Additional parameters — color, AOX (adsorbable organic halogens)
- **Pharma:** Additional — TDS, antibiotic residues, solvents
- **Tannery:** Additional — total chromium, hexavalent chromium (near-zero)
- **Food Processing:** Higher BOD in raw effluent, seasonal variation
- **Distillery:** Extremely high BOD/COD in raw, ZLD often mandatory

### What Industries Must Submit
1. **Daily ETP operation logs** — operator signatures, chemical consumption, flow rates
2. **Monthly/quarterly self-monitoring reports** — lab test results from NABL-accredited labs
3. **Form V (Annual Environmental Statement)** — under Rule 14, EP Rules 1986
4. **OCEMS data** — real-time for Red category (pH, TSS, COD, BOD, flow rate — auto-transmitted to CPCB/SPCB servers)

> **Positioning note:** For Red-category factories, JalRakshak is a **supplementary reporting/analytics layer** (self-monitoring, reports, alerts) — **not** a replacement for the mandatory real-time OCEMS auto-transmission to CPCB/SPCB. Be explicit about this in sales so you don't overpromise. Orange/Green/White (no OCEMS mandate) are where JalRakshak can be the primary compliance tool.

Records must be maintained for **minimum 3 years** and produced during inspections.

---

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Backend API | **FastAPI (Python)** | You already know it, fast to build, async support |
| AI Layer | **Claude API (claude-sonnet-5)** | Summaries, recommendations, anomaly explanations |
| PDF Reports | **ReportLab** or **WeasyPrint** | Python-native PDF generation (not react-pdf since this is Python backend) |
| Database | **SQLite** (MVP) → **PostgreSQL** (scale) | Start simple, migrate later |
| Frontend | **Streamlit** (MVP) → **Next.js** (production) | Streamlit for speed, Next.js when you need a real dashboard |
| WhatsApp Alerts | **Twilio WhatsApp API** | You already know this from JalSathi |
| File Processing | **pandas + openpyxl** | Parse CSV/Excel uploads |
| Hosting | **Render** (Starter tier) | You already have this setup |
| Domain | **jalrakshak.in** or similar | Register when ready |

---

## Database Schema

```sql
-- Tenancy: an org is a paying account (a single factory, or a consultant
-- managing many). Every domain table below carries org_id for isolation —
-- required by the Consultant tier (manage up to 10 factories). Enforce
-- org_id filtering in every query (row-level isolation), not just in the UI.
CREATE TABLE orgs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    plan TEXT NOT NULL DEFAULT 'basic',  -- basic, pro, enterprise, consultant
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users log in and belong to one org
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,  -- bcrypt/argon2; never store plaintext
    role TEXT NOT NULL DEFAULT 'member',  -- owner, admin, member
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES orgs(id)
);

-- Factory/Client registration (scoped to an org)
CREATE TABLE factories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,  -- tenant isolation
    name TEXT NOT NULL,
    industry_type TEXT NOT NULL,  -- textile, pharma, food_processing, tannery, etc.
    cpcb_category TEXT NOT NULL,  -- red, orange, green, white
    discharge_destination TEXT NOT NULL,  -- inland_surface_water, public_sewer, land
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    cto_number TEXT,  -- Consent to Operate number
    cto_expiry DATE,
    contact_name TEXT,
    contact_phone TEXT,  -- for WhatsApp alerts
    contact_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES orgs(id)
);

-- Note: factory_limits, readings, flow_data, reports, and alerts below all
-- reference factory_id, which already scopes them to an org through factories.
-- Always join/filter via a factory the current user's org owns.

-- Custom limits per factory (from their CTO document)
-- If not set, falls back to CPCB general standards
CREATE TABLE factory_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    parameter TEXT NOT NULL,  -- ph, bod, cod, tss, oil_grease, tds, etc.
    min_value REAL,  -- for pH (lower bound)
    max_value REAL NOT NULL,  -- discharge limit
    unit TEXT NOT NULL,  -- mg/L, °C, MPN/100mL
    source TEXT DEFAULT 'cpcb_general',  -- cpcb_general, spcb_specific, cto_specific
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

-- Daily ETP monitoring readings (uploaded via CSV)
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    reading_date DATE NOT NULL,
    parameter TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    sample_point TEXT DEFAULT 'etp_outlet',  -- etp_inlet, etp_outlet, final_discharge
    lab_name TEXT,  -- NABL lab that tested
    is_violation INTEGER DEFAULT 0,  -- 1 if exceeds limit
    violation_severity TEXT,  -- warning (80-100% of limit), critical (>100%)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

-- Flow data (water intake vs discharge volumes)
CREATE TABLE flow_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    reading_date DATE NOT NULL,
    water_intake_kld REAL,  -- kiloliters per day intake
    water_discharge_kld REAL,  -- kiloliters per day discharged
    water_recycled_kld REAL,  -- kiloliters per day recycled
    etp_chemical_consumption_kg REAL,
    etp_power_consumption_kwh REAL,
    operator_name TEXT,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

-- Generated compliance reports
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    report_type TEXT NOT NULL,  -- monthly, quarterly, annual_form_v
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_readings INTEGER,
    total_violations INTEGER,
    compliance_score REAL,  -- percentage
    ai_summary TEXT,  -- Claude-generated summary
    ai_recommendations TEXT,  -- Claude-generated recommendations
    pdf_path TEXT,  -- path to generated PDF
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);

-- Alert history
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factory_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,  -- threshold_warning, violation, trend_alert, cto_expiry
    parameter TEXT,
    current_value REAL,
    limit_value REAL,
    message TEXT NOT NULL,
    sent_via TEXT DEFAULT 'whatsapp',  -- whatsapp, email
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factory_id) REFERENCES factories(id)
);
```

---

## CSV Upload Format (What Factories Will Upload)

### Template you provide to factories:

```csv
date,sample_point,ph,bod_mg_l,cod_mg_l,tss_mg_l,oil_grease_mg_l,tds_mg_l,ammoniacal_nitrogen_mg_l,temperature_c,flow_intake_kld,flow_discharge_kld,flow_recycled_kld,lab_name,operator_name
2026-07-01,etp_outlet,7.2,25,180,85,8,1800,35,32,150,120,30,SGS Lab Vizag,Raju K
2026-07-02,etp_outlet,7.5,28,210,92,9,1900,40,33,155,125,30,SGS Lab Vizag,Raju K
2026-07-03,etp_outlet,6.8,32,260,105,12,2050,48,34,160,130,30,SGS Lab Vizag,Raju K
```

**Minimum required columns:** date, ph, bod, cod, tss
**Optional columns:** everything else (app works with partial data)

---

## Project Structure

```
jalrakshak/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # CPCB limits, app settings
│   ├── models.py                # SQLAlchemy/Pydantic models
│   ├── database.py              # DB connection
│   │
│   ├── routers/
│   │   ├── upload.py            # CSV/Excel upload endpoint
│   │   ├── reports.py           # Report generation endpoints
│   │   ├── dashboard.py         # Dashboard data endpoints
│   │   ├── alerts.py            # Alert configuration endpoints
│   │   └── factories.py         # Factory CRUD endpoints
│   │
│   ├── services/
│   │   ├── parser.py            # CSV/Excel parsing + validation
│   │   ├── compliance.py        # Check readings against limits
│   │   ├── anomaly.py           # Trend analysis + anomaly detection
│   │   ├── ai_summary.py        # Claude API integration
│   │   ├── pdf_generator.py     # Compliance report PDF
│   │   ├── whatsapp_alert.py    # Twilio WhatsApp notifications
│   │   └── form_v.py            # Annual Form V generation
│   │
│   └── templates/
│       └── report_template.html # HTML template for PDF (if using WeasyPrint)
│
├── streamlit_app/
│   ├── app.py                   # Streamlit dashboard (MVP frontend)
│   ├── pages/
│   │   ├── upload.py            # Upload data page
│   │   ├── dashboard.py         # Charts + compliance overview
│   │   ├── reports.py           # Download reports page
│   │   └── settings.py          # Factory configuration
│   └── components/
│       └── charts.py            # Plotly/Altair chart components
│
├── data/
│   ├── cpcb_limits.json         # Default CPCB discharge limits
│   ├── sector_limits.json       # Industry-specific limits
│   └── sample_data.csv          # Demo data for testing
│
├── requirements.txt
├── Dockerfile
├── render.yaml
└── README.md
```

---

## Step-by-Step Build Plan

### STEP 1: Set Up Project + Define CPCB Limits (Day 1)

**What:** Create project skeleton, define all CPCB parameters as a config file.

**File: `data/cpcb_limits.json`**
```json
{
  "inland_surface_water": {
    "ph": { "min": 5.5, "max": 9.0, "unit": "" },
    "bod": { "max": 30, "unit": "mg/L" },
    "cod": { "max": 250, "unit": "mg/L" },
    "tss": { "max": 100, "unit": "mg/L" },
    "oil_grease": { "max": 10, "unit": "mg/L" },
    "tds": { "max": 2100, "unit": "mg/L" },
    "ammoniacal_nitrogen": { "max": 50, "unit": "mg/L" },
    "temperature": { "max": 40, "unit": "°C" },
    "total_chromium": { "max": 2.0, "unit": "mg/L" },
    "hexavalent_chromium": { "max": 0.1, "unit": "mg/L" },
    "lead": { "max": 0.1, "unit": "mg/L" },
    "mercury": { "max": 0.01, "unit": "mg/L" },
    "fecal_coliform": { "max": 1000, "unit": "MPN/100mL" }
  },
  "public_sewer": {
    "ph": { "min": 5.5, "max": 9.0, "unit": "" },
    "bod": { "max": 350, "unit": "mg/L" },
    "tss": { "max": 600, "unit": "mg/L" },
    "oil_grease": { "max": 20, "unit": "mg/L" },
    "tds": { "max": 2100, "unit": "mg/L" },
    "ammoniacal_nitrogen": { "max": 50, "unit": "mg/L" },
    "temperature": { "max": 45, "unit": "°C" }
  }
}
```

**Commands:**
```bash
mkdir jalrakshak && cd jalrakshak
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi uvicorn pandas openpyxl anthropic reportlab twilio sqlalchemy pydantic streamlit plotly
```

---

### STEP 2: Build CSV Parser + Validator (Day 2–3)

**What:** Parse uploaded CSV/Excel, validate column names, check data types, flag missing values.

**File: `app/services/parser.py`**

Core logic:
```python
import pandas as pd
from datetime import datetime

REQUIRED_COLUMNS = ['date', 'ph']
OPTIONAL_COLUMNS = ['bod_mg_l', 'cod_mg_l', 'tss_mg_l', 'oil_grease_mg_l', 
                     'tds_mg_l', 'ammoniacal_nitrogen_mg_l', 'temperature_c',
                     'flow_intake_kld', 'flow_discharge_kld', 'flow_recycled_kld',
                     'lab_name', 'operator_name', 'sample_point']

def parse_upload(file_path: str) -> dict:
    """Parse CSV/Excel and return validated DataFrame + errors"""
    
    # Read file
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Check required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return {"success": False, "error": f"Missing required columns: {missing}"}
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True)
    
    # Validate numeric ranges (basic sanity checks)
    errors = []
    if 'ph' in df.columns:
        invalid_ph = df[(df['ph'] < 0) | (df['ph'] > 14)]
        if len(invalid_ph) > 0:
            errors.append(f"{len(invalid_ph)} rows have invalid pH (must be 0-14)")
    
    if 'temperature_c' in df.columns:
        invalid_temp = df[df['temperature_c'] > 100]
        if len(invalid_temp) > 0:
            errors.append(f"{len(invalid_temp)} rows have unrealistic temperature >100°C")
    
    # Flag nulls
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            errors.append(f"{count} null values in required column '{col}'")
    
    return {
        "success": True,
        "data": df,
        "row_count": len(df),
        "date_range": f"{df['date'].min()} to {df['date'].max()}",
        "columns_found": list(df.columns),
        "warnings": errors
    }
```

---

### STEP 3: Build Compliance Checker (Day 3–4)

**What:** Compare each reading against CPCB limits (or custom factory CTO limits). Flag violations with severity levels.

**File: `app/services/compliance.py`**

Core logic:
```python
import json

def load_limits(discharge_destination: str, custom_limits: dict = None) -> dict:
    """Load CPCB limits, override with custom CTO limits if provided"""
    with open('data/cpcb_limits.json') as f:
        all_limits = json.load(f)
    
    limits = all_limits.get(discharge_destination, all_limits['inland_surface_water'])
    
    # Override with factory-specific CTO limits
    if custom_limits:
        for param, values in custom_limits.items():
            limits[param] = values
    
    return limits

def check_compliance(df, limits: dict) -> dict:
    """Check each reading against limits, return violations"""
    
    # Parameter mapping: CSV column name -> limit key
    param_map = {
        'ph': 'ph',
        'bod_mg_l': 'bod',
        'cod_mg_l': 'cod',
        'tss_mg_l': 'tss',
        'oil_grease_mg_l': 'oil_grease',
        'tds_mg_l': 'tds',
        'ammoniacal_nitrogen_mg_l': 'ammoniacal_nitrogen',
        'temperature_c': 'temperature'
    }
    
    violations = []
    warnings = []
    
    for _, row in df.iterrows():
        for csv_col, limit_key in param_map.items():
            if csv_col not in df.columns or pd.isna(row.get(csv_col)):
                continue
            
            value = row[csv_col]
            limit = limits.get(limit_key)
            if not limit:
                continue
            
            has_min = 'min' in limit
            has_max = 'max' in limit

            # Check max limit (hard breach)
            if has_max and value > limit['max']:
                violations.append({
                    'date': str(row['date']),
                    'parameter': limit_key,
                    'value': value,
                    'limit': limit['max'],
                    'unit': limit.get('unit', ''),
                    'severity': 'critical',
                    'exceedance_pct': round(((value - limit['max']) / limit['max']) * 100, 1)
                })

            # Check min limit (hard breach — e.g. pH below lower bound)
            if has_min and value < limit['min']:
                violations.append({
                    'date': str(row['date']),
                    'parameter': limit_key,
                    'value': value,
                    'limit': limit['min'],
                    'unit': limit.get('unit', ''),
                    'severity': 'critical',
                    'note': f'Below minimum {limit["min"]}'
                })

            # Warning logic (only if not already a violation)
            is_violation = (has_max and value > limit['max']) or (has_min and value < limit['min'])
            if not is_violation:
                if has_min:
                    # RANGE parameter (e.g. pH): warn when creeping toward either bound.
                    # Do NOT use the 80%-of-max rule here — for pH that would flag ~7.2 as a
                    # warning even though it sits comfortably inside the 5.5–9.0 range.
                    band = (limit['max'] - limit['min']) * 0.05  # within 5% of the span of a bound
                    if value >= limit['max'] - band or value <= limit['min'] + band:
                        warnings.append({
                            'date': str(row['date']),
                            'parameter': limit_key,
                            'value': value,
                            'min': limit['min'],
                            'max': limit['max'],
                            'unit': limit.get('unit', ''),
                            'severity': 'warning',
                            'note': 'Approaching range bound'
                        })
                elif has_max and value > limit['max'] * 0.8:
                    # "Lower is better" parameter (BOD, COD, TSS, …): warn at 80% of the limit.
                    warnings.append({
                        'date': str(row['date']),
                        'parameter': limit_key,
                        'value': value,
                        'limit': limit['max'],
                        'unit': limit.get('unit', ''),
                        'severity': 'warning',
                        'usage_pct': round((value / limit['max']) * 100, 1)
                    })
    
    # Calculate compliance score
    total_checks = len(df) * len([c for c in param_map if c in df.columns])
    violation_count = len(violations)
    compliance_score = round(((total_checks - violation_count) / total_checks) * 100, 1) if total_checks > 0 else 100
    
    return {
        'compliance_score': compliance_score,
        'total_readings': len(df),
        'total_checks': total_checks,
        'violations': violations,
        'warnings': warnings,
        'violation_count': violation_count,
        'warning_count': len(warnings)
    }
```

---

### STEP 4: Build AI Summary with Claude (Day 4–5)

**What:** Send compliance results to Claude, get plain-language summary and actionable recommendations.

**File: `app/services/ai_summary.py`**

```python
import anthropic
import json

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

def generate_compliance_summary(factory_name: str, compliance_result: dict, period: str) -> dict:
    """Generate AI-powered compliance summary and recommendations"""
    
    prompt = f"""You are an industrial wastewater compliance expert in India. 
Analyze this factory's ETP monitoring data and provide:
1. A plain-language compliance summary (3-4 sentences) suitable for the factory manager
2. Specific technical recommendations to fix any violations
3. Risk assessment for the next reporting period

Factory: {factory_name}
Reporting Period: {period}
Compliance Score: {compliance_result['compliance_score']}%
Total Readings: {compliance_result['total_readings']}
Violations: {compliance_result['violation_count']}
Warnings: {compliance_result['warning_count']}

Violation Details:
{json.dumps(compliance_result['violations'][:20], indent=2)}

Warning Details:
{json.dumps(compliance_result['warnings'][:20], indent=2)}

Respond in this exact JSON format:
{{
  "summary": "...",
  "recommendations": ["rec1", "rec2", "rec3"],
  "risk_level": "low|medium|high|critical",
  "risk_explanation": "...",
  "parameter_insights": {{
    "parameter_name": "insight about this parameter's trend"
  }}
}}

Respond with ONLY the JSON, no markdown, no backticks."""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError:
        return {
            "summary": response.content[0].text,
            "recommendations": [],
            "risk_level": "unknown",
            "risk_explanation": "Could not parse AI response"
        }
```

---

### STEP 5: Build PDF Report Generator (Day 5–6)

**What:** Generate a professional compliance report PDF with charts, violation table, AI summary.

**File: `app/services/pdf_generator.py`**

Use **ReportLab** (Python-native, no headless browser — same philosophy as your react-pdf approach).

Report structure:
```
Page 1: Cover Page
  - Factory name, CTO number, reporting period
  - Compliance score (large, color-coded)
  - Report generation date

Page 2: Executive Summary
  - AI-generated summary
  - Risk level indicator
  - Key recommendations

Page 3: Parameter-wise Analysis
  - Table: Parameter | Avg | Min | Max | Limit | Status
  - Color-coded: Green (OK), Yellow (warning), Red (violation)

Page 4: Violation Log
  - Date | Parameter | Value | Limit | Exceedance %
  - Sorted by severity

Page 5: Trend Charts
  - Line charts for each parameter over the reporting period
  - Limit lines shown as red dashed lines

Page 6: Flow Data Summary
  - Water intake vs discharge vs recycled
  - ETP efficiency calculation

Page 7: Recommendations
  - AI-generated technical recommendations
  - Next steps

Footer on every page:
  - "Generated by JalRakshak | jalrakshak.in | Report ID: XXX"
  - Disclaimer: "This report is for internal compliance tracking. 
    Official submissions must be signed by authorized signatory."
```

---

### STEP 6: Build WhatsApp Alerts (Day 6–7)

**What:** Send WhatsApp notifications when parameters approach or breach limits.

> ⚠️ **Production WhatsApp requires approved templates.** Alerts are *business-initiated* messages. Outside the 24-hour customer-service window, WhatsApp only allows **pre-approved Business template messages** — you cannot send the free-form text below in production. You must: (1) register a WhatsApp Business sender, (2) submit alert templates for approval with variable placeholders, and (3) send via `content_sid` + `content_variables`. The `whatsapp:+14155238886` sandbox number is **dev-only**. If template approval is a blocker at launch, fall back to **SMS or email** for alerts (same trigger logic).

**File: `app/services/whatsapp_alert.py`**

```python
from twilio.rest import Client
import os

def send_whatsapp_alert(to_number: str, factory_name: str, alert_data: dict):
    """Send WhatsApp alert for compliance issues"""
    
    client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    
    if alert_data['severity'] == 'critical':
        emoji = "🔴"
        header = "VIOLATION ALERT"
    else:
        emoji = "🟡"
        header = "WARNING"
    
    message_body = f"""{emoji} *{header} — {factory_name}*

Parameter: {alert_data['parameter'].upper()}
Value: {alert_data['value']} {alert_data['unit']}
Limit: {alert_data['limit']} {alert_data['unit']}
Date: {alert_data['date']}

{'Exceedance: ' + str(alert_data.get('exceedance_pct', '')) + '%' if alert_data['severity'] == 'critical' else 'At ' + str(alert_data.get('usage_pct', '')) + '% of limit'}

Action needed. Check ETP operations immediately.

— JalRakshak"""

    message = client.messages.create(
        body=message_body,
        from_='whatsapp:+14155238886',  # Twilio sandbox (replace with production number)
        to=f'whatsapp:+91{to_number}'
    )
    
    return message.sid
```

**Alert triggers:**
- **Immediate:** Any parameter exceeds CPCB limit → Critical alert
- **Warning:** Any parameter reaches 80% of limit → Warning alert
- **Trend:** Parameter rising >10% over 3 consecutive readings → Trend alert
- **CTO expiry:** 30 days before CTO expiry → Reminder alert

---

### STEP 7: Build Streamlit Dashboard (Day 7–10)

**What:** Simple web UI for uploading data, viewing compliance status, downloading reports.

**File: `streamlit_app/app.py`**

Dashboard pages:

**Page 1: Upload Data**
- File upload widget (CSV/Excel)
- Preview parsed data
- Click "Analyze" → runs compliance check
- Show results: score, violations, warnings

**Page 2: Compliance Dashboard**
- Big compliance score card (color-coded)
- Parameter-wise status bars
- Trend charts (plotly line charts with limit lines)
- Violation timeline

**Page 3: Reports**
- Select reporting period (monthly/quarterly)
- Generate PDF report
- Download button
- View AI summary inline

**Page 4: Settings**
- Factory details (name, industry type, CTO number)
- Custom parameter limits (override CPCB defaults)
- WhatsApp notification number
- Discharge destination (inland water / sewer)

---

### STEP 8: Build FastAPI Backend (Day 8–10)

**What:** API endpoints for the Streamlit frontend (and future Next.js dashboard).

> **MVP scope:** This FastAPI layer is **optional for the MVP**. Streamlit can import and call the `services/` modules (`parser`, `compliance`, `pdf_generator`, …) directly — no HTTP layer needed to ship. Build FastAPI when you add the Next.js dashboard or need external API access (Enterprise tier). Deferring it shaves days off the timeline.

**Key endpoints:**
```
POST   /api/upload              — Upload CSV/Excel file
GET    /api/compliance/{id}     — Get compliance results
POST   /api/reports/generate    — Generate PDF report
GET    /api/reports/{id}/download — Download PDF
GET    /api/dashboard/{factory_id} — Dashboard data (charts, scores)
POST   /api/factories           — Register new factory
PUT    /api/factories/{id}/limits — Set custom limits
GET    /api/alerts/{factory_id}  — Alert history
POST   /api/alerts/test         — Send test WhatsApp alert
```

---

### STEP 9: Deploy on Render (Day 11)

**What:** Deploy both FastAPI backend and Streamlit frontend.

```yaml
# render.yaml
services:
  - type: web
    name: jalrakshak-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: TWILIO_ACCOUNT_SID
        sync: false
      - key: TWILIO_AUTH_TOKEN
        sync: false
    plan: starter  # $7/mo, always on

  - type: web
    name: jalrakshak-app
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run streamlit_app/app.py --server.port $PORT
    plan: free
```

---

### STEP 10: Create Demo Data + Record Demo Video (Day 12–13)

**What:** Create realistic sample data and a 2-minute demo video.

**Sample data should include:**
- 30 days of readings for a fictional pharma company in Vizag
- Mix of compliant readings, warnings, and 2-3 violations
- Realistic parameter values that tell a story (e.g., BOD creeping up over a week, then spiking)

**Demo flow:**
1. Upload CSV → show parsed data
2. Click Analyze → compliance score appears (e.g., 91.3%)
3. Show violation flags (BOD exceeded on July 15, COD warning on July 18)
4. Show trend charts with limit lines
5. Generate PDF report → download
6. Show WhatsApp alert received on phone

**Record this as a screen recording and upload to YouTube for sharing with potential customers.**

---

### STEP 11: Go Talk to People WITH the Demo (Day 14+)

Now you walk into meetings with a working product on your laptop.

**Target #1: Environmental consultants in Vizag/Hyderabad**
- They file SPCB reports for 20-30 factories
- Your tool saves them hours per client per month
- They become your distribution channel

**Target #2: NABL water testing labs**
- They already have the data — they generate it
- Natural partnership: lab tests → data auto-flows into JalRakshak → report generated
- Revenue share or referral model

**Target #3: EHS officers at pharma companies**
- Vizag pharma corridor (Divis Labs suppliers, Aurobindo suppliers)
- Offer 30-day free trial with their real data

---

## Revenue Model

| Plan | Price | What's Included |
|---|---|---|
| **Basic** | ₹5,000/month | CSV upload, compliance check, PDF reports (monthly) |
| **Pro** | ₹10,000/month | + WhatsApp alerts, trend analysis, AI recommendations |
| **Enterprise** | ₹25,000/month | + Custom CTO limits, Form V generation, multi-plant, API access |
| **Consultant** | ₹15,000/month | Manage up to 10 factories, bulk reports |

---

## Timeline Summary

| Day | Task | Deliverable |
|---|---|---|
| 1 | Project setup + CPCB limits config | Skeleton + cpcb_limits.json |
| 2-3 | CSV parser + validator | Working upload + parse |
| 3-4 | Compliance checker | Readings vs limits engine |
| 4-5 | Claude AI summary integration | AI-generated insights |
| 5-6 | PDF report generator | Downloadable compliance PDF |
| 6-7 | WhatsApp alerts (Twilio) | Working alert system |
| 7-10 | Streamlit dashboard | Full UI |
| 8-10 | FastAPI backend | API endpoints |
| 11 | Deploy on Render | Live URLs |
| 12-13 | Demo data + video | YouTube demo |
| 14+ | Talk to consultants/labs/factories | First customer |

---

## What You Already Have (Zero New Learning)

- FastAPI → JalSathi, VaidyaMitra, KisanMitra
- Claude API → All 3 agents + invoice system
- Twilio WhatsApp → JalSathi, VaidyaMitra
- Streamlit → All 3 agents
- PDF generation → Invoice system (@react-pdf/renderer, switch to ReportLab for Python)
- Data pipelines over messy Excel → APWRIMS sync pipeline
- SQLite → JalSathi (10-table DB)
- Render deployment → All agents
- Domain knowledge → You're literally a water resources engineer

**You can build this entire MVP in 2 weeks. Every single component uses skills you already have.**
