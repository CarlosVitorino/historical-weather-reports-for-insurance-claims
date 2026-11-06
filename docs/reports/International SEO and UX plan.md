# International SEO and UX plan (2026-11-06)

How weatherevidence.com should present itself once there is more than one market. Companion to
`International expansion and data sources - Nordics.md` (which market, which data) and
`SEO implementation plan.md` (current US SEO). Planning only; no code changed.

## Where the site is today (from the code)

- One language (`<html lang="en">`), one currency (`PRICE = "$9.99"` in `content.py`, `priceCurrency:
  "USD"` in `seo.py`), imperial units (`units.py`: "US claim files read imperial").
- Addresses are US-only end to end: US Census geocoder (`geocode.py`) and Geoapify autocomplete
  filtered to `countrycode:us` (`suggest.py`).
- Programmatic pages `/storm-reports/{state}/{city}` are built from US Storm Events / Local Storm
  Reports (`storm_pages.py`, `data/us_cities.csv`).
- Report-type pages (`report_pages.py`: car hail, car accident, frozen pipes, slip-and-fall) and
  guides (`content.py`) are US-specific in wording (NWS, NOAA, NCEI certified records, US claim
  practice).
- `docs/build-plan.md` notes the **EU withdrawal-right consent is not built** "because buyers are
  US-only". That stops being true the day a Danish consumer can buy.

## Principles

1. **Two different things decide a report: the address and the reader.** The address's country
   decides the data sources, thresholds and claim rules. The visitor's language decides the site and
   PDF language. Don't conflate them (a German lawyer may order a Danish report; a Dane abroad may
   browse from Spain).
2. **Localise, don't translate.** Each market's pages answer that market's claim questions
   (skybrud ≥ 15 mm / 30 min, storm ≥ 17.2 m/s in DK; ≥ 20.8 m/s for Naturskadepool in NO), cite its
   institutions (DMI, Ankenævnet for Forsikring, MET Norway, Finans Norge) and use its claim
   vocabulary. A translated US page about NOAA and NWS warnings is useless to a Dane — and Google
   treats thin translations as low value.
3. **Don't touch what ranks in the US.** US pages stay where they are, at the root.
4. **Same quotable-answer recipe as the US plan.** Self-contained sentences that AI answers can cite.

## URL structure — recommendation: subfolders per market

| Option | Verdict |
|---|---|
| **Subfolders** `weatherevidence.com/dk/` (Danish), `/no/` (Norwegian) | **Recommended.** Inherits the domain's authority, one deploy, one Search Console property with per-folder filters. |
| ccTLDs `weatherevidence.dk`, `.no` | Strongest local trust signal, but each starts at zero authority and needs its own backlinks. Buy them now and 301 to the subfolder; revisit if a market takes off. |
| Subdomains `dk.weatherevidence.com` | No advantage over subfolders here. |
| `?lang=` parameters | No. |

- US stays at `/` (no `/us/` move: it would reset rankings for no gain).
- Folder = market, not just language: `/dk/` is Danish-language **and** Danish addresses/DKK/DMI.
  If an English version of a Nordic market is ever needed, use `/dk/en/`.
- Localised slugs inside each folder: `/dk/stormrapporter/…`, `/dk/skybrud/…`, not `/dk/storm-reports/`.

### hreflang
- Only between pages that are genuinely equivalent (home ↔ home, order ↔ order, a guide that exists
  in both). Most market pages will have **no** equivalent and get no hreflang — that's correct.
- Values: root `en-US`, `/dk/` `da-DK`, `/no/` `nb-NO`, plus `x-default` → root home.
- Reciprocal links on every page in the set, and in the sitemap (`seo.sitemap` gets an
  `xhtml:link` per alternate). Self-referencing canonical per page; never canonicalise a market page
  to the US page.

### Structured data per market
- `Product.offers` per market: `priceCurrency` (DKK/NOK), price incl. VAT, `areaServed`.
- `inLanguage` on Articles. Organization stays one entity.

## UX

### Market selection
- **No automatic IP or language redirects.** They break crawling (Googlebot crawls mostly from the
  US) and annoy travellers and foreign professionals.
- Instead: a **dismissible suggestion banner** when `Accept-Language` or the visitor's country
  differs from the page's market ("Denne side er til amerikanske adresser. Se Weather Evidence for
  Danmark →"). Remember the choice in a cookie.
- A **country/language switcher** in the header and footer (flag + country name, not flags alone),
  linking to the equivalent page if one exists, else that market's home.

### Order flow
- The order form lives inside each market folder and is locked to that country's addresses:
  - Denmark: the official address register (Danmarks Adresser via Dataforsyningen/Datafordeler —
    free, government; check the current endpoint, the old DAWA service is being retired).
  - Norway: Kartverket's address API (Geonorge).
  - Keep Census + Geoapify for the US.
- If someone types a foreign address into the wrong market's form, say so and link to the right
  market, rather than "address not found".
- Prices shown in local currency, **including VAT**, with the PDF language matching the site.
- Metric units, local date format (6.11.2026), 24-hour times, local time zone on the PDF.
- **EU consumer law (Denmark, Finland, Sweden):** before payment, the buyer must explicitly consent
  to immediate delivery and acknowledge losing the 14-day withdrawal right for digital content. This
  is the item build-plan.md left for the lawyer (L1–L4) — it becomes required. Check creem's
  merchant-of-record handling of EU/Norwegian VAT. Norway is EEA: similar consumer rules.
- Legal pages (terms, privacy, imprint) per market language; the GDPR basis is the same site-wide.

### The report itself
- Same structure and promise ("every value names the station that measured it, with distance and
  bearing") — that is the product, in every market.
- Per-market sections replace US ones: e.g. DK has no NWS warnings or Storm Events, so instead a
  **threshold check against the policy definitions** ("Storm per forsikringspraksis: ≥ 17,2 m/s —
  målt 23,4 m/s ved station X, 4,2 km NØ") and a cloudburst 30-minute check.
- State what the records do **not** establish, as in the US report — even more important where DMI
  raw data isn't quality-controlled.

## Content per market (Denmark as the first example)

Equivalents of the US content, built around Danish claims:

| US today | Denmark version |
|---|---|
| `/storm-reports/{state}/{city}` (Storm Events, LSR) | **Storm and cloudburst days by municipality** from DMI station data crossing 17.2 / 24.5 m/s or 15 mm / 30 min. No Storm Events equivalent exists, so the pages must come from measurements. |
| — | **Named-storm pages** (big storms get names people search for; e.g. Floris and Amy hit Norway in 2025): "Stormen X: målt vind ved din adresse". Strong, timely search and news interest after each storm. |
| Car hail damage report | Skybrud / water-in-basement report (the biggest DK peril) |
| Wind / roof guide | Stormskade: how insurers and Ankenævnet decide (17.2 vs 24.5 m/s, burden of proof) |
| NCEI certified records page | "DMI-data som dokumentation" — what DMI publishes, what it doesn't certify |
| — | Lightning (lynnedslag) — hypothesis, test with keyword data |

## Keyword research before building

`International demand check.md` found no demand abroad for the *translated US hail term*, and
`SEO implementation plan.md` therefore excluded international. That check covered DE/ES/PT/FR/AU and
hail only — **the Nordics and the wind/cloudburst angle haven't been tested.** Run the same
one-bulk-call DataForSEO check per market before writing pages, e.g.:

- 🇩🇰 `stormskade dokumentation`, `skybrud forsikring`, `hvor meget blæste det`, `vindstyrke [by]`,
  `dmi vejrdata historisk`, `nedbør skybrud [by]`, `lynnedslag forsikring`, `stormen [name]`
- 🇳🇴 `naturskade storm`, `vindstyrke historikk`, `hvor mye blåste det`, `stormen [name]`

If volumes are near zero, the market can still work through **insurers, loss adjusters and claims
lawyers directly** (B2B outreach), where SEO matters less.

## Code shape (when it's time to build)

- A `Market` definition: country code, folder, language, currency + price, units, time zone rules,
  geocoder, data sources, thresholds, legal texts, report types. US becomes the first `Market` with
  today's values, so the US path is unchanged.
- Strings in per-language files instead of inline copy; page copy written per market, not machine
  translated.
- `seo.py`: sitemap with hreflang alternates, per-market Product schema.
- Analytics and Search Console segmented per folder.

## Suggested order

1. Danish + Norwegian keyword check (cheap; decides SEO vs B2B-first).
2. Danish data prototype (DMI stations + lightning → PDF) — proves the report before any site work.
3. `Market` abstraction with US as the only market (no visible change; tests stay green).
4. `/dk/` home, order flow, legal pages incl. withdrawal-right consent, DKK pricing.
5. Danish guides + storm/cloudburst-day pages + named-storm pages.
6. Banner + switcher, hreflang, sitemap.
