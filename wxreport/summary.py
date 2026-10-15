"""Page 1 of the report: the area map and four key facts. Also used to keep the landing page's sample honest."""
from math import cos, radians, sin

from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Flowable, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

from . import areamap, pdf
from .report import ReportContext
from .timewin import fmt_local

AMBER, AMBER_LINE = colors.HexColor("#f2a93b"), colors.HexColor("#c9821a")
RED, BLUE, NAVY = colors.HexColor("#d9442e"), colors.HexColor("#3d7fc2"), colors.HexColor("#12263f")
WIND, GREY = colors.HexColor("#6b4fa0"), colors.HexColor("#5d6b7c")


# -- key facts ----------------------------------------------------------------------------------------
def key_facts(ctx: ReportContext) -> list[tuple[str, str, str]]:
    """Four (label, value, detail) facts for page 1, in plain words."""
    from . import units
    t = lambda x: fmt_local(x, ctx.loc.tz)  # noqa: E731
    facts = []
    sd = ctx.primary
    pg = sd.peak_gust() if sd else None
    if pg:
        st = sd.station
        facts.append(("Peak wind gust", f"{units.mph(pg[1]):.0f} mph",
                      f"{t(pg[0])} · {st.icao or st.id}, {st.proximity}"))
    else:
        facts.append(("Peak wind gust", "Not reported", "The nearest station reported no gust that day"
                      if sd else (ctx.stations_note or "No station data")))

    inside = [w for w in ctx.warnings if w.site_inside]
    if inside:
        names = sorted({w.name for w in inside})
        span = f"{t(min(w.issue for w in inside))} – {t(max(w.expire for w in inside))}"
        n = f" ({len(inside)})" if len(inside) > 1 else ""
        facts.append(("Warning area", "Inside", f"{' & '.join(names)}{n} · {span}"))
    elif ctx.warnings_note:
        facts.append(("Warning area", "Unavailable", "The warning archive could not be reached"))
    else:
        area = sorted({w.name for w in ctx.warnings})
        facts.append(("Warning area", "Outside" if area else "None",
                      ("County or zone listed: " + ", ".join(area)) if area else "No warning covered the property"))

    se = ctx.storm_events
    tors = [e for e in (se.events if se else []) if e.event_type == "Tornado" and e.distance_mi is not None]
    lsr_tor = [r for r in ctx.lsrs if r.type == "Tornado"]
    if tors:
        e = min(tors, key=lambda e: e.distance_mi)
        facts.append(("Nearest tornado", e.tor_scale or "Tornado", f"Path {e.proximity} at its closest"))
    elif lsr_tor:
        r = min(lsr_tor, key=lambda r: r.distance_mi)
        facts.append(("Nearest tornado", "Reported", f"Storm report {r.proximity}, {t(r.time)}"))
    else:
        detail = "No tornado recorded within 25 mi"
        if se and se.status == "not_published":
            detail += " (Storm Events not yet published)"
        facts.append(("Nearest tornado", "None", detail))

    hail = [r for r in ctx.lsrs if r.type == "Hail" and r.distance_mi <= 5 and r.magnitude]
    radar = [h for h in ctx.hail if h.distance_mi <= 5 and h.max_size_in]
    if hail:
        def size(r):
            try:
                return float(r.magnitude.split()[0])
            except (ValueError, IndexError):
                return 0.0
        r = max(hail, key=lambda r: (size(r), -r.distance_mi))
        facts.append(("Largest hail within 5 mi", f"{size(r):g} in", f"Reported {r.proximity}, {t(r.time)}"))
    elif radar:
        h = max(radar, key=lambda h: (h.max_size_in, -h.distance_mi))
        facts.append(("Largest hail within 5 mi", f"{h.max_size_in:g} in", f"Radar estimate {h.proximity}, {t(h.time)}"))
    else:
        facts.append(("Largest hail within 5 mi", "None", "No hail reported or detected"))
    return facts


_LBL = ParagraphStyle("fl", fontName="Helvetica", fontSize=6.6, leading=8, textColor=pdf.MUTED)
_VAL = ParagraphStyle("fv", fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=pdf.INK)
_DET = ParagraphStyle("fd", fontName="Helvetica", fontSize=7.6, leading=9.4, textColor=pdf.INK)


def facts_table(ctx: ReportContext) -> Table:
    cells = [[Paragraph(pdf.esc(lbl.upper()), _LBL), Paragraph(pdf.esc(val), _VAL), Paragraph(pdf.esc(det), _DET)]
             for lbl, val, det in key_facts(ctx)]
    t = Table([cells], colWidths=[areamap.MAP_W_PT / 4] * 4, hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BOX", (0, 0), (-1, -1), 0.6, pdf.RULE),
                           ("LINEBEFORE", (1, 0), (-1, -1), 0.6, pdf.RULE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return t


# -- map ------------------------------------------------------------------------------------------------
class AreaMap(Flowable):
    def __init__(self, ctx: ReportContext):
        super().__init__()
        self.ctx, self.ext = ctx, ctx.area

    def wrap(self, aw, ah):
        return areamap.MAP_W_PT, areamap.MAP_H_PT

    def draw(self):
        c, e, ctx = self.canv, self.ext, self.ctx
        W, H = areamap.MAP_W_PT, areamap.MAP_H_PT
        pt = e.to_pt
        c.saveState()
        p = c.beginPath()
        p.rect(0, 0, W, H)
        c.clipPath(p, stroke=0, fill=0)
        if e.basemap is not None:
            c.drawImage(ImageReader(e.basemap), 0, 0, W, H)
        else:
            c.setFillColor(colors.HexColor("#f3f5f7"))
            c.rect(0, 0, W, H, stroke=0, fill=1)

        # warning areas
        for w in ctx.warnings:
            for b in w.bulletins[:1]:
                if not b.polygon:
                    continue
                path = c.beginPath()
                for i, (la, lo) in enumerate(b.polygon):
                    (path.moveTo if i == 0 else path.lineTo)(*pt(la, lo))
                path.close()
                c.setFillColor(AMBER, alpha=0.13)
                c.setStrokeColor(AMBER_LINE)
                c.setLineWidth(1.1)
                c.setDash(4, 3)
                c.drawPath(path, stroke=1, fill=1)
                c.setDash()

        # distance rings
        sx, sy = pt(e.lat, e.lon)
        ppm = e.pt_per_mile()
        r = e.ring_step
        c.setStrokeColor(colors.HexColor("#4b5868"), alpha=0.55)
        c.setLineWidth(0.6)
        c.setFont("Helvetica", 6.5)
        while r <= e.radius_mi + 1e-6:
            c.circle(sx, sy, r * ppm, stroke=1, fill=0)
            lx, ly = sx + r * ppm * cos(radians(60)), sy + r * ppm * sin(radians(60))
            if 4 < lx < W - 20 and 4 < ly < H - 10:
                c.setFillColor(colors.white, alpha=0.85)
                c.rect(lx - 1, ly - 2, c.stringWidth(f"{r:g} mi", "Helvetica", 6.5) + 2, 8.5, stroke=0, fill=1)
                c.setFillColor(GREY)
                c.drawString(lx, ly, f"{r:g} mi")
            r += e.ring_step
        c.setStrokeAlpha(1)

        # radar hail
        for h in ctx.hail:
            if h.max_size_in:
                x, y = pt(h.lat, h.lon)
                c.setFillColor(BLUE, alpha=0.22)
                c.setStrokeColor(BLUE, alpha=0.85)
                c.setLineWidth(0.6)
                c.circle(x, y, 2.2 + 2.0 * h.max_size_in, stroke=1, fill=1)
        c.setFillAlpha(1)
        c.setStrokeAlpha(1)

        # tornado paths (Storm Events)
        se = ctx.storm_events
        for ev in (se.events if se else []):
            if ev.event_type == "Tornado" and ev.begin_latlon:
                (x1, y1), (x2, y2) = pt(*ev.begin_latlon), pt(*(ev.end_latlon or ev.begin_latlon))
                c.setStrokeColor(RED)
                c.setLineWidth(3.4)
                c.setLineCap(1)
                c.line(x1, y1, x2, y2)

        # storm reports
        for rep in ctx.lsrs:
            x, y = pt(rep.lat, rep.lon)
            if rep.type == "Hail":
                c.setFillColor(BLUE)
                c.setStrokeColor(colors.white)
                c.setLineWidth(0.6)
                d = c.beginPath()
                d.moveTo(x, y + 3.6); d.lineTo(x + 3.6, y); d.lineTo(x, y - 3.6); d.lineTo(x - 3.6, y); d.close()
                c.drawPath(d, stroke=1, fill=1)
            elif rep.type == "Tornado":
                c.setFillColor(RED)
                c.setStrokeColor(colors.white)
                tri = c.beginPath()
                tri.moveTo(x, y + 4.2); tri.lineTo(x + 3.8, y - 2.6); tri.lineTo(x - 3.8, y - 2.6); tri.close()
                c.drawPath(tri, stroke=1, fill=1)
            elif "wind" in rep.type.lower():
                c.setFillColor(WIND)
                c.setStrokeColor(colors.white)
                c.circle(x, y, 2.8, stroke=1, fill=1)

        # weather stations
        c.setFont("Helvetica-Bold", 6.8)
        for s in ctx.stations:
            x, y = pt(s.station.lat, s.station.lon)
            if not (0 <= x <= W and 0 <= y <= H):
                continue
            c.setFillColor(NAVY)
            c.setStrokeColor(colors.white)
            c.setLineWidth(1)
            c.rect(x - 4, y - 4, 8, 8, stroke=1, fill=1)
            label = s.station.icao or s.station.id
            tw = c.stringWidth(label, "Helvetica-Bold", 6.8)
            c.setFillColor(colors.white, alpha=0.9)
            c.roundRect(x + 6, y - 4.5, tw + 5, 9.5, 2, stroke=0, fill=1)
            c.setFillColor(NAVY, alpha=1)
            c.drawString(x + 8.5, y - 2, label)

        # property
        c.setFillColor(AMBER, alpha=0.3)
        c.circle(sx, sy, 9, stroke=0, fill=1)
        c.setFillColor(AMBER, alpha=1)
        c.setStrokeColor(colors.HexColor("#0b1a2e"))
        c.setLineWidth(1.8)
        c.circle(sx, sy, 4.6, stroke=1, fill=1)
        c.setFont("Helvetica-Bold", 7.5)
        tw = c.stringWidth("Property", "Helvetica-Bold", 7.5)
        c.setFillColor(colors.white, alpha=0.95)
        c.roundRect(sx + 9, sy + 3, tw + 7, 11, 2.5, stroke=0, fill=1)
        c.setFillColor(pdf.INK, alpha=1)
        c.drawString(sx + 12.5, sy + 6, "Property")

        # north arrow, scale bar, attribution
        c.setFillColor(colors.white, alpha=0.9)
        c.roundRect(W - 24, H - 32, 18, 26, 3, stroke=0, fill=1)
        c.setFillColor(pdf.INK, alpha=1)
        arrow = c.beginPath()
        arrow.moveTo(W - 15, H - 10); arrow.lineTo(W - 11, H - 20); arrow.lineTo(W - 15, H - 17); arrow.lineTo(W - 19, H - 20)
        arrow.close()
        c.drawPath(arrow, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(W - 15, H - 29, "N")
        miles = e.ring_step
        bar = miles * ppm
        c.setFillColor(colors.white, alpha=0.9)
        c.roundRect(6, 6, bar + 30, 16, 3, stroke=0, fill=1)
        c.setFillColor(pdf.INK, alpha=1)
        c.rect(11, 11, bar, 2.4, stroke=0, fill=1)
        c.setFont("Helvetica", 6.5)
        c.drawString(14 + bar, 10, f"{miles:g} mi")
        note = areamap.ATTRIBUTION if e.basemap is not None else "Basemap unavailable"
        c.setFont("Helvetica", 5.8)
        tw = c.stringWidth(note, "Helvetica", 5.8)
        c.setFillColor(colors.white, alpha=0.85)
        c.rect(W - tw - 8, 0, tw + 8, 9, stroke=0, fill=1)
        c.setFillColor(GREY, alpha=1)
        c.drawString(W - tw - 4, 2.6, note)
        c.restoreState()
        c.setStrokeColor(pdf.RULE)
        c.setLineWidth(0.6)
        c.rect(0, 0, W, H, stroke=1, fill=0)


class Legend(Flowable):
    ITEMS = [("site", "Property"), ("station", "Weather station"), ("warn", "Warning area"),
             ("path", "Tornado path"), ("radar", "Radar hail"), ("hail", "Hail report"), ("wind", "Wind report"),
             ("tor", "Tornado report")]

    def wrap(self, aw, ah):
        return areamap.MAP_W_PT, 14

    def draw(self):
        c = self.canv
        x, y = 0, 4
        c.setFont("Helvetica", 7)
        for kind, label in self.ITEMS:
            cx = x + 5
            if kind == "site":
                c.setFillColor(AMBER); c.setStrokeColor(colors.HexColor("#0b1a2e")); c.setLineWidth(1.2)
                c.circle(cx, y + 2.5, 3.2, stroke=1, fill=1)
            elif kind == "station":
                c.setFillColor(NAVY); c.rect(cx - 3.2, y - 0.7, 6.4, 6.4, stroke=0, fill=1)
            elif kind == "warn":
                c.setFillColor(AMBER, alpha=0.18); c.setStrokeColor(AMBER_LINE); c.setDash(2, 1.5); c.setLineWidth(0.8)
                c.rect(cx - 5, y - 1, 10, 7, stroke=1, fill=1); c.setDash(); c.setFillAlpha(1)
            elif kind == "path":
                c.setStrokeColor(RED); c.setLineWidth(2.6); c.setLineCap(1); c.line(cx - 5, y + 2.5, cx + 5, y + 2.5)
            elif kind == "radar":
                c.setFillColor(BLUE, alpha=0.25); c.setStrokeColor(BLUE); c.setLineWidth(0.6)
                c.circle(cx, y + 2.5, 3.4, stroke=1, fill=1); c.setFillAlpha(1)
            elif kind == "hail":
                c.setFillColor(BLUE); d = c.beginPath(); d.moveTo(cx, y + 6); d.lineTo(cx + 3.4, y + 2.5)
                d.lineTo(cx, y - 1); d.lineTo(cx - 3.4, y + 2.5); d.close(); c.drawPath(d, stroke=0, fill=1)
            elif kind == "wind":
                c.setFillColor(WIND); c.circle(cx, y + 2.5, 2.8, stroke=0, fill=1)
            elif kind == "tor":
                c.setFillColor(RED); t = c.beginPath(); t.moveTo(cx, y + 6.4); t.lineTo(cx + 3.6, y - 0.6)
                t.lineTo(cx - 3.6, y - 0.6); t.close(); c.drawPath(t, stroke=0, fill=1)
            c.setFillColor(GREY)
            c.drawString(x + 13, y, label)
            x += 13 + c.stringWidth(label, "Helvetica", 7) + 12
