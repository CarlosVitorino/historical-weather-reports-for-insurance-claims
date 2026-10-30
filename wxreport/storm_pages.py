"""Storm Reports pages: the section index, state hubs and city pages ("Plano, TX hail storm history"), a strict
tree (index → state → city). Built from wxreport.storms; wording follows content.py (never official or certified).

Titles lead with city names and "hail storm": "{county} hail" reads as "jail" to Google (docs/storm-reports-plan.md).
"""
import json
import re
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from html import escape
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from . import BRAND
from .geo import compass
from .storms import CITY_MIN_DAYS, HAIL_MIN_IN, HISTORY_FROM, WIND_MIN_MPH, City

PRICE = "$9.99"
SECTION = "/storm-reports"
NCEI = '<a href="https://www.ncei.noaa.gov/stormevents/" rel="noopener" target="_blank">NCEI Storm Events Database</a>'
IEM_LSR = ('<a href="https://mesonet.agron.iastate.edu/lsr/" rel="noopener" target="_blank">NWS Local Storm Reports'
           '</a> (archived by the Iowa Environmental Mesonet)')
SOURCES_NOTE = (f'<p class="fine sr-src">Sources: {NCEI} (reviewed) and {IEM_LSR} (preliminary). {BRAND} is '
                f'independent and not affiliated with NOAA or the National Weather Service. Storm reports show what was '
                f'reported at a place and time; they do not establish conditions at any one property.</p>')

# NWS hail size references, inches.
HAIL_NAMES = [(4.5, "softball"), (4.0, "grapefruit"), (3.0, "teacup"), (2.75, "baseball"), (2.5, "tennis ball"),
              (2.0, "hen egg"), (1.75, "golf ball"), (1.5, "ping pong ball"), (1.25, "half dollar"), (1.0, "quarter"),
              (0.88, "nickel"), (0.75, "penny")]
_PLACE = re.compile(r"^(\d*\.?\d+)\s+([NSEW]{1,3})\s+(.+)$")


# -- words -----------------------------------------------------------------------------------------
def hail_name(inches: float | None) -> str:
    if inches is None:
        return ""
    return next((n for size, n in HAIL_NAMES if inches >= size - 1e-6), "")


def long_date(d: date) -> str:
    return f"{d:%B} {d.day}, {d.year}"


def short_date(d: date) -> str:
    return f"{d:%b} {d.day}, {d.year}"


def plural(n: int, word: str, many: str = "") -> str:
    return f"{n} {word if n == 1 else many or word + 's'}"


def join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def place(r: dict) -> str:
    """'3.12 NNE Cottondale' (miles and direction, as NWS and NCEI publish them) -> '3.1 mi NNE of Cottondale'."""
    p = (r.get("place") or "").strip()
    m = _PLACE.match(p)
    if m:
        miles = float(m.group(1))
        return f"{miles:.1f} mi {m.group(2)} of {m.group(3)}" if miles >= 0.05 else m.group(3)
    return p or (f"{r['county']} County" if r.get("county") else "Location not named")


def from_city(r: dict, city: City) -> str:
    """Where a report is relative to the city centre: '3.1 mi NE of central Plano'."""
    d = r["distance_mi"]
    return f"central {city.name}" if d < 0.5 else f"{d:.1f} mi {compass(r['bearing'])} of central {city.name}"


def what(r: dict) -> str:
    """One report in words: '1.75 in hail (golf ball)', '75 mph gust (estimated)', 'Tornado (EF1)'."""
    if r["kind"] == "hail":
        if not r["magnitude"]:
            return "Hail"
        n = hail_name(r["magnitude"])
        return f"{r['magnitude']:.2f} in hail" + (f" ({n})" if n else "")
    if r["kind"] == "wind":
        if r["magnitude"] is None:
            return "Wind damage"
        how = f" ({r['detail']})" if r["detail"] in ("measured", "estimated") else ""
        return f"{r['magnitude']:.0f} mph gust{how}"
    rating = r["detail"] or ""
    return "Tornado" + (" (unrated)" if rating in ("", "EFU", "EF-U") else f" ({rating})")


def summary(s: dict) -> str:
    """A storm day in a few words: '1.75 in hail (golf ball) · 1 tornado · 70 mph wind'."""
    bits = []
    if s.get("max_hail"):
        n = hail_name(s["max_hail"])
        bits.append(f"{s['max_hail']:.2f} in hail" + (f" ({n})" if n else ""))
    if s.get("n_tornado"):
        bits.append(plural(s["n_tornado"], "tornado", "tornadoes"))
    if (s.get("max_wind") or 0) >= WIND_MIN_MPH:
        bits.append(f"{s['max_wind']:.0f} mph wind")
    elif s.get("max_wind") or s.get("n_damage"):
        bits.append("wind damage")   # NOAA rates damage-only wind with a lower, estimated speed
    return " · ".join(bits) or plural(s["n"], "report")


def inches(x: float) -> str:
    """'1.00 inch', '2.75 inches (baseball size)'."""
    n = hail_name(x)
    return f"{x:.2f} {'inch' if x == 1 else 'inches'}" + (f" ({n} size)" if n else "")


def _local(r: dict, tz: ZoneInfo) -> datetime:
    return datetime.fromisoformat(r["time_utc"].replace("Z", "+00:00")).astimezone(tz)


# -- shared blocks ---------------------------------------------------------------------------------
def badge(reviewed: bool) -> str:
    return ('<span class="sr-badge rev">Reviewed</span>' if reviewed
            else '<span class="sr-badge pre">Preliminary</span>')


def crumbs(trail: list[tuple[str, str | None]]) -> str:
    parts = [f'<a href="{p}">{escape(n)}</a>' if p else f'<span aria-current="page">{escape(n)}</span>'
             for n, p in trail]
    return f'<nav class="crumbs" aria-label="Breadcrumb">{" / ".join(parts)}</nav>'


def status_note(synced: str | None, tz: ZoneInfo) -> str:
    """Preliminary reports, in one line; the explanation and the last check open on demand."""
    when = ""
    if synced:
        t = datetime.fromisoformat(synced).astimezone(tz)
        when = f" Last checked {long_date(t.date())}, {t:%-I:%M %p %Z}."
    return (f'<details class="sr-status pre"><summary>{badge(False)}<span>May still change</span></summary>'
            f'<p>These are the reports the National Weather Service received during and after the storm. NOAA reviews '
            f'them for its Storm Events Database 2–4 months later and this page updates then; sizes, times and places '
            f'can still change.{escape(when)}</p></details>')


def tiles(items: list[tuple[str, str, str]]) -> str:
    cells = "".join(f"<div><dt>{escape(k)}</dt><dd><b>{escape(v)}</b><span>{escape(sub)}</span></dd></div>"
                    for k, v, sub in items)
    return f'<dl class="sr-tiles">{cells}</dl>'


def storm_map(reports: list[dict], tz: ZoneInfo, label: str, center: City | None = None) -> str:
    points = [[r["lat"], r["lon"], r["kind"], f"{_local(r, tz):%-I:%M %p} · {what(r)} · {place(r)}"]
              for r in reports if r["lat"] is not None]
    paths = [[[r["lat"], r["lon"]], [r["end_lat"], r["end_lon"]]] for r in reports
             if r["kind"] == "tornado" and r["lat"] is not None and r["end_lat"] is not None]
    data: dict = {"points": points, "paths": paths}
    ring = ""
    if center:
        data |= {"center": [center.lat, center.lon, center.name], "ring_mi": center.radius_mi}
        ring = f'<span><i class="lg lg-ring"></i>{center.radius_mi:.0f} miles from central {escape(center.name)}</span>'
    attr = escape(json.dumps(data, separators=(",", ":")), quote=True)
    kinds = {r["kind"] for r in reports}
    legend = "".join(item for kind, item in (
        ("hail", '<span><i class="lg lg-report"></i>Hail</span>'),
        ("wind", '<span><i class="lg lg-wind"></i>Wind</span>'),
        ("tornado", '<span><i class="lg lg-path"></i>Tornado</span>')) if kind in kinds)
    return (f'<figure class="sr-map"><div id="storm-map" data-storm="{attr}" role="img" aria-label="{escape(label)}">'
            f'</div><figcaption class="sr-mleg">{legend}{ring}</figcaption></figure>')


def severity(r: dict) -> tuple:
    """Tornadoes first, then the largest hail, then the strongest wind (damage-only wind counts as 58 mph)."""
    rank = {"tornado": 2, "hail": 1, "wind": 0}[r["kind"]]
    return rank, r["magnitude"] if r["magnitude"] is not None else (WIND_MIN_MPH if r["kind"] == "wind" else 0)


def report_list(reports: list[dict], tz: ZoneInfo, city: City | None = None, top: int | None = None) -> str:
    """Every report, in time order. With `top`, a long list shows its `top` most severe reports and folds the rest."""
    if top and len(reports) > top + 2:
        keep = set(map(id, sorted(reports, key=severity, reverse=True)[:top]))
        first = [r for r in reports if id(r) in keep]
        rest = [r for r in reports if id(r) not in keep]
        return (report_list(first, tz, city) +
                f'<details class="sr-more"><summary>{len(rest)} more reports</summary>'
                f'{report_list(rest, tz, city)}</details>')
    rows = ""
    for r in reports:
        where = from_city(r, city) if city else place(r)
        meta = ([place(r)] if city else []) + [f"{r['county']} County" if r["county"] else "", r["reporter"]]
        remark = " ".join(paragraphs(r["remark"]))
        remark = f'<p class="sr-remark">{escape(remark)}</p>' if remark else ""
        rows += (f'<li class="k-{r["kind"]}"><time class="sr-t" datetime="{r["time_utc"]}">'
                 f'{_local(r, tz):%-I:%M %p}</time><div><b>{escape(what(r))}</b>'
                 f'<span class="sr-pl">{escape(where)}</span>'
                 f'<span class="sr-ml">{escape(" · ".join(m for m in meta if m))}</span>{remark}</div></li>')
    return f'<ul class="sr-list">{rows}</ul>'


_GARBLED = re.compile("(?:\u00ef\u00bf\u00bd|\ufffd)+")   # UTF-8 replacement characters, as stored or mis-decoded


def paragraphs(text: str) -> list[str]:
    """NWS/NCEI narrative text: '||' separates paragraphs; drop characters NCEI could not encode."""
    return [" ".join(p.split()) for p in _GARBLED.sub("", text or "").split("||") if p.strip()]


def narratives(reports: list[dict]) -> str:
    """The NWS description of the storm: the first paragraph, the rest folded."""
    seen: list[str] = []
    for r in reports:
        if r["episode_narrative"] and r["episode_narrative"] not in seen:
            seen.append(r["episode_narrative"])
    if not seen:
        return ""
    quotes = ""
    for text in seen[:3]:
        first, *rest = paragraphs(text) or [""]
        more = ""
        if rest:
            more = ("<details class=\"sr-more\"><summary>Read the full description</summary>" +
                    "".join(f"<p>{escape(x)}</p>" for x in rest) + "</details>")
        quotes += f'<blockquote class="sr-quote"><p>{escape(first)}</p>{more}</blockquote>'
    return f'<section class="sr-block"><h2>What the National Weather Service wrote</h2>{quotes}</section>'


def cta(day: date | None = None, where: str = "") -> str:
    if day:
        head = "Was your property in this storm?"
        text = (f"Get the records for one address on {long_date(day)}: wind measured at nearby stations, NWS warnings, "
                f"storm reports, hail and lightning, each with its distance from the property. PDF, {PRICE}.")
        href = f"/order?loss_date={day.isoformat()}"
    else:
        head = f"Check one address{' in ' + where if where else ''} on one date"
        text = ("Wind measured at nearby stations, NWS warnings, storm reports, hail and lightning for one address and "
                f"date of loss, each with its distance from the property. PDF, {PRICE}.")
        href = "/order"
    return (f'<aside class="cta-box"><div><b>{escape(head)}</b><span>{text}</span></div>'
            f'<a class="btn btn-amber" href="{href}">Check an address</a></aside>')


def major_tag(day: dict) -> str:
    return '<span class="sr-tag">Major storm</span>' if day.get("major") else ""


# -- storm table: the index and the state pages -----------------------------------------------------
PERIODS = {"7d": "Last 7 days", "30d": "Last 30 days", "year": "This year", "all": f"Since {HISTORY_FROM}"}
KINDS = {"all": "All storms", "hail": f"Hail {HAIL_MIN_IN:.0f} in+", "tornado": "Tornado", "wind": "Damaging wind",
         "major": "Major storm"}
SORTS = {"date": "Date", "hail": "Largest hail", "wind": "Strongest wind"}
FILTER_ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M7 12h10M10 18h4" '
               'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
PAGE_SIZE = 50


@dataclass(frozen=True)
class TableQuery:
    """What the visitor asked the table for. Defaults are the indexed view; anything else is noindex."""
    q: str = ""
    period: str = "30d"
    kind: str = "all"
    sort: str = "date"
    page: int = 1

    @classmethod
    def parse(cls, params) -> "TableQuery":
        def pick(key, allowed, default):
            v = (params.get(key) or "").strip().lower()
            return v if v in allowed else default
        try:
            page = max(1, min(int(params.get("page") or 1), 10_000))
        except ValueError:
            page = 1
        return cls(" ".join((params.get("q") or "").split())[:60], pick("period", PERIODS, "30d"),
                   pick("kind", KINDS, "all"), pick("sort", SORTS, "date"), page)

    @property
    def filtered(self) -> bool:
        return self != TableQuery(page=self.page) or self.page > 1

    def url(self, path: str, **change) -> str:
        """This query with some fields changed, as a link; defaults are left out so links stay short."""
        q = replace(self, **change)
        params = {k: v for k, v in (("q", q.q), ("period", q.period), ("kind", q.kind), ("sort", q.sort),
                                    ("page", q.page)) if v != getattr(TableQuery(), k)}
        return path + ("?" + urlencode(params) if params else "")


def table_rows(cities: list[tuple[City, list[dict]]], tq: TableQuery, today: date) -> list[tuple[City, dict]]:
    start = {"7d": today - timedelta(days=6), "30d": today - timedelta(days=29), "year": date(today.year, 1, 1),
             "all": date(HISTORY_FROM, 1, 1)}[tq.period]
    match = {"all": lambda d: True, "hail": lambda d: (d["max_hail"] or 0) >= HAIL_MIN_IN,
             "tornado": lambda d: d["n_tornado"] > 0, "major": lambda d: d["major"],
             "wind": lambda d: (d["max_wind"] or 0) >= WIND_MIN_MPH or d["n_damage"] > 0}[tq.kind]
    q = tq.q.lower().replace(",", " ").split()
    rows = [(c, d) for c, days in cities if all(w in c.label.lower().replace(",", " ").split()
                                                  or w in c.state_name.lower().split() for w in q)
            for d in days if d["day"] >= start and match(d)]
    key = {"date": lambda r: (r[1]["day"], r[0].population),
           "hail": lambda r: (r[1]["max_hail"] or 0, r[1]["day"]),
           "wind": lambda r: (r[1]["max_wind"] or 0, r[1]["day"])}[tq.sort]
    return sorted(rows, key=key, reverse=True)


def _select(name: str, options: dict, value: str, label: str, cls: str = "") -> str:
    opts = "".join(f'<option value="{k}"{" selected" if k == value else ""}>{escape(v)}</option>'
                   for k, v in options.items())
    return f'<label class="sr-f {cls}"><span>{label}</span><select name="{name}">{opts}</select></label>'


def _cell_hail(d: dict) -> str:
    if not d["max_hail"]:
        return '<span class="sr-none">—</span>'
    n = hail_name(d["max_hail"])
    return f'<b>{d["max_hail"]:.2f} in</b>' + (f'<small>{escape(n)}</small>' if n else "")


def _cell_wind(d: dict) -> str:
    """A speed, or nothing: damage-only wind reports have no reading (NOAA's damage-based estimates under 58 mph
    are not readings either)."""
    if (d["max_wind"] or 0) >= WIND_MIN_MPH:
        return f'<b>{d["max_wind"]:.0f} mph</b>'
    return '<span class="sr-none">—</span>'


def day_href(city: City, day: date, latest: date) -> str:
    """A storm day on its city page: the plain page for the latest storm, ?day= for the others."""
    return city.path if day == latest else f"{city.path}?day={day.isoformat()}"


def day_row(city: City, d: dict, href: str) -> str:
    """One city on one storm day as a table row. One link per row, stretched over the whole row (.sr-rl)."""
    tornado = f'<b>{d["n_tornado"]}</b>' if d["n_tornado"] else '<span class="sr-none">—</span>'
    return (f'<tr><td class="sr-cd" data-label="Date">{d["day"]:%a}, {short_date(d["day"])}</td>'
            f'<td class="sr-cc" data-label="City"><a class="sr-rl" href="{href}">{escape(city.name)}</a>'
            f'<span class="sr-st">{city.state}</span>{major_tag(d)}</td>'
            f'<td class="sr-cn" data-label="Largest hail">{_cell_hail(d)}</td>'
            f'<td class="sr-cn" data-label="Strongest wind">{_cell_wind(d)}</td>'
            f'<td class="sr-cn" data-label="Tornadoes">{tornado}</td></tr>')


def storm_table(path: str, tq: TableQuery, rows: list[tuple[City, dict]], cities: list[City],
                latest: dict[str, date], states: list[tuple[str, str, int]], state: str = "") -> str:
    """Filters (plain GET form) + sortable table + pages. Every control is a link or a form field: no JS needed."""
    state_opts = {"": "All states"} | {s.lower(): f"{name} ({n})" for s, name, n in states}
    names = "".join(f'<option value="{escape(c.label, quote=True)}">' for c in sorted(cities, key=lambda c: c.label))
    active = sum([bool(state), tq.period != "30d", tq.kind != "all"])
    count = f'<span class="sr-fcount">{active}</span>' if active else ""
    form = (f'<form class="sr-filters" method="get" action="{SECTION}" data-autosubmit>'
            f'<label class="sr-f sr-fq"><span>City</span><input type="search" name="q" list="sr-cities" '
            f'value="{escape(tq.q, quote=True)}" placeholder="Search a city" autocomplete="off">'
            f'<datalist id="sr-cities">{names}</datalist></label>'
            f'<button class="sr-fbtn" type="button" aria-expanded="false" aria-controls="sr-fsheet" hidden>'
            f'{FILTER_ICON}<span class="sr-vh">Filters</span>{count}</button>'
            f'<div class="sr-fsheet" id="sr-fsheet" role="group" aria-label="Filters">'
            f'<div class="sr-fsh"><b>Filters</b><button class="sr-fclose" type="button" aria-label="Close">×</button></div>'
            f'{_select("state", state_opts, state, "State")}{_select("period", PERIODS, tq.period, "Period")}'
            f'{_select("kind", KINDS, tq.kind, "Storm")}{_select("sort", SORTS, tq.sort, "Sort by", "sr-fsort")}'
            f'<div class="sr-factions"><a class="btn btn-ghost" href="{SECTION}">Reset</a>'
            f'<button class="btn btn-navy" type="submit">Apply</button></div></div></form>'
            f'<script defer src="/static/storm-filters.js"></script>')

    pages = max(1, -(-len(rows) // PAGE_SIZE))
    page = min(tq.page, pages)
    shown = rows[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]

    def th(key: str, cls: str = "") -> str:
        on = tq.sort == key
        attrs = ' aria-sort="descending"' if on else ""
        return (f'<th class="{cls}"{attrs}><a href="{escape(tq.url(path, sort=key, page=1), quote=True)}"'
                f'{" class=on" if on else ""}>{SORTS[key]}{" ↓" if on else ""}</a></th>')

    body = "".join(day_row(c, d, day_href(c, d["day"], latest[c.geoid])) for c, d in shown)
    if shown:
        table = (f'<div class="sr-tw"><table class="sr-table"><thead><tr>{th("date")}<th>City</th>{th("hail", "sr-cn")}'
                 f'{th("wind", "sr-cn")}<th class="sr-cn">Tornadoes</th></tr></thead><tbody>{body}</tbody></table></div>')
    else:
        widen = "" if tq.period == "all" else (f' <a href="{escape(tq.url(path, period="all", page=1), quote=True)}">'
                                               f'Show {PERIODS["all"].lower()}</a>.')
        table = f'<p class="sr-empty">No storm days match these filters.{widen}</p>'
    nav = ""
    if pages > 1:
        prev = (f'<a href="{escape(tq.url(path, page=page - 1), quote=True)}">← Newer</a>' if page > 1 else "<span></span>")
        nxt = (f'<a href="{escape(tq.url(path, page=page + 1), quote=True)}">Older →</a>' if page < pages else "<span></span>")
        nav = f'<nav class="sr-pager" aria-label="Pages">{prev}<span>Page {page} of {pages}</span>{nxt}</nav>'
    reset = (f' · <a href="{path}">Clear filters</a>' if tq.filtered else "")
    count = f'<p class="sr-count" role="status">{plural(len(rows), "storm day")} · {PERIODS[tq.period]}{reset}</p>'
    return form + count + table + nav


def storm_index(path: str, heading: str, lede: str, trail: list, table: str, where: str = "") -> str:
    return f"""<div class="sr-wrap sr-wide">{crumbs(trail)}
<header class="sr-intro"><p class="eyebrow">Storm Reports</p><h1>{escape(heading)}</h1>
<p class="lede">{lede}</p></header>
<section class="sr-block sr-tbl">{table}</section>
{cta(where=where)}{SOURCES_NOTE}</div>"""


# -- city page -------------------------------------------------------------------------------------
def also_hit(others: list[City]) -> str:
    if not others:
        return ""
    links = ", ".join(f'<a href="{c.path}">{escape(c.label)}</a>' for c in others)
    return f'<p class="sr-also">Also hit that day: {links}</p>'


def chip_bit(d: dict) -> str:
    """A storm day in two or three words, for the day strip: '2.00″ hail', 'Tornado', '66 mph', 'Wind damage'."""
    if d["max_hail"] and d["max_hail"] >= HAIL_MIN_IN:
        return f"{d['max_hail']:.2f}″ hail"
    if d["n_tornado"]:
        return "Tornado"
    if (d["max_wind"] or 0) >= WIND_MIN_MPH:
        return f"{d['max_wind']:.0f} mph"
    return "Wind damage"


def day_strip(city: City, days: list[dict], selected: dict) -> str:
    """Phones: the storm days as a row of chips above the card, and a button for the full list (a bottom sheet)."""
    latest = days[0]
    chips = "".join(
        f'<a class="sr-chip{" major" if d["major"] else ""}" href="{day_href(city, d["day"], latest["day"])}#storm" '
        f'data-day{" aria-current=true" if d is selected else ""}><b>{d["day"]:%b} {d["day"].day}'
        f'{"" if d["day"].year == latest["day"].year else d["day"].strftime(" ’%y")}</b>'
        f'<span>{escape(chip_bit(d))}</span></a>' for d in days)
    return (f'<nav class="sr-strip" aria-label="Storm days near {escape(city.name)}"><div class="sr-chips-x">{chips}'
            f'</div><a class="sr-all" href="#storm-days" data-sheet>All {len(days)} days</a></nav>')


def storm_panel(city: City, days: list[dict], selected: dict, also: list[City], synced: str | None) -> str:
    """One storm day near the city, in full, as its own card. The page swaps this card when another day is picked."""
    tz = ZoneInfo(city.tz)
    i = next(n for n, d in enumerate(days) if d is selected)
    d, latest = selected, days[0]
    href = lambda x: day_href(city, x["day"], latest["day"])  # noqa: E731
    pills = (('<span class="sr-pill">Latest</span>' if d is latest else
              f'<a class="sr-tolatest" href="{city.path}#storm" data-day>Latest storm →</a>') + major_tag(d))
    status = "" if d["reviewed"] else status_note(synced, tz)
    figures = tiles([
        ("Largest hail", f"{d['max_hail']:.2f} in" if d["max_hail"] else "—",
         hail_name(d["max_hail"]) or ("" if d["max_hail"] else "none reported")),
        ("Strongest wind", f"{d['max_wind']:.0f} mph" if (d["max_wind"] or 0) >= WIND_MIN_MPH else "—",
         "gust" if (d["max_wind"] or 0) >= WIND_MIN_MPH else "no reading"),
        ("Tornadoes", str(d["n_tornado"]), "reported" if d["n_tornado"] else "none reported"),
        ("Reports", str(d["n"]), f"within {city.radius_mi:.0f} mi")])
    newer = (f'<a href="{href(days[i - 1])}#storm" data-day>← Newer storm</a>' if i > 0 else "<span></span>")
    older = (f'<a href="{href(days[i + 1])}#storm" data-day>Older storm →</a>' if i + 1 < len(days)
             else "<span></span>")
    return f"""<article class="sr-panel" id="storm" tabindex="-1" aria-labelledby="storm-title">
<header class="sr-ph"><p class="sr-pk">Storm near {escape(city.name)}</p>
<h2 id="storm-title">{d["day"]:%A}, {long_date(d["day"])}</h2><div class="sr-pills">{pills}</div></header>
{day_strip(city, days, d)}<div class="sr-pb">{figures}{status}
{storm_map(d["reports"], tz, f"Map of the storm reports near {city.name} on {long_date(d['day'])}", city)}
<h3 class="sr-pt">{plural(d["n"], "report")}</h3>{report_list(d["reports"], tz, city, top=6)}{also_hit(also)}
{narratives(d["reports"]) if d["reviewed"] else ""}</div>
<footer class="sr-pf"><div class="sr-porder"><b>Was your property in this storm?</b><span>Records for one address on
{long_date(d["day"])}: station wind, NWS warnings, storm reports, hail and lightning. PDF, {PRICE}.</span></div>
<a class="btn btn-amber" href="/order?loss_date={d["day"].isoformat()}">Check an address</a>
<nav class="sr-pager" aria-label="Other storms near {escape(city.name)}">{newer}{older}</nav></footer></article>"""


def storm_days_list(city: City, days: list[dict], selected: dict) -> str:
    """Every storm day near the city, by year; picking one shows it in the storm card."""
    latest = days[0]
    groups = ""
    for year in sorted({d["day"].year for d in days}, reverse=True):
        items = ""
        for d in (d for d in days if d["day"].year == year):
            cur = ' aria-current="true"' if d is selected else ""
            items += (f'<li><a href="{day_href(city, d["day"], latest["day"])}#storm" data-day{cur}>'
                      f'<span class="sr-ld">{d["day"]:%a}, {d["day"]:%b} {d["day"].day}</span>'
                      f'<span class="sr-ls">{escape(summary(d))}</span>{major_tag(d)}</a></li>')
        n = sum(1 for d in days if d["day"].year == year)
        groups += f'<h3>{year} <span>{plural(n, "storm day")}</span></h3><ul>{items}</ul>'
    return (f'<nav class="sr-dlist" id="storm-days" aria-label="Storm days near {escape(city.name)}">'
            f'<h2>Storm days <span>{len(days)}</span><button class="sr-fclose" type="button" data-sheet-close '
            f'aria-label="Close" hidden>×</button></h2><div class="sr-dscroll">{groups}</div></nav>')


def city_page(city: City, days: list[dict], selected: dict, also: dict[date, list[City]], nearby: list[City],
              synced: str | None) -> str:
    """The city's record (fixed), then a workspace: the list of storm days and the picked day as a card."""
    big = max((d for d in days if d["max_hail"]), key=lambda d: (d["max_hail"], d["day"]), default=None)
    hail_days = sum(1 for d in days if (d["max_hail"] or 0) >= HAIL_MIN_IN)
    tornado_days = sum(1 for d in days if d["n_tornado"])
    first_year = days[-1]["day"].year
    lede = (f"Every day with large hail, damaging wind or a tornado within {city.radius_mi:.0f} miles of central "
            f"{escape(city.name)} since {first_year}, with each storm's reports on a map.")
    if big:
        lede += f" The largest hail was {inches(big['max_hail'])} on {long_date(big['day'])}."
    record = tiles([
        ("Storm days", str(len(days)), "all types"),
        ("Hail days", str(hail_days), f"{HAIL_MIN_IN:.0f} in or larger"),
        ("Largest hail", f"{big['max_hail']:.2f} in" if big else "—", short_date(big["day"]) if big else "none"),
        ("Tornado days", str(tornado_days), "any rating")])
    near_block = ""
    if nearby:
        chips = "".join(f'<li><a href="{c.path}">{escape(c.label)}</a></li>' for c in nearby)
        near_block = f'<section class="sr-block"><h2>Nearby cities</h2><ul class="sr-chips">{chips}</ul></section>'
    return f"""<div class="sr-wrap sr-wide">{crumbs([("Home", "/"), ("Storm Reports", SECTION),
                                        (city.state_name, f"{SECTION}/{city.state.lower()}"), (city.name, None)])}
<header class="sr-intro"><p class="eyebrow">Storm Reports · {escape(city.state_name)}</p>
<h1>{escape(city.label)} hail storm history</h1><p class="lede">{lede}</p></header>
<section class="sr-record" aria-label="{escape(city.name)} since {first_year}"><p class="sr-rk">{escape(city.name)} since
{first_year}<span> · within {city.radius_mi:.0f} mi of the center</span></p>{record}</section>
<div class="sr-work">{storm_panel(city, days, selected, also.get(selected["day"], []), synced)}
{storm_days_list(city, days, selected)}</div>
{near_block}{SOURCES_NOTE}</div>
<script defer src="/static/storm-city.js"></script>"""


# -- titles and descriptions -----------------------------------------------------------------------
def city_title(city: City, days: list[dict]) -> str:
    return f"{city.label} hail storm history: {plural(len(days), 'storm day')} since {days[-1]['day'].year}"


def city_description(city: City, days: list[dict]) -> str:
    latest, big = days[0], max((d["max_hail"] or 0 for d in days), default=0)
    out = f"Hail, wind and tornado reports near {city.label} on {plural(len(days), 'day')} since {days[-1]['day'].year}"
    out += f", largest hail {big:.2f} in." if big else "."
    return out + f" Latest storm {short_date(latest['day'])}: {summary(latest)}."


def city_indexable(n_days: int) -> bool:
    return n_days >= CITY_MIN_DAYS
