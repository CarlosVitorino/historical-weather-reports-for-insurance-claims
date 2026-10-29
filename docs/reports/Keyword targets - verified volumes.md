# Keyword targets — verified volumes (2026-10-29)

Fills the gap the competitor research left open: *"no verified volumes for any core term"*
(`docs/research_notes/Competitor SEO and ads positioning/keywords_serp.md`). Volumes, difficulty and
CPC below are from DataForSEO via OpenSEO (US, location 2840, English). Saved to the OpenSEO project
"Weather Evidence" (`weatherevidence.com`), tagged `final` + `tier:p0|p1|p2`.

---

## The headline

**The market is smaller than the competitor research implied — and it is hail-centric.** Most
"insurance claim" phrasings the research flagged as the money terms (`weather report for insurance
claim`, `storm report by address`, `historical weather data for insurance claim`, `how to get NOAA
weather data for insurance claim`) are **below Google Ads' measurable floor** — DataForSEO returns no
volume for them. That does not mean no one searches them; it means they are too long-tail to measure
in Ads data. The measurable, winnable demand sits in the **"hail report by address"** and
**"verification report"** families.

Demand is also **event-driven** (spikes in the days/weeks after a storm), so Google Trends' 5-year
direction is a weak signal here — the "rising" terms below are rising from near-zero. Volumes and
KD are the reliable inputs, not trend direction.

---

## Final list (15 keywords)

### P0 — win first (5): the money terms, winnable KD, high CPC

| Keyword | Vol | KD | CPC | Intent* |
|---|---|---|---|---|
| hail report by address | 140 | 0 | 4.72 | commercial |
| hail history by address | 70 | 4 | 5.15 | commercial |
| hail verification report | 40 | 2 | 8.05 | commercial |
| wind verification report | 20 | 0 | 16.27 | commercial |
| lightning strike report by address | 20 | 28 | 2.98 | commercial |

These are the product's core "one address, one date" queries, all with low difficulty and real CPC
(advertisers pay for them). Map to the home/product page and a free-preview address form.

### P1 — next (5): entry + local + the explainer

| Keyword | Vol | KD | CPC | Intent* |
|---|---|---|---|---|
| hail report near me | 260 | 28 | 3.98 | informational |
| weather history by date | 880 | 55 | 2.25 | informational |
| hail map by address | 30 | 28 | 3.93 | informational |
| did it hail in my area | 20 | 28 | — | informational |
| certified weather report | 50 | 47 | 9.89 | informational |

`weather history by date` (880) is the largest measurable term but KD 55 — use it as a top-of-funnel
entry, not a win-first target. `certified weather report` is the "Is this certified?" explainer page
(high CPC, and the legally-safe way to intercept the term).

### P2 — reserve (5): harder, or below floor

| Keyword | Vol | KD | CPC | Note |
|---|---|---|---|---|
| historical weather report | 320 | 70 | 5.87 | real volume, hard KD |
| past weather by zip code | 40 | 56 | — | hard KD |
| weather report for insurance claim | — | — | — | zero in Ads data, but the exact product framing |
| storm history by address | — | — | — | zero in Ads data |
| wind report by address | — | — | — | zero in Ads data |

\* DataForSEO labels most of these "informational" (a default when paid-ad data is thin). The CPC
figures show the P0 terms are effectively **transactional** — someone searching "hail report by
address" wants to buy a report. I saved P0 with `intent: commercial` for that reason.

---

## Below-threshold strategic terms (content targets, not volume keywords)

These returned zero in Ads data but are worth building **pages/guides** for, because the competitor
research shows the SERPs are weak or vendor-only:

- **Guides (honest, free-data-first):** `how to get NOAA weather data for insurance claim`,
  `how to prove hail damage to insurance`, `how insurance companies verify weather claims`,
  `how to find past weather for a date`.
- **The "certified" explainer:** `certified weather report cost`, `NOAA certified weather data`.
- **Competitor:** `stormrecord alternative`, `hailtrace alternative`.

These are the content play from `docs/reports/Competitor SEO and ads positioning.md` §"Storm-event
pages are the unclaimed SEO slot" — they win by being the plain-English answer the SERP lacks, not by
volume.

---

## The strategic read

1. **Own "hail report by address"** (140, KD 0) — the proven money term, winnable, and the query the
   direct competitor StormRecord already ranks for. It should be the home page's exact-match target.
2. **Own the "verification report" cluster** (`hail verification report`, `wind verification report`,
   `lightning strike report by address`) — these are low-KD, high-CPC, and match the product's
   multi-peril differentiator (StormRecord leaves hail/lightning "Not queried").
3. **"weather report for insurance claim" is not the SEO lever** the research assumed — it's below the
   measurable floor. Keep it in the copy and page title (it's the product framing), but don't expect
   to rank it alone; it rides on the hail/wind/lightning terms above.
4. **Guides + storm-event pages are the volume play**, not the "by address" terms — consistent with the
   existing report's conclusion that date-specific storm pages are the unclaimed slot.

One unchanged caveat from the existing research: **`weather report for insurance claim` and
"certified" language carry legal risk** (`docs/reports/Competitor SEO and ads positioning.md` §Legal
wording). This keyword list does not change that; the "certified weather report" term should be
intercepted with a "not certified — here's how to get NCEI certified data ($180+)" explainer, never
with a claim of certification.

---

## Where it lives

- **OpenSEO**: project "Weather Evidence" (`weatherevidence.com`), 15 keywords tagged `final` +
  `tier:p0|p1|p2`, with metrics.
- **This file** is the readable record; the competitor/ad research remains in
  `docs/research_notes/Competitor SEO and ads positioning/` and `docs/reports/`.
