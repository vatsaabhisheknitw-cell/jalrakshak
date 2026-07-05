# Reference Library — CPCB / BIS / WHO source documents

Local reference corpus for JalRakshak. **Not committed to git** (bulky PDFs, ~67 MB) — only this `INDEX.md` is tracked. Everything here was downloaded 2026-07 from official sources (primarily https://www.cpcb.gov.in/effluent-emission/).

## Structure

| Folder | Files | Contents |
|---|---|---|
| `general-standards/` | 1 | CPCB General Standards, Schedule VI (EP Rules 1986) — the master effluent standard |
| `effluent-standards/` | 82 | Industry-specific effluent standards (bulk-downloaded from CPCB) |
| `drinking-water/` | 2 | BIS (IS 10500) + WHO drinking-water specifications |
| `water-quality-criteria/` | 3 | Primary / designated-best-use / coastal water-quality criteria |
| `air-quality/` | 1 | National Ambient Air Quality Standards |

## Provenance / verification
- **`general-standards/GeneralStandards.pdf` is the primary source** used to verify `data/cpcb_limits.json` — reconciled line-by-line on **2026-07-05**. Every general-standard value in the app matches this gazette document (EP Rules 1986, Schedule VI, Part-A: Effluents).

## ⚠️ CPCB served identical files under different names
During content-hash dedup, these filenames were found **byte-for-byte identical** — CPCB's server returned the *same* PDF for different industry links. The extra copies were removed (one kept per group). **If you need the real standard for a removed industry, re-fetch it from the specific CPCB/SPCB notification — the file here is NOT that industry's standard:**

- `Carbon_black.pdf`, `NitricAcid.pdf`, `423.pdf` → identical to **`Calcum_carbide.pdf`** → carbon-black & nitric-acid standards are **not actually present**
- `CalorAlkali.pdf` (chlor-alkali), `426.pdf` → identical to **`Asbestos_manufacturing.pdf`** → chlor-alkali standard **not actually present**
- `107-ceramic`, `108-foundry`, `109-glass`, `110-lime_kiln` → identical to **`111-reheating_furnace_industry.pdf`** (possibly a shared notification — verify per industry)

Benign duplicates (your named file matched a numeric bulk download — same real standard): `Cement.pdf`=`Cement_13.03.2018.pdf`, `Thermal_power.pdf`=`TPP_Effluent_Norms.pdf`, `thermalp.pdf`=`TPP_New_Emission_Norms.pdf`, `Electroplasting.pdf`=`Rev_Stand_ElectPlate_30032012.pdf`, `man-made-fibre.pdf`=`02-man-made-fibre.pdf`, `petroleum_oil_refinery.pdf`=`03-...`, `fertiliser_industry.pdf`=`17-...`, `sulphuric_industry.pdf`=`23-...`, plus `402/412/416/417-1/424` matching Caustic soda / textile / stone-crushing / Fermentation / Smelting.

## Not downloaded (dead links on CPCB's own page)
- `Standards_Rubber.pdf` and `507-1.pdf` — HTTP 404 on cpcb.gov.in. Re-fetch from an alternate source if needed.

## Note on filenames
Many effluent files keep CPCB's opaque numeric names (`449.pdf`, `482-1.pdf`, …). Ask and I can map each number to its industry from the CPCB page link text.
