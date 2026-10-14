# Build plan — Historical weather reports for insurance claims

Size: **First version**. The smallest product a real person can use end to end, built well enough that you can learn from their use of it.

## 1. Plan

### The idea in my own words
A claims adjuster, public adjuster or policyholder has a loss at a specific address on a specific date. They need one PDF that shows what the free US government records say happened *at or near that address on that day*. It must say which station measured each value, how far away (and in which direction) each measurement or report is, and what the records do **not** establish. The free data exists, but it is spread across awkward formats. A forensic meteorologist costs hundreds or thousands of dollars. The competitor (StormRecord) blends station data through Visual Crossing and skips four things. We sell those four things for $9.99:

1. **Station-pinned measurements.** Every value comes from one named GHCNh station, with its ID and QC flags. Nothing is blended.
2. **Distance and bearing.** Every station, storm report and hail or lightning point gets "x.x mi NNW of the loss site".
3. **NCEI Storm Events database.** The official, reviewed record, which is separate from the preliminary LSRs.
4. **Hail and lightning feeds.** NEXRAD hail signatures and lightning counts near the site.

We must also match what the sample already has: LSRs with IDs and reporters, NWS bulletins with VTEC IDs, timezone/DST handling, retrieval and generation times, and a canonical report ID.

### Assumptions (tell me if any are wrong)
- **A1.** v1 is an order page: the buyer enters address + loss date + email, pays $9.99 through **creem.io** checkout, and a creem webhook triggers report generation and delivery of a download link. The same generator is also a CLI for the founder. No accounts.
- **A2.** "Deterministic" means the same inputs plus the same frozen data snapshot give a byte-identical PDF. Raw source responses are stored with their retrieval time and a SHA-256. The report ID is derived from those values, so any report can be regenerated and verified later. The printed "generated" time is the snapshot time, not the wall clock.
- **A3.** ~~Single region~~ **Any US address** (decided by the founder; overrides the brief's "single region"). The first test case is Bloomington, IN, 2026-02-19, so it can be compared head-to-head with the StormRecord sample. Timezone is resolved offline from coordinates; the NWS office comes from the point.
- **A4.** Geocoding uses the US Census Geocoder (a government source, free, no key).

### Where the brief contradicts itself or the data
- **C1. "US government sources only" vs. matching the sample.** The sample's archived bulletins and LSRs come from the Iowa Environmental Mesonet (Iowa State University), not a government server. `api.weather.gov` keeps only recent alerts. Proposal: use IEM for archived NWS text (verbatim NWS products) and label it as such in the report.
- **C2. Lightning has no free federal point feed.** Point-level NLDN data is Vaisala's and is licensed. NCEI SWDI publishes only aggregated NLDN tile counts (0.1°/day). GOES GLM satellite lightning is free, but it is heavy NetCDF. Proposal: SWDI NLDN tile counts in v1, clearly labelled as coarse; GLM later if buyers ask. **Their redistribution terms need a legal check (see L2).**
- **C3. "Three free public inputs"** undercounts the sources the brief itself names. I read it as three delivery formats: the legacy NCEI token API, GHCNh hourly files, and Storm Events per-year gzip CSVs. Alerts, LSRs, SWDI hail/lightning and geocoding are extra free inputs. I am treating the "do not build" item as "no paid or proprietary feeds".
- **C4. Storm Events lags about 3–4 months.** For a loss last week the report must say "not yet published for this month", never "no events". Many claims are filed within weeks, so this limits gap #3 for recent losses.

### Legal (the stop condition)
The brief says to pin down the legal exposure before building. I can't give legal advice. These are the exposures I can see, for a lawyer to review **before the first sale**:
- **L1.** Reliance and misrepresentation if a claim is decided on the report. Mitigation: StormRecord-style "what this establishes / does not establish" language, plus terms of sale.
- **L2.** Data licensing. NOAA/NWS data is public domain. NLDN lightning (Vaisala) and IEM have their own terms, so republishing them in a paid product needs checking.
- **L3.** Naming StormRecord in comparative selling (trademark, comparative advertising).
- **L4.** Never presenting the report as a certified record or expert opinion. Expert testimony is out of scope.

If any of these comes back as a blocker, that is the stop condition, and I'll tell you before building more.

### Stack
**Python 3.11 + ReportLab + requests + pandas**, run with one command (`make report ADDRESS=... DATE=...`). ReportLab has an `invariant` mode that gives byte-identical PDFs, and Python is the natural fit for parsing GHCNh files and gzip CSVs. Raw responses are cached on disk under `data/snapshots/<report-id>/` with a manifest. No database is needed in v1. Tests run under pytest using recorded real responses as fixtures.

## 2. Foundation
- [ ] Python package `wxreport` with a CLI, `make setup` / `make report` / `make test`; FastAPI order-page skeleton (`make serve`).
- [ ] Census geocoder → lat/lon, county, timezone; local-date window with DST (23/24/25-hour days).
- [ ] Snapshot store: raw bytes + retrieval time + SHA-256 + manifest; canonical report ID.
- [ ] A skeleton PDF (cover + sources page) generated deterministically.
- Done when: `make report` produces an identical PDF twice from the same snapshot.

## 3. Core: the report
- [ ] GHCNh: nearest stations with distance and bearing, hourly table from the nearest complete station, QC flags, ISD fallback.
- [ ] NWS bulletins (with VTEC) and LSRs, each with distance and bearing from the site.
- [ ] Storm Events: county and nearby events with distance and bearing, plus "not yet published" handling.
- [ ] SWDI NEXRAD hail signatures and lightning counts near the site.
- [ ] Full PDF matching or beating every section of the sample. First real report: Bloomington, IN, 2026-02-19.
- Done when: that report is generated from live data and compared side by side with the sample.

## 4. Harden
- [ ] Failures a user will meet: unmatched address, address outside the region, future date, missing station hours, a source being down (report says "unavailable", never zero), Storm Events lag.
- [ ] Tests for the core path from recorded fixtures; determinism test.
- Done when: you are comfortable sending a report to a real adjuster.

## 5. Ship and learn
- [ ] creem.io checkout (test mode, then live) + webhook → generate → download link; order log (address, date, report ID, paid, feedback).
- [ ] Lawyer review of L1–L4 → stop / go.
- Done when: there is evidence for or against adjusters paying $9.99.

## Decisions
- Python + ReportLab: deterministic PDF output and the best fit for parsing the source formats.
- Payments via creem.io (founder's choice): a minimal order page + webhook fulfilment; this is the order form, not a marketing site.
- Nationwide coverage from v1 (founder's choice): all sources are national anyway; costs only station-inventory and timezone lookups.
- Census Geocoder, with an operator coordinate override for addresses it can't match (rural routes, new builds); the PDF says when coordinates were supplied manually.
