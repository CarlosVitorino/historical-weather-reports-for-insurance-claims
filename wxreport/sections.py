"""The report's pages. Every figure names its source record and its distance and bearing from the site."""
from datetime import datetime, timedelta

from reportlab.graphics.shapes import Drawing, Line, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.platypus import CondPageBreak, KeepTogether, PageBreak, Paragraph
from reportlab.lib.styles import ParagraphStyle

from . import pdf, units
from .pdf import P, STYLES, Spacer, esc, inch, table
from .report import ReportContext
from .sources import ghcnh, nws, stormevents, swdi
from .timewin import fmt_local

MONO = ParagraphStyle("mono", parent=STYLES["cell"], fontName="Courier", fontSize=7, leading=8.6)
W = 7.0 * inch  # usable width


def _t(ctx, t: datetime, with_date=False) -> str:
    return fmt_local(t, ctx.loc.tz, with_date)


def _day_label(ctx) -> str:
    d = ctx.day.day
    return f"{d:%B} {d.day}, {d.year}"


def _mono(text: str) -> Paragraph:
    return Paragraph(esc(text).replace("\n", "<br/>").replace("  ", "&nbsp; "), MONO)


def _note(text: str):
    return P(f"<i>{esc(text)}</i>", "small")


def _status_line(note: str | None):
    return [_note(note), Spacer(1, 4)] if note else []


# -- key findings ------------------------------------------------------------------------------
def _gust_text(ctx, sd: ghcnh.StationDay) -> str | None:
    pg = sd.peak_gust()
    if not pg:
        return None
    t, ms, origin = pg
    via = " (peak-wind remark)" if origin != "gust" else ""
    return (f"<b>{units.mph(ms):.0f} mph</b> ({units.kt(ms):.0f} kt) at {_t(ctx, t)}{via} — "
            f"{esc(sd.station.name.title())} {sd.station.icao or sd.station.id}, {sd.station.proximity} of the site")


def findings(ctx: ReportContext) -> list:
    rows = []
    sd = ctx.primary
    if sd:
        rows.append(["Peak wind gust, nearest reporting station",
                     P(_gust_text(ctx, sd) or "No gust reported by this station on this date.", "cell")])
        others = [s for s in ctx.stations if s.status == "ok" and s is not sd and s.peak_gust()]
        if others:
            best = max(others, key=lambda s: s.peak_gust()[1])
            if best.peak_gust()[1] > (sd.peak_gust() or (0, 0))[1]:
                rows.append(["Highest gust, other listed stations", P(_gust_text(ctx, best), "cell")])
        pr = sd.precipitation(ctx.day)
        if pr:
            total, counted, missing, trace = pr
            txt = f"<b>{units.fmt_precip_in(total, trace)} in</b> at {sd.station.icao or sd.station.id}"
            if missing:
                txt += f" — <b>incomplete</b>: {missing} of {counted + missing} hourly periods have no usable report"
            rows.append(["Liquid precipitation, nearest station", P(txt, "cell")])
        # Point out a materially wetter listed station (≥ 0.10 in more): rain can be very local.
        base = pr[0] if pr else 0.0
        wetter = [(s2, s2.precipitation(ctx.day)) for s2 in ctx.stations if s2.status == "ok" and s2 is not sd]
        wetter = [(s2, p2) for s2, p2 in wetter if p2 and p2[0] >= base + 2.54]
        if wetter:
            s2, p2 = max(wetter, key=lambda x: x[1][0])
            txt2 = (f"<b>{units.fmt_precip_in(p2[0], p2[3])} in</b> at {esc(s2.station.name.title())} "
                    f"({s2.station.id}), {s2.station.proximity}")
            if p2[2]:
                txt2 += f" — {p2[2]} hour(s) missing"
            rows.append(["Most precipitation, other listed stations" if pr else "Precipitation, listed stations",
                         P(txt2, "cell")])
        hi, lo = sd.max_of("temperature"), sd.min_of("temperature")
        if hi:
            rows.append(["Temperature range, nearest station",
                         f"{units.f(lo[1]):.0f}–{units.f(hi[1]):.0f} °F"])
    else:
        rows.append(["Station measurements", ctx.stations_note or "No station reported on this date."])

    inside = [w for w in ctx.warnings if w.site_inside]
    if inside:
        txt = "; ".join(f"{esc(w.name)} {w.vtec_id} ({_t(ctx, w.issue)}–{_t(ctx, w.expire)})" for w in inside)
        rows.append(["Warnings whose polygon contained the site", P(f"<b>{len(inside)}</b>: {txt}", "cell")])
    area = [w for w in ctx.warnings if not w.polygon_based]
    if area:
        names = sorted({w.name for w in area})
        rows.append(["Watches / advisories for the site's county or zone", ", ".join(names)])
    if not ctx.warnings and not ctx.warnings_note:
        rows.append(["NWS warnings", "None in effect for the site on this date."])

    se = ctx.storm_events
    tors = [e for e in (se.events if se else []) if e.event_type == "Tornado" and e.distance_mi is not None]
    if tors:
        e = min(tors, key=lambda e: e.distance_mi)
        rows.append(["Nearest tornado (Storm Events)",
                     P(f"<b>{e.tor_scale or 'unrated'}</b>, path passed <b>{e.proximity}</b> of the site at "
                       f"its closest; {e.tor_length_mi} mi long, {e.tor_width_yd} yd wide (event {e.event_id})",
                       "cell")])
    ground_hail = [(r.distance_mi, r) for r in ctx.lsrs if r.type == "Hail" and r.distance_mi <= 5]
    if ground_hail:
        biggest = max(ground_hail, key=lambda x: (_size(x[1].magnitude), -x[0]))[1]
        rows.append(["Largest hail reported within 5 mi (LSR)",
                     P(f"<b>{esc(biggest.magnitude)}</b> ({biggest.qualifier or 'qualifier not given'}), "
                       f"{biggest.proximity}, {_t(ctx, biggest.time)}", "cell")])
    near_radar = [h for h in ctx.hail if h.distance_mi <= 5 and h.max_size_in]
    if near_radar:
        h = max(near_radar, key=lambda h: (h.max_size_in, -h.distance_mi))
        rows.append(["Largest radar-estimated hail within 5 mi",
                     P(f"<b>{h.max_size_in:.2f} in</b>, {h.proximity}, {_t(ctx, h.time)} ({h.radar})", "cell")])
    site_tiles = [x for x in ctx.lightning if x.contains_site]
    if site_tiles or ctx.lightning:
        n = sum(x.count for x in site_tiles)
        rows.append(["Lightning, grid cell containing the site",
                     f"{n} NLDN strikes recorded (UTC day{'s' if len(site_tiles) > 1 else ''} "
                     f"{', '.join(_ymd(x.utc_day) for x in site_tiles) or 'covering the date'})"])
    if se and se.status != "ok":
        rows.append(["NCEI Storm Events", se.note])
    return [P("Key findings", "h1"),
            table(rows, col_widths=[2.2 * inch, 4.8 * inch], header=False),
            Spacer(1, 4),
            _note("Each finding names the record it comes from. Records near the site do not by themselves "
                  "establish conditions at the property. Detailed records and their limitations follow.")]


def _size(mag: str) -> float:
    try:
        return float(mag.split()[0])
    except (ValueError, IndexError):
        return 0.0


def _ymd(s: str) -> str:
    return f"{s[:4]}-{s[4:6]}-{s[6:]}"


# -- cover -------------------------------------------------------------------------------------
def cover(ctx: ReportContext) -> list:
    loc, day = ctx.loc, ctx.day
    place = loc.matched_address or loc.input_address
    gen = _t(ctx, datetime.fromisoformat(ctx.snap.frozen_at), True)
    zones = ", ".join(ctx.zones) or "not determined"
    return [P(pdf.PRODUCT, "title"),
            P(f"Report ID <b>{ctx.report_id}</b> · Data retrieved {esc(gen)}", "small"),
            Spacer(1, 10),
            P(esc(place), "big"),
            P(f"<b>{_day_label(ctx)}</b> · local weather date ({day.hours} hours) · {esc(loc.tz)}", "body"),
            Spacer(1, 6),
            table([["Coordinates", f"{loc.lat:.5f}, {loc.lon:.5f}"],
                   ["County · NWS zones · office",
                    f"{loc.county + ', ' + loc.state if loc.county else 'Not determined'} · {zones} · "
                    f"{ctx.wfo or 'not determined'}"],
                   ["Location method", "US Census Geocoder address match" if loc.method == "census"
                    else "Coordinates supplied by the requester; the address was not geocoded"],
                   ["Address as entered", loc.input_address],
                   ["Local day", f"{_t(ctx, day.start_utc, True)} to {_t(ctx, day.end_utc, True)} "
                                 f"({day.start_utc:%Y-%m-%d %H:%M}Z–{day.end_utc:%Y-%m-%d %H:%M}Z)"]],
                  col_widths=[1.9 * inch, 5.1 * inch], header=False, zebra=False),
            Spacer(1, 10)] + findings(ctx)


# -- stations ----------------------------------------------------------------------------------
def _station_rows(ctx):
    rows = [["Station", "Position from site", "Reports", "Peak gust", "Max sustained", "Precip (in)", "Temp °F"]]
    for sd in ctx.stations:
        st = sd.station
        label = P(f"<b>{esc(st.name.title())}</b><br/>{st.id}{' · ' + st.icao if st.icao else ''}"
                  f"<br/><font size=6.5 color='#5b6675'>{esc(sd.network) if sd.status == 'ok' else ''}</font>", "cell")
        if sd.status != "ok":
            rows.append([label, st.proximity, "unavailable", "—", "—", "—", "—"])
            continue
        pg, ws = sd.peak_gust(), sd.max_of("wind_speed")
        pr = sd.precipitation(ctx.day)
        hi, lo = sd.max_of("temperature"), sd.min_of("temperature")
        precip = "—"
        if pr:
            precip = units.fmt_precip_in(pr[0], pr[3]) + (f" ({pr[2]} missing hr)" if pr[2] else "")
        rows.append([label, st.proximity, str(len(sd.obs)),
                     f"{units.mph(pg[1]):.0f} mph · {_t(ctx, pg[0])}" if pg else
                     ("none reported" if sd.has_wind else "not measured"),
                     f"{units.mph(ws[1]):.0f} mph · {_t(ctx, ws[0])}" if ws else "not measured",
                     precip, f"{units.f(lo[1]):.0f}–{units.f(hi[1]):.0f}" if hi else "—"])
    return rows


def _wind(o: ghcnh.Obs) -> str:
    d, s = o.values.get("wind_direction"), o.values.get("wind_speed")
    if s is None:
        return "—"
    if s == 0:
        return "calm"
    dtxt = "VRB" if o.codes.get("wind_direction") == "V" or d is None else f"{d:03.0f}°"
    return f"{dtxt} {units.mph(s):.0f}"


def _obs_rows(ctx, sd: ghcnh.StationDay):
    zone = "" if ctx.day.hours != 24 else " (" + _t(ctx, ctx.day.start_utc).rsplit(" ", 1)[1] + ")"
    hm = (lambda t: _t(ctx, t).rsplit(" ", 1)[0]) if zone else (lambda t: _t(ctx, t))
    rows = [[f"Local time{zone}", "Type", "Temp °F", "Dew °F", "RH %", "Wind mph", "Gust mph", "Vis mi",
             "Precip in", "Weather", "QC"]]
    pg = sd.peak_gust()
    logged = sd.log_obs
    for o in logged:
        v = o.values
        precip = v.get("precipitation")
        trace = o.codes.get("precipitation") in ("T", "2")
        rows.append([hm(o.t), {"FM15": "METAR", "FM16": "SPECI"}.get(o.report_type, o.report_type or "hourly"),
                     units.fmt(units.f(v["temperature"])), units.fmt(units.f(v["dew_point_temperature"])),
                     units.fmt(v["relative_humidity"], 0), _wind(o),
                     units.fmt(units.mph(v["wind_gust"]), 0),
                     units.fmt(units.mi(v["visibility"]), 1),
                     units.fmt_precip_in(precip, trace, missing=""),
                     ", ".join(o.weather) or "", " ".join(o.flags)])
    t = table(rows, col_widths=[x * inch for x in [0.72, 0.5, 0.45, 0.45, 0.38, 0.68, 0.45, 0.42, 0.48, 1.97, 0.5]],
              small=True)
    if pg:
        # Highlight the report carrying the peak (or the first one at/after a PK WND time).
        i = next((i for i, o in enumerate(logged, start=1) if o.t >= pg[0]), None)
        if i:
            t.setStyle([("BACKGROUND", (0, i), (-1, i), colors.HexColor("#fde8c8"))])
    return t


def wind_chart(ctx, sd: ghcnh.StationDay) -> Drawing:
    """Wind speed and gust (mph) through the local day, with precipitation bars, at one station."""
    w, h, left, bottom = W, 1.9 * inch, 34, 22
    pw, ph = w - left - 34, h - bottom - 14
    d = Drawing(w, h)
    t0, span = ctx.day.start_utc, (ctx.day.end_utc - ctx.day.start_utc).total_seconds()
    speeds = [(o.t, units.mph(o.values["wind_speed"])) for o in sd.obs if o.values.get("wind_speed") is not None]
    gusts = [(o.t, units.mph(o.values["wind_gust"])) for o in sd.obs if o.values.get("wind_gust") is not None]
    pg = sd.peak_gust()
    ymax = max([v for _, v in speeds + gusts] + ([units.mph(pg[1])] if pg else []) + [20])
    ymax = (int(ymax / 10) + 1) * 10
    x = lambda t: left + pw * (t - t0).total_seconds() / span  # noqa: E731
    y = lambda v: bottom + ph * v / ymax  # noqa: E731
    grid = colors.HexColor("#d9dee5")
    for v in range(0, ymax + 1, 10 if ymax <= 60 else 20):
        d.add(Line(left, y(v), left + pw, y(v), strokeColor=grid, strokeWidth=0.4))
        d.add(String(left - 4, y(v) - 2.5, str(v), fontSize=6, textAnchor="end", fillColor=pdf.MUTED))
    hrs = int(span // 3600)
    for hh in range(0, hrs + 1, 3):
        t = t0 + timedelta(hours=hh)
        d.add(Line(x(t), bottom, x(t), bottom - 3, strokeColor=pdf.MUTED, strokeWidth=0.4))
        d.add(String(x(t), bottom - 11, _t(ctx, t).replace(":00", "").rsplit(" ", 1)[0], fontSize=6,
                     textAnchor="middle", fillColor=pdf.MUTED))
    # precipitation bars per routine-report period (right axis, inches)
    bars = [(o.t, units.inch(o.values["precipitation"])) for o in sd.routine_reports()
            if o.values.get("precipitation")]
    pmax = max([v for _, v in bars] + [0.1])
    for t, v in bars:
        bh = ph * 0.6 * v / pmax
        d.add(Rect(x(t) - 3, bottom, 6, bh, fillColor=colors.HexColor("#f2a541"), strokeColor=None))
    d.add(String(left + pw + 4, bottom + ph * 0.6 - 2, f"{pmax:.2f} in", fontSize=6, fillColor=colors.HexColor("#c77d12")))
    # Sustained wind: a line broken wherever reports are more than 90 minutes apart (gaps stay visible).
    run, prev = [], None
    for t, v in speeds + [(None, None)]:
        if t is None or (prev is not None and (t - prev).total_seconds() > 5400):
            if len(run) >= 4:
                d.add(PolyLine(run, strokeColor=colors.HexColor("#7aa6d6"), strokeWidth=0.9))
            elif len(run) == 2:
                d.add(Rect(run[0] - 1, run[1] - 1, 2, 2, fillColor=colors.HexColor("#7aa6d6"), strokeColor=None))
            run = []
        if t is not None:
            run += [x(t), y(v)]
            prev = t
    # Gusts are only reported when they occur: plotted as points with a stem, never joined.
    for t, v in gusts:
        d.add(Line(x(t), y(0), x(t), y(v), strokeColor=pdf.ACCENT, strokeWidth=0.3))
        d.add(Rect(x(t) - 1.6, y(v) - 1.6, 3.2, 3.2, fillColor=pdf.ACCENT, strokeColor=None))
    if pg:
        d.add(String(x(pg[0]) + 3, y(units.mph(pg[1])) - 2, f"{units.mph(pg[1]):.0f} mph", fontSize=6.5,
                     fillColor=pdf.ACCENT, fontName="Helvetica-Bold"))
    d.add(String(left, h - 8, "mph", fontSize=6, fillColor=pdf.MUTED))
    d.add(String(left + 30, h - 8, "■ gust   — sustained wind (gaps = no reports)   ▮ hourly precipitation", fontSize=6,
                 fillColor=pdf.MUTED))
    return d


def stations(ctx: ReportContext) -> list:
    out = [PageBreak(), P("Station-pinned measurements", "h1"),
           P(f"NOAA GHCNh hourly observations from the nearest stations that reported on {_day_label(ctx)}. "
             "Every value below was measured at the named station; nothing is blended, averaged across "
             "stations or interpolated to the site.", "body"), Spacer(1, 4)]
    out += _status_line(ctx.stations_note)
    if ctx.stations:
        out.append(table(_station_rows(ctx), col_widths=[x * inch for x in [1.75, 0.95, 0.55, 1.15, 1.15, 0.8, 0.65]]))
    sd = ctx.primary
    if not sd:
        return out
    st = sd.station
    pr = sd.precipitation(ctx.day)
    out += [Spacer(1, 8), P(f"Observation log — {esc(st.name.title())} ({st.icao or st.id}), {st.proximity} "
                            f"of the site", "h2"),
            P(f"Station {st.id} at {st.lat:.4f}, {st.lon:.4f}, elevation "
              f"{units.fmt(st.elev_m, 0, 'm')}; {esc(sd.network)}. " +
              (f"All {len(sd.obs)} reports in the local day are listed: routine hourly METARs and special reports "
               "(SPECI) issued when conditions changed." if sd.log_obs is sd.obs else
               f"{len(sd.obs)} sub-hourly records; top-of-hour records are listed, and the peaks above use all "
               "records."), "body"),
            Spacer(1, 4), wind_chart(ctx, sd), Spacer(1, 4), _obs_rows(ctx, sd), Spacer(1, 4)]
    notes = ["Wind is the reported 2-minute sustained speed; gust is the peak short-duration speed in the report. "
             "A 'PK WND' remark gives the highest instantaneous wind since the previous routine report and is "
             "included in the peak gust where it is higher. The highlighted row holds the peak gust.",
             "Precipitation in a report is the running total since the last routine METAR. A blank means the "
             "report carried no precipitation group. '<0.01' is a measured trace."]
    if pr and pr[2]:
        notes.append(f"{pr[2]} hourly precipitation period(s) had no routine report or the station reported "
                     "its precipitation sensor or amount as unavailable; the daily total excludes them and "
                     "should be treated as a minimum.")
    if "USCRN" in sd.network:
        notes.append("USCRN stations measure wind at 1.5 m above ground, not the standard 10 m used at airports, "
                     "so their wind speeds read lower and are not directly comparable.")
    if any(o.flags for o in sd.obs):
        notes.append("QC: GHCNh quality codes other than 'passed' are shown as element:code (see Sources and "
                     "limitations).")
    if any(o.metar.rstrip("=").endswith("$") for o in sd.obs):
        notes.append("Some reports end with '$', the ASOS maintenance indicator: the station flagged that a sensor "
                     "needed maintenance when it sent them.")
    out += [_note(n) for n in notes]
    return out


# -- warnings ----------------------------------------------------------------------------------
def warnings(ctx: ReportContext) -> list:
    out = [PageBreak(), P("NWS watches, warnings and advisories", "h1"),
           P(f"Every NWS VTEC event in effect for the site's location during {_day_label(ctx)}. For "
             "polygon-based warnings, each bulletin's polygon is tested against the site's coordinates.", "body"),
           Spacer(1, 4)]
    out += _status_line(ctx.warnings_note)
    if not ctx.warnings:
        if not ctx.warnings_note:
            out.append(P("No watch, warning or advisory was in effect for the site on this date.", "body"))
        return out
    rows = [["Event / NWS event ID", "In effect (local)", "Site relation", "Bulletins"]]
    for w in ctx.warnings:
        if w.polygon_based:
            rel = "<b>Inside warning polygon</b>" if w.site_inside else \
                f"Outside polygon — {w.min_distance:.1f} mi from its edge"
        else:
            rel = f"County/zone listed ({esc(w.ugc)})"
        rows.append([P(f"<b>{esc(w.name)}</b><br/>{w.vtec_id}", "cell"),
                     f"{_t(ctx, w.issue, True)} – {_t(ctx, w.expire)}", P(rel, "cell"), str(len(w.bulletins))])
    out.append(table(rows, col_widths=[x * inch for x in [2.1, 2.3, 1.9, 0.7]]))
    out.append(_note("Bulletin counts include updates (Severe Weather Statements) and are not counts of distinct "
                     "storms. Full bulletin text is reproduced in Appendix B."))
    return out


# -- storm reports -----------------------------------------------------------------------------
def lsrs(ctx: ReportContext) -> list:
    out = [CondPageBreak(2.5 * inch), Spacer(1, 6),
           P(f"NWS Local Storm Reports within {nws.LSR_RADIUS_MI:.0f} miles", "h1"),
           P("Preliminary reports from spotters, officials, the public and automated stations, as issued by NWS "
             "offices, with each report's position relative to the site.", "body"), Spacer(1, 4)]
    out += _status_line(ctx.lsrs_note)
    if not ctx.lsrs:
        if not ctx.lsrs_note:
            out.append(P(f"No Local Storm Report within {nws.LSR_RADIUS_MI:.0f} miles on this date.", "body"))
        return out
    rows = [["#", "Local time", "Report", "Magnitude", "Location", "From site", "Source"]]
    for i, r in enumerate(ctx.lsrs, 1):
        mag = r.magnitude + (f" ({r.qualifier})" if r.magnitude and r.qualifier else "")
        rows.append([f"L{i:02d}", _t(ctx, r.time), P(f"<b>{esc(r.type)}</b>", "cell"), mag or "—",
                     f"{r.city}, {r.county} Co., {r.state}", r.proximity, r.source])
    out.append(table(rows, col_widths=[x * inch for x in [0.35, 0.8, 1.3, 1.0, 1.75, 0.85, 0.95]]))
    remarks = [(i, r) for i, r in enumerate(ctx.lsrs, 1) if r.remark]
    if remarks:
        out += [Spacer(1, 4), P("Report remarks (as issued)", "h2")]
        out.append(table([["#", "Remark", "Product"]] +
                         [[f"L{i:02d}", r.remark, r.product_id] for i, r in remarks],
                         col_widths=[0.35 * inch, 4.9 * inch, 1.75 * inch]))
    return out


def storm_events(ctx: ReportContext) -> list:
    se = ctx.storm_events
    out = [CondPageBreak(2.5 * inch), Spacer(1, 6), P("NCEI Storm Events Database", "h1"),
           P(f"NOAA's reviewed record of significant weather, compiled by NWS offices after the event. Events "
             f"overlapping the local date within {stormevents.RADIUS_MI:.0f} miles of the site, or listed for "
             "the site's county or forecast zone.", "body"), Spacer(1, 4)]
    if se is None or se.status != "ok":
        out.append(P(esc(se.note if se else "Not queried."), "body"))
        return out
    out.append(_note(f"Edition {_ymd(se.edition)}; this edition covers events through "
                     f"{se.covered_through[:4]}-{se.covered_through[4:]}."))
    if not se.events:
        out.append(P("No Storm Events record matched the site and date.", "body"))
        return out
    rows = [["#", "Event", "Local time", "Magnitude", "From site", "Damage", "Source / ID"]]
    for i, e in enumerate(se.events, 1):
        mag = e.tor_scale or e.magnitude or "—"
        if e.event_type == "Tornado" and e.tor_length_mi:
            mag += f", {e.tor_length_mi} mi × {e.tor_width_yd} yd"
        rows.append([f"S{i:02d}", P(f"<b>{esc(e.event_type)}</b><br/>{esc(e.cz_name.title())}, {esc(e.state.title())}",
                                   "cell"),
                     f"{_t(ctx, e.begin)}" + (f" – {_t(ctx, e.end)}" if e.end != e.begin else ""),
                     mag, e.proximity, e.damage_property or "—", P(f"{esc(e.source)}<br/>{e.event_id}", "cell")])
    out.append(table(rows, col_widths=[x * inch for x in [0.35, 1.35, 1.25, 1.2, 1.0, 0.6, 1.25]]))
    mags = "Magnitude: hail in inches; wind in knots (MG measured, EG estimated); tornadoes by EF rating."
    out.append(_note(mags + " Tornado distance is to the straight line between the published start and end "
                     "points, an approximation of the damage path."))
    narr = [(i, e) for i, e in enumerate(se.events, 1) if e.narrative]
    if narr:
        out += [Spacer(1, 4), P("Event narratives (as published)", "h2")]
        out.append(table([["#", "Narrative"]] + [[f"S{i:02d}", e.narrative] for i, e in narr],
                         col_widths=[0.35 * inch, 6.65 * inch]))
    eps = {}
    for e in se.events:
        if e.episode_narrative:
            eps.setdefault(e.episode_id, e.episode_narrative)
    if eps:
        out += [Spacer(1, 4), P("Episode context (printed once per episode)", "h2")]
        out += [P(f"<b>Episode {k}.</b> {esc(v)}", "small") for k, v in sorted(eps.items())]
    return out


# -- hail & lightning --------------------------------------------------------------------------
def hail_lightning(ctx: ReportContext) -> list:
    out = [CondPageBreak(2.5 * inch), Spacer(1, 6), P("Hail and lightning", "h1"),
           P(f"NEXRAD radar hail detections within {swdi.HAIL_RADIUS_MI:.0f} miles", "h2"),
           P("Radar-estimated maximum hail size for each storm cell on each radar scan (NEXRAD Level-III hail "
             "algorithm, via NOAA SWDI). These are estimates of hail aloft, not ground measurements; several "
             "radars may detect the same storm.", "body"), Spacer(1, 3)]
    out += _status_line(ctx.hail_note)
    if ctx.hail:
        rows = [["Local time", "Radar · cell", "Max size (in)", "Prob. hail", "Prob. severe", "From site"]]
        for h in ctx.hail:
            rows.append([_t(ctx, h.time), f"{h.radar} · {h.cell}", units.fmt(h.max_size_in, 2),
                         units.fmt(h.prob, 0, "%"), units.fmt(h.severe_prob, 0, "%"), h.proximity])
        out.append(table(rows, col_widths=[x * inch for x in [1.0, 1.2, 1.1, 1.0, 1.0, 1.7]]))
    elif not ctx.hail_note:
        out.append(P("No radar hail detection within this radius on this date.", "body"))

    out += [Spacer(1, 6), P(f"Lightning strike counts within {swdi.LIGHTNING_RADIUS_MI:.0f} miles", "h2"),
            P("Counts of NLDN lightning strikes per 0.1° grid cell (about 6–7 miles across) per UTC day, as published "
              "by NOAA NCEI. Point-level strike locations and times are licensed data and are not included. A UTC "
              "day runs from 7 PM to 7 PM Eastern Standard Time (adjust for other zones), so a count can include "
              "strikes outside the local date.", "body"), Spacer(1, 3)]
    out += _status_line(ctx.lightning_note)
    if ctx.lightning:
        days = sorted({x.utc_day for x in ctx.lightning})
        cells = {}
        for x in ctx.lightning:
            cells.setdefault((x.lat, x.lon), [x, {}])[1][x.utc_day] = x.count
        rows = [["Cell centre", "From site"] + [f"Strikes {_ymd(d)} UTC" for d in days]]
        for (clat, clon), (x, counts) in sorted(cells.items(), key=lambda kv: kv[1][0].distance_mi):
            rows.append([f"{clat:.1f}, {clon:.1f}", P(f"<b>{x.proximity}</b>" if x.contains_site else x.proximity,
                                                       "cell")] + [str(counts.get(d, 0)) for d in days])
        dw = 4.0 / len(days)
        out.append(table(rows, col_widths=[1.3 * inch, 1.7 * inch] + [dw * inch] * len(days)))
        out.append(_note("A count of 0 means the cell is not in the published file for that day; NCEI lists only "
                         "cells with at least one strike."))
    elif not ctx.lightning_note:
        out.append(P("No lightning recorded within this radius on the UTC day(s) covering this date.", "body"))
    sd = ctx.primary
    if sd:
        ltg = [o for o in sd.obs if "LTG" in o.metar.split("RMK")[-1] or "TS" in "".join(o.wx_raw)]
        if ltg:
            out.append(_note(f"{sd.station.icao or sd.station.id} also reported thunder or lightning in "
                             f"{len(ltg)} report(s), first at {_t(ctx, ltg[0].t)} (see the observation log)."))
    return out


# -- sources -----------------------------------------------------------------------------------
STATUS = {"ok": "retrieved", "error": "unavailable", "absent": "not published"}


def sources(ctx: ReportContext) -> list:
    rows = [["Source record", "Retrieved (UTC)", "Status", "SHA-256 (first 16)"]]
    for name in sorted(ctx.snap.sources):
        s = ctx.snap.sources[name]
        rows.append([name, s["retrieved_at"].replace("+00:00", "Z"), STATUS.get(s["status"], s["status"]),
                     (s.get("sha256") or "")[:16]])
    gen = _t(ctx, datetime.fromisoformat(ctx.snap.frozen_at), True)
    out = [PageBreak(), P("Sources and limitations", "h1"),
           P("Data sources", "h2"),
           P("<b>Station measurements:</b> NOAA NCEI Global Historical Climatology Network – hourly (GHCNh), per-station "
             "per-year files. Units converted from metric for display. Quality codes: '2', '3', '6', '7' mark suspect "
             "or erroneous values in the legacy source; lowercase letters mark GHCNh checks the value failed; "
             "unflagged values passed or were not checked.", "body"),
           P("<b>Warnings and bulletins:</b> NWS VTEC events and the verbatim text of NWS bulletins, retrieved from the "
             "Iowa Environmental Mesonet archive of NWS products (Iowa State University). Zones from api.weather.gov.",
             "body"),
           P("<b>Local Storm Reports:</b> NWS Local Storm Reports via the Iowa Environmental Mesonet. Preliminary; "
             "duplicates and corrections are reproduced as issued.", "body"),
           P("<b>Storm Events:</b> NOAA NCEI Storm Events Database bulk CSV (edition noted in that section).", "body"),
           P("<b>Hail and lightning:</b> NOAA NCEI Severe Weather Data Inventory (NEXRAD Level-III hail) and NCEI "
             "daily NLDN lightning tile counts.", "body"),
           P("<b>Location:</b> US Census Bureau Geocoder; timezone from coordinates (IANA tz database).", "body"),
           P("Distances and bearings", "h2"),
           P("Distances are great-circle miles from the site's coordinates; bearings are the direction from the site "
             "to the record (e.g. '4.6 mi WSW' means the record lies west-southwest of the site). A record's own "
             "position may be approximate: storm reports are often given to the nearest town or road.", "body"),
           P("What this report establishes", "h2"),
           P("This report compiles public US government weather records for the selected location and date. Records "
             "near the site do not by themselves establish conditions at the exact property. Missing values are not "
             "zero, and 'not published yet' is different from 'no record'. It does not determine property damage, "
             "causation, insurance coverage or legal admissibility, and it is not a certified government record or "
             "expert opinion.", "body"),
           P("Retrieval and report identity", "h2"),
           P(f"Data retrieved: {esc(gen)}. Report ID: {ctx.report_id}. Every source response used is stored "
             "unmodified; the hashes below identify those exact bytes, and the report ID is derived from them and "
             "their retrieval times, so this report can be regenerated byte-for-byte and verified.", "body"),
           Spacer(1, 4),
           table(rows, col_widths=[x * inch for x in [2.6, 1.6, 0.9, 1.9]])]
    return out


# -- appendices --------------------------------------------------------------------------------
def appendices(ctx: ReportContext) -> list:
    out = []
    sd = ctx.primary
    if sd:
        out += [PageBreak(), P(f"Appendix A — Raw station reports, {sd.station.icao or sd.station.id}", "h1"),
                P("Each report exactly as archived in GHCNh (UTC times in the METAR/SPECI text).", "body"),
                Spacer(1, 4)]
        out.append(table([["Local time", "Report text"]] +
                         [[_t(ctx, o.t), _mono(o.metar)] for o in sd.obs if o.metar],
                         col_widths=[0.85 * inch, 6.15 * inch]))
    if ctx.warnings:
        out += [PageBreak(), P("Appendix B — NWS bulletin text", "h1"),
                P("Bulletins reproduced verbatim from the NWS text product archive, ordered by event and issue time.",
                  "body")]
        for w in ctx.warnings:
            for j, b in enumerate(w.bulletins, 1):
                head = (f"<b>{esc(w.name)} · {w.vtec_id} · bulletin {j}</b> ({b.kind.lower()}, "
                        f"{_t(ctx, b.issued, True)})")
                if b.polygon:
                    head += " — site " + ("inside polygon" if b.inside else f"{b.distance_mi:.1f} mi outside polygon")
                out.append(KeepTogether([Spacer(1, 6), P(head, "cell"), Spacer(1, 2)]))
                out.append(_mono(b.text))
            if not w.bulletins:
                out += [Spacer(1, 6), P(f"<b>{esc(w.name)} · {w.vtec_id}</b> — bulletin text unavailable.", "cell")]
    return out


def render_report(ctx: ReportContext) -> bytes:
    flow = (cover(ctx) + stations(ctx) + warnings(ctx) + lsrs(ctx) + storm_events(ctx) + hail_lightning(ctx)
            + sources(ctx) + appendices(ctx))
    return pdf.render(flow, ctx.report_id, title=f"{pdf.PRODUCT} {ctx.report_id}")
