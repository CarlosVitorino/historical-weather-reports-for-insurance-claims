"""Search-facing content: how the report is made, what "certified" means, and how-to guides.

Each page answers one question people search for, in plain words, and links to the sources it names. Wording rules
(see docs/reports/Competitor SEO and ads positioning.md): never call the report certified, official, a NOAA report,
court-admissible or proof; say what it shows and where each number comes from.
"""
from dataclasses import dataclass
from datetime import date

from . import BRAND
from .report import MIN_DATE

PRICE = "$9.99"


@dataclass(frozen=True)
class Page:
    path: str
    title: str          # <title>: the query first, brand last
    h1: str
    eyebrow: str
    description: str    # meta description, ~150 characters
    updated: date
    body: str
    guide: bool = False


def _a(href: str, text: str) -> str:
    return f'<a href="{href}" rel="noopener" target="_blank">{text}</a>'


NCEI_STORM_EVENTS = _a("https://www.ncei.noaa.gov/stormevents/", "NCEI Storm Events Database")
SPC_REPORTS = _a("https://www.spc.noaa.gov/climo/reports/", "Storm Prediction Center storm reports")
GHCNH = _a("https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly",
           "Global Historical Climatology Network – hourly (GHCNh)")
CDO = _a("https://www.ncei.noaa.gov/cdo-web/", "Climate Data Online")
IEM_VTEC = _a("https://mesonet.agron.iastate.edu/vtec/search.php", "Iowa Environmental Mesonet warning search")
SWDI = _a("https://www.ncei.noaa.gov/products/severe-weather-data-inventory", "Severe Weather Data Inventory")
NCEI_CERT = _a("https://www.ncei.noaa.gov/services/certification", "NCEI's certification page")
CENSUS = _a("https://geocoding.geo.census.gov/", "US Census Bureau Geocoder")

CTA = f"""<div class="cta-box"><div><b>Get these records for one address and date</b>
<span>Stations, warnings, storm reports, Storm Events, radar hail and lightning in one PDF, each with its distance
and direction from the property. {PRICE}.</span></div><a class="btn btn-amber" href="/order">Start a report</a></div>"""


METHODOLOGY = Page(
    path="/methodology",
    title=f"How the report is built: sources and methods — {BRAND}",
    h1="How the report is built",
    eyebrow="Methodology",
    description="The public NOAA, NWS and Census records behind every report, how distances and warning checks are "
                "worked out, how current each source is, and what the report does not show.",
    updated=date(2026, 10, 15),
    body=f"""
<p class="lede">Every number in the report comes from a public US government record, and the report names the record
it came from. Values are shown as published, never blended or smoothed. Here is what we use and how.</p>

<h2>1. The location</h2>
<p>The address is matched with the {CENSUS}. When it can't be matched, for example a rural or new property, you place
a pin on the map and the report says the location was set by pin. All distances are measured from that one point.</p>

<h2>2. Measured weather at nearby stations</h2>
<p>Wind, gusts, rain and temperature come from NOAA's {GHCNH}, the archive of hourly reports from airport and other
weather stations. The report lists the nearest stations, each with its distance and direction from the property, and
shows every report the station sent that day. It leads with the nearest airport station, because those measure wind
to a common standard, unless another wind-measuring station is much closer.</p>
<p>A station measures the weather where it stands, not at the property. The distance is printed next to every reading so
you can judge how close it is.</p>

<h2>3. Warnings and the warning-area check</h2>
<p>Every National Weather Service watch and warning for the day is taken from the {IEM_VTEC} archive of NWS products
(Iowa State University), with the full bulletin text. For warnings drawn as an area on the map, the report checks
whether the property's point was inside that area, and if not, how far outside it was.</p>

<h2>4. Storm reports</h2>
<p>NWS Local Storm Reports are what spotters, emergency managers, the public and automated stations reported on the
day: hail sizes, measured and estimated gusts, damage, tornadoes. They are preliminary, and the report shows them as
issued, sorted by distance from the property.</p>

<h2>5. NOAA Storm Events</h2>
<p>The {NCEI_STORM_EVENTS} is NOAA's reviewed record of significant weather, including tornado paths. It is
published a few months after each month ends. For recent dates the report says it is not published yet, which is
different from "no event".</p>

<h2>6. Radar hail and lightning</h2>
<p>Radar hail detections come from NEXRAD radar via NOAA's {SWDI}. They estimate hail aloft from the radar, not hail
measured on the ground. Lightning comes from the same inventory as daily strike counts per grid cell of about
6–7 miles. Individual strike locations are not public, so the report gives counts near the property, not exact
strikes.</p>

<h2>Distances and directions</h2>
<p>Distances are straight-line miles from the property. Directions point from the property to the record, so "4.7 mi
WSW" means the record lies west-southwest of the property. Some records have approximate positions: storm reports are
often placed at the nearest town or road.</p>

<h2>Same inputs, same report</h2>
<p>Every source response is stored exactly as received, with a fingerprint (SHA-256 hash) and the time it was
retrieved. The report ID is derived from those fingerprints, so the same ID always means the same PDF, and anyone can
check the numbers against the original sources listed on the report's last pages.</p>

<h2>What the report does not do</h2>
<ul><li>It does not say whether weather caused damage, or whether a loss is covered.</li>
<li>It is not a certified government record or an expert opinion.
<a href="/certified-weather-records">When you need one of those</a>.</li>
<li>Missing values are shown as missing, never as zero.</li>
<li>It covers US addresses and dates from {MIN_DATE.year} to yesterday. No forecasts.</li></ul>
{CTA}""")


CERTIFIED = Page(
    path="/certified-weather-records",
    title=f"Certified weather records: what they are and when you need one — {BRAND}",
    h1="Do you need a certified weather record?",
    eyebrow="Certified records",
    description="What a certified NOAA weather record is, when a court or attorney may ask for one, when an expert "
                "meteorologist is the right call, and what an address report is for.",
    updated=date(2026, 10, 29),
    body=f"""
<p class="lede">Usually not for a claim, sometimes for a lawsuit. A {BRAND} report is <b>not</b> a certified record. Here
is the difference, so you can pick what your situation needs.</p>

<h2>What "certified" means</h2>
<p>NOAA's National Centers for Environmental Information (NCEI) can certify copies of its own weather records, so they
meet the authentication rules for records used as evidence in court. Only NCEI does this for NOAA data. You order it
from NCEI and pay a fee — about $180 for the first 40 pages, and most orders start higher. A {BRAND} report is
{PRICE} and is not certified. See {NCEI_CERT} for current prices and turnaround.</p>
<p>A certified copy is the raw record, such as a station's observations. It does not interpret the record for your
address or say how far the station was from it.</p>

<h2>When you may need one</h2>
<ul><li>A lawsuit, appraisal or hearing where your attorney asks for authenticated records.</li>
<li>A subpoena or court rule that requires certified copies.</li></ul>

<h2>When you may need an expert</h2>
<p>If the cause of damage or the date of loss is disputed and the claim is large, a consulting meteorologist can study
the event and testify. That costs far more and takes longer, and is the right tool when the outcome depends on expert
opinion.</p>

<h2>What an address report is for</h2>
<p>For most claims the question is simpler: what did public records show near this property on this date? The report
answers that in one PDF: measured gusts at named stations, whether the property was inside a warning area, storm
reports and NOAA Storm Events, radar hail and lightning, each with its distance and direction. It is useful for a
claim file, a conversation with an adjuster, or as a starting point for an expert, who can trace every number back
to its source.</p>

<table class="ctable"><thead><tr><th></th><th>{BRAND} report</th><th>NCEI certified copy</th>
<th>Consulting meteorologist</th></tr></thead><tbody>
<tr><td>What you get</td><td>Records for one address and date, with distances</td><td>Authenticated raw records</td>
<td>Expert analysis and testimony</td></tr>
<tr><td>Certified for court</td><td>No</td><td>Yes</td><td>Expert's own opinion</td></tr>
<tr><td>Turnaround</td><td>About a minute</td><td>Days or longer</td><td>Days to weeks</td></tr>
<tr><td>Price</td><td>{PRICE}</td><td>NCEI fee</td><td>Quoted per case</td></tr>
</tbody></table>
<p class="fine">Not legal advice. Ask your attorney or adjuster what they need before you order anything.</p>
{CTA}""")


GUIDE_NOAA = Page(
    path="/guides/noaa-weather-data-for-insurance-claim",
    title=f"How to get NOAA weather data for an insurance claim — {BRAND}",
    h1="How to get NOAA weather data for an insurance claim",
    eyebrow="Guide",
    description="Step by step: find storm reports, NOAA Storm Events, station wind measurements, warnings and radar hail "
                "for your address and date of loss, all from free public sources.",
    updated=date(2026, 10, 15),
    guide=True,
    body=f"""
<p class="lede">All of the weather records an insurer looks at are public and free. They are spread across several
NOAA and NWS sites. Here is where to find each one for your address and date of loss.</p>

<h2>1. Write down the exact location and date</h2>
<p>Use the property's coordinates, not just the city. Use the local date: a storm at 11 pm local time is already the
next day in UTC, which many NOAA files use. If you're not sure of the date, see
<a href="/guides/date-of-loss-weather">how to check your date of loss</a>.</p>

<h2>2. Check storm reports for the day</h2>
<p>The {SPC_REPORTS} list hail, wind and tornado reports for each day, with times and positions. They are preliminary
but available the next morning. Note how far each report is from the property.</p>

<h2>3. Search the NOAA Storm Events Database</h2>
<p>The {NCEI_STORM_EVENTS} is NOAA's reviewed record. Search by state, county and date. It includes hail sizes, wind
speeds, damage notes and tornado paths. It appears a few months after the month ends, so a recent storm may not be
there yet.</p>

<h2>4. Get measured wind from the nearest station</h2>
<p>Find the nearest airport weather station and download its hourly observations from NOAA's {CDO} or {GHCNH}. Look
for the gust values during the storm. See <a href="/guides/wind-speed-on-a-specific-date">how to read wind speed for
a specific date</a>.</p>

<h2>5. Check whether the property was under a warning</h2>
<p>The {IEM_VTEC} lets you search warnings by point. It shows severe thunderstorm and tornado warnings whose area
contained that location, with the bulletin text.</p>

<h2>6. Look for radar hail</h2>
<p>NOAA's {SWDI} has NEXRAD hail detections by area and date. They estimate hail aloft, so treat them as supporting
evidence alongside ground reports.</p>

<h2>7. Put it together with distances</h2>
<p>For each record, write down its distance and direction from the property and the source it came from. An adjuster
will weigh a measured gust 3 miles away differently from a report 20 miles away.</p>
<p class="fine">Need records certified for court? That is a separate NCEI service: see
<a href="/certified-weather-records">certified weather records</a>.</p>
{CTA}""")


GUIDE_DATE = Page(
    path="/guides/date-of-loss-weather",
    title=f"How to check the weather on your date of loss — {BRAND}",
    h1="How to check the weather on your date of loss",
    eyebrow="Guide",
    description="Why the date of loss matters for a weather claim, how to confirm which day the storm hit your "
                "address, and what to do when the damage was found days or weeks later.",
    updated=date(2026, 10, 15),
    guide=True,
    body=f"""
<p class="lede">The date of loss is the day the storm happened, not the day you found the damage. Insurers check it
against weather records, so it's worth confirming before you file.</p>

<h2>Why the date matters</h2>
<p>A claim is checked against the weather on the date you give. If the storm happened on a different day, the records
for your date may show nothing, even though the damage is real. Policy start dates and filing deadlines also depend
on it.</p>

<h2>If you found the damage later</h2>
<ul><li>List the days with storms since the last time you know the roof or property was fine.</li>
<li>Check {SPC_REPORTS} for hail or wind reports near you on each of those days.</li>
<li>Pick the day with the strongest records closest to the property, and check it in detail.</li></ul>

<h2>Watch for storms around midnight</h2>
<p>Many NOAA files use UTC time. A storm at 8 pm Central is already the next day in UTC. Always convert to local time
before deciding the date. Our report covers the full local day, midnight to midnight, in the property's time zone.</p>

<h2>Check more than one source</h2>
<p>Storm reports can be missing in rural areas, and stations can be miles away. A stronger picture combines measured
gusts at nearby stations, warnings that covered the property, ground reports and radar hail. When they agree on one
day, that's your date of loss.</p>

<h2>Comparing two possible dates</h2>
<p>Order a report for each date and compare them side by side. Each costs {PRICE} and shows the same sections, so the
difference is easy to see.</p>
{CTA}""")


GUIDE_WIND = Page(
    path="/guides/wind-speed-on-a-specific-date",
    title=f"How to find the wind speed at an address on a specific date — {BRAND}",
    h1="How to find the wind speed at an address on a specific date",
    eyebrow="Guide",
    description="Wind is measured at weather stations, not at every address. How to find the nearest station, read "
                "gusts versus sustained wind, and judge how close the measurement is.",
    updated=date(2026, 10, 15),
    guide=True,
    body=f"""
<p class="lede">No one measures the wind at every house. The closest you can get is the nearest weather station that
recorded that day, plus any measured gusts reported nearby.</p>

<h2>1. Find the nearest stations</h2>
<p>Airport stations (ASOS and AWOS) measure wind to a common standard and report at least every hour, and more often
during storms. NOAA keeps their history in {GHCNH}, which you can browse through {CDO}. Note each station's distance
from the property.</p>

<h2>2. Read gusts, not just wind speed</h2>
<p><b>Sustained wind</b> is the average over about two minutes. <b>Gusts</b> are the short peaks, and they are what
damages roofs and trees. Look for the highest gust in the hours of the storm, and the time it was recorded.</p>

<h2>3. Mind the units and the time</h2>
<p>Station files often use knots or meters per second, and UTC time. 1 knot is 1.15 mph; 1 m/s is 2.24 mph. Convert
times to the property's local time.</p>

<h2>4. Add measured gusts from storm reports</h2>
<p>Storm reports sometimes include gusts measured by other stations or trained spotters, closer to the property. The
{SPC_REPORTS} and the {NCEI_STORM_EVENTS} mark whether a gust was measured or estimated.</p>

<h2>5. Judge how close is close enough</h2>
<p>Thunderstorm gusts can vary a lot over a few miles. A station 3 miles away says more than one 20 miles away, and
a property inside a severe thunderstorm warning area supports a strong gust even where no station measured it.</p>
<p>Our report does this for you: it lists the nearest stations with distance and direction, charts the wind through
the day, marks the peak gust, and adds warnings and storm reports nearby.</p>
{CTA}""")


GUIDE_HAIL = Page(
    path="/guides/hail-damage-claim",
    title=f"Did it hail at your address? How to prove hail damage — {BRAND}",
    h1="Did it hail at your address?",
    eyebrow="Guide",
    description="How to prove hail fell at your address on your date of loss, what size hail damages a roof, how to "
                "tell hail from wear, and how to document it for an insurance claim.",
    updated=date(2026, 10, 29),
    guide=True,
    body=f"""
<p class="lede">A hail claim is decided on two things: whether hail actually fell at your address on your date of
loss, and whether the damage looks like hail and not age. Here is how to prove both, in order.</p>

<h2>1. Prove the storm first</h2>
<p>Before you climb a ladder, establish that hail fell near your property on that date. The records are public: the
{SPC_REPORTS} list hail by day with size and position, the {NCEI_STORM_EVENTS} is NOAA's reviewed record, and radar
hail appears in the {SWDI}. The work is pulling all three and measuring each report's distance and direction from your
address — a report three miles away means more than one twenty miles away.</p>
<p>Our report does this step in about a minute: the hail reports near your address on your date of loss, each with its
size, distance and direction, plus ground reports and radar detections side by side. {PRICE}.</p>

<h2>2. Know what size hail damages a roof</h2>
<p>Generally, hail needs to be about 1¼ inches (half-dollar size) to damage heavy composite or wood-shake shingles.
Lightweight shingles can show damage from 1-inch (quarter-size) hail. Hail under about ¾ inch usually only marks
shingles that were already deteriorated.</p>

<h2>3. Check the soft metal first</h2>
<p>Soft metal does not age the way shingles do, so it is the clearest sign hail reached your property. Look for dents
and spatter marks on gutters, downspouts, roof vents, pipe boots, window screens, the AC unit fins, the mailbox and
fence caps. These show the hail's size and which way it came from.</p>

<h2>4. The test square</h2>
<p>Mark a 10 by 10 foot square on each roof slope with chalk and count the hits inside it. A hail hit on a shingle is
a bruise: granules knocked off, the spot soft, the mat underneath sometimes cracked. Hits are random; they do not run
in lines.</p>

<h2>5. Hail, or wear and tear?</h2>
<table class="ctable"><thead><tr><th>What you see</th><th>What it usually is</th></tr></thead><tbody>
<tr><td>Random soft bruises with the granules gone</td><td>Hail</td></tr>
<tr><td>Small pits or bubbles with no bruise</td><td>Blistering</td></tr>
<tr><td>Scuffs or scrapes in a line or pattern</td><td>Foot traffic or mechanical damage</td></tr>
<tr><td>Even granule loss across the whole slope</td><td>Age and wear</td></tr>
</tbody></table>
<p>Claim what is hail. Leave the rest alone — photographing the wear too shows the adjuster you can tell the
difference.</p>

<h2>6. Build the paper trail</h2>
<p>Photograph everything before repairs, wide then close, and label each by slope and direction. Keep the claim
number, the date of loss, every call and email with the carrier, and the summary you send the adjuster after the
visit.</p>

<h2>The one step worth paying for</h2>
<p>Steps 2 to 6 are yours to do with a camera and chalk. Step 1 — proving the storm — is the tedious, technical one:
four NOAA sources, distances and directions, ground reports versus radar. Our report does it in about a minute, in one
PDF you can attach to the claim.</p>
{CTA}""")


GUIDE_LIGHTNING = Page(
    path="/guides/lightning-damage-claim",
    title=f"Lightning strike near your house? How to check — {BRAND}",
    h1="Lightning strike near your house?",
    eyebrow="Guide",
    description="How to tell whether lightning struck near your property on your date of loss, what public data shows, "
                "when a commercial strike report is worth it, and how to document the damage.",
    updated=date(2026, 10, 29),
    guide=True,
    body=f"""
<p class="lede">Lightning claims usually turn on one question: was a strike near your property on your date of loss.
Detection networks record every cloud-to-ground strike with GPS, and NOAA publishes daily counts. Here is how to check,
from cheapest to most detailed.</p>

<h2>1. Start with the free public data</h2>
<p>NOAA's {SWDI} publishes daily lightning strike counts in grid cells of about 6–7 miles. It will not give you an
exact strike location, but it tells you whether lightning was near your property at all on that date — which is the
first thing an adjuster asks. Our report includes this: lightning counts near your address on your date of loss,
alongside hail, wind and warnings. {PRICE}.</p>

<h2>2. If you need an exact strike location</h2>
<p>Commercial detection networks record individual strikes with GPS coordinates and timestamps. A report from one of
them (for example Vaisala's STRIKEnet, sold through CoreLogic) typically searches a radius around your address for a
given window and costs roughly $95. The public data is a good first step: if it shows no lightning near you, you may
not need to spend the $95.</p>

<h2>3. Document the physical evidence</h2>
<p>Photograph scorched outlets, melted or discolored fixtures, a tripped breaker panel, and damage to outdoor equipment
like the AC compressor. Keep every damaged item until the adjuster has seen it — a fried surge protector or a melted
outlet is physical evidence of the strike.</p>

<h2>4. Get an electrician's report</h2>
<p>A written assessment from a licensed electrician, on their letterhead, connects the electrical damage to the event.
It is the piece adjusters weight most heavily alongside the weather data.</p>

<h2>5. Assemble the proof of loss</h2>
<p>Many policies require a sworn Proof of Loss form that ties each damaged item to the event. Match your inventory and
receipts to the lightning counts and the electrician's report. Submit by the deadline in the demand letter — missing it
can sink a valid claim.</p>

<h2>The cheap first step</h2>
<p>Before you pay for an exact strike report, check the public counts. If lightning was near your address on your date
of loss, our report shows it for {PRICE}; if not, it saves you the cost of a $95 commercial report.</p>
{CTA}""")


GUIDE_INSURER = Page(
    path="/guides/how-insurers-verify-weather-claims",
    title=f"How insurance companies verify weather claims — {BRAND}",
    h1="How insurance companies verify weather claims",
    eyebrow="Guide",
    description="What adjusters check when they verify a weather claim: storm reports, NOAA Storm Events, radar and "
                "warnings, why dates get disputed, and what to attach so the records match your date of loss.",
    updated=date(2026, 10, 29),
    guide=True,
    body=f"""
<p class="lede">When you file a weather claim, the adjuster checks your claimed date of loss against archived records.
Here is what they look at, why dates get disputed, and how to make sure the records match what you say happened.</p>

<h2>1. What they check</h2>
<p>The {SPC_REPORTS} list hail, wind and tornado reports for each day, with times and positions. The
{NCEI_STORM_EVENTS} is NOAA's reviewed record, including tornado paths. NEXRAD radar hail and wind appear in the
{SWDI}, and the {IEM_VTEC} archive shows which warnings covered your address. An adjuster will compare your date of
loss against all of these.</p>

<h2>2. Why dates get disputed</h2>
<p>The date of loss is the day the storm happened, not the day you found the damage. NOAA records often use UTC time,
so a storm late in the evening can already be the next day. And "no hail report near you" does not mean "no hail" —
reports are sparse in rural areas, and a report may simply not have been filed.</p>

<h2>3. The distance problem</h2>
<p>A report is only as useful as its distance from your property. An adjuster will weigh a measured gust three miles
away very differently from a report twenty miles away. For every record, the distance and direction from your address
matters.</p>

<h2>4. What to attach</h2>
<p>Attach the weather records for your address and date, plus photographs and any repair estimates. The goal is for the
records and your claim to agree: same date, same place, same event. Where they disagree, be ready to explain why — a
different day, a nearby station, or a preliminary report.</p>

<h2>See what the adjuster sees</h2>
<p>Our report is the same public records an adjuster checks, organized for one address and date — hail, wind, warnings
and lightning, each with its distance and direction. Run it before you file, so you know what the records say before
the insurer does. {PRICE}.</p>
{CTA}""")


GUIDES = [GUIDE_NOAA, GUIDE_DATE, GUIDE_WIND, GUIDE_HAIL, GUIDE_LIGHTNING, GUIDE_INSURER]
PAGES = {p.path: p for p in [METHODOLOGY, CERTIFIED, *GUIDES]}
