# SEO & AI-visibility plan — Weather Evidence (revised 2026-10-29)

## Where we are

Live, well-built, at search-near-zero (12 pages indexed, ~110 impressions/28 days). The keyword
investigation and the GEO (generative-engine) research both concluded, and the conclusions hold:

- The market is **hail-centric but tiny**. `hail report by address` (140, KD 0) is the only measurable
  money term; `weather report for insurance claim` is below the Ads floor — honest framing, not a keyword.
- **"Historical weather data"** terms are data/API intent, not report-buying — excluded.
- **International, multi-day, bulk, and API** have no measurable search demand — excluded.
- **Separate per-peril landing pages** = doorway pages — excluded.
- **Exact-match keywords are context signals, not ranking signals.** AI (Perplexity, ChatGPT, Claude,
  Gemini) cites pages that *answer the question in quotable form*. All hail-led title/meta/schema
  over-optimization was reverted; the copy is broad and honest, and "hail" lives in the content as a topic.

**Principle: answer the real questions in self-contained, quotable sentences — and classify content by
the buyer's *case*, not by keyword.**

---

## Done — 2026-10-29

1. **Reverted hail-led over-optimization** — `<title>`, meta description, and Product structured data are
   back to broad wording ("Weather report by address…", "Weather Evidence report"). Syntax verified.
2. **Certified page** (`/certified-weather-records`) — added the direct, quotable answer to
   "certified weather report cost": *"about $180 for the first 40 pages… A Weather Evidence report is
   $9.99 and is not certified"* (NCEI fee verified), plus a quotable-copy fix ("A Weather Evidence report"
   instead of "Our report").
3. **Three case guides added** to `content.py` (now 6 guides total), each written to the recipe below:

| Guide | Path | The hook |
|---|---|---|
| Did it hail at your address? | `/guides/hail-damage-claim` | "Steps 2–6 are yours with a camera; Step 1 (prove the storm) is what our report does in a minute." |
| Lightning strike near your house? | `/guides/lightning-damage-claim` | "Check the public counts for $9.99 before you pay $95 for an exact strike report." |
| How insurance companies verify weather claims | `/guides/how-insurers-verify-weather-claims` | "See what the adjuster sees, before they do." |

These are served automatically (routes + guides index + sitemap, since they're in `GUIDES`).

---

## The case-guide recipe (the reusable pattern)

Distilled from researching how the best guides in this space (ClaimClosed, LegalClarity, state DOI
guides) actually convert:

1. **Short answer first** — the lede states the whole thing in two sentences.
2. **Numbered, concrete steps** — real specifics (hail-size thresholds, the 10×10 chalk test square,
   "check the soft metal first", hail-vs-wear table), so it genuinely helps someone do it themselves.
3. **The report is the shortcut for exactly one step** — the weather-data step ("prove the storm") — never
   a fake substitute for the whole process. This keeps it honest and legally safe.
4. **Adapt the hook to the case's reality** — hail = the tedious distance-measuring step; lightning =
   the $95-vs-$9.99 price check; insurer-verification = "see what they see".

---

## Remaining priorities

### Priority 1 — Corroboration (off-page) — the biggest lever, still open

LLMs cite you because *other places mention you*.

1. Get listed in the "best hail/weather report tools" roundups (HailMate, roofingsoftwareguide.com).
2. Be present where adjusters/homeowners/roofers talk: r/Insurance, r/Roofing, r/homeowners — honest
   answers, no astroturfing.
3. Reviews (Trustpilot or equivalent) once there are real customers.
4. Directory listings where AI actually looks for this category.

### Priority 2 — Storm-event pages (unique data, later)

`/storms/{state}/{county}/{yyyy-mm-dd}`, built only where NCEI/SPC records exist — unique, non-commodity
data ("did it hail in [county] on [date]?"). Never every city × every date.

### Priority 3 — Measurement

1. Search Console: striking distance in 2–4 weeks + the new **Generative AI performance report**.
2. Manual AI-citation check (monthly): search the top questions in Perplexity/ChatGPT/Claude — is Weather
   Evidence cited, where, and where not.

---

## Housekeeping (already done — don't redo)

- **AI crawlers**: `robots.txt` uses `User-agent: *`, only `/admin`/`/api`/`/webhooks` blocked. ✅
- **Server-side rendering**: FastAPI + Jinja2. ✅
- **Structured data**: `Product`/`Offer`, `Organization`, `Article`, `BreadcrumbList` present — housekeeping. ✅
- **Legal wording**: "not certified records or expert opinions" — keep. ✅

---

## Deliberately removed / ruled out

- Separate per-peril landing pages (`/hail-report`, `/wind-report`, `/lightning-report`) — doorway pages.
- "Historical weather" informational terms — data/API intent, tagged `awareness` in OpenSEO.
- Named-competitor comparison on the homepage — legal risk + zero-volume keywords; the generic
  "Free / Weather Evidence / Forensic" table stays.
- International, multi-day, bulk, API expansion — no measurable search demand.
