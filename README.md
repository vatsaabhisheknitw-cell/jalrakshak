# JalRakshak — Water Compliance SaaS

Upload daily ETP effluent data → validate against CPCB / factory-CTO discharge
limits → flag violations → generate an SPCB-ready compliance PDF → alert on
breaches. AI (Claude) writes the plain-language summary and recommendations.

MVP is **Streamlit-first**: the UI calls `app/services/` directly, so there's
no separate API to run. FastAPI is scaffolded for later (Next.js dashboard /
external API), not needed now.

## Quickstart

```bash
cd jalrakshak
python -m venv venv
venv\Scripts\activate          # Windows  (source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

cp .env.example .env           # optional — app runs without keys (AI/alerts degrade)
python -m app.database         # create SQLite schema (optional for the demo)

streamlit run streamlit_app/app.py
```

Then click **Use sample data** to run the demo end-to-end.

## Layout

```
jalrakshak/
├── app/
│   ├── config.py              # paths, model id (claude-sonnet-5), param maps, thresholds
│   ├── database.py            # SQLite schema (multi-tenant: orgs/users/org_id)
│   └── services/
│       ├── parser.py          # CSV/Excel parse + validation
│       ├── compliance.py      # readings vs limits (correct pH range logic)
│       ├── ai_summary.py      # Claude summary (graceful fallback, no key needed)
│       ├── pdf_generator.py   # ReportLab compliance PDF
│       └── whatsapp_alert.py  # Twilio WhatsApp/SMS (template caveats inside)
├── streamlit_app/app.py       # MVP UI
├── data/
│   ├── cpcb_limits.json       # general standards — VERIFY before production
│   ├── sector_limits.json     # sector overrides — VERIFY
│   └── sample_data.csv        # 30-day demo (pharma, Vizag) with a few violations
├── requirements.txt · render.yaml · .env.example
```

## Correctness / compliance notes

- **pH is a range parameter.** Warnings for pH fire only near either bound
  (5.5 / 9.0), not at "80% of max" (which would wrongly flag pH 7.3). See
  `app/services/compliance.py`.
- **Verify the limits.** `data/*.json` are drafts. Confirm every value against
  the current CPCB / Schedule VI notification and each factory's CTO. `TDS 2100`
  and `Temperature 40°C` are flagged (`_verify`) as needing confirmation.
- **WhatsApp needs approved templates** for business-initiated alerts in
  production; the sandbox is dev-only. SMS fallback is provided. See
  `app/services/whatsapp_alert.py`.
- **Red category:** this is a supplementary reporting layer, not an OCEMS
  replacement.
- **Multi-tenant:** every domain row is org-scoped (`orgs`/`users`/`org_id`) —
  enforce org filtering in every query for the Consultant tier.

## Config

Set in `.env` (all optional for the demo):

| Var | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude AI summaries (else heuristic fallback) |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | WhatsApp/SMS alerts |

Disclaimer: reports are for internal compliance tracking. Official submissions
must be signed by an authorized signatory.
