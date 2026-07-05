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

## Filename → Industry / Standard  (effluent-standards/)

Labels are the anchor text from the CPCB effluent-emission page (2026-07). Note: that page mixes effluent, air-emission, and noise standards, so a few entries below are emission/noise/water-quality rather than effluent.

| Filename | Industry / Standard |
|---|---|
| `02-man-made-fibre.pdf` | Man-Made Fibres (Synthetic) |
| `03-petroleum_oil_refinery.pdf` | Petroleum Oil Refinery |
| `100-common_hazardous_waste_ (incinerator).pdf` | Common Hazardous Waste Incinerator |
| `102-refractory.pdf` | Refractory Industry |
| `103-cashew_seed_industry.pdf` | Cashew Seed Processing Industry |
| `104-plaster_of_paris.pdf` | Plaster of Paris Industry |
| `105-sewage_treatment_plants.pdf` | Sewage treatment plant |
| `106-industrial_boiler.pdf` | Industrial Boiler |
| `111-reheating_furnace_industry.pdf` | SO2 and NOx Standards for Reheating Furnace Industry |
| `113-Kerosene.pdf` | Kerosene Standards |
| `114-standards.pdf` | Automobile Service Station, Bus Depot or Workshop |
| `116-standards.pdf` | Hot Mix Plant |
| `117-CPC_Plants.pdf` | Calcined Petroleum Coke (CPC) units |
| `17-fertiliser_industry.pdf` | Fertilizer Industry |
| `23-sulphuric_industry.pdf` | Sulphuric Acid Plant |
| `35-coffee.pdf` | Coffee Industry |
| `38-petrochemical.pdf` | Petrochemicals (Basic & Intermediates) |
| `39-hotel.pdf` | Hotel Industry |
| `42-paint.pdf` | Paint Industry |
| `425.pdf` | (unidentified — scanned PDF, no page label) |
| `427-1.pdf` | Foundries |
| `427.pdf` | Re-Heating (Reverberatory) Furnaces |
| `428.pdf` | Thermal Power Plants |
| `430-1.pdf` | Aluminium Plants |
| `431-1.pdf` | Stone Crushing Unit |
| `437.pdf` | Tannery (After Primary Treatment) |
| `438.pdf` | Inorganic Chemical Industry (Waste Water Discharge) |
| `439.pdf` | Bullion Refining (Waste Water Discharge) |
| `440.pdf` | Noise Limits for Automobiles (Free Field) at One Meter indB(A) |
| `441-1.pdf` | Glass Industry |
| `442-1.pdf` | Slaughter House, Meat & Sea Food Industry |
| `442.pdf` | Lime Kiln |
| `449.pdf` | Tanneries |
| `451-1.pdf` | Ceramic Industry |
| `453-1.pdf` | Starch Industry |
| `454-1.pdf` | Beehive Hard Coke Oven |
| `455-1.pdf` | Soft Coke Industry |
| `455.pdf` | Briquette Industry (Coal) |
| `456-1.pdf` | Edible Oil & Vanaspati Industry |
| `458-1.pdf` | Flour Mills, Grain processing, Paddy processing, pulse making or Grinding mills |
| `459-1.pdf` | Boilers |
| `463-1.pdf` | Oil Drilling and Gas Extraction Industry |
| `475.pdf` | Emission Standard for SO From Cupola Furnace |
| `479-1.pdf` | Battery Manufacturing Industry |
| `481.pdf` | Environmental Standards for Gas/Naptha-Based Thermal Power Plants |
| `482-1.pdf` | Environmental Standards for Coal Washeries |
| `482.pdf` | Temperature Limit for Discharge of Condenser Cooling |
| `484-1.pdf` | Water Quality Standards for Coastal Waters Marine Outfalls |
| `492-1.pdf` | Noise Standards for Fire Crackers |
| `494-1.pdf` | Standards for Coal Mines |
| `501.pdf` | Noise Limit for Generator Sets run with Diesel |
| `51-Food_Proicessing.pdf` | Food and Fruit Processing Industry |
| `514.pdf` | Guidelines for Pollution Control in Ginning Mills |
| `52-Jute_Processing.pdf` | Jute Processing Industry |
| `56-Dairy.pdf` | Dairy |
| `73-pharmaceuticals.pdf` | Pharmaceutical (Manufacturing and Formulation) Industry |
| `74-brick_kiln.pdf` | Brick Kiln |
| `93-Water_Quality_Bathing.pdf` | Primary Water Quality Criteria for Bathing Water |
| `95-final.pdf` | Emission Limits for New Diesel Engines (upto 800 KW) for |
| `96-final.pdf` | Emission Standards for Diesel Engines (Engine Rating more than 0.8 MW (800 KW) for Power Plant, Generator Set applications and other Requirements |
| `Airport.pdf` | Airport Noise |
| `Asbestos_manufacturing.pdf` | Asbestos Manufacturing Units |
| `CETP.pdf` | Common Effluent Treatment Plants |
| `Calcum_carbide.pdf` | Calcium Carbide |
| `Caustic_soda-industry.pdf` | Caustic Soda Industry |
| `Cement_13.03.2018.pdf` | Cement Plants |
| `DyeandDye_Inter_Indus.pdf` | Dye and Dye Intermediate Industry |
| `Fermentation.pdf` | Fermentation Industry (Distilleries, Maltries, Breweries) |
| `Iron_steel(integrated).pdf` | Iron & Steel (Integrated) |
| `ORGANICCHEMICAL.pdf` | Organic Chemicals Manufacturing Industry |
| `Pesticide_2025.pdf` | Pesticide Industry |
| `Petrol-and-Carosin-GSR-535-E.pdf` | Emission Standards for new GenSets (upto 19 KW run on Petrol and Kerosene with Implementation Schedule) |
| `PulpandPaper.pdf` | Small Pulp and Paper Industry |
| `Rev_Stand_ElectPlate_30032012.pdf` | Electroplating Anodizing Industry |
| `Smelting.pdf` | Copper, Lead & Zinc Smelting |
| `Sponge_iron_plant(rotary-kiln).pdf` | Sponge Iron Plant (Rotary Kiln) |
| `Sugar.pdf` | Sugar Industry |
| `TPP_Effluent_Norms.pdf` | Thermal Power Plants - Effluent |
| `TPP_New_Emission_Norms.pdf` | Thermal Power Plants - Emission |
| `integrated_textile.pdf` | Integrated textile units (cotton/wool/carpet/polyester; printing/dyeing/bleaching; garments) |
| `sodaash.pdf` | Soda Ash Industry (Solvay Process) |
| `stone_crushing.pdf` | Stone Crushing Unit |


## Sector limits extracted → `../sector_limits.json`
26 effluent sectors were extracted from these local PDFs (2026-07) and written to
`data/sector_limits.json`, incl. pharmaceutical, distillery, textile, tannery,
seafood/slaughter, pulp & paper, caustic soda, pesticide, fertilizer, edible oil,
organic & inorganic chemicals, dye, bullion, paint, man-made fibre, starch, coffee,
battery (2 types), coal washery, coal mine, oil & gas drilling, STP, thermal-power
effluent, glass. Several were recovered from consolidated numeric PDFs (Organic
Chemicals ← 456-1, Dye ← 439, Paint ← 437, Man-Made Fibre ← 451-1).

## ⚠️ Needs a better version (could NOT extract — scanned image or garbled PDF)
These effluent PDFs have no usable text layer (scanned) or came out as OCR garbage,
so their values are NOT in sector_limits.json. Re-source a text-based PDF (or an
OCR'd copy) to add these — **starred are commercially high-value**:

| File | Sector | Problem |
|---|---|---|
| `51-Food_Proicessing.pdf` | ⭐ Food & Fruit Processing | scanned, 0 chars |
| `Sugar.pdf` | ⭐ Sugar Industry | garbled glyph codes |
| `Rev_Stand_ElectPlate_30032012.pdf` | ⭐ Electroplating & Anodizing | OCR garbage |
| `Iron_steel(integrated).pdf` | Iron & Steel (Integrated) | scanned, 0 chars |
| `Smelting.pdf` | Copper / Lead / Zinc Smelting | scanned, 0 chars |
| `03-petroleum_oil_refinery.pdf` | Petroleum Oil Refinery | scanned, 0 chars |
| `23-sulphuric_industry.pdf` | Sulphuric Acid Plant | scanned, 0 chars |
| `sodaash.pdf` | Soda Ash (Solvay) | scanned, 0 chars |
| `52-Jute_Processing.pdf` | Jute Processing | scanned, 0 chars |
| `458-1.pdf` | Flour Mills / Grain / Paddy processing | scanned, 0 chars |
| `Sponge_iron_plant(rotary-kiln).pdf` | Sponge Iron (Rotary Kiln) | near-empty (91 chars) |
| `102-refractory.pdf` | Refractory | scanned, 0 chars |
| `103-cashew_seed_industry.pdf` | Cashew Seed Processing | scanned, 0 chars |
| `104-plaster_of_paris.pdf` | Plaster of Paris | scanned, 0 chars |
| `100-common_hazardous_waste_ (incinerator).pdf` | Common Hazardous Waste Incinerator | scanned, 0 chars |
| `39-hotel.pdf` | Hotel Industry | scanned, 0 chars |
| `425.pdf` | (unidentified) | scanned, 0 chars |
