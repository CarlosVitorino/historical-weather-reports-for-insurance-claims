# Next steps — getting traffic (2026-10-30)

Companion to [`SEO implementation plan.md`](SEO%20implementation%20plan.md). That plan built the
foundation; this one answers the harder question — **how do we actually get traffic** — based on the
real Search Console numbers rather than the keyword theory.

---

## The honest state (Search Console, 2026-10-30)

- **0 clicks**, ~130 impressions over 28 days, 1 click total.
- Only **3 queries** have any impressions, all "certified"-adjacent: `certified weather reports`
  (pos 8.7), `weather data certification` (pos 19), `weather data for insurance claims` (pos 59).
- The six guides are barely indexed (4–6 impressions each).
- Striking distance: **zero**.

Two weeks of solid on-page work did not move this, because there is almost no steady search demand to
move. The best keyword (`hail report by address`) is 140 searches/month; the product's buyers search
in the week their claim is disputed, then it drops to nothing.

**Conclusion: SEO is the foundation, not the growth engine. Traffic for this product is spiky and
event-driven, and it has to be chased to where it spikes.**

---

## The reframe

Weather Evidence sells a $9.99 report that people buy in a specific moment — when a storm damage claim
is filed or disputed. Demand is not a steady trickle; it is a spike in the days after every hailstorm.
So "more traffic" means **being present at the moment of demand**, through four levers:

| Lever | What it is | Why it's the play |
|---|---|---|
| **Storm-event pages** | Programmatic `/storms/{state}/{county}/{date}` pages from NCEI/SPC records | The only real recurring organic traffic: "did it hail in [city] on [date]" is searched by thousands after every storm, and no one owns date-specific pages |
| **Community** | r/Insurance, r/Roofing, r/homeowners, roofing/PA forums | Buyers are already there asking the exact questions the guides answer — direct referral traffic *and* the corroboration that feeds AI citations |
| **Capped ads test** | $10–20/day, phrase/exact, ≤$1 CPC | Measures click-to-buy rate, and being *already running* means you capture the spike instead of missing it |
| **Partnerships** | Roofers, public adjusters | They buy per-claim and refer — distribution that bypasses search entirely |

---

## The next steps, in order

### 1. Build the storm-event pages (highest leverage — a build)

The one thing that can produce real, recurring organic traffic. Scope it deliberately:

- **Data source:** NCEI Storm Events + SPC storm reports (already the product's inputs).
- **Page template:** event list with times/sizes/gusts, nearest ASOS observations, map,
  "preliminary vs final" label, and a "check your exact address → $9.99 report" CTA.
- **Discipline:** generate a page **only where records exist** — never every city × every date. This
  is the difference between "unique, non-commodity data" (safe, AI-friendly) and scaled-content spam.
- **Launch region first:** one hail-prone market (Dallas/Fort Worth, Denver, or the Midwest) before
  going nationwide. Prove the pattern, then expand.

### 2. Go where the buyers are (fastest traffic — no build)

Answer questions honestly in the communities where the buyer already is. The guides are the source
material:

- **r/Insurance** — "how do I prove the storm hit my house", "is this hail or wear and tear".
- **r/Roofing** / contractor forums — "how to document a claim for a customer".
- **r/homeowners** — "my insurer denied my wind claim".

Rule: **help first, link when it's genuinely the answer** (the guide or the sample report), never
drive-by drops. This is both referral traffic and the corroboration AI looks for.

### 3. Run the capped ads test (measure + capture spikes)

Per the competitor research's unit-economics: at $9.99 the break-even is ~$1/click, so:

- **$10–20/day**, US only, phrase and exact match, manual CPC or Max Clicks capped at **$1.00**.
- Target `hail report by address` + the hail/verification long-tails.
- Treat it as a **measurement** (what share of clicks buy?) and a **storm-spike capture** tool, not a
  growth engine.
- Pre-build a **paused "storm surge" campaign**; enable it with ZIP/radius targets within hours of a
  big SPC hail cluster.

### 4. Partnerships (background, compounding)

One roofer or public adjuster who buys per-claim is worth many one-off buyers. A 10-report pack (or
bulk price) for them raises average order value without touching the $9.99 entry price. This was
flagged earlier as the realistic AOV lever.

---

## What this does *not* include

- More on-page keyword work — the site is already AI-ready and well-structured; more of it won't move
  a near-zero-demand niche.
- Waiting on SEO to mature — the data says it won't, at least not at a meaningful scale.
- International/multi-day/bulk/API — already ruled out (no measurable demand).

---

## Decision needed

The next concrete move is either **(1) scope the storm-event pages build** (data pipeline, template,
one launch region) or **(2) draft the community playbook** (which subreddits, what to answer, how to
link without spamming). Pick one and we start it.
