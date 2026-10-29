# SEO & AI-visibility plan — Weather Evidence (revised 2026-10-29)

## Where we are

Live, well-built, at search-near-zero (12 pages indexed, ~110 impressions/28 days). Keyword work is
done and the conclusions hold:

- The market is **hail-centric but tiny**. `hail report by address` (140, KD 0) is the only measurable
  money term; `weather report for insurance claim` is below the Ads floor. That phrasing is honest
  framing, not a keyword.
- **"Historical weather data"** terms are data/API intent, not report-buying — excluded.
- **International, multi-day, bulk and API** all have no measurable search demand — excluded.
- **Separate per-peril landing pages** = doorway pages — excluded.
- After the GEO research: **exact-match keywords are context signals, not ranking signals.** AI
  (Perplexity, ChatGPT, Claude, Gemini) cites pages that *answer the question in quotable form*, not
  pages that repeat a phrase. All hail-led title/meta/schema over-optimization was reverted; the site
  copy is broad and honest again, and "hail" lives in the content as a topic.

**Principle: answer the real questions in self-contained, quotable sentences. Topical coverage,
clarity, and corroboration win — not keyword placement.**

---

## Priority 1 — Corroboration (off-page) — the biggest lever, currently absent

LLMs cite you because *other places mention you*. This is now the top priority and the one thing the
plan has never addressed.

1. **Get listed in the "best hail/weather report tools" roundups** the competitor research already
   found (HailMate, roofingsoftwareguide.com, and similar). One honest comparison mention outweighs
   ten keyword tweaks.
2. **Be present where adjusters/homeowners/roofers talk**: r/Insurance, r/Roofing, r/homeowners —
   honest answers under a real name, no astroturfing.
3. **Reviews**: a Trustpilot (or equivalent) listing, once there are real customers.
4. **Directory listings**: any weather/insurance/claims directories where AI actually looks for this
   category.

Measure by searching your key questions in Perplexity and ChatGPT and seeing whether "Weather
Evidence" shows up — and where it appears, and where it doesn't.

---

## Priority 2 — Optimize the answer pages (on-page, quick wins)

These are the pages AI cites, and two already rank:

- **`/certified-weather-records`** (already pos 8.3) — make the direct answer to *"certified weather
  report cost"* its own line ("NCEI charges ~$180+; ours is not certified — here's the link"). One
  quotable sentence, first.
- **`/methodology`** — this is your credibility/proof page. Ensure it leads with a self-contained
  "how it's built" summary that can be quoted as-is.
- **`/compare`** — add **named competitors** (StormRecord, HailTrace, AtmosDays, Stormview). AI and
  Perplexity love comparison tables; a neutral, sourced table is directly quotable.

---

## Priority 3 — Answer-block / quotable-copy pass (on-page, quick)

The single highest-value GEO tweak the site doesn't yet do consistently:

1. Add a **1–2 sentence answer block** under each page's H1 (homepage and guides) — a self-contained
   "what this is" that survives being lifted out, no pronouns, every fact names its subject.
2. **Audit copy for quotability**: each claim should stand alone when extracted. (The report PDF
   already does this — "each reading names its station and distance" — the web copy should match.)

The "What you get" question-headings and the FAQ are already correct; keep them.

---

## Priority 4 — Storm-event pages (unique data, later)

**`/storms/{state}/{county}/{yyyy-mm-dd}`**, built only where NCEI/SPC records exist.

This survives because it's **unique, non-commodity data** ("did it hail in [county] on [date]?") —
exactly the kind of first-hand content AI values and Google's scaled-content rules *don't* punish.
Never every city × every date; "no records" pages are the risk. Each page: event list with
times/sizes/gusts, nearest ASOS observations, map, preliminary-vs-final label, "check your address" CTA.

---

## Housekeeping (already done — don't redo)

- **AI crawlers**: `robots.txt` uses `User-agent: *`, only `/admin`/`/api`/`/webhooks` blocked — AI
  bots are allowed. ✅
- **Server-side rendering**: FastAPI + Jinja2. ✅
- **Structured data**: `Product`/`Offer`, `Organization`, `Article`, `BreadcrumbList` already present.
  Housekeeping, not a lever — don't invest more.
- **Legal wording**: "not certified records or expert opinions" — keep.

---

## Measurement

1. **Search Console**: re-check striking distance in 2–4 weeks; also watch the new **Generative AI
   performance report** in Search Console for AI-overview impressions.
2. **AI citation check** (manual, monthly): search your top questions in Perplexity, ChatGPT, and
   Claude — is Weather Evidence cited? Which pages? What's missing?
3. **Done when**: the homepage shows impressions for the hail/weather cluster, `/certified-weather-records`
   holds top 5, and Weather Evidence starts appearing in AI answers for "weather report for insurance
   claim" and "did it hail at my address".
