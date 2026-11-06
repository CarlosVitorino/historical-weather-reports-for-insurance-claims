# International expansion and extra data sources — Nordics + US (2026-11-06)

Desk research, no code changed. Two questions:

1. Which countries outside the US have (a) storm perils that drive insurance claims, (b) open
   government weather data with an API, and (c) a real need for an address-level evidence report?
   Scandinavia first.
2. Which extra open, historical sources could back each report with **more than one source**?

Builds on `International demand check.md` (DE/ES/PT/FR/AU search demand, 2026-10-29), which found the
"hail report by address" search term is a US phenomenon.

> **Scope note.** `CLAUDE.md` / `build-brief.md` say *v1 is US government sources only*, *no forecast
> data*, and *no feeds beyond the three free public inputs*. Everything below is a proposal for
> after v1, not something to build now without a decision. The brief's own test — sell a handful of
> US reports against StormRecord — should ideally come before a second market.

---

## 1. Nordics — headline

**Denmark first, Norway second, Sweden and Finland weaker.** Hail is not the angle in any of them:
I found no Nordic hail-loss figures, and European hail studies centre on Central/Southern Europe. The
claim-driving perils are **windstorm** (all four), **cloudburst** (DK, SE) and **lightning**. A
Nordic report would be a wind + rain + lightning report, with hail as a minor line.

### Data availability

| | Station observations | Lightning | Licence |
|---|---|---|---|
| 🇩🇰 DMI | Free API (free key), OGC API–Features | Free API, 6 sensors, since **2002**; CG+/CG−/cloud-to-cloud | Free; DMI states raw data is **not quality-controlled** |
| 🇸🇪 SMHI | Free API, no key; quality-controlled "corrected archive" + latest months | Archive API (year/month/day → zipped shapefiles) | CC BY 4.0 |
| 🇳🇴 MET Norway (Frost) | Free API (free client ID), ~2,200 stations, 10-min to annual | In Frost, returned in UALF (plain-text lightning format) | CC BY 4.0 / NLOD |
| 🇫🇮 FMI | Free WFS, no key; max **7 days** per sub-daily request | `fmi::observations::lightning::*` stored queries; historical range unconfirmed | CC BY 4.0; radar archive on AWS |

**Missing everywhere: a Storm Events equivalent.** The nearest is the European Severe Weather
Database (ESWD, ESSL). Its standard terms **ban commercial use** and republishing raw data; a paid
route exists (fee by organisation size, contact eswd@essl.org). Until then a Nordic report is
station measurements + lightning + distance/bearing — two of the brief's four gaps, not four.

### Demand and claim rules by country

**🇩🇰 Denmark — strongest case**
- The policyholder carries the burden of proof that a storm occurred and caused the damage; the
  insurance complaints board (Ankenævnet for Forsikring) rejects claims without evidence.
- Policies use measurable thresholds:
  - **Storm:** 17.2 m/s (insurance practice); DMI's meteorological definition is 24.5 m/s.
  - **Cloudburst (skybrud):** rain under 15 mm in 30 min is not a "violent cloudburst"; older
    rulings also cite ~40–50 mm/day.
- A report that says "station X, 4.2 km NE, gust Y m/s / Z mm in 30 min" maps directly onto the
  policy wording.
- Volume: 8,806 homes had cloudburst water damage in 2024 (Forsikring & Pension via Bolius);
  2011 Copenhagen cloudburst: ~90,000 claims, ~DKK 6 bn.
- No DMI address product found. **Possible competitor:** forsikringsvejret.dk (address storm
  lookup, mentioned by an insurer) — not yet inspected.

**🇳🇴 Norway — good, wind only**
- Storm damage counts as a natural peril (Norsk Naturskadepool) only above **20.8 m/s**; measured
  wind is the reference. Exactly what the report documents.
- No paid MET Norway consumer certificate found.

**🇸🇪 Sweden — weak: the institute already sells this**
- SMHI **Försäkringsväder** for insurers: per-claim station lookups, next-day extreme-weather
  emails, radar + lightning, and signed weather certificates (väderintyg) usable in court, including
  return-period statements ("a 50-year rain"). 3 or 6 free certificates/year by tier.
- Hard to beat the national institute's own signed certificate.

**🇫🇮 Finland** — good data, no demand evidence or threshold-based claim rules found. Deprioritise.

### Nordic risks
- **Data quality / liability:** DMI raw data is unchecked. Evidence reports need a clear disclaimer
  and plausibility checks.
- **Language:** reports likely need Danish/Norwegian to be accepted.
- **Attribution:** CC BY requires source credit on every report — easy.

### Suggested Nordic pilot (if/when)
Denmark, one region: DMI stations + DMI lightning, checks against 17.2 m/s and 15 mm/30 min,
Danish-language PDF, distance/bearing as in the US report. Sell a handful — the same test as the US.

---

## 2. More than one source per report

### Not GFS / forecasts
GFS is a forecast model. "The model predicted 25 m/s" is easy for an adjuster or opposing expert to
dismiss, and the brief excludes forecast data. The useful form of the idea is **reanalysis** (models
re-run after the fact with observations assimilated).

### Order sources by strength of evidence
The current code promises *"Every value names the one station that measured it. Nothing is blended
or interpolated."* (`wxreport/sources/ghcnh.py`). Keep that promise by putting each tier in its own
labelled section, never merging values across tiers:

1. **Measured** — station reading with distance and bearing (today's headline; GHCNh, Storm Events,
   NWS warnings and Local Storm Reports).
2. **Remote-sensed over the address** — radar, satellite lightning, radar hail size.
3. **Modelled at the address** — reanalysis, labelled as a model estimate.

Then a **corroboration line**: do the sources agree? e.g. "Station 6 km NE measured 22 m/s;
reanalysis at your address estimates 19–24 m/s." Showing disagreement openly is the legal protection.

### What the US report uses today (from `wxreport/sources/`)
- `ghcnh.py` — NOAA GHCNh hourly station measurements
- `stormevents.py` — NCEI Storm Events
- `nws.py` — NWS warnings (VTEC, via IEM) + Local Storm Reports
- `swdi.py` — NEXRAD Level-III hail detections per storm cell; **NLDN lightning only as daily
  counts per 0.1° tile** (~6–7 mi), because point-level NLDN is Vaisala-licensed

### US additions (best next step — free, US-only, fit the brief's gaps)

| Source | Adds | Notes |
|---|---|---|
| **GOES GLM** satellite lightning | **Time-stamped, located flashes** — upgrades today's daily tile counts | Free on AWS (`noaa-goes16/18/19`), since 2017. ~20 s NetCDF files over the full disk: query narrow windows. ~8 km pixels, so "flash within N km", not "strike at the roof". |
| NOAA **MRMS MESH** | Gridded maximum hail size over the address (~1 km), vs today's per-cell NEXRAD detections | Free on AWS (`noaa-mrms-pds`) from **Oct 2020**; MYRORSS covers 1998–2011; 2012–2020 patchy. Attribution requested. |
| ERA5 reanalysis (tier 3) | Modelled wind/precip at the address, any date | ~31 km grid — context only. Licence not yet confirmed. |

### Nordic additions

| Source | Adds | Notes |
|---|---|---|
| National radar (DMI/SMHI/FMI/MET) | Rainfall over the address — key for Danish cloudburst claims | FMI radar archive on AWS, CC BY 4.0. Others' archives not checked. |
| **CERRA** reanalysis (5.5 km, Europe) | Modelled wind/rain at the address | Data **ends June 2021**; extension planned, not live. Licence not confirmed. |
| ERA5 | Same, current to within days | Coarse, context only. |
| **MTG Lightning Imager** (EUMETSAT) | Second lightning source next to national networks | Operational since **late 2024**; account needed; commercial terms unconfirmed. |
| OPERA pan-European radar | — | **Avoid**: commercial use of composites needs an ECOMET licence. |

---

## 3. Open questions / to verify before building

- Has the US "sell a handful vs StormRecord" test been run, and with what result?
- Decision to relax the brief's "US-only" and "three inputs" limits.
- ERA5, CERRA and EUMETSAT MTG licence terms for commercial resale (check the CDS dataset pages and
  eumetsat.int/eumetsat-data-licensing).
- What forsikringsvejret.dk offers, who runs it, and its price.
- FMI lightning historical range and query limits; MET Norway UALF parsing.
- ESWD commercial fee.
- MRMS MESH coverage 2012–2020.

---

## Sources

**Nordic data:** [SMHI lightning API](https://opendata.smhi.se/apidocs/lightning) ·
[SMHI metobs API](https://opendata.smhi.se/apidocs/metobs) ·
[DMI Getting Started](https://www.dmi.dk/friedata/dokumentation/getting-started) ·
[DMI QGIS guide (lightning)](https://opendatadocs.dmi.govcloud.dk/Guides/QGIS_Plugin_Guide) ·
[DMI Terms of Use](https://www.dmi.dk/friedata/dokumentation/terms-of-use) ·
[Frost how-to](https://frost.met.no/howto.html) ·
[Frost data clarifications](https://d73bbb8.frost.met.no/dataclarifications.html) ·
[FMI open data licence](https://en.ilmatieteenlaitos.fi/open-data-licence) ·
[FMI on AWS](https://en.ilmatieteenlaitos.fi/open-data-on-aws-s3) ·
[fmiopendata](https://github.com/pnuu/fmiopendata) ·
[wetterdienst FMI](https://wetterdienst.readthedocs.io/en/latest/data/provider/fmi/observation/index.html)

**ESWD:** [User agreement (non-commercial, 2026-04-17)](https://www.essl.org/cms/wp-content/uploads/20260417_ESWD-User-Agreement-for-Non-Commercial-Use.pdf) ·
[ESSL ESWD page](https://www.essl.org/cms/?p=169)

**Demand / claim rules:** [SMHI Försäkringsväder](https://www.smhi.se/professionella-tjanster/sakerhet-och-beredskap/smhi-forsakringsvader) ·
[SMHI 2021 update](https://www.smhi.se/nyheter/nyheter/2021-09-29-mer-anvandarvanlig-tjanst-for-smhis-forsakringsvader) ·
[Ankenævnet ruling (skybrud/storm)](https://www.lovguiden.dk/dokument/ankenaevnet-forsikring/30-11-2011-afvisning-af-dækning-for-nedbørsskade-uenighed-om-skybrud-og-storm) ·
[Ankenævnet practice overview](https://www.lovguiden.dk/praksisoversigt/stormskade-skybrud-piskeregn) ·
[Deas (forsikringsvejret.dk, 17.2 m/s)](https://deas.dk/?p=9294) ·
[ing.dk storm thresholds](https://ing.dk/artikel/lufthavn-kritiserer-dmi-storm-prognoserne-holdt-ikke-stik) ·
[Bolius 2024 cloudburst figures](https://www.bolius.dk/din-husforsikring-kan-stige-paa-grund-af-mange-skybrud-99831) ·
[2011 Copenhagen cloudburst](https://en.wikipedia.org/wiki/2011_cloudburst_in_Denmark) ·
[Smartepenger: naturskade 20.8 m/s](https://www.smartepenger.no/skadeforsikring/3241-naturskadeforsikring) ·
[Norsk Naturskadepool annual report 2025](https://res.cloudinary.com/forsikringsdrift/image/upload/05-2026-Attachment-1-Annual-report-2025-for-Norwegian-Natural-Perils-Pool.pdf) ·
[Munich Re hail research 2025](https://www.munichre.com/en/insights/natural-disaster-and-climate-change/hail-research-2025.content.html) ·
[PartnerRe on European hail losses](https://www.partnerre.com/perspectives/the-contribution-of-climate-change-to-europes-increasing-hail-losses/)

**Extra sources:** [CERRA (CDS)](https://cds.climate.copernicus.eu/datasets/reanalysis-cerra-single-levels) ·
[C3S CERRA](https://climate.copernicus.eu/copernicus-regional-reanalysis-europe-cerra) ·
[EMS2026 CERRA extension](https://meetingorganizer.copernicus.org/EMS2026/EMS2026-590.html) ·
[EUMETSAT MTG dissemination](https://www.eumetsat.int/first-dissemination-operational-data-meteosat-third-generation) ·
[MTG LI gridded data guide](https://satellite-resources.readthedocs.io/en/latest/MTG_Lightning_Imager_gridded_data.html) ·
[IEM MRMS archives](https://mesonet.agron.iastate.edu/archive/mrms.php) ·
[NOAA MRMS on AWS](https://aws.amazon.com/marketplace/pp/prodview-6odvdc4md2jjc) ·
[MYRORSS](https://ams.confex.com/ams/38RADAR/webprogram/Handout/Paper320843/222_ortega_et_al_myrorss.pdf) ·
[GOES GLM L2 (data.gov)](https://catalog.data.gov/dataset/noaa-goes-r-series-geostationary-lightning-mapper-glm-level-2-lightning-detection-events-g) ·
[GOES on AWS](https://aws.amazon.com/marketplace/pp/prodview-guxsdrz6onxd6) ·
[EUMETNET OPERA](https://www.eumetnet.eu/?p=1081) ·
[OPERA ORD HVD summary](https://eumetnet.github.io/openradardata-documentation/ORD_HVD_summary/)
