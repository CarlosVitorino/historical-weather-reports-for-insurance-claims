# Competitor SEO and ads positioning: per-address historical weather / hail reports for US insurance claims (as of Oct 2026)

Method note: the sandbox proxy blocked direct fetches of every competitor domain (stormrecord.com, hailstrike.com, hailtrace.com, interactivehailmaps.com all failed DNS or returned a CONNECT 403). Everything below comes from web-search result pages and snippets, which the search tool had already summarized, plus the founder's StormRecord sample in `docs/materials/`. Exact headline wording, sitemap.xml and robots.txt could not be checked first-hand. Treat quoted phrases as snippet text, not verified page copy. Some vendor pages are years old (noted where it applies).

## Price points, packaging and headline value propositions

### Takeaway
The market splits into three price bands:
1. **Instant per-address PDFs at $2.99–$50.** StormRecord at $9.99, WeatherGuidance at $9.95, HailPoint at $9.95, StormerSite at $14.95, AnythingWeather at $40, HailTrace at $40, HailStrike at $35–$50. StormAuditor is at $2.99.
2. **Contractor map subscriptions at $60/month to $2,500/year.** These are HailStrike, Interactive Hail Maps/Hail Recon, HailPoint and HailTrace.
3. **Meteorologist or forensic reports at $150–$1,000+, or quote-only.** These are HailTrace, CompuWeather and AnythingWeather Premium.

NOAA's own certified copy starts at $180. The most important finding is that StormRecord already sells exactly the "$9.99, one address, one date" product. The other $9.95 products are hail-only lookback histories, not single-date multi-source reports.

### Cited Findings
**StormRecord (stormrecord.com), the closest direct competitor**
- Free preview, then the full PDF is $9.99 for one U.S. address and one local calendar date. No account or subscription. Searches cover yesterday through the past three years. — [StormRecord homeowner page](https://www.stormrecord.com/homeowner/); [StormRecord /report](https://stormrecord.com/report/); [StormRecord blog](https://stormrecord.com/blog/weather-report-for-insurance-claim/)
- The iOS App Store listing shows **$49.99 per report** ("generated on demand for a specific U.S. address and date"). This conflicts with the $9.99 on the website, so it may be app-specific pricing or out of date. — [App Store: StormRecord](https://apps.apple.com/us/app/stormrecord/id6758730551)
- The site has a separate construction vertical: "Weather Monitoring for Construction Projects". — [StormRecord /construction](https://stormrecord.com/construction/)
- The PDF itself is titled **"Weather Evidence Report"** and carries IDs like `SR-2026-02-19-KBMG-…`. It runs 12 pages. — `docs/materials/StormRecord_Sample_Report.pdf.md`

**WeatherGuidance (HailIntel / StormIntelligence)**
- Basic hail/wind (≥50 mph) history by address: $9.95 for 0–3 years, $14.95 for 4–6 years, $19.95 for 7–10 years. This tier is aimed at homeowners and contractors.
- "Forensic" report: $29.95 for up to 3 years. It adds other weather types and an event map, and is aimed at adjusters, attorneys and engineers. — [weatherguidance.com hailintel_verify_home](https://www.weatherguidance.com/hailintel_verify_home.html)
- Per-storm maps cost $49.95, or 2 for $79.95. Subscriptions start at $49.95/month. These pages look old. — [Hail Intel](http://www.weatherguidance.com/hailintel_home.html); [StormIntelligence](http://www.weatherguidance.com/Hail_Reports.html)

**HailPoint**
- Hail Address Verification Report: $9.95, "No subscription necessary". It gives maximum hail size at the address and within 1, 3, 5 and 10 miles. Volume discounts are offered.
- Lookback conflicts: the report page says Jan 1, 2018, while the products page says Jan 1, 2013.
- Subscriptions: $59.95/month metro, $69.95/month state, $89.95/month national. — [hailpoint.com/hail-report-by-address](https://www.hailpoint.com/hail-report-by-address); [hailpoint.com/products](https://www.hailpoint.com/products)

**StormerSite**
- Hail History Report: $14.95. It covers "all potential hail activity in the last 6 years within a 3 mile radius". The pricing page is roughly 3 years old. — [stormersite.com/hail-history-reports](https://www.stormersite.com/hail-history-reports)
- Pitched to adjusters and insurers for setting the date of loss. — [StormerSite home](https://www.stormersite.com/)

**StormAuditor**
- Free hail, wind and storm history by address. A full report is **$2.99** with no subscription. Uses 15+ years of NOAA data. — [stormauditor.com](https://www.stormauditor.com/)

**HailScore (myhailscore.com)**
- Free 0–100 hail exposure score per US address. No signup or card for the basic score and ledger. The dated event list unlocks with an email. Paid detailed PDFs are optional (price not found). Denver-based. — [myhailscore.com](https://www.myhailscore.com/); [HailScore comparison blog](https://www.myhailscore.com/blog/hailscore-vs-hailtrace-vs-interactive-hail-maps)

**HailTrace**
- Three per-report tiers. Source: HailTrace's own pages, echoed by a competitor's (HailMate) pricing post.
  - "Weather History" at $40: "compiled from our active database of storms and not reviewed by a meteorologist". Covers 2011 to present.
  - "Meteorologist Reviewed" at $150: confirms the date of loss.
  - Certified forensic at $1,000: "causation explained".
  - One HailTrace page shows $40 beside the Meteorologist Reviewed heading, so its own pages are inconsistent. — [HailTrace hail-reports](https://hailtrace.com/hail-reports); [Weather History](https://hailtrace.com/hail-reports/weather-history); [Meteorologist Reviewed](https://hailtrace.com/hail-reports/meteorologist-reviewed); [HailTrace FAQ](https://hailtrace.com/faq); [HailMate cost roundup](https://hailmate.ai/blog/hail-tracking-software-cost)
- Subscriptions are quote/demo only. A single storm map costs $230, credited toward a subscription. — [roofingsoftwareguide HailTrace pricing](https://roofingsoftwareguide.com/reviews/hailtrace-pricing/)
- Archive: hail back to 2010, wind back to 2020. — [HailTrace FAQ](https://hailtrace.com/faq)

**HailStrike (OneSite reports, AniSwath maps)**
- OneSite Full $50, OneSite Lite $45, OneSite Basic $35. Subscribers get discounts and bulk credits. — [hailstrike.com/onesite/order](https://hailstrike.com/onesite/order)
- Subscription tiers are $149, $249 and $2,500/year. Premium Plus+ at $149 includes 1 full OneSite report. Ultimate at $249 includes 4 full and 10 lite reports per day. — [hailstrike.com/pricing](https://hailstrike.com/pricing)
- Older trade-press coverage (around 2016) says OneSite takes just an address, returns 5 years of hail history (size, duration, speed, direction) in under 3 minutes, and has a CertainTeed contractor partnership. — [Roofing Magazine](https://roofingmagazine.com/mobile-app-provides-roofing-contractors-with-hail-storm-data-at-exact-locations/); [Roofing Contractor](https://roofingcontractor.com/articles/90724-certainteed-partners-with-hailstrike-to-connect-credentialed-contractors-with-storm-torn-roofs)

**Interactive Hail Maps / Hail Recon**
- $999/year for one state, $1,499 for three states, $1,999 nationwide. "All Plans Include Unlimited Hail Maps". "Unlimited branded" Hail Impact Reports (date, size, direction, duration) are included, so there is no per-report price. The pricing page is roughly 4 years old. A 2026 third-party post repeats the same figures and adds homeowner contact data at $799/year per state. — [IHM pricing](https://www.interactivehailmaps.com/pricing-page/); [Hail Impact Reports](https://www.interactivehailmaps.com/hail-impact-reports/); [HailMate cost roundup](https://hailmate.ai/blog/hail-tracking-software-cost)

**AnythingWeather (HailWATCH: HailFACTS / WindFACTS / LightningFACTS)**
- HailFACTS costs $40. It gives hail size at the address and within 1, 3 and 10 miles, with history from 2006.
- WindFACTS costs $40. It covers winds from 40 mph up, in 1-mph increments.
- LightningFACTS costs $199.
- A meteorologist-written "Premium" report exists, but no price was found.
- A stale "2017 Hail Climate Report" is still listed at $499. — [store.anythingweather.com](https://store.anythingweather.com/weather_verification_reports); [HailFACTS](https://www.anythingweather.com/products/hailwatch/hailfacts/); [Policyholders & PAs page](https://www.anythingweather.com/solutions/insurance-and-legal/policyholders-public-adjusters/)

**CompuWeather (forensic, enterprise)**
- No public price; "Contact Us for information and pricing". Formal signed reports by Certified Consulting Meteorologists, delivered in 5 business days or sooner. Also sells cheaper data-only nearest-station products. — [compuweather.com](https://compuweather.com/); [About](https://compuweather.com/about-us/)

**Weather and Climate Expert (weatherandclimateexpert.com)**
- Sells a meteorologist-style "Wind Verification Report" and causation analysis. Price not found. — [Wind Verification Report](https://weatherandclimateexpert.com/wind-verification-report/)

**NOAA NCEI certification (government baseline)**
- Certified data is priced in 40-page increments plus $12 shipping. 1–40 pages costs $180 ($168 + $12); 161–200 pages costs $852. "Most orders start at $191." — [NCEI Data Certification](https://www.ncei.noaa.gov/services/certification)

**Visual Crossing / Weather Underground**
- Visual Crossing publishes blog content on using its history data for insurance claims. I found no evidence that it sells a certified per-address claim report. StormRecord resells or compiles Visual Crossing values. — [Visual Crossing blog](https://www.visualcrossing.com/resources/blog/how-can-i-find-past-weather-information-for-my-insurance-claim/); [StormRecord About](https://stormrecord.com/about/)

### Inferences
- $9.99 is not a differentiated price point. StormRecord, HailPoint and WeatherGuidance are all at about $9.95–$9.99, and StormAuditor undercuts at $2.99. Weather Evidence has to win on content (station-pinned, NCEI Storm Events, radar hail, lightning, all in one date-specific report), not on price.
- The ladder competitors use is: free lookup or score, then a $10–$50 automated PDF, then a $150 meteorologist-reviewed report, then $1,000+ forensic. A $9.99 product sits at the bottom rung. The upsell rung (meteorologist review) is explicitly out of scope per CLAUDE.md, so the product must be framed as self-sufficient.
- **Naming conflict risk:** StormRecord's PDF is titled "Weather Evidence Report". A brand called "Weather Evidence" could be confused with it, or seen as derivative. Check trademark and SEO overlap before committing.

### Gaps
- Exact homepage H1 or headline copy for each vendor could not be captured, because direct fetches were blocked.
- No current verified HailScore paid-PDF price, AnythingWeather Premium price, or CompuWeather price.
- Weather Source and "WeatherSure" turned up no consumer per-report product. Weather Source appears to be B2B data, but I found no source either way. "Certified Weather reports" as a named vendor was not found.

## Target audiences (from copy, nav and tiers)

### Takeaway
Only StormRecord, StormAuditor and HailScore clearly lead with homeowners. Most hail vendors (HailTrace, HailStrike, IHM/Hail Recon, HailPoint subscriptions) are contractor lead-generation tools that bolt per-address reports onto map subscriptions. Forensic firms target attorneys, insurers and engineers.

### Cited Findings
- StormRecord has dedicated /homeowner/ and /construction/ pages, and its blog targets homeowner-intent queries ("weather report for insurance claim", "how insurance companies verify weather claims"). — [homeowner](https://www.stormrecord.com/homeowner/); [blog](https://stormrecord.com/blog/how-insurance-companies-verify-weather-claims/)
- HailTrace is built for contractors and insurers. A homeowner reportedly cannot just enter an address and get a report. This is per HailScore, a competitor, so it may be biased. — [HailScore comparison](https://www.myhailscore.com/blog/hailscore-vs-hailtrace-vs-interactive-hail-maps)
- HailTrace's blog targets adjusters: "4 Reports to Find a Date of Loss and Close a Weather Claim Fast". — [HailTrace blog](https://blog.hailtrace.com/4-reports-to-find-a-date-of-loss-and-close-a-weather-claim-fast/)
- HailStrike audience in trade press: insurance adjusters, CAT teams, IAs, public adjusters, roofing contractors and roofing engineers. — [Roofing Magazine](https://roofingmagazine.com/mobile-app-allows-access-site-date-specific-hail-reporting-data/)
- IHM/Hail Recon is positioned around "Get There First" for canvassing roofers, and sells homeowner contact data. — [interactivehailmaps.com](https://www.interactivehailmaps.com/); [HailMate](https://hailmate.ai/blog/hail-tracking-software-cost)
- WeatherGuidance splits its tiers by audience: Basic for homeowners and contractors, Forensic for adjusters, attorneys and engineers. — [WeatherGuidance](https://www.weatherguidance.com/hailintel_verify_home.html)
- AnythingWeather has separate nav paths for "Policyholders & Public Adjusters" and "Insurance Companies & Adjusters". — [policyholders](https://www.anythingweather.com/solutions/insurance-and-legal/policyholders-public-adjusters/); [insurers](https://www.anythingweather.com/solutions/insurance-and-legal/insurance-companies-adjusters/)
- CompuWeather: "attorneys, insurers, and engineers", with services also open to the general public. — [CompuWeather About](https://compuweather.com/about-us/)
- Newer homeowner-facing entrants: StormAuditor, HailScore, Hail411 ("for Roofers, Restoration, and Adjusters") and HailDrive. — [stormauditor.com](https://www.stormauditor.com/); [hail411.info](https://hail411.info/); [haildrive.com](https://haildrive.com/)
- Comparison and affiliate content is a channel in its own right: HailMate ("Every Published Price") and roofingsoftwareguide.com rank for "[vendor] pricing" queries. — [HailMate](https://hailmate.ai/blog/hail-tracking-software-cost); [roofingsoftwareguide](https://roofingsoftwareguide.com/roundups/hailtrace-alternatives-storm-tracking-tools-compared/)

### Inferences
- The homeowner and public-adjuster segment buying a single report is served mainly by StormRecord and by cheap hail-only lookups. Contractor-tool vendors treat homeowners as leads, not customers.
- Claims adjusters (the CLAUDE.md test audience) are courted mainly by subscription vendors and HailTrace's date-of-loss content. A $9.99 "no account" report is a plausible wedge for independent or field adjusters who don't want a subscription.

### Gaps
- No Reddit or adjuster-forum threads surfaced. Search returned only law-firm and roofer blogs, so real buyer sentiment on these vendors is unknown. Trustpilot exists for HailPoint ([link](https://www.trustpilot.com/review/www.hailpoint.com)) but its content wasn't retrieved.

## Site structure visible to search engines

### Takeaway
Programmatic local SEO is the dominant pattern among the newer, cheap players. Examples are StormAuditor (`/storm-data/{state}/{city}`), StormerSite (`/hail_reports/{city_state}/{year}`) and HailScore (city blog posts). These are paired with free address lookups as lead magnets. StormRecord relies on a small set of intent pages plus a how-to blog. No vendor was found with "storm on [date] in [city]" pages for individual storm dates.

### Cited Findings
- StormAuditor runs state and city pages in all 50 states, each with a 12-month event summary, historical record and free address check. Examples: [/storm-data/tx/kyle](https://www.stormauditor.com/storm-data/tx/kyle), [/storm-data/nj/jersey-city](https://www.stormauditor.com/storm-data/nj/jersey-city), [/storm-data/ca](https://www.stormauditor.com/storm-data/ca). It also has a "Storm History Lookup — Historical Storms by Address & Date" tool page at [/storm-history](https://www.stormauditor.com/storm-history). — [StormAuditor](https://www.stormauditor.com/)
- StormerSite has a daily-dated homepage ("Today's Hail Reports - 10/14/2026") and city/year archive pages: [/hail_reports/dallas_texas/all](https://www.stormersite.com/hail_reports/dallas_texas/all), [/hail_reports/dallas_texas/2026](https://www.stormersite.com/hail_reports/dallas_texas/2026). — [StormerSite](https://www.stormersite.com/)
- HailScore has city plus year blog posts ("Hail Damage in Aurora, CO (2026): Storm History, Risk, and Free Address Check"), a "Did Hail Hit My House? Free Check by Address & Date" landing page, and competitor-comparison posts. — [Aurora post](https://www.myhailscore.com/blog/hail-damage-aurora-co-2026); [did-hail-hit-my-address](https://www.myhailscore.com/did-hail-hit-my-address); [comparison](https://www.myhailscore.com/blog/hailscore-vs-hailtrace-vs-interactive-hail-maps)
- StormRecord has `/homeowner/`, `/construction/`, `/report/`, `/about/` and a `/blog/` of intent-keyword posts: "weather-report-for-insurance-claim", "historical-weather-data-insurance-claim" and "how-insurance-companies-verify-weather-claims". It also has an iOS app. — [StormRecord blog](https://stormrecord.com/blog/historical-weather-data-insurance-claim/)
- HailTrace has a per-tier product page for each report (/hail-reports/weather-history, /meteorologist-reviewed), a FAQ, a separate blog subdomain, and free "1-Star" hail maps. — [HailTrace](https://hailtrace.com/hail-reports); [roofingsoftwareguide](https://roofingsoftwareguide.com/reviews/hailtrace-pricing/)
- HailStrike has /pricing, /onesite/order and a hail report newsletter (/newsletter) as a lead magnet. — [HailStrike newsletter](https://hailstrike.com/newsletter)
- AnythingWeather has product pages per peril (HailFACTS, WindFACTS, LightningFACTS) and a "Storm Archive". — [stormarchive](https://www.anythingweather.com/products/hailwatch/stormarchive/)
- CompuWeather runs content-marketing posts that argue against free data: "Considering Using Free Historical Weather Data? Three Questions…", "Not Using a Weather Expert Can Cost You Your Case", "Consulting with a Weather Expert vs. a Weather Report". — [CompuWeather blog](https://compuweather.com/considering-using-free-historical-weather-data-three-questions-to-think-about/)
- GAF hosts "WeatherHub: Interactive Hail Maps" for its contractors, a manufacturer-distributed free map. — [GAF](https://www.gaf.com/en-us/resources/business-services/interactive-hail-map)

### Inferences
- The SEO gap: no one seems to own **date-specific storm pages**, such as "hail in Dallas on May 2, 2024" or "wind storm [city] [date]", built from NCEI Storm Events. Those match how claim buyers search: they know the date of loss. Programmatic pages per NCEI event date and county, each ending in "get the report for your address", would be distinct from StormAuditor's city pages.
- Free address lookups are table stakes for lead capture. A free preview (StormRecord's model) is the minimum.

### Gaps
- No sitemap.xml or robots.txt was inspected because fetches were blocked. Page counts and indexation are unknown.
- I could not confirm whether StormRecord has any city or date programmatic pages.

## Trust and legal language (and risks)

### Takeaway
There are two camps. Cautious sellers (StormRecord, HailScore) say they are not certified, not expert opinion, and not proof of property conditions. Aggressive sellers use "court-approved", "insurance-approved in many cases", "stand up in court" and even Daubert/FRE 702 claims. Only NCEI can issue certified copies of US government weather records.

### Cited Findings
- StormRecord: "automated compilation, not a certified government copy or expert opinion". "A reported event elsewhere in a county does not establish conditions at your property." Acceptance "depends on the reviewing insurer", with no guarantee of claim outcome. It gives no expert testimony, legal advice or coverage determinations. Its blog also concedes that NOAA data is free and "there is no universal requirement to buy a weather report". — [StormRecord blog](https://stormrecord.com/blog/weather-report-for-insurance-claim/); [About](https://stormrecord.com/about/); [homeowner](https://www.stormrecord.com/homeowner/)
- StormRecord's "NOAA and NWS observations" claim on the homeowner page conflicts with its blog and About page, which say values are Visual Crossing compilations "not identical to a direct NOAA station download". The sample report says "NOAA and other weather networks — Compiled by Visual Crossing". — [homeowner](https://www.stormrecord.com/homeowner/); [blog](https://stormrecord.com/blog/historical-weather-data-insurance-claim/); `docs/materials/StormRecord_Sample_Report.pdf.md`
- The StormRecord sample shows "Hail size: Not queried" and "Lightning observations: Not queried". Its "Peak wind gust" is a gridded or blended value with no named station, distance or bearing. — `docs/materials/StormRecord_Sample_Report.pdf.md`
- AnythingWeather says HailFACTS is "insurance-approved in many cases" and that its reports "stand up in court" (marketing claim). — [HailFACTS](https://www.anythingweather.com/products/hailwatch/hailfacts/)
- Search summaries found that some seller calls its report "court-approved", and another claims its reports pass FRE 702/Daubert. The search summary did not reliably attribute these to a vendor, so they are unattributed. — [search context incl. weatherandclimateexpert.com](https://weatherandclimateexpert.com/how-to-find-accurate-weather-data-for-insurance-and-legal-disputes/)
- CompuWeather leans on credentials: Certified Consulting Meteorologists (AMS), plus reports "prepared and signed by credentialed forensic experts". — [CompuWeather](https://compuweather.com/)
- HailTrace reserves "certified" for its $1,000 forensic tier, and its $40 report is explicitly "not reviewed by a meteorologist". — [HailTrace FAQ](https://hailtrace.com/faq)
- HailScore: the score reflects "hail exposure near the address, not roof damage". — [myhailscore.com](https://www.myhailscore.com/)
- NCEI: the Department of Commerce certifies archived data "to meet the authentication requirements for records submitted as evidence in a court of law". NDBC says NCEI is "the only place" to get certified copies of U.S. weather information. — [NCEI certification](https://www.ncei.noaa.gov/services/certification); [NDBC FAQ](https://www.ndbc.noaa.gov/faq/certified.shtml)
- Expert commentary: certification authenticates records but does not establish sensor accuracy or interpretation. The Storm Events Database may undercount maximum hail size. A county-level event doesn't establish conditions at a property. — [weatherandclimateexpert.com](https://weatherandclimateexpert.com/weather-data-for-court-foia-costs-180-or-subpoena/); [J.S. Held](https://www.jsheld.com/insights/articles/weather-reports-insurance-claims-finding-a-trustworthy-source)
- The NWS "Weather Enterprise" lists private forensic hail services, which is relevant for not implying a NOAA endorsement. — [weather.gov/enterprise/fs-hail-3c](https://www.weather.gov/enterprise/fs-hail-3c)

### Inferences
- These are risky terms for a $9.99 automated product: "certified", "court-admissible/approved", "insurance-approved", "NOAA report" (which implies a government document), "proof of damage", and "expert". Given the brief's stated stop risk ("Legally issues"), copy closer to StormRecord's disclaimers plus a pointer to NCEI certification ($180+) is the safer pattern.
- The domain "weatherevidence.com" and the word "Evidence" already carry legal connotations. Pair them with clear "not certified / not expert opinion" language.

### Gaps
- No court rulings found on the admissibility of any of these vendors' automated reports.

## Weaknesses and gaps a $9.99 instant per-address report could exploit

### Takeaway
The cheap tier is either hail-only lookback history (HailPoint, WeatherGuidance, StormerSite, StormAuditor) or StormRecord's single-date report. StormRecord uses blended Visual Crossing values without a named station, distance or bearing, and leaves hail and lightning "Not queried". A report that is station-pinned, multi-peril, NCEI-sourced and date-specific at $9.99 is the open slot. Mid-tier sellers charge $35–$50 for a single peril.

### Cited Findings
- StormRecord gaps: Visual Crossing blended values, no station pinning, hail and lightning "Not queried", 3-year lookback limit, and a $49.99 vs $9.99 price inconsistency between app and site. — `docs/materials/StormRecord_Sample_Report.pdf.md`; [StormRecord /report](https://stormrecord.com/report/); [App Store](https://apps.apple.com/us/app/stormrecord/id6758730551)
- Single-peril pricing elsewhere: HailFACTS $40 and WindFACTS $40 sold separately, and LightningFACTS $199. — [AnythingWeather store](https://store.anythingweather.com/weather_verification_reports)
- HailTrace's $40 tier is algorithmic. Its wind archive only goes back to 2020. — [HailTrace FAQ](https://hailtrace.com/faq)
- Contractor platforms require subscriptions, demos or quotes (HailTrace, IHM at $999+/year, HailStrike at $149+/month), and target roofers rather than claimants. — [HailMate](https://hailmate.ai/blog/hail-tracking-software-cost)
- NCEI certified copies cost $180+ and are raw records, not interpreted per-address reports. — [NCEI](https://www.ncei.noaa.gov/services/certification)
- CompuWeather takes 5 business days and quote-based pricing. — [CompuWeather](https://compuweather.com/)
- Buyer need: carriers check the claimed date of loss against archived data. The date of loss is when the damage happened, not when it was noticed. — [prequalifyroof.com](https://prequalifyroof.com/guides/hail-damage-roof-claim/); [estimateondemand.com](https://estimateondemand.com/date-of-loss-prior-hail-damage-roof-claims/)

### Inferences
- Positioning angle: "the measurements, with the station named." Each value would cite a NOAA/NWS station ID with distance and bearing from the address, plus NCEI Storm Events, NWS warnings, radar hail (MESH) and lightning in one date-specific PDF for $9.99. That is a direct contrast with StormRecord's blended values and with the $40-per-peril sellers.
- Offer a "this vs. certified NCEI copy vs. forensic meteorologist" explainer, which is honest and SEO-friendly. Use the founder's own NCEI price ($180) as the anchor.
- SEO wedge: date-specific storm-event pages (NCEI event, county and date) that StormAuditor and StormerSite's city-level pages don't cover. A free preview on each page leads to the $9.99 purchase.
- Pricing pressure: StormAuditor's $2.99 and the free HailScore/StormAuditor lookups mean hail-only "did hail hit my address" queries are commoditized. Avoid competing there; lead with multi-source, date-specific measurements.

### Gaps
- Whether insurers or adjusters actually accept or prefer any of the cheap reports is unverified; no adjuster-side source was found.
- Ad spend and paid-search positioning (Google Ads copy) could not be observed.
