"""The chart at the head of each kind of report. One drawing, two outputs: the PDF (reportlab) and the site (SVG), so the
page for a report shows exactly what the buyer gets. Colours are flat, with no transparency, and match the site.

Each function returns None when there is nothing worth drawing: the tables in focus.py still say so in words.
"""
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from html import escape
from zoneinfo import ZoneInfo

from reportlab.graphics.shapes import Circle, Drawing, Group, Line, PolyLine, Polygon, Rect, String
from reportlab.lib import colors

from . import timeline

WEB = (480, 250)
PDF = (640, 240)    # drawn 7 inches wide: its text comes out at about 7.5pt, like the report's tables, not zoomed in
INK, MUTED, FAINT, RULE = "#14202e", "#5d6b7c", "#8a96a5", "#e3e8ee"
AMBER, AMBER_INK, AMBER_50 = "#f2a93b", "#8a5a0b", "#fdf5e8"
SKY, SKY_FILL, NAVY, STEEL, ICY = "#3d7fc2", "#d8e5f2", "#1c3554", "#9db4cc", "#6d5bd0"
_SVG_FONT = {"sans": "Geist,sans-serif", "mono": "Geist Mono,monospace"}


def _rl(fill):
    return colors.HexColor(fill) if fill else None


@dataclass
class Figure:
    label: str
    size: tuple = WEB
    ops: list = field(default_factory=list)

    def line(self, x1, y1, x2, y2, color=RULE, width=1.0, dash=None):
        self.ops.append(("line", x1, y1, x2, y2, color, width, dash))

    def rect(self, x, y, w, h, fill, stroke=None, r=0):
        self.ops.append(("rect", x, y, w, h, fill, stroke, r))

    def circle(self, x, y, r, fill, stroke=None, width=1.0):
        self.ops.append(("circle", x, y, r, fill, stroke, width))

    def polygon(self, pts, fill):
        self.ops.append(("polygon", pts, fill))

    def polyline(self, pts, color, width):
        self.ops.append(("polyline", pts, color, width))

    def diamond(self, x, y, r, fill):
        self.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill)

    def text(self, x, y, s, size=10.5, fill=MUTED, anchor="middle", bold=False, mono=False):
        self.ops.append(("text", x, y, str(s), size, fill, anchor, bold, mono))

    def svg(self) -> str:
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.size[0]} {self.size[1]}" role="img" '
             f'aria-label="{escape(self.label, quote=True)}">']
        pts = lambda p: " ".join(f"{x:.1f},{y:.1f}" for x, y in p)  # noqa: E731
        for op in self.ops:
            kind, *a = op
            if kind == "line":
                x1, y1, x2, y2, color, width, dash = a
                d = f' stroke-dasharray="{dash[0]} {dash[1]}"' if dash else ""
                o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                         f'stroke-width="{width}"{d}/>')
            elif kind == "rect":
                x, y, w, h, fill, stroke, r = a
                s = f' stroke="{stroke}"' if stroke else ""
                o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}"{s}/>')
            elif kind == "circle":
                x, y, r, fill, stroke, width = a
                s = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{s}/>')
            elif kind == "polygon":
                o.append(f'<polygon points="{pts(a[0])}" fill="{a[1]}" stroke="{a[1]}" stroke-width=".4"/>')
            elif kind == "polyline":
                o.append(f'<polyline points="{pts(a[0])}" fill="none" stroke="{a[1]}" stroke-width="{a[2]}" '
                         'stroke-linejoin="round"/>')
            else:
                x, y, s, size, fill, anchor, bold, mono = a
                o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                         f'font-weight="{600 if bold else 400}" font-family="{_SVG_FONT["mono" if mono else "sans"]}">'
                         f'{escape(s)}</text>')
        return "".join(o) + "</svg>"

    def drawing(self, width: float) -> Drawing:
        W, H = self.size
        k = width / W
        g = Group(transform=(k, 0, 0, k, 0, 0))
        y_ = lambda y: H - y  # noqa: E731
        flat = lambda p: [v for x, y in p for v in (x, y_(y))]  # noqa: E731
        for op in self.ops:
            kind, *a = op
            if kind == "line":
                x1, y1, x2, y2, color, width_, dash = a
                g.add(Line(x1, y_(y1), x2, y_(y2), strokeColor=_rl(color), strokeWidth=width_, strokeDashArray=dash))
            elif kind == "rect":
                x, y, w, h, fill, stroke, r = a
                g.add(Rect(x, y_(y + h), w, h, rx=r, ry=r, fillColor=_rl(fill), strokeColor=_rl(stroke),
                           strokeWidth=1 if stroke else 0))
            elif kind == "circle":
                x, y, r, fill, stroke, width_ = a
                g.add(Circle(x, y_(y), r, fillColor=_rl(fill), strokeColor=_rl(stroke), strokeWidth=width_ if stroke else 0))
            elif kind == "polygon":
                g.add(Polygon(flat(a[0]), fillColor=_rl(a[1]), strokeColor=_rl(a[1]), strokeWidth=.4))   # no seams
            elif kind == "polyline":
                g.add(PolyLine(flat(a[0]), strokeColor=_rl(a[1]), strokeWidth=a[2], strokeLineJoin=1))
            else:
                x, y, s, size, fill, anchor, bold, mono = a
                font = "Courier-Bold" if mono and bold else "Courier" if mono else "Helvetica-Bold" if bold else "Helvetica"
                g.add(String(x, y_(y), s, fontName=font, fontSize=size, fillColor=_rl(fill), textAnchor=anchor))
        d = Drawing(width, H * k)
        d.add(g)
        return d


def _legend(f: Figure, x: float, items: list[tuple[str, str]], y: float = 12) -> None:
    """One row above the plot, so every mark on a chart is named on it. Items are (swatch, label)."""
    for swatch, label in items:
        if swatch == "ground":
            f.diamond(x + 4, y, 3.8, SKY)
        elif swatch == "radar":
            f.circle(x + 4, y, 3.4, SKY_FILL, SKY)
        elif swatch == "largest":
            f.circle(x + 4, y, 4, AMBER)
        elif swatch == "line":
            f.line(x - 4, y, x + 8, y, NAVY, 1.8)
        elif swatch == "freezing":
            f.rect(x - 2, y - 4, 10, 8, SKY_FILL, SKY)
        elif swatch == "dash":
            f.text(x + 3, y + 3.5, "–", 10.5, FAINT)
        else:           # a filled bar in this colour
            f.rect(x - 2, y - 4, 10, 8, swatch, r=1)
        f.text(x + 12, y + 3.5, label, 9.5, MUTED, "start")
        x += 26 + len(label) * 4.9


def _clock(t: datetime) -> str:
    return t.strftime("%-I %p") if t.minute == 0 else t.strftime("%-I:%M %p")


def hail(records: list[dict], tz: str, name, size=WEB) -> Figure | None:
    """Size against local time, both axes fitted to the records. name(size) gives the everyday size."""
    shown = [r for r in records if r["size"]]
    if not shown:
        return None
    W, H = size
    zone = ZoneInfo(tz)
    L, R, T, B = 62, 14, 34, 26
    pw, ph = W - L - R, H - T - B
    first, last = min(r["t"] for r in shown), max(r["t"] for r in shown)
    pad = max(600, (last - first).total_seconds() * .08)
    t0, t1 = first - timedelta(seconds=pad), last + timedelta(seconds=pad)
    lo, hi = min(r["size"] for r in shown), max(r["size"] for r in shown)
    extra = max(0, 1.5 - (hi - lo)) / 2
    ymin, ymax = max(0, lo - .3 - extra), hi + .35 + extra
    X = lambda t: L + pw * (t - t0).total_seconds() / (t1 - t0).total_seconds()  # noqa: E731
    Y = lambda v: T + ph * (1 - (v - ymin) / (ymax - ymin))  # noqa: E731
    f = Figure(f"Hail size against time near the location, {len(shown)} records", size)
    f.line(L, T + ph, W - R, T + ph, "#c6d0db")
    minutes = (t1 - t0).total_seconds() / 60
    step = next(m for m in (15, 30, 60, 120, 240, 1440) if minutes / m <= 6)
    tick = t0.astimezone(zone).replace(minute=0, second=0, microsecond=0)
    while tick <= t1:
        if tick >= t0:
            f.line(X(tick), T, X(tick), T + ph, RULE, 1, (2, 3))
            f.text(X(tick), H - 8, _clock(tick), 9.5, FAINT)
        tick += timedelta(minutes=step)
    for v in (1, 1.75, 2.5, 4):
        if ymin < v < ymax:
            f.line(L, Y(v), W - R, Y(v))
            f.text(L - 8, Y(v) - 1, f"{v:g} in", 9.5, INK, "end")
            f.text(L - 8, Y(v) + 9, name(v), 8.5, FAINT, "end")
    for r in shown:
        if r["what"] != "Ground report":
            f.circle(X(r["t"]), Y(r["size"]), 3.4, SKY_FILL, SKY)
    for r in shown:
        if r["what"] == "Ground report":
            f.diamond(X(r["t"]), Y(r["size"]), 3.8, SKY)
    within = [r for r in shown if r["dist"] <= 5]
    big = max(within or shown, key=lambda r: (r["size"], -r["dist"]))
    _legend(f, L, [("ground", "Ground report"), ("radar", "Radar estimate"),
                   ("largest", "Largest within 5 mi" if within else "Largest record")])
    x, y = X(big["t"]), Y(big["size"])
    f.circle(x, y, 5, AMBER, "#ffffff", 1.5)
    left = x < L + pw / 2
    f.text(x + (8 if left else -8), y - 8, f'{big["size"]:g} in, {big["dist"]:.1f} mi away', 10.5, INK,
           "start" if left else "end", True)
    return f


def hour_columns(hrs: list[timeline.Hour], now: datetime, tz: str, what: str, size=WEB) -> Figure | None:
    """One column an hour: lowest visibility as a bar, then the hour, temperature and weather. `now` is highlighted."""
    if not any(h.reports for h in hrs):
        return None
    W, H = size
    zone = ZoneInfo(tz)
    L, T, BASE = 8, 50, 178
    col = (W - 2 * L) / len(hrs)
    top = max(3.0, *[h.vis_mi or 0 for h in hrs])
    key = now.replace(minute=0, second=0, microsecond=0)
    f = Figure(f"Lowest visibility, temperature and weather for each hour around the {what}", size)
    _legend(f, L + 4, [(STEEL, "Lowest visibility that hour"), (AMBER, f"Hour of the {what}"), ("dash", "No visibility reported")])
    for i, h in enumerate(hrs):
        x, on = L + i * col, h.t == key
        cx = x + col / 2
        if on:
            f.rect(x + 2, 24, col - 4, H - 28, AMBER_50, AMBER, 9)
            f.text(cx, 38, what.upper(), 8.5, AMBER_INK, bold=True, mono=True)
        if h.vis_mi is not None:
            bar = max(3, (BASE - T - 16) * h.vis_mi / top)
            f.rect(cx - 15, BASE - bar, 30, bar, AMBER if on else STEEL, r=3)
            f.text(cx, BASE - bar - 6, f"{h.vis_mi:.1f} mi", 10.5, INK, bold=True)
        else:
            f.text(cx, BASE - 6, "–", 10.5, FAINT)
        f.text(cx, BASE + 18, h.t.astimezone(zone).strftime("%-I %p"), 10, INK if on else MUTED, bold=on)
        f.text(cx, BASE + 34, f"{h.temp_f:.0f}°F" if h.temp_f is not None else "–", 10.5, MUTED, mono=True)
        word = (h.weather[0] if h.weather else "none reported" if h.reports else "no report")
        word = word.replace("unknown precipitation", "precipitation").capitalize()
        f.text(cx, BASE + 50, word if col > 90 or len(word) < 12 else word[:10] + "…", 8.6, MUTED)
    return f


def temperature(hrs: list[timeline.Hour], tz: str, mark: datetime | None = None, mark_label: str = "",
                wet: bool = False, size=WEB) -> Figure | None:
    """Temperature through the period, freezing always in view, hours at or below it filled, the coldest marked."""
    known = [h for h in hrs if h.temp_f is not None]
    span = (hrs[-1].t - hrs[0].t).total_seconds() if hrs else 0
    if len(known) < 2 or not span:
        return None
    W, H = size
    zone = ZoneInfo(tz)
    L, R, T, B = 30, 12, 46 if wet else 32, 26 + (16 if wet else 0)
    pw, ph = W - L - R, H - T - B
    lo, hi = min(h.temp_f for h in known), max(h.temp_f for h in known)
    ymin, ymax = min(30, math.floor(lo / 10) * 10), max(40, (math.floor(hi / 10) + 1) * 10)
    X = lambda t: L + pw * (t - hrs[0].t).total_seconds() / span  # noqa: E731
    Y = lambda v: T + ph * (1 - (v - ymin) / (ymax - ymin))  # noqa: E731
    z = Y(32)
    f = Figure("Hourly temperature with the hours at or below freezing shaded", size)
    _legend(f, L + 4, [("line", "Temperature, °F"), ("freezing", "At or below 32°F")])
    if wet:     # what the station reported in the air: no record here measures ice on a surface
        _legend(f, L + 4, [(ICY, "Freezing rain, ice or snow reported at the station"),
                           (SKY, "Other precipitation reported")], 28)
    for v in range(ymin, ymax + 1, 10 if ymax - ymin <= 40 else 20):
        f.line(L, Y(v), W - R, Y(v))
        f.text(L - 6, Y(v) + 3.5, v, 9.5, FAINT, "end", mono=True)
    runs, run = [], []
    for h in hrs:
        if h.temp_f is None:
            runs.append(run)
            run = []
        else:
            run.append(h)
    runs = [r for r in [*runs, run] if len(r) > 1]
    for r in runs:     # the shading under freezing, split where the line crosses 32°F
        for a, b in zip(r, r[1:]):
            x1, y1, x2, y2 = X(a.t), Y(a.temp_f), X(b.t), Y(b.temp_f)
            if y1 <= z and y2 <= z:
                continue
            if y1 >= z and y2 >= z:
                f.polygon([(x1, z), (x1, y1), (x2, y2), (x2, z)], SKY_FILL)
            else:
                xc = x1 + (x2 - x1) * (z - y1) / (y2 - y1)
                f.polygon([(x1, z), (x1, y1), (xc, z)] if y1 > z else [(xc, z), (x2, y2), (x2, z)], SKY_FILL)
    for t, lab in [(h.t, h.t.astimezone(zone)) for h in hrs if h.t.astimezone(zone).hour == 0]:
        f.line(X(t), T, X(t), T + ph, RULE, 1, (2, 3))
        f.text(X(t) + 3, H - 8, f"{lab:%b} {lab.day}", 9.5, FAINT, "start")
    for r in runs:
        f.polyline([(X(h.t), Y(h.temp_f)) for h in r], NAVY, 1.8)
    f.line(L, z, W - R, z, SKY, 1, (5, 4))
    if wet:
        y = T + ph + 6
        for h in hrs:
            if h.precipitating or (h.precip_mm or 0) > 0:
                f.rect(X(h.t), y, pw / len(hrs) + .4, 8, ICY if h.icy else SKY)
    c = timeline.coldest(hrs)
    x, y = X(c.t), Y(c.temp_f)
    f.circle(x, y, 4.5, NAVY, "#ffffff", 1.5)
    left = x < W * .6
    f.text(x + (9 if left else -14), y + (14 if T + ph - y > 18 else -6), f"{c.temp_f:.0f}°F, the lowest", 11.5, INK,
           "start" if left else "end", True)
    if mark is not None:
        x = X(mark)
        f.line(x, T - 6, x, T + ph, AMBER, 2)
        f.text(x - 5, T + 3, mark_label, 10, AMBER_INK, "end", True)
    return f
