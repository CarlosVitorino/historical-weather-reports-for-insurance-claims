"""Build the landing page's data graphics from the real sample report (the trimmed Bloomington fixture).

    .venv/bin/python scripts/make_site_map.py
      → wxreport/static/site-map.json   records for the live hero map (static/hero.js)
      → wxreport/static/wind-chart.svg  the day's measured wind at the report's station

Everything shown is a real record from that report: the address, the station that measured the peak gust,
the NWS tornado-warning polygons, the Storm Events tornado path, radar hail detections and hail reports.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wxreport.report import gather  # noqa: E402


def main():
    ctx = gather("401 N College Ave, Bloomington, IN", "2026-02-19",
                 root=ROOT / "tests/fixtures/snapshots", offline=True)
    wind_chart(ctx)
    map_data(ctx)


def map_data(ctx):
    """The same records as JSON for the live hero map (Leaflet on real map tiles)."""
    import json
    from wxreport import units
    sd = ctx.primary
    tor = next(e for e in ctx.storm_events.events if e.event_type == "Tornado")
    r6 = lambda v: round(v, 5)  # noqa: E731
    pg = sd.peak_gust()
    data = {
        "site": [r6(ctx.loc.lat), r6(ctx.loc.lon)],
        "station": {"at": [r6(sd.station.lat), r6(sd.station.lon)], "name": sd.station.icao,
                    "gust_mph": round(units.mph(pg[1])), "proximity": sd.station.proximity},
        "warnings": [[[r6(a), r6(b)] for a, b in w.bulletins[0].polygon] for w in ctx.warnings if w.polygon_based],
        "tornado": {"path": [list(map(r6, tor.begin_latlon)), list(map(r6, tor.end_latlon))],
                    "scale": tor.tor_scale, "proximity": tor.proximity},
        "radar_hail": [[r6(h.lat), r6(h.lon), h.max_size_in] for h in ctx.hail if h.max_size_in and h.distance_mi <= 9],
        "hail_reports": [[r6(r.lat), r6(r.lon)] for r in ctx.lsrs if r.type == "Hail" and r.distance_mi <= 9],
    }
    path = ROOT / "wxreport/static/site-map.json"
    path.write_text(json.dumps(data, separators=(",", ":")))
    print(path)


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
