# Google Ads (search) for historical weather / hail / storm reports, US, 2025–2026

Research method note: WebFetch and direct HTTP to most sites (support.google.com, searchengineland.com, stormrecord.com, hailstrike.com) were blocked from this environment (DNS failure or proxy 403). Every finding below comes from search-result snippets and summaries, not full-page reads. Google's own policy pages appeared in results, but their exact current wording could not be checked. Before anyone acts on a policy point, open the cited page directly.

## 1. Competitors on these searches and their ad copy / offers

### Takeaway
There is a clear competitive set of instant per-address weather and hail report sellers, with prices from $2.99 to $49.95 per report, plus contractor-focused subscriptions. StormRecord is the direct analogue: $9.99, instant PDF, NOAA/NWS data. I could not see any live ad copy. The Ads Transparency Center needs a manual lookup, and no indexed listing turned up for these vendors.

### Cited Findings
- **StormRecord**: $9.99 PDF for one US address and one local calendar date, delivered instantly, built from archived NOAA and NWS observations, with a free preview before purchase. Coverage runs from yesterday back about 3 years. Its own disclaimer calls the report "an automated compilation, not a certified government record or expert opinion" and gives no guarantee that an insurer will accept it. It also tells buyers to ask their adjuster what they need. — [StormRecord home](https://www.stormrecord.com/); [StormRecord blog: weather report for insurance claim](https://stormrecord.com/blog/weather-report-for-insurance-claim/); [StormRecord homeowner page](https://www.stormrecord.com/homeowner/); [StormRecord blog: historical weather data for an insurance claim](https://stormrecord.com/blog/historical-weather-data-insurance-claim/)
- **StormAuditor**: positions itself as "Free Hail, Wind & Storm History by Address". A single report costs $2.99 (web view, PDF and emailed copy), and there are subscription plans with a daily allowance. Its figures are *estimated* hail and wind at the property. — [StormAuditor](https://www.stormauditor.com/)
- **StormerSite**: Hail History Reports at $14.95. — [StormerSite Hail History Reports](https://www.stormersite.com/hail-history-reports)
- **WeatherStrike**: $49.95 per Basic Report, covering a date range of up to 7 years. — [WeatherStrike](https://www.weatherstrike.com/)
- **Titan Weather**: "Property Weather Report by Address: Hail and Wind History". Subscription tiers, with the first 3 reports free and no card required. — [Titan Weather](https://titanweather.com/)
- **HailTrace**: sells "Storm & Hail Reports that Streamline Insurance Claims". Its "Reviewed Report" has a meteorologist confirm the storm details. No price surfaced. The company says it has 8 meteorologists and covers the US, Canada and Australia. — [HailTrace hail reports](https://hailtrace.com/hail-reports); [Hook Agency roundup](https://hookagency.com/blog/hail-trackers-for-roofing/)
- **GAF WeatherHub**: contractor-facing, with unlimited address-level reports at tiers of $349, $499 and $649 per year. The tier-to-contractor mapping was unclear in the source. It advertises hail and wind swaths "with NOAA verification" and 3-year storm history. — [GAF WeatherHub](https://www.gaf.com/en-us/resources/business-services/interactive-hail-map); [GAF interactive hail map](https://gaf.com/en-us/for-professionals/tools/interactive-hail-map)
- **HailStrike**: interactive hail maps, storm history, and hail reports "to support your claim". No price surfaced. — [HailStrike](https://hailstrike.com/)
- **Meteomatics MetX Claims**: a claims workflow that ends in a downloadable PDF weather report. No price surfaced. — [MetX Claims](https://www.meteomatics.com/en/metx-claims/)
- **Interactive Hail Maps / Hail Recon**: a roofer subscription. The companion app generates and emails "comprehensive hail impact reports", with hail sizes in ¼-inch steps. — [Hail Recon app listing](https://apps.appfollow.io/ios/hail-recon/602877045?country=us)
- **The official alternative**: NCEI certified data is "certified to meet the authentication requirements for records submitted as evidence in a court of law". Orders are priced in 40-page increments plus $12 shipping. The page says "most orders start at $191", while its table shows $180 for 1–40 pages. Regional climate centers charge $25–$50 certification fees on top of their data fees. — [NCEI certification](https://www.ncei.noaa.gov/certification); [MRCC pricing](https://www.mrcc.purdue.edu/data_serv/customOrdering.jsp); [NRCC](https://www.nrcc.cornell.edu/services/access/access.html)
- **NWS framing**: a local NWS office describes its compiled storm data as "preliminary and uncertified" and points users to NCEI Storm Data for certified reports. — [NWS Amarillo storm data](https://www.weather.gov/ama/stormdata)
- **How to look up rivals' ads**: the Ads Transparency Center is public at adstransparency.google.com and needs no login. Searching works best by the advertiser's legal name, falling back to the landing-page domain. — [Fraud Blocker guide](https://fraudblocker.com/articles/google-ads-transparency-center); [AdsInsightPro guide](https://www.adsinsightpro.com/blog/google-ads-transparency-center-guide/)

### Inferences
- Price-led messages that fit the market: "$9.99 instant PDF" matches StormRecord exactly and undercuts StormerSite ($14.95), WeatherStrike ($49.95) and NCEI certified copies (about $180+). StormAuditor at $2.99 means price alone is not a moat. Differentiate on station-pinned measurements with distance and bearing, the Storm Events database, and hail/lightning sources, which are the four gaps the project brief lists.
- StormRecord's own disclaimer wording ("not a certified government record or expert opinion") is a ready template for the honesty that ad and landing copy need (see section 4).
- Several rivals use "free" as a hook: StormAuditor's tagline and Titan's 3 free reports. A free preview, like StormRecord's, is the closest equivalent that keeps the $9.99 price. Under Google's dishonest-pricing rules, a paid product must never be called "free" (see section 4).

### Gaps
- No actual ad headlines or descriptions were retrieved for any competitor. The Transparency Center was not reachable from here and no indexed results surfaced. Before launch, manually search adstransparency.google.com for stormrecord.com, stormauditor.com, stormersite.com, weatherstrike.com, titanweather.com, hailtrace.com and hailstrike.com, and run a live SERP check on "hail report by address" and "weather report for insurance claim".
- SpyFu and Semrush public pages for these domains were not retrieved.
- HailTrace, HailStrike, Interactive Hail Maps and MetX prices were not found.

## 2. Estimated CPCs for relevant keywords

### Takeaway
I found no public Keyword Planner, Semrush or SpyFu CPC figures for "hail report", "storm report by address", "weather history by date" or "certified weather report". The only data points are cross-industry averages (about $5.26–$5.42 CPC) and roofing/restoration figures, where storm and insurance-claim intent runs $5–$60+ per click. Treat contractor-intent and "insurance claim" terms as expensive. The cheaper bets are informational data terms ("weather on [date]", "hail history [address]"), but their CPCs have to be checked in Keyword Planner.

### Cited Findings
- WordStream/LocaliQ 2025 benchmarks (16,000+ US advertisers, April 2024 to March 2025): all-industry average CPC of $5.26, CTR of 6.66%, conversion rate of 7.52%, cost per lead of $70.11. Other coverage of the same benchmark gives a $5.42 CPC (up from $4.66) and an 8.18% conversion rate. The year labels conflict between sources. — [Search Engine Land](https://searchengineland.com/google-ads-costs-keep-rising-but-conversion-rates-improved-in-2025-477927); [Shopifreaks](https://www.shopifreaks.com/google-ads-cpcs-rose-to-5-42-in-2025-with-87-of-industries-seeing-increases-but-conversion-rates-climbed-to-8-18-as-automation-improves/); [Segwise](https://segwise.ai/blog/google-ads-benchmarks-industry-insights)
- The 2026 WordStream/LocaliQ report (April 2025 to March 2026) cites a cross-industry CPC of $5.42 and a CTR of 6.64%. — [The E Digital](https://www.theedigital.com/blog/2025-google-ads-benchmarks)
- Ecommerce search, 2026: 4.01% conversion rate, $4.14 CPC, 8.28% CTR. — [The Ad Spend](https://theadspend.com/blog/google-ads-search-ecommerce)
- Storm-damage restoration keywords (vendor estimates): insurance-intent terms run $5–$15 per click with 3–5% conversion rates, and emergency-intent terms run $15–$45 in competitive markets. "Roof storm damage" gets about 3,600 searches a month (Semrush, cited by the vendor). — [PushLeads](https://pushleads.com/restoration-company-seo/water-damage-restoration-seo/storm-damage-ppc-advertising-for-restoration-companies/)
- Roofing storm-season CPCs reportedly rise 200–400% after storms. — [Stackmatix](https://www.stackmatix.com/blog/roofing-google-ads-storm-season). Competitive roof-replacement terms reportedly cost $35–$60+ per click. — [Silverback Strategies](https://www.silverbackstrategies.com/lists/best-google-ads-agencies-for-roofing-ranked-and-reviewed/)
- Finance and insurance is among the lowest-converting verticals, at 2.64%. — [Search Engine Journal](https://www.searchenginejournal.com/what-are-good-google-ads-benchmarks/546995/)
- The underlying data is free: NOAA SPC hail, wind and tornado reports are public domain and downloadable as CSV. This feeds "free" informational competition on the search results page. — [NOAA SPC reports](https://www.spc.noaa.gov/climo/reports/today.html); [Apify SPC scraper](https://apify.com/wishbone_data/spc-storm-reports)

### Inferences
- "Hail damage insurance claim", "storm damage insurance claim" and "roof hail damage" share an auction with roofers and public adjusters, whose per-lead value is in the thousands of dollars. Those CPCs will very likely be far above what a $9.99 product can support (see section 3), and they surge right after storms, which is exactly when demand peaks.
- The likely cheaper variants are data and record phrasing without contractor intent: "hail report by address", "hail history [city]", "weather on [date] [city]", "what was the weather on [date]", "past weather by zip code", "storm report [date] [county]", "NOAA storm report by address". Many of these are informational, with weather.gov, Weather Underground and free hail maps ranking organically, so CTR and conversion rate may be low even where CPCs are low.
- "Certified weather report" is risky on two counts: possibly expensive litigation intent, and possible policy and consumer-protection problems if the product is not certified. Bid on it only with copy that says plainly the report is not certified (or exclude it).

### Gaps
- No keyword-level CPC or volume for the five named terms. Next step: run them in Google Keyword Planner (free with an Ads account) with US targeting and record the low and high top-of-page bid ranges.

## 3. Unit economics at $9.99

### Takeaway
After payment fees, about $9.20–$9.40 per sale is available for ads. The break-even CPC is net revenue × conversion rate: about $0.19 at 2% CVR, about $0.47 at 5%, and about $0.93 at 10%. At benchmark CPCs of $4–$5.50, break-even would need a 45–60% conversion rate, which is implausible. A single-report $9.99 product only works on Google Ads with long-tail clicks under $1 and strong landing-page conversion, or with a higher average order value.

### Cited Findings
- Average Google Ads CPC is $5.26–$5.42 and ecommerce search CPC is $4.14. — [Search Engine Land](https://searchengineland.com/google-ads-costs-keep-rising-but-conversion-rates-improved-in-2025-477927); [The Ad Spend](https://theadspend.com/blog/google-ads-search-ecommerce)
- Conversion rates: all-industry average 7.52–8.18% (mostly lead-gen, not purchases) — [Search Engine Land](https://searchengineland.com/google-ads-costs-keep-rising-but-conversion-rates-improved-in-2025-477927). Ecommerce search 4.01% — [The Ad Spend](https://theadspend.com/blog/google-ads-search-ecommerce). Finance and insurance 2.64% — [Search Engine Journal](https://www.searchenginejournal.com/what-are-good-google-ads-benchmarks/546995/). General online-store average about 1.8–2.04% — [Triple Whale](https://www.triplewhale.com/blog/what-is-a-good-conversion-rate.md).
- Triple Whale's 2025 Google Ads data (18,000+ brands): conversion rate down about 9%, median CPA $23.74–$28.14. — [Triple Whale](https://www.triplewhale.com/blog/google-ads-benchmarks)
- StormRecord's free preview before purchase is a likely conversion lever for this kind of product. — [StormRecord](https://www.stormrecord.com/)

### Inferences
- Break-even table, assuming about $9.30 net after processor fees (an assumption: Creem's exact fee was not verified here):

  | Conversion rate (click to purchase) | Break-even CPC |
  |---|---|
  | 2% | $0.19 |
  | 5% | $0.47 |
  | 10% | $0.93 |
  | 15% | $1.40 |
  | 20% | $1.86 |

- A searcher who types "hail report for [address] [date]" has very high purchase intent and gets an instant result with a preview, so a 10–20% click-to-purchase rate is plausible but unproven. Even then, the ceiling is roughly $1–$2 CPC. Any keyword whose top-of-page bid is above about $1.50 should be excluded at launch.
- Levers that raise what a click is worth: a multi-date or multi-address bundle, an adjuster or contractor pack (say 10 reports), or a date-range report. Each one raises revenue per conversion without changing the $9.99 entry price.
- Suggested test budget logic: about $10–$20 a day with manual CPC or Max Clicks capped at about $1. Judge each keyword after about 100–200 clicks. At a 10% CVR, that is 10–20 sales, enough to see whether CVR is in the viable range.

### Gaps
- No public benchmark exists for conversion rates on low-price ($5–$15) instant digital reports bought from search. The benchmarks above are lead-gen or physical ecommerce figures and are proxies only.
- Creem's fee schedule was not verified here.

## 4. Google Ads policies that could matter

### Takeaway
The biggest risks are misrepresentation (implying a NOAA or government affiliation or "certified" status) and the government documents and official services policy, which since October 2025 auto-adds a "Not a government website" disclosure to ads in that category. The financial services verification programs found in this research cover the UK, the EU/EEA and other non-US markets. Nothing found shows that a US advertiser selling weather data, not insurance, needs it. Dishonest-pricing rules forbid calling a paid report "free".

### Cited Findings
- **Misrepresentation**: Google prohibits "misleading statements or obscuring or omitting material information about your identity, affiliations or qualifications", and business names that do not clearly represent the advertiser. Accounts can be suspended on detection without prior warning for egregious misrepresentation. — [Google Ads Misrepresentation policy](https://support.google.com/adspolicy/answer/6020955?hl=en)
- **Unreliable claims**: bars "inaccurate claims or claims that entice the user with an improbable result… as the likely outcome". In practice this rules out promising things like "Get your claim approved". — [Google Ads Misrepresentation policy](https://support.google.com/adspolicy/answer/6020955?hl=en)
- **Dishonest pricing**: advertisers must "clearly and conspicuously disclose the payment model or full expense" and must not advertise chargeable products as free. — [Google Ads Misrepresentation policy](https://support.google.com/adspolicy/answer/6020955?hl=en)
- **Government affiliation**: Google's Merchant Center misrepresentation policy lists "misleading use or mimicry of official government sites, stamps, seals, or agency names" as an example of falsely implying affiliation. — [Merchant Center misrepresentation](https://support.google.com/merchants/answer/6150127?hl=en). A Google spokesperson has said: "We prohibit ads that mislead users by implying an affiliation with a government agency." — [The Markup, 2021](https://themarkup.org/google-the-giant/2021/05/13/ads-are-impersonating-government-websites-in-google-results-despite-ban)
- **Government documents and official services policy**: expanded in March 2023 to cover government-authorised providers. Violations do not lead to immediate suspension without warning. — [Google policy page](https://support.google.com/adspolicy/answer/12921812?hl=en-GB). From October 22, 2025, Google automatically adds a "Not a government website" disclosure to Search ads in this category unless the advertiser is certified as a government provider. — [Kliken help article](https://help.kliken.com/en/articles/12461228-google-ads-policy-update-government-documents-and-services-disclosure-october-2025). Tightened rules require an authorized provider's domain to be linked from an official government website. — [Search Engine Land](https://searchengineland.com/google-tightens-ads-policy-for-government-document-providers-484342). Some advertisers report suspensions under this policy they believe were wrong. — [ClickGuard](https://www.clickguard.com/blog/google-ads-disapproving-accounts/)
- **Financial services verification**: rolling out to 24 more EU/EEA markets from July 23 (2026), with insurance in scope. It is done through partner G2 plus Google's own verification, country by country. The UK program requires FCA authorization. G2's country list does not include the US. — [Search Engine Land](https://searchengineland.com/google-expands-financial-services-ad-verification-across-24-european-markets-480833); [Google blog](https://blog.google/products/ads-commerce/eu-financial-advertiser-verification/); [PPC Land](https://ppc.land/google-expands-financial-ad-verification-to-24-eu-and-eea-countries/)
- **Certification facts for copy accuracy**: only NCEI, on behalf of the Department of Commerce, issues certified records for court use. NWS calls its own compiled storm data preliminary and uncertified. — [NCEI certification](https://www.ncei.noaa.gov/certification); [NWS Amarillo](https://www.weather.gov/ama/stormdata)

### Inferences
- Is a NOAA-data report a "government document"? Probably not: it is a private compilation of public data, not a government-issued record or a filing service. But ads using "NOAA report", "official weather report" or "certified weather record" could be classified as government-document or government-affiliated and draw the auto-disclosure or a disapproval. Recommended copy: "Built from public NOAA/NWS records" plus "Independent report — not affiliated with NOAA". Do not use NOAA logos or seals, a .gov look, or "official" or "certified".
- Do not use "certified" in headlines. If bidding on "certified weather report" queries, say in the ad "Not a certified NCEI record" and offer the NCEI route on the landing page, as StormRecord does.
- Do not promise claim outcomes ("win your claim", "insurer-approved"). "Evidence to support your claim" or "document conditions at your address" stays within the policy.
- Show the price in the ad ("$9.99 instant PDF") and on the landing page before checkout to satisfy the dishonest-pricing rules. A "free preview" is fine only if the preview really is free.
- The business name in ads must match the site (WeatherEvidence) and must not imply a government or insurer brand.
- Destination requirements (from general Google policy knowledge; specific pages not retrieved): the landing page must work, show the business identity and contact details, include a privacy policy, and match the ad's promise. Destination pages not retrieved: verify.

### Gaps
- The current wording of the US-specific Financial products and services policy was not retrieved. Confirm that a non-insurance data seller does not trigger any insurance-related restriction.
- The Destination requirements and Advertiser verification pages were not retrieved. Google generally requires advertiser identity verification for most accounts; confirm the timing for new accounts.

## 5. Campaign structure: storm-triggered geo, negatives, match types, assets, conversion tracking

### Takeaway
Use a small, tightly themed Search campaign with phrase and exact match on report and history intent, a large negative list, and a standing "storm surge" campaign or ad group that is switched on by ZIP or radius after SPC hail and wind reports (the same pre-built-and-paused pattern roofers use). Track purchases server-side from Creem webhooks. Carry the gclid through checkout metadata and upload with offline conversion import or enhanced conversions. A redirect-only pixel is not reliable enough.

### Cited Findings
- **Storm playbook (roofing agencies)**: pre-build storm campaigns and keep them paused, then within hours of an event activate geo-targets for the hit ZIPs and pause the others. — [Stackmatix](https://www.stackmatix.com/blog/roofing-google-ads-storm-season). Target SPC hail swaths at ZIP level rather than metro DMAs, which reach neighborhoods that were not hit. — [Elevarus storm playbook](https://elevarus.com/roofing-storm-response-paid-search-playbook/). Teams use custom polygon or radius targeting from storm maps — [OnlineJobs posting](https://www.onlinejobs.ph/jobseekers/job/1625947) — and raise bids in storm-impact ZIPs within a day of the event — [Colorado Web Impressions](https://coloradowebimpressions.com/roofing-ppc-colorado); [Silverback](https://www.silverbackstrategies.com/lists/best-google-ads-agencies-for-roofing-ranked-and-reviewed/)
- **Bidding during storms**: Smart Bidding can underperform because it learns from evergreen conversion data. One playbook recommends a separate storm conversion action, starting on Maximize Conversions with a daily cap and moving to tCPA after about 30 conversions in 30 days. — [Elevarus](https://elevarus.com/roofing-storm-response-paid-search-playbook/)
- **Storm CPC inflation**: 200–400% after storms. — [Stackmatix](https://www.stackmatix.com/blog/roofing-google-ads-storm-season)
- **Offline conversion import (GCLID)**: requires auto-tagging. GCLIDs are kept for 90 days, so conversions must be uploaded within that window. Enhanced conversions for leads accepts PII-matched uploads up to 63 days. For advertisers new to offline import, Google recommends starting with enhanced conversions for leads. If a click has not been processed yet, wait about 6 hours before a scheduled upload. — [Google: offline conversion imports FAQ](https://support.google.com/google-ads/answer/10029210); [Google: set up offline conversions using GCLID](https://support.google.com/google-ads/answer/7012522)
- **Unverified**: a third-party blog says that from June 15, 2026, offline conversion and enhanced-conversions-for-leads uploads moved to the Data Manager API and are blocked in the Google Ads API except for allowlisted legacy tokens. — [Relevant Audience](https://www.relevantaudience.com/google-ads-en/google-ads-offline-conversion-import-guide/)
- **Enhanced conversions for web**: the tag sends the GCLID plus an order ID at conversion, and hashed user data can be uploaded later keyed to the order ID. Google-reported median uplift is about 5% on Search, figures repeated by vendors. — [Google Ads API docs](https://developers.google.cn/google-ads/api/docs/conversions/enhanced-conversions/web-setup?hl=en); [Shopify blog](https://www.shopify.com/blog/enhanced-conversions-google-ads)
- **Third-party checkout**: when checkout is on another domain, the GCLID is not present there. A forum workaround is to append the GCLID to the checkout URL. — [Stape community](https://community.stape.io/t/google-ads-conversions-third-party-domain/3693)
- **Creem**: checkout creation accepts `metadata` and a `success_url`. After payment the buyer is redirected to the success_url with checkout_id, order_id, customer_id, product_id, request_id and a signature as query parameters. The `checkout.completed` webhook contains the checkout, order, product and customer objects, and its signature should be verified. Webhook retries stop after about a day, so reconciliation is advisable. Success URLs must be HTTPS. — [Creem quickstart](https://docs.creem.io/getting-started/quickstart); [Creem webhooks](https://docs.creem.io/code/webhooks); [goloop/creem](https://github.com/goloop/creem); [Medium write-up](https://medium.com/@maziki/i-spent-a-day-integrating-creem-a-payment-service-into-a-react-native-app-f47296701afe). An analytics vendor attributes Creem revenue by passing a visitor ID in checkout metadata and reading it from `checkout.completed`. — [Piqo docs](https://ogmetatags.com/docs/creem)

### Inferences
- **Structure for a first test** (about $10–$20 a day, US):
  1. *Evergreen "Report" campaign*: ad groups for (a) hail report by address/date, (b) storm/wind report by address/date, (c) weather history by date for an insurance claim, (d) "past weather for [date]" long-tail. Use phrase and exact match only at launch; broad match under Smart Bidding needs conversion volume this account won't have. Manual CPC or Max Clicks with a bid cap of about $1.00–$1.50 (from the section 3 math).
  2. *Storm-surge campaign, paused by default*: identical keywords plus "[city] hail storm [month]" variants. After an SPC hail or wind report cluster, enable it with radius or ZIP targets around the reports for about 2–6 weeks, since claims are filed in the weeks after the storm. Set location targeting to "Presence" (people in or regularly in the area). Don't raise bids into roofer-inflated auctions; the gain comes from relevance, not higher bids.
  3. Optional *adjuster/contractor* ad group ("weather verification report for adjusters") to test whether professional buyers convert. Keep insurance-integration features out of scope, per the brief.
- **Starter negatives** (in addition to those in the brief): forecast, radar, live, today, tomorrow, 10 day, hourly, app, jobs, career, salary, meteorologist degree, map free, free, tracker, alert, roofer, roofing, contractor, repair, replacement, near me, lawyer, attorney, adjuster jobs, public adjuster, insurance quote, insurance companies, cheap insurance, car insurance, auto, hurricane tracker, chaser, siren. Add "free" only after checking whether free-intent searchers convert on the preview. Review search terms weekly.
- **Assets**: sitelinks for "Sample report", "What's included", "Not certified? Get NCEI certified data", "FAQ for adjusters". Callouts: "Instant PDF", "Address-specific", "NOAA/NWS source data", "Distance and bearing to station". A structured snippet listing the data types (Hail, Wind, Lightning, Precipitation, Storm Events). A price asset at $9.99. Use no logos resembling NOAA's.
- **Ad copy examples within policy**: "Hail Report for Your Address — $9.99 Instant PDF"; "Weather on Your Loss Date, by Address"; "Built From Public NOAA/NWS Records"; "Independent Report – Not a Gov't Site". Avoid "Official", "Certified", "NOAA Report" and "Get Your Claim Paid".
- **Conversion tracking with Creem**:
  1. Auto-tagging on. On landing, store gclid, gbraid and wbraid in a first-party cookie and in the server session.
  2. When creating the Creem checkout server-side, put gclid/gbraid and an internal order reference in `metadata`.
  3. On a verified `checkout.completed` webhook, record the purchase (value 9.99 USD, order_id as the transaction ID for deduplication).
  4. Upload it as a click conversion (offline import with gclid, or enhanced conversions using the hashed buyer email). Check whether this now goes through the Data Manager API.
  5. Also fire a client-side Google tag purchase event on the HTTPS success_url page with the same order_id, so Google can deduplicate. Use the server upload as the primary conversion action and the browser tag as secondary or for diagnostics.

### Gaps
- No source confirms that Creem has a native Google Ads integration; a custom webhook-to-Google upload is assumed.
- No data on how long after a storm homeowners and adjusters search for loss-date reports (to size the surge window). The 2–6 weeks above is an inference, not a sourced figure.
- I could not verify whether Google classifies weather-data reports under any restricted category. A small pre-launch test (a few ads, low budget) will show any automatic disclosures or limited-approval labels.
