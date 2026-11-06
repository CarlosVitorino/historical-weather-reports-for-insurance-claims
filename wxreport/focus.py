"""A short report's own content: its chart and four facts on page one, then the section that answers its question.

Each kind holds only the records for that question (reporttypes.reads). The full record set is the default report's.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from reportlab.platypus import CondPageBreak

from . import charts, timeline, units
from .pdf import Badge, P, Spacer, esc, inch, mono, table
from .report import ReportContext
from .storm_pages import hail_name
from .timewin import fmt_local


def _t(ctx, t: datetime, with_date=False) -> str:
    return fmt_local(t, ctx.loc.tz, with_date)


def _hour(ctx, t: datetime) -> str:
    return t.astimezone(ZoneInfo(ctx.loc.tz)).strftime("%a %b %-d, %-I %p")


def _size(mag: str) -> float:
    try:
        return float(mag.split()[0])
    except (ValueError, IndexError):
        return 0.0


def _note(text: str):
    return P(f"<i>{esc(text)}</i>", "small")


def _station(ctx) -> str:
    st = ctx.primary.station if ctx.primary else None
    return f"{st.icao or st.id}, {st.proximity}" if st else "no station"


def _head(ctx, title: str, intro: str) -> list:
    out = [P(title, "h1"), P(intro, "body"), Spacer(1, 4)]
    if ctx.history_note:
        out += [_note(ctx.history_note), Spacer(1, 4)]
    return out


def figure(ctx, size=charts.WEB) -> tuple[charts.Figure | None, str]:
    """This report's chart and its caption, for the PDF and for the report's page on the site."""
    st, tz = _station(ctx), ctx.loc.tz
    slug = ctx.kind.slug
    if slug == "car-hail-damage":
        shown = _shown_hail(ctx)
        return charts.hail(shown, tz, hail_name, size), f"{len([r for r in shown if r['size']])} hail records near the location"
    if not ctx.hours:
        return None, ""
    if slug == "car-accident":
        return (charts.hour_columns(ctx.hours, ctx.event_utc, tz, "accident", size), f"Lowest visibility each hour at {st}")
    if slug == "slip-and-fall-on-ice":
        return (charts.temperature(_before(ctx), tz, ctx.event_utc, "Fall", wet=True, size=size),
                f"72 hours before the fall at {st}. The bars show what the station reported, not ice on the ground")
    if slug == "frozen-pipes":
        return charts.temperature(ctx.hours, tz, size=size), f"The week before the date at {st}"
    return None, ""


def chart(ctx) -> list:
    """Page one of a kind of report leads with this, where the standard report has its map."""
    fig, caption = figure(ctx, charts.PDF)
    return [fig.drawing(7.0 * inch), Spacer(1, 2), _note(caption), Spacer(1, 8)] if fig else []


MARK, SOFT = "#fde8c8", "#fdf5e8"    # the row asked about; a row worth a second look


def _wx(h: timeline.Hour) -> str:
    return ", ".join(h.weather) if h.reports else "no report"


def _precip(h: timeline.Hour) -> str:
    return units.fmt_precip_in(h.precip_mm, h.trace, missing="")


def _tint(tbl, rows, color: str = SOFT) -> None:
    from reportlab.lib import colors
    tbl.setStyle([("BACKGROUND", (0, i), (-1, i), colors.HexColor(color)) for i in rows])


def _bold(rows: list[list], cells, small: bool = True) -> None:
    """Make these (row, column) cells stand out: the figure a marked row is marked for."""
    for i, c in cells:
        rows[i][c] = P(f"<b>{esc(rows[i][c])}</b>", "tiny" if small else "cell")


def _extremes(rows, hrs, col: int, value, best) -> list:
    """Cells holding the highest or lowest reading of a column. Ties all count; no readings, no cells."""
    known = [value(h) for h in hrs if value(h) is not None]
    return [(i, col) for i, h in enumerate(hrs, 1) if known and value(h) == best(known)]


def _hour_rows(ctx, hrs: list[timeline.Hour], mark: datetime | None, label: str, cells=(), soft=None, soft_label=""):
    """label: the badge on the hour of `mark`. cells: columns to bold, as (column, value, min or max). soft: an hour
    worth a second look, with its own badge."""
    rows = [["Hour", "Temp °F", "Vis mi", "Gust mph", "Precip in", "Weather reported", ""]]
    for h in hrs:
        rows.append([_hour(ctx, h.t), units.fmt(h.temp_f, 0), units.fmt(h.vis_mi, 1), units.fmt(h.gust_mph, 0),
                     _precip(h), _wx(h), ""])
    for col, value, best in cells:
        _bold(rows, _extremes(rows, hrs, col, value, best))
    key = mark.replace(minute=0, second=0, microsecond=0) if mark else None
    light = next((i for i, h in enumerate(hrs, 1) if h is soft and h.t != key), None)
    main = next((i for i, h in enumerate(hrs, 1) if h.t == key), None)
    if light:
        rows[light][6] = Badge(soft_label)
    if main:
        rows[main][6] = Badge(label)
    t = table(rows, col_widths=[x * inch for x in [1.35, 0.55, 0.5, 0.6, 0.6, 2.65, 0.75]], small=True)
    if light:
        _tint(t, [light])
    if main:
        _tint(t, [main], MARK)
    return t


def _covering(ctx, at: datetime | None = None) -> list:
    """Warnings that covered the location: a polygon holding it, or its county or zone. Near misses are left out."""
    return [w for w in ctx.warnings if (not w.polygon_based or w.site_inside)
            and (at is None or w.issue <= at < w.expire)]


def _warnings(ctx, title: str, listed: list, empty: str) -> list:
    out = [CondPageBreak(1.2 * inch), Spacer(1, 8), P(title, "h2")]
    if ctx.warnings_note:
        return out + [P(esc(ctx.warnings_note), "body")]
    if not listed:
        return out + [P(empty, "body")]
    rows = [["Product", "From", "To", "How it covered the location"]]
    rows += [[w.name, _t(ctx, w.issue, True), _t(ctx, w.expire, True),
              "Inside the warning area" if w.polygon_based else "County or zone listed"] for w in listed]
    return out + [table(rows, col_widths=[x * inch for x in [2.5, 1.5, 1.5, 1.5]])]


def _warning_fact(ctx, at: datetime | None = None) -> tuple[str, str, str]:
    if ctx.warnings_note:
        return ("Warnings", "Unavailable", "The warning archive could not be reached")
    active = _covering(ctx, at)
    if not active:
        return ("Warnings", "None", "No watch or warning in effect then" if at else "None covered the location")
    names = sorted({w.name for w in active})
    more = f" and {len(names) - 2} more" if len(names) > 2 else ""
    return ("Warnings", str(len(active)), ", ".join(names[:2]) + more)


# -- car hail ------------------------------------------------------------------------------------
def _hail_records(ctx, miles: float = 15) -> list[dict]:
    ground = [{"t": r.time, "what": "Ground report", "size": _size(r.magnitude), "where": r.proximity,
               "dist": r.distance_mi, "detail": f"{r.city}, {r.source}"}
              for r in ctx.lsrs if r.type == "Hail" and r.distance_mi <= miles]
    radar = [{"t": h.time, "what": "Radar estimate", "size": h.max_size_in, "where": h.proximity,
              "dist": h.distance_mi, "detail": f"{h.radar}, estimate of hail aloft"}
             for h in ctx.hail if h.max_size_in and h.distance_mi <= miles]
    return ground + radar


def _key_hail(records: list[dict]) -> tuple[dict | None, dict | None]:
    """The largest hail and the closest record: within 5 miles when there are any, else of all of them."""
    near = [r for r in records if r["dist"] <= 5] or records
    if not near:
        return None, None
    return max(near, key=lambda r: (r["size"], -r["dist"])), min(near, key=lambda r: r["dist"])


def _shown_hail(ctx) -> list[dict]:
    """Every ground report, the largest radar estimates, and the records page one names: the chart's and timeline's."""
    records = _hail_records(ctx)
    ground = [r for r in records if r["what"] == "Ground report"]
    radar = sorted((r for r in records if r["what"] != "Ground report"), key=lambda r: (-r["size"], r["dist"]))[:15]
    shown = ground + radar
    shown += [r for r in _key_hail(records) if r and r not in shown]
    return sorted(shown, key=lambda r: r["t"])


def _car_hail_facts(ctx) -> list[tuple[str, str, str]]:
    near = [r for r in _hail_records(ctx) if r["dist"] <= 5]
    facts = []
    if near:
        big = max(near, key=lambda r: (r["size"], -r["dist"]))
        name = hail_name(big["size"])
        facts.append(("Largest hail within 5 mi", f"{big['size']:g} in",
                      f"{big['what']} {big['where']}, {_t(ctx, big['t'])}" + (f" · {name} size" if name else "")))
        c = min(near, key=lambda r: r["dist"])
        facts.append(("Closest hail record", f"{c['dist']:.1f} mi", f"{c['what']}, {c['size']:g} in, {_t(ctx, c['t'])}"))
        first, last = min(r["t"] for r in near), max(r["t"] for r in near)
        facts.append(("Hail records between", _t(ctx, first).rsplit(" ", 1)[0], f"and {_t(ctx, last)}, within 5 mi"))
    else:
        facts += [("Largest hail within 5 mi", "None", "No hail reported or detected"),
                  ("Closest hail record", "None", "None within 5 mi"), ("Hail records between", "None", "None within 5 mi")]
    return facts + [_warning_fact(ctx)]


def _car_hail(ctx) -> list:
    all_records, shown = _hail_records(ctx), _shown_hail(ctx)
    out = _head(ctx, "Hail timeline", "Every hail report on the ground within 15 miles of this location, with the "
                "largest radar estimates, in time order. Use it to match the hail to where the vehicle was.")
    if shown:
        rows = [["Local time", "Record", "Size in", "Common size", "From location", "Detail", ""]]
        rows += [[_t(ctx, r["t"]), r["what"], f"{r['size']:g}" if r["size"] else "—", hail_name(r["size"]) or "—",
                  r["where"], r["detail"], ""] for r in shown]
        big, close = _key_hail(all_records)
        marked = [shown.index(big) + 1, shown.index(close) + 1]
        _bold(rows, [(marked[0], 2), (marked[1], 4)], small=False)
        rows[marked[0]][6], rows[marked[1]][6] = Badge("Largest"), Badge("Closest")
        if big is close:
            rows[marked[0]][6] = Badge("Largest, closest")
        hail_table = table(rows, col_widths=[x * inch for x in [0.9, 0.95, 0.45, 0.9, 0.85, 2.15, 0.8]])
        _tint(hail_table, marked)
        out.append(hail_table)
        hidden = len(all_records) - len(shown)
        scope = "within 5 miles" if big["dist"] <= 5 else "listed"
        out += [Spacer(1, 3), _note(f"Largest and closest are of the records {scope}." +
                                    (f" {hidden} smaller radar estimates are not listed." if hidden > 0 else ""))]
    else:
        out.append(P("No hail was reported or detected within 15 miles on this date.", "body"))
    out += _warnings(ctx, "Watches and warnings for this location", _covering(ctx),
                     "None covered this location on this date.")
    out += [Spacer(1, 6), _note("These records are for this location only. If the vehicle was somewhere else when the "
                                "hail fell, that location needs its own report. Radar estimates hail aloft, not hail "
                                "on the ground. Nothing here identifies a vehicle or says what caused its damage.")]
    return out


# -- car accident --------------------------------------------------------------------------------
def _car_accident_facts(ctx) -> list[tuple[str, str, str]]:
    h = timeline.hour_at(ctx.hours, ctx.event_utc)
    if not h or not h.reports:
        reason = f"{_station(ctx)} has no report for that hour"
        facts = [("Weather that hour", "No report", reason), ("Visibility", "No report", reason),
                 ("Temperature", "No report", reason)]
    else:
        facts = [("Weather that hour", h.weather[0].capitalize() if h.weather else "None reported", _station(ctx)),
                 ("Visibility", units.fmt(h.vis_mi, 1, "mi"), f"Lowest that hour · {_station(ctx)}"),
                 ("Temperature", units.fmt(h.temp_f, 0, "°F"), f"Air at {_station(ctx)}, not the road")]
    return facts + [_warning_fact(ctx, ctx.event_utc)]


def _car_accident(ctx) -> list:
    out = _head(ctx, f"Hour by hour around {_t(ctx, ctx.event_utc)}",
                f"The three hours either side of the accident at {_station(ctx)}. The marked row is the hour of the "
                "accident. Visibility is the lowest reported in each hour.")
    if ctx.hours:
        out += [_hour_rows(ctx, ctx.hours, ctx.event_utc, "Accident",
                           [(2, lambda h: h.vis_mi, min), (3, lambda h: h.gust_mph, max)]),
                Spacer(1, 3), _note("In bold: the lowest visibility" + (" and the highest gust" if any(
                    h.gust_mph is not None for h in ctx.hours) else "") + " in these hours.")]
    active = _covering(ctx, ctx.event_utc)
    out += _warnings(ctx, "Watches and warnings in effect at that time", active,
                     "None for this location at that time.")
    out += [Spacer(1, 6), _note("Temperature and visibility are measured at the station, not on the road. This report "
                                "does not show the road surface, and it does not say who was at fault.")]
    return out + _bulletins(ctx, active)


def _bulletins(ctx, active: list) -> list:
    """The latest bulletin out at the moment, verbatim, for each warning in effect."""
    out = []
    for w in active:
        out_now = [b for b in w.bulletins if b.issued <= ctx.event_utc] or w.bulletins[:1]
        if out_now:
            b = out_now[-1]
            out += [Spacer(1, 8), P(f"Text of the {esc(w.name)}, as issued {esc(_t(ctx, b.issued, True))}", "h2"),
                    mono(b.text)]
    return out


# -- slip and fall --------------------------------------------------------------------------------
def _before(ctx) -> list[timeline.Hour]:
    return [h for h in ctx.hours if h.t <= ctx.event_utc]


def _ice_facts(ctx) -> list[tuple[str, str, str]]:
    hrs = _before(ctx)
    now = timeline.hour_at(hrs, ctx.event_utc)
    wet = timeline.last_precip(hrs)
    temp = units.fmt(now.temp_f, 0, "°F") if now and now.temp_f is not None else "No report"
    last = "None" if not wet else f"{wet.t.astimezone(ZoneInfo(ctx.loc.tz)):%b %-d, %-I %p}"
    return [("Temperature at that time", temp, f"Air at {_station(ctx)}"),
            ("Last precipitation", last, (", ".join(wet.precipitating) or "Measured precipitation") if wet
             else "None in the previous 72 hours"),
            ("Hours at or below 32°F", str(timeline.at_or_below(hrs, 32)), f"Of the {len(hrs)} hours up to the fall"),
            ("Times it crossed 32°F", str(timeline.crossings(hrs)), "Rising or falling, in those hours")]


def _daily_rows(ctx, hrs: list[timeline.Hour], thresholds: tuple[float, ...]):
    tz = ZoneInfo(ctx.loc.tz)
    days: dict = {}
    for h in hrs:
        days.setdefault(h.t.astimezone(tz).date(), []).append(h)
    rows = [["Local day", "Low °F", "High °F", *[f"Hours ≤ {x:.0f}°F" for x in thresholds], "Precip in", "Weather", ""]]
    for d, group in days.items():
        temps = [h.temp_f for h in group if h.temp_f is not None]
        wet = [h.precip_mm for h in group if h.precip_mm is not None]
        kinds = list(dict.fromkeys(w for h in group for w in h.precipitating))
        rows.append([f"{d:%a %b} {d.day}", units.fmt(min(temps) if temps else None, 0),
                     units.fmt(max(temps) if temps else None, 0),
                     *[str(timeline.at_or_below(group, x)) for x in thresholds],
                     units.fmt_precip_in(sum(wet) if wet else None, any(h.trace for h in group), missing="—"),
                     ", ".join(kinds[:4]), ""])
    widths = [1.0, 0.55, 0.55] + [0.75] * len(thresholds) + [0.6]
    lows = [min((h.temp_f for h in g if h.temp_f is not None), default=None) for g in days.values()]
    wet = [sum(h.precip_mm or 0 for h in g) for g in days.values()]
    coldest = [i for i, v in enumerate(lows, 1) if v is not None and v == min(x for x in lows if x is not None)]
    wettest = [i for i, v in enumerate(wet, 1) if v and v == max(wet)]
    _bold(rows, [(i, 1) for i in coldest] + [(i, 3 + len(thresholds)) for i in wettest])
    for i in coldest:
        rows[i][-1] = Badge("Coldest day")
    out = table(rows, col_widths=[x * inch for x in widths + [6.2 - sum(widths), 0.8]], small=True)
    _tint(out, coldest)
    return out


def _ice(ctx) -> list:
    hrs = _before(ctx)
    out = _head(ctx, "The 72 hours before the fall",
                f"Temperature, precipitation and reported weather at {_station(ctx)}, day by day and then hour by hour. "
                "The marked row is the hour of the fall.")
    if hrs:
        out += [_daily_rows(ctx, hrs, (32,)), Spacer(1, 3),
                _note("In bold: the lowest temperature and the most precipitation. The first and last days are "
                      "partial: they count only the hours inside the 72."), Spacer(1, 8),
                CondPageBreak(1.5 * inch), P("Hour by hour", "h2"),
                _hour_rows(ctx, hrs, ctx.event_utc, "Fall",
                           [(1, lambda h: h.temp_f, min), (4, lambda h: h.precip_mm or None, max)],
                           timeline.last_precip(hrs), "Last precip"),
                Spacer(1, 3), _note("In bold: the coldest hours and the most precipitation in an hour.")]
        depth = [h for h in hrs if h.snow_depth_in is not None]
        if depth:
            out += [Spacer(1, 4), _note(f"Snow depth last reported by the station: {depth[-1].snow_depth_in:.0f} in, "
                                        f"{_hour(ctx, depth[-1].t)}.")]
        missed = timeline.missing(hrs)
        if missed:
            out += [Spacer(1, 3), _note(f"{missed} of these hours have no station report.")]
    out += _warnings(ctx, "Watches and warnings during these hours", _covering(ctx),
                     "None covered this location during these hours.")
    out += _ice_reports(ctx)
    out += [Spacer(1, 6), _note("These readings are from the station named above. They do not show whether ice was on "
                                "any surface, when a surface was treated, or who was responsible for it. This is not "
                                "a certified record; a court may require one.")]
    return out


_ICY = ("freez", "ice", "sleet", "snow")


def _amount(r) -> str:
    """A report with no measurement arrives as 0, which would read as none."""
    return "—" if not r.magnitude or _size(r.magnitude) == 0 else r.magnitude


def _ice_reports(ctx, miles: float = 10) -> list:
    """Ice and snow reported nearby, up to the fall."""
    out = [CondPageBreak(1.2 * inch), Spacer(1, 8), P(f"Ice and snow reports within {miles:.0f} miles", "h2")]
    if ctx.lsrs_note:
        return out + [P(esc(ctx.lsrs_note), "body")]
    near = [r for r in ctx.lsrs if r.distance_mi <= miles and r.time <= ctx.event_utc
            and any(x in r.type.lower() for x in _ICY)]
    if not near:
        return out + [P("None in the Local Storm Reports for these hours.", "body")]
    rows = [["Local time", "Report", "Amount", "Place", "From location", "Source", ""]]
    rows += [[_hour(ctx, r.time), r.type, _amount(r), f"{r.city}, {r.county} Co.", r.proximity, r.source, ""]
             for r in near]
    close = min(range(len(near)), key=lambda i: near[i].distance_mi) + 1
    amounts = [_size(r.magnitude) if r.magnitude else 0 for r in near]
    big = [i for i, v in enumerate(amounts, 1) if v and v == max(amounts)]    # ties all count
    _bold(rows, [(close, 4)] + [(i, 2) for i in big])
    for i in big:
        rows[i][6] = Badge("Largest")
    rows[close][6] = Badge("Largest, closest" if close in big else "Closest")
    reports = table(rows, col_widths=[x * inch for x in [1.2, 0.85, 0.75, 1.55, 0.85, 1.0, 0.8]], small=True)
    _tint(reports, [close, *big])
    return out + [reports]


# -- frozen pipes ---------------------------------------------------------------------------------
def _frozen_facts(ctx) -> list[tuple[str, str, str]]:
    hrs = ctx.hours
    c = timeline.coldest(hrs)
    return [("Lowest temperature", units.fmt(c.temp_f, 0, "°F") if c else "No report",
             f"{_hour(ctx, c.t)} · {_station(ctx)}" if c else _station(ctx)),
            ("Hours at or below 32°F", str(timeline.at_or_below(hrs, 32)), f"Of {len(hrs)} hours"),
            ("Hours at or below 20°F", str(timeline.at_or_below(hrs, 20)), f"Of {len(hrs)} hours"),
            ("Longest stretch at or below 32°F", f"{timeline.longest_run(hrs, 32)} h", "Unbroken hours")]


def _frozen(ctx) -> list:
    out = _head(ctx, "The cold before the pipe burst",
                f"Air temperature at {_station(ctx)} for the seven days before the date, and that date.")
    if ctx.hours:
        out += [_daily_rows(ctx, ctx.hours, (32, 20)), Spacer(1, 3),
                _note("In bold: the lowest temperature and the most precipitation."), Spacer(1, 8)]
        below = [h for h in ctx.hours if h.temp_f is not None and h.temp_f <= 32]
        if below:
            out.append(P(f"First reading at or below 32°F: <b>{esc(_hour(ctx, below[0].t))}</b>. "
                         f"Last: <b>{esc(_hour(ctx, below[-1].t))}</b>.", "body"))
        else:
            out.append(P("No reading at or below 32°F in these eight days.", "body"))
        missed = timeline.missing(ctx.hours)
        if missed:
            out += [Spacer(1, 3), _note(f"{missed} of these hours have no station report.")]
    out += _warnings(ctx, "Watches and warnings during these days", _covering(ctx),
                     "None covered this location during these days.")
    out += [Spacer(1, 6), _note("This is outdoor air at the station. It does not show the temperature inside the "
                                "building, whether the heat was on, or what froze a pipe.")]
    return out


FACTS = {"car-hail-damage": _car_hail_facts, "car-accident": _car_accident_facts,
         "slip-and-fall-on-ice": _ice_facts, "frozen-pipes": _frozen_facts}
SECTIONS = {"car-hail-damage": _car_hail, "car-accident": _car_accident, "slip-and-fall-on-ice": _ice,
            "frozen-pipes": _frozen}


def key_facts(ctx: ReportContext) -> list[tuple[str, str, str]] | None:
    return FACTS[ctx.kind.slug](ctx) if ctx.kind.slug in FACTS else None


def section(ctx: ReportContext) -> list:
    return SECTIONS[ctx.kind.slug](ctx) if ctx.kind.slug in SECTIONS else []
