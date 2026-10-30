# Storm Reports — plan (2026-10-30)

A public section, `/storm-reports`, that grows one city at a time as storms happen, built from public NWS/NCEI
records. It is the organic-traffic lever from `docs/reports/Next steps - getting traffic.md` §1, reshaped by the
keyword and SERP checks below.

## Decisions (founder, 2026-10-30)

| # | Decision | Evidence |
|---|---|---|
| 1 | Section name **Storm Reports** | `storm reports` 4,400/mo KD 13; `storm log` 30/mo; `storm archive` no data (DataForSEO, US) |
| 2 | Titles lead with **city names + "hail storm"**, never "{county} hail" | SERP for `tarrant county hail` is 13 jail results; `collin county hail` 14,800/mo is "jail" volume |
| 3 | The indexed unit is the **city**, not the storm day | `denver hail storm` 1,000/mo (peak 90,500), `dallas hail storm` 480 (peak 22,200); `dallas hail storm 2025` 10, `denver hail 2025` 10 |
| 4 | A city page is created on the city's **first hail ≥ 1 in or tornado** | Wind is 24,100 of the 31,959 significant 2026 reports but barely searched (`wind damage dallas` 10/mo) |
| 5 | Pages start from storms on or after **2026-10-21**; cities of **50,000+** only | Founder: "5 or 10 pages max for now"; storms 6 months old have little search demand |
| 6 | **Major storm** is a tag on a city's storm day, not a page | As separate pages, 62 of 89 "major storms" in 2026 hit one city and duplicated its page; 3 hit 5+ cities |
| 8 | City **centre = Wikidata coordinate** (downtown), **radius scaled to city size** (8–20 mi) | Census internal points were off (Phoenix 8.6 mi north of downtown, San Francisco offshore); a fixed 8 mi from downtown Phoenix missed north Phoenix |
| 7 | The section is a strict tree: **index → state → city** | Founder review 2026-10-30: cross-links between storm and city pages made it easy to lose track |

Rejected along the way: one page per storm day per region (169 pages for Dallas–Fort Worth alone; nationwide about
13,000 a year), and a launch from 2026-01-01 (about 308 city pages at once).

## What exists

| Page | URL | Exists when | Indexed when |
|---|---|---|---|
| City | `/storm-reports/tx/plano` | First hail ≥ 1 in or tornado within 8 mi on/after 2026-10-21 | 3+ storm days since 2021 |
| State hub | `/storm-reports/az` | The state has a city page | Always |
| Index | `/storm-reports` | Always | Always |
| City page, another storm day | `/storm-reports/tx/plano?day=2024-06-02` | Any storm day of a city with a page | Never (canonical to the city page) |
| Filtered views | `/storm-reports?period=all&kind=major&q=plano` | Any filter, sort or page | Never (canonical to the base URL) |

The index and each state page are one table: date, city, largest hail, strongest wind, tornadoes, with a **Major
storm** tag when that city had hail ≥ 2 in or a tornado. Filters (city search, state, period, storm type) and column
sorting are plain GET links, so they work without JavaScript; with it, a filter applies as soon as it changes. Default
view: the last 30 days, newest first. On phones each row becomes a card. A city page has the city's record at the top (a labelled band: storm days, hail days, largest hail, tornado days since
2021, within its radius), then a workspace: the list of storm days (sticky, left) and the picked day as a card (dark
header with the date; that day's hail, wind, tornadoes and report count; map; reports; NWS text; "check an address on
this date"). The latest storm is the default; picking another day swaps the card in place and sets `?day=`.

At launch (data through 2026-10-30): 7 city pages (Phoenix, Glendale, Flagstaff AZ; El Paso TX; Santa Fe NM;
West Palm Beach, Palm Beach Gardens FL); Phoenix, Glendale and Santa Fe are tagged Major storm.

Expected growth, from the 2026 simulation (hail + tornado trigger, 50,000+ cities): about 308 city pages a year,
most in March–July, a handful a month in winter.

## Data and lifecycle

| Source | Used for | Lag |
|---|---|---|
| NWS Local Storm Reports, via Iowa Environmental Mesonet (`/geojson/lsr.php`, national) | **Preliminary** reports | Minutes |
| NCEI Storm Events Database (yearly CSV, national) | **Reviewed** reports | 2–4 months |

1. A storm first appears from Local Storm Reports, labelled *preliminary*.
2. When NCEI publishes that month, its records replace the month's Local Storm Reports and the label becomes
   *reviewed*.

The job runs inside the server process (like `housekeeping.py`): Local Storm Reports for the last 3 days every
hour, NCEI's file listing once a day. `wxreport storms backfill` does the first load (about a minute, 185,000
reports for 2021–2026). Data lives in `DATA_DIR/storms.db` and can always be rebuilt, so it is not backed up.

## Wording

Same rules as the rest of the site: independent, not affiliated with NOAA or NWS; "reports", never "official" or
"certified"; preliminary data says so. Every page offers the address-level report for a date as a box, not as the
point of the page.

## Next

1. Deploy, submit the sitemap, and watch Search Console for 4–6 weeks: indexing, impressions on city queries.
2. Then decide: lower the population cut-off (10,000+ is 3,206 cities), add strong wind as a trigger, or keep going.
3. Later, maybe: outbreak pages for storms that hit 5+ cities (3 in 2026: Chicago suburbs on Mar 10, Jun 11, Jul 27).
4. Open: the free "storm history by address" tool (one page aimed at `hail report by address`, `hail history by
   address`), proposed 2026-10-30, not yet decided.
