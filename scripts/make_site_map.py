"""Draw the landing page's hero map from the real sample report data (the trimmed Bloomington fixture).

    .venv/bin/python scripts/make_site_map.py   →  wxreport/static/site-map.svg

Everything plotted is a real record from that report: the address, the airport station that measured the
peak gust, the NWS tornado-warning polygons, the Storm Events tornado path, radar hail detections and
ground hail reports. Positions are true to scale (miles from the address).
"""
import sys
from math import cos, radians
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wxreport.report import gather  # noqa: E402

R_MI, SIZE = 9.0, 560
PX = (SIZE / 2 - 22) / R_MI
C = SIZE / 2
AMBER, RED, SKY, INK = "#f2a93b", "#ff7a66", "#8fc8ff", "#e6edf5"


def main():
    ctx = gather("401 N College Ave, Bloomington, IN", "2026-02-19",
                 root=ROOT / "tests/fixtures/snapshots", offline=True)
    lat0, lon0 = ctx.loc.lat, ctx.loc.lon
    kx = 69.172 * cos(radians(lat0))

    def xy(lat, lon):
        return C + (lon - lon0) * kx * PX, C - (lat - lat0) * 69.0 * PX

    def inside(lat, lon, r=R_MI):
        x, y = xy(lat, lon)
        return ((x - C) ** 2 + (y - C) ** 2) ** .5 <= r * PX

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" role="img" '
           f'aria-label="Map of weather records around one address on one day">',
           '<defs><clipPath id="disc"><circle cx="280" cy="280" r="{:.1f}"/></clipPath>'.format(R_MI * PX),
           f'<radialGradient id="bg"><stop offset="0" stop-color="#16304f"/><stop offset="1" stop-color="#0d1f35"/></radialGradient></defs>',
           f'<circle cx="{C}" cy="{C}" r="{R_MI * PX:.1f}" fill="url(#bg)" stroke="rgba(255,255,255,.14)"/>',
           '<g clip-path="url(#disc)">']
    # warning polygons
    for w in ctx.warnings:
        if not w.polygon_based:
            continue
        poly = w.bulletins[0].polygon
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (xy(a, b) for a, b in poly))
        out.append(f'<polygon points="{pts}" fill="rgba(242,169,59,.09)" stroke="{AMBER}" stroke-opacity=".7" '
                   f'stroke-width="1.4" stroke-dasharray="5 4"/>')
    # rings
    for r in (3, 6):
        out.append(f'<circle cx="{C}" cy="{C}" r="{r * PX:.1f}" fill="none" stroke="rgba(255,255,255,.13)"/>')
    for r in (3, 6, 9):
        out.append(f'<text x="{C + 4}" y="{C - r * PX + 13:.1f}" fill="rgba(230,237,245,.45)" font-size="10.5" '
                   f'font-family="Geist Mono,monospace">{r} mi</text>')
    # radar hail
    for h in ctx.hail:
        if h.max_size_in and inside(h.lat, h.lon):
            x, y = xy(h.lat, h.lon)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.2 + 2.2 * h.max_size_in:.1f}" fill="{SKY}" '
                       f'fill-opacity=".28" stroke="{SKY}" stroke-opacity=".8" stroke-width="1"/>')
    # ground hail reports
    for r in ctx.lsrs:
        if r.type == "Hail" and inside(r.lat, r.lon):
            x, y = xy(r.lat, r.lon)
            out.append(f'<rect x="{x - 3.6:.1f}" y="{y - 3.6:.1f}" width="7.2" height="7.2" fill="{SKY}" '
                       f'transform="rotate(45 {x:.1f} {y:.1f})"/>')
    # tornado path
    tor = next(e for e in ctx.storm_events.events if e.event_type == "Tornado")
    (x1, y1), (x2, y2) = xy(*tor.begin_latlon), xy(*tor.end_latlon)
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{RED}" stroke-width="7" '
               f'stroke-linecap="round" stroke-opacity=".9"/>')
    out.append('</g>')
    # station
    st = ctx.primary.station
    sx, sy = xy(st.lat, st.lon)
    out.append(f'<rect x="{sx - 6:.1f}" y="{sy - 6:.1f}" width="12" height="12" rx="2" fill="#fff"/>')
    # site pin
    out.append(f'<circle cx="{C}" cy="{C}" r="15" fill="{AMBER}" fill-opacity=".18"/>'
               f'<circle cx="{C}" cy="{C}" r="7" fill="{AMBER}" stroke="#0b1a2e" stroke-width="2.5"/>')
    # north arrow
    out.append(f'<g transform="translate({SIZE - 40},40)" fill="rgba(230,237,245,.6)" font-family="Geist,sans-serif" '
               f'font-size="11" text-anchor="middle"><path d="M0 -14 6 4 0 0 -6 4z"/><text y="18">N</text></g>')

    def label(x, y, lx, ly, title, sub, anchor="start"):
        tx = lx + (8 if anchor == "start" else -8)
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" stroke="rgba(255,255,255,.5)"/>'
                   f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="2" fill="#fff"/>'
                   f'<text x="{tx:.1f}" y="{ly - 3:.1f}" fill="#fff" font-family="Geist,sans-serif" font-size="13.5" '
                   f'font-weight="600" text-anchor="{anchor}">{title}</text>'
                   f'<text x="{tx:.1f}" y="{ly + 13:.1f}" fill="{INK}" fill-opacity=".72" font-family="Geist,sans-serif" '
                   f'font-size="12" text-anchor="{anchor}">{sub}</text>')

    label(C + 9, C + 4, C + 52, C + 58, "The address", "401 N College Ave")
    label(sx - 4, sy + 6, sx - 8, sy + 92, "70 mph gust measured", f"Airport station, {st.proximity}")
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    label(mx - 14, my - 2, 74, my - 78, "EF2 tornado path", f"{tor.proximity.split()[0]} mi from the address")
    near = min((h for h in ctx.hail if h.max_size_in), key=lambda h: h.distance_mi)
    hx, hy = xy(near.lat, near.lon)
    label(hx + 4, hy - 6, SIZE - 70, hy - 92, "Radar-detected hail", f"{near.max_size_in:.2f} in, {near.proximity}", "end")
    out.append('</svg>')
    path = ROOT / "wxreport/static/site-map.svg"
    path.write_text("\n".join(out))
    print(path)
    wind_chart(ctx)


def wind_chart(ctx):
    """Small light-theme chart of the day's measured wind at the report's station, peak annotated."""
    from wxreport import units
    from wxreport.timewin import fmt_local
    sd = ctx.primary
    W, H, L, B, T = 360, 132, 26, 22, 18
    pw, ph = W - L - 8, H - B - T
    t0, span = ctx.day.start_utc, (ctx.day.end_utc - ctx.day.start_utc).total_seconds()
    ymax = 80
    X = lambda t: L + pw * (t - t0).total_seconds() / span  # noqa: E731
    Y = lambda v: T + ph * (1 - v / ymax)  # noqa: E731
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Wind speed and gusts measured at {sd.station.icao} through the day">']
    for v in (0, 40, 80):
        o.append(f'<line x1="{L}" x2="{W - 8}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#e3e8ee"/>'
                 f'<text x="{L - 6}" y="{Y(v) + 3.5:.1f}" font-size="9.5" fill="#7b8899" text-anchor="end" '
                 f'font-family="Geist Mono,monospace">{v}</text>')
    for h, lab in ((0, "12 AM"), (6, "6 AM"), (12, "Noon"), (18, "6 PM"), (24, "12 AM")):
        x = L + pw * h / 24
        o.append(f'<text x="{x:.1f}" y="{H - 6}" font-size="9.5" fill="#7b8899" text-anchor="middle" '
                 f'font-family="Geist,sans-serif">{lab}</text>')
    pts = [(o_.t, units.mph(o_.values["wind_speed"])) for o_ in sd.obs if o_.values.get("wind_speed") is not None]
    run, prev = [], None
    for t, v in pts + [(None, None)]:
        if t is None or (prev and (t - prev).total_seconds() > 5400):
            if len(run) > 1:
                o.append(f'<polyline points="{" ".join(run)}" fill="none" stroke="#9db4cc" stroke-width="1.6" '
                         f'stroke-linejoin="round"/>')
            run = []
        if t is not None:
            run.append(f"{X(t):.1f},{Y(v):.1f}")
            prev = t
    for o_ in sd.obs:
        if o_.values.get("wind_gust") is not None:
            o.append(f'<circle cx="{X(o_.t):.1f}" cy="{Y(units.mph(o_.values["wind_gust"])):.1f}" r="3" fill="#1c3554"/>')
    t, ms, _ = sd.peak_gust()
    px, py = X(t), Y(units.mph(ms))
    o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="#f2a93b" stroke="#fff" stroke-width="2"/>'
             f'<text x="{px - 9:.1f}" y="{py + 4:.1f}" font-size="12" font-weight="600" fill="#14202e" text-anchor="end" '
             f'font-family="Geist,sans-serif">{units.mph(ms):.0f} mph · {fmt_local(t, ctx.loc.tz)}</text>')
    o.append("</svg>")
    path = ROOT / "wxreport/static/wind-chart.svg"
    path.write_text("".join(o))
    print(path)


if __name__ == "__main__":
    main()
