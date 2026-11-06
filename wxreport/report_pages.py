"""The public page for each kind of report, and the /reports index. Wording follows content.py: say what the report
shows and where it comes from, and say plainly what it can't show."""
import hashlib
import json
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

from . import BRAND
from .content import GUIDE_DATE, GUIDE_HAIL, GUIDE_INSURER, GUIDE_WIND, PRICE, Page
from .brand import mark_svg
from .reporttypes import TYPES

ART = json.loads((Path(__file__).parent / "static/report-art.json").read_text())   # scripts/make_report_art.py
UPDATED = date(2026, 11, 6)
CERTIFIED_LINK = '<a href="/certified-weather-records">certified record</a>'
SECTION = ("Reports", "/reports")


@dataclass(frozen=True)
class Spec:
    slug: str
    title: str
    h1: str
    description: str
    card: str                   # one line, for the cards and the /reports list
    lede: str
    who: list[tuple[str, str]]  # who uses it, and for what
    shows: list[str]
    limits: list[str]
    faq: list[tuple[str, str]]
    sample: str
    related: tuple = ()
    menu: str = ""              # a few words, for the Reports menu
    shows_title: str = ""
    limits_title: str = ""
    covers: str = ""            # for the comparison on /reports
    leads: str = ""
    situations: tuple = ()      # when someone needs it, for the cards


SPECS = [
    Spec("car-hail-damage",
         f"Hail report for a damaged car: date, size and distance — {BRAND}",
         "Hail report for a damaged car",
         f"When hail fell near where your car was parked, how big it was and how far away, from public records. For a "
         f"comprehensive claim, a repair estimate or a car sale. {PRICE} PDF.",
         "For a car, truck or fleet hit by hail.",
         "When did hail fall where your car was parked, and how big was it? Enter the location and date, and get every "
         "hail record nearby in time order, in one PDF.",
         [("Car owners", "Back up a comprehensive claim with the date, or find out which storm it was."),
          ("Dent repair shops", "Put the hail record in the customer's claim file."),
          ("Dealers and fleets", "Date hail on vehicles kept outdoors."),
          ("Buyers and sellers", "Check whether hail fell where a car with dents was kept. The report can't identify "
                                 "a car, only what fell at a place.")],
         ["A hail timeline: every ground report within 15 miles and the largest radar estimates, in time order",
          "The largest hail within 5 miles, with its size in everyday terms, such as golf ball",
          "The closest hail record and the time span of hail near the location",
          "Watches and warnings that covered the location"],
         ["It covers one location. If the car might have been at home or at work, order one for each.",
          "It doesn't identify a vehicle or say what caused its damage.",
          "Radar estimates hail aloft, not hail on the ground."],
         [("Which address should I enter?", "Where the car was when the hail fell, such as your home, your workplace "
           "or a parking lot. You can place a pin on the map for a parking lot."),
          ("Does insurance need this?", "Often not. Hail is usually handled under comprehensive coverage, and many "
           "claims go through on photos and an estimate. It helps most when the date is unclear or questioned."),
          ("What if I don't know the date?", f'Read <a href="{GUIDE_DATE.path}">how to check your date of loss</a> or '
           'look up your city in <a href="/storm-reports?period=all&amp;kind=hail">Storm Reports</a>.')],
         "/static/sample-car-hail-damage.pdf", (GUIDE_HAIL, GUIDE_DATE, GUIDE_INSURER),
         'For a dented or damaged vehicle', 'Every hail record near the car, in time order.',
         'It records the storm, not the car.',
         'The day, in local time', 'Hail chart and timeline, warnings',
         ('Hail dented your parked car', 'An insurer questions the date', "You're buying a car with dents")),
    Spec("car-accident",
         f"Weather report for a car accident, hour by hour — {BRAND}",
         "Weather report for a car accident",
         f"Hour-by-hour weather around the time of an accident: visibility, rain, fog, freezing rain, temperature and "
         f"warnings, from the nearest station. {PRICE} PDF.",
         "For a crash where the weather played a part.",
         "What was the weather when the accident happened? Enter the location, date and time, and see what the nearest "
         "station recorded in the hours around it.",
         [("Drivers", "Add detail when a police report only says rain or fog."),
          ("Attorneys and paralegals", "See early what the records show, before deciding on a certified record or an "
                                       "expert."),
          ("Fleet and trucking managers", "Put the weather in an incident file.")],
         ["The three hours either side of the accident at the nearest station: temperature, lowest visibility, "
          "highest gust, precipitation and the weather reported",
          "The weather, visibility and temperature for the hour of the accident on page one",
          "Every watch and warning in effect at that moment, with the text of the latest bulletin"],
         ["Readings come from the station, not the road. The report names the station and its distance.",
          "It doesn't show the road surface, or whether black ice was there.",
          f"It doesn't say who was at fault, and it isn't a {CERTIFIED_LINK}."],
         [("How exact does the time need to be?", "Your best estimate is fine: the report covers three hours either "
           "side."),
          ("Can it show black ice?", "No record does that directly. It shows air temperature, freezing rain or snow "
           "and recent precipitation, which are the conditions that form it."),
          ("Can I use this in court?", 'It isn\'t certified, and a court may require a certified record. See '
           '<a href="/certified-weather-records">certified weather records</a>.')],
         "/static/sample-car-accident.pdf", (GUIDE_WIND, GUIDE_DATE, GUIDE_INSURER),
         'Visibility, ice and rain at the time', 'The hours around the accident, not a summary of the day.',
         'It records the air at the station, not the road.',
         '3 hours either side', 'Hours around the accident, warnings and their text',
         ('Rain, fog or ice cut visibility', 'The police report only says rain', 'A fleet needs an incident file')),
    Spec("slip-and-fall-on-ice",
         f"Weather report for a slip and fall on ice — {BRAND}",
         "Weather report for a slip and fall on ice",
         f"The 72 hours before a fall on ice or snow: temperature, precipitation, thaw and refreeze, from the nearest "
         f"station. For injured people and property managers. {PRICE} PDF.",
         "For a fall on snow or ice outdoors.",
         "When did it last snow or rain, and did it freeze again? See the 72 hours before a fall, hour by hour, from "
         "the nearest weather station.",
         [("People who were hurt", "See what the weather did before you speak to an insurer or a lawyer."),
          ("Landlords and property managers", "Answer a complaint with the timing of the weather."),
          ("Snow removal contractors", "Compare service records with when snow or ice fell."),
          ("Attorneys", "Sort cases early, before ordering a certified record or an expert.")],
         ["Each day's low, high, precipitation and hours at or below 32°F",
          "Every hour of the 72 hours before the fall, with the hour of the fall marked",
          "When precipitation last fell, and what kind",
          "How many times the temperature crossed 32°F",
          "Watches and warnings during those hours",
          "Ice and snow reports within 10 miles"],
         ["It shows the weather at a station, not ice on a sidewalk or parking lot.",
          "It doesn't show when a surface was cleared or treated, or who was responsible.",
          f"It isn't a {CERTIFIED_LINK}. Some New York courts have rejected uncertified website printouts, so ask "
          "your attorney what you need."],
         [("Is this enough for a lawsuit?", 'Probably not on its own. It tells you what the records show, cheaply and '
           'early. For a case, your attorney may need <a href="/certified-weather-records">certified records</a> or '
           'a meteorologist.'),
          ("Does it show snow totals?", "It shows the precipitation and snow reported by the station, and snow depth "
           "when the station reports it. It doesn't give a snowfall total for the location."),
          ("What time should I enter?", "When the fall happened, as closely as you can. The report reads back 72 hours "
           "from there.")],
         "/static/sample-slip-and-fall-on-ice.pdf", (GUIDE_INSURER, GUIDE_DATE),
         'The 72 hours before a fall', 'What the weather did before the fall.',
         'It records the weather, not the surface.',
         '72 hours before', '72 hours of weather, warnings, ice and snow reports',
         ('You fell on an icy sidewalk', 'A tenant or visitor complained', "You're checking snow removal")),
    Spec("frozen-pipes",
         f"Weather report for a frozen pipe claim — {BRAND}",
         "Weather report for a frozen pipe claim",
         f"How cold it got and for how long in the week before a pipe burst: lows and hours below freezing from the "
         f"nearest station. {PRICE} PDF.",
         "For a pipe that burst in the cold.",
         "How cold was it before the pipe burst, and for how long? Enter the address and the date you found it, and see "
         "the week before from the nearest weather station.",
         [("Homeowners", "Put the cold on record for a claim and narrow down when it happened."),
          ("Landlords and tenants", "See the weather behind a dispute over a burst pipe."),
          ("Owners of vacant or second homes", "Date a loss you found on your next visit."),
          ("Plumbers and restoration companies", "Add the weather to the job file.")],
         ["The lowest temperature, and when it happened",
          "Hours at or below 32°F and at or below 20°F, day by day",
          "The longest unbroken stretch at or below freezing",
          "The first and last readings at or below 32°F",
          "Watches and warnings during those days"],
         ["It's outdoor air at the station, not the temperature inside the building.",
          "It doesn't show whether the heat was on. Insurers often ask for utility or thermostat records for that.",
          "It doesn't say a pipe froze, or why."],
         [("Which date should I enter?", "The day you found the burst pipe. The report covers that day and the seven "
           "days before it."),
          ("Why does it matter if the house was empty?", "Many policies require reasonable care to keep the heat on or "
           "drain the system, so insurers look closely at vacant homes. Check your policy's wording."),
          ("What temperature freezes a pipe?", "It depends on insulation and exposure, so the report gives the hours "
           "at two levels, 32°F and 20°F, rather than a verdict.")],
         "/static/sample-frozen-pipes.pdf", (GUIDE_INSURER, GUIDE_DATE),
         'The cold before a pipe burst', 'How cold it got, and for how long.',
         'It records the air outside, not the building.',
         '7 days before, and the date', 'Eight days of cold, warnings',
         ('You found a burst pipe', 'A vacant home flooded in a freeze', 'An insurer asks how cold it was')),
]


CC_BY = "https://creativecommons.org/licenses/by/2.0/"
# Open-licence photos, toned by scripts/make_report_photos.py. Credited wherever a card shows them.
PHOTOS = {
    "car-hail-damage": ("A windshield cracked by a hailstone", "Win Henderson, FEMA", "Public domain",
                        "https://commons.wikimedia.org/wiki/File:FEMA_-_44376_-_truck_windshield_with_hail_damage_in_OK.jpg", ""),
    "car-accident": ("A police car beside a crash on a snowy road", "D Coetzee", "CC0",
                     "https://commons.wikimedia.org/wiki/File:Police-car-snowy-road.jpg", ""),
    "slip-and-fall-on-ice": ("A city sidewalk covered in ice", "tlianza", "CC BY 2.0",
                             "https://www.flickr.com/photos/20133719@N00/3127743450", CC_BY),
    "frozen-pipes": ("Water frozen as it left a pipe", "Skakerman", "CC BY 2.0",
                     "https://www.flickr.com/photos/27482959@N08/3324523470", CC_BY),
}


def _pdf(s: "Spec") -> str:
    """The sample's address, changing with its content so a browser never shows an old copy."""
    data = (Path(__file__).parent / s.sample.removeprefix("/")).read_bytes()
    return f"{s.sample}?v={hashlib.sha256(data).hexdigest()[:8]}"


def credits() -> str:
    def one(p):
        lic = f'<a href="{p[4]}" rel="noopener license" target="_blank">{p[2]}</a>' if p[4] else p[2]
        return f'<a href="{p[3]}" rel="noopener" target="_blank">{p[1]}</a> ({lic})'
    return f'<p class="rt-credit">Photos, cropped and toned: {", ".join(one(p) for p in PHOTOS.values())}.</p>'


def card(s: "Spec") -> str:
    photo, kind = PHOTOS[s.slug], TYPES[s.slug]
    when = "".join(f"<li>{escape(x)}</li>" for x in s.situations)
    return f"""<a class="rt-card" href="{kind.path}"><span class="rt-ph"><img loading="lazy" width="800" height="500"
src="/static/photo-{s.slug}.webp" alt="{escape(photo[0], quote=True)}"><b>{escape(kind.name)}</b></span>
<span class="rt-body"><span class="rt-text">{escape(s.card)}</span><ul class="rt-when">{when}</ul>
<span class="rt-link">See this report <i aria-hidden="true">→</i></span></span></a>"""


def _start(slug: str, label: str = "Start this report") -> str:
    return f'<a class="btn btn-amber" href="/order?type={slug}">{label}</a>'


def _sample_card(s: "Spec") -> str:
    a = ART[s.slug]
    facts = "".join(f'<div><dt>{escape(f["label"])}</dt><dd><b>{escape(f["value"])}</b>{escape(f["detail"])}</dd></div>'
                    for f in a["facts"])
    return f"""<div class="rp rp-auto"><div class="rp-head">{mark_svg(24)}<div><div class="k">Sample report · {a["pages"]} pages</div>
<b>{escape(a["place"])}</b><span>{escape(a["date"])}</span></div></div>
<figure class="rp-chart">{a["chart"]}<figcaption class="vis-cap">{escape(a["caption"].upper())}</figcaption></figure>
<dl class="facts">{facts}</dl>
<div class="rp-foot"><span>Real records, real report</span><a href="{_pdf(s)}" target="_blank" rel="noopener">Open the
full sample →</a></div></div>"""


def _steps(s: "Spec") -> str:
    kind = TYPES[s.slug]
    what = "location, date and time" if kind.time_label else "location and date"
    return f"""<ol class="steps"><li><div><b>Enter the {what}</b><span>Pick the address from the suggestions, or place a
pin on the map.</span></div></li><li><div><b>Confirm the location and pay</b><span>You see the exact spot on a map before
paying {PRICE}. Secure checkout by Creem.</span></div></li><li><div><b>Download the PDF</b><span>Built from the government
archives while you wait, with a copy sent to your email.</span></div></li></ol>"""


def _body(s: Spec) -> str:
    kind, a = TYPES[s.slug], ART[s.slug]
    who = "".join(f"<li><h3>{escape(x)}</h3><p>{escape(y)}</p></li>" for x, y in s.who)
    shows = "".join(f"<li>{x}</li>" for x in s.shows)
    limits = "".join(f"<li>{x}</li>" for x in s.limits)
    faq = "".join(f"<details><summary>{escape(q)}</summary><p>{x}</p></details>" for q, x in s.faq)
    others = "".join(card(o) for o in SPECS if o.slug != s.slug)
    guides = "".join(f'<li><a href="{g.path}"><b>{escape(g.h1)}</b><span>{escape(g.description)}</span></a></li>'
                     for g in s.related)
    return f"""<section class="hero rh"><div class="wrap rh-main"><div>
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/reports">Reports</a> / {escape(kind.name)}</nav>
<p class="eyebrow">{escape(kind.name)} report</p><h1>{escape(s.h1)}</h1><p class="lede">{s.lede}</p>
<div class="cta-row">{_start(s.slug, f"Get this report — {PRICE}")}<a class="btn btn-ghost-dark" href="{_pdf(s)}" target="_blank"
 rel="noopener">View a sample report</a></div>
<ul class="assure"><li>Any US address</li><li>Delivered in about a minute</li><li>No subscription</li></ul>
<p class="rh-up">Updated {UPDATED:%B} {UPDATED.day}, {UPDATED.year}</p></div>
{_sample_card(s)}</div></section>
<section class="rs"><div class="wrap rs-two"><div><p class="eyebrow">What it shows</p><h2>{escape(s.shows_title)}</h2>
<ul class="rc-list">{shows}</ul><p class="rs-more">A short report on this question. Need every record for the date,
including raw station reports and all warning text? See the <a href="/">Property damage report</a>.</p></div>
<div class="rs-pages"><a href="{_pdf(s)}#page=2" target="_blank" rel="noopener"><img loading="lazy" width="935" height="1210"
 src="/static/sample-{s.slug}-p2.webp" alt="Page 2 of the {escape(kind.name.lower())} sample"></a>
<a href="{_pdf(s)}" target="_blank" rel="noopener"><img loading="lazy" width="935" height="1210"
 src="/static/sample-{s.slug}-p1.webp" alt="Page 1 of the {escape(kind.name.lower())} sample"></a></div></div></section>
<section class="rs alt"><div class="wrap"><div class="section-head"><p class="eyebrow">Who uses it</p>
<h2>Who orders this report, and why.</h2></div><ul class="rs-who">{who}</ul></div></section>
<section class="rs"><div class="wrap rs-lim"><div><p class="eyebrow">What it doesn't show</p><h2>{escape(s.limits_title)}</h2>
<p class="lede">A compilation of public records has limits. Here they are before you buy.</p></div>
<ul class="rs-limits">{limits}</ul></div></section>
<section class="rs alt"><div class="wrap"><div class="section-head"><p class="eyebrow">How it works</p>
<h2>Ordered in a minute, delivered in another.</h2></div>{_steps(s)}</div></section>
<section class="rs"><div class="wrap"><div class="section-head center"><p class="eyebrow">Questions</p>
<h2>Common questions.</h2></div><div class="faq">{faq}</div></div></section>
<section class="rs alt"><div class="wrap"><div class="section-head"><p class="eyebrow">More reports</p>
<h2>Other reports.</h2></div><div class="rt-grid rt-three">{others}</div>{credits()}
<div class="rs-guides"><h3>Related guides</h3><ul class="glist">{guides}</ul></div></div></section>
<section class="cta"><div class="wrap"><h2>{escape(kind.name)} report for your date.</h2>
<p>{PRICE} for one PDF, from public NOAA and NWS records. {a["pages"]} pages in the sample.</p>{_start(s.slug)}</div></section>"""


PAGES = {TYPES[s.slug].path: Page(path=TYPES[s.slug].path, title=s.title, h1=s.h1, eyebrow="Report",
                                  description=s.description, updated=UPDATED, body=_body(s), parent=SECTION)
         for s in SPECS}
CARDS = "".join(card(s) for s in SPECS)
MENU = [(TYPES[s.slug].name, TYPES[s.slug].path, s.menu) for s in SPECS]
