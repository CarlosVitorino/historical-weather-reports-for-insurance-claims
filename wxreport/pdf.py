"""Deterministic PDF rendering. ReportLab's invariant mode fixes the creation date and document ID,
and only built-in fonts are used, so identical report data gives a byte-identical file."""
from io import BytesIO

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import DOMAIN, PRODUCT
from .brand import draw_mark

rl_config.invariant = 1

INK = colors.HexColor("#1b2430")
MUTED = colors.HexColor("#5b6675")
RULE = colors.HexColor("#c9d1db")
ACCENT = colors.HexColor("#1f4e79")
SHADE = colors.HexColor("#eef2f6")

_base = getSampleStyleSheet()
STYLES = {
    "title": ParagraphStyle("title", parent=_base["Title"], alignment=TA_LEFT, fontSize=20, leading=24,
                            textColor=INK, spaceAfter=4),
    "h1": ParagraphStyle("h1", parent=_base["Heading1"], fontSize=15, leading=19, textColor=ACCENT,
                         spaceBefore=6, spaceAfter=6),
    "h2": ParagraphStyle("h2", parent=_base["Heading2"], fontSize=11.5, leading=14, textColor=INK,
                         spaceBefore=8, spaceAfter=4),
    "body": ParagraphStyle("body", parent=_base["BodyText"], fontSize=9, leading=12, textColor=INK),
    "small": ParagraphStyle("small", parent=_base["BodyText"], fontSize=7.5, leading=9.5, textColor=MUTED),
    "cell": ParagraphStyle("cell", parent=_base["BodyText"], fontSize=8, leading=10, textColor=INK),
    "tiny": ParagraphStyle("tiny", parent=_base["BodyText"], fontSize=7, leading=8.4, textColor=INK),
    "big": ParagraphStyle("big", parent=_base["BodyText"], fontSize=16, leading=19, textColor=INK,
                          fontName="Helvetica-Bold"),
}


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def table(rows: list[list], col_widths: list[float] | None = None, header: bool = True,
          zebra: bool = True, small: bool = False) -> Table:
    """Plain values are escaped; pass a Paragraph (via P) for a cell that needs markup."""
    style_name = "tiny" if small else "cell"
    cells = [[P(esc(c), style_name) if isinstance(c, (str, int, float)) else c for c in r] for r in rows]
    t = Table(cells, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LINEBELOW", (0, 0), (-1, -1), 0.25, RULE),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
             ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), SHADE), ("LINEBELOW", (0, 0), (-1, 0), 0.75, ACCENT)]
    if zebra:
        for i in range(2 if header else 1, len(rows), 2):
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8fafc")))
    t.setStyle(TableStyle(style))
    return t


def _numbered_canvas(report_id: str):
    class NumberedCanvas(rl_canvas.Canvas):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self._pages = []

        def showPage(self):
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._pages)
            for state in self._pages:
                self.__dict__.update(state)
                self.setFont("Helvetica", 7)
                self.setFillColor(MUTED)
                draw_mark(self, 0.75 * inch, 0.5 * inch - 2.2, 9)
                self.drawString(0.75 * inch + 13, 0.5 * inch,
                                f"{PRODUCT} · {DOMAIN} — Page {self._pageNumber} of {total} — ID: {report_id}")
                super().showPage()
            super().save()
    return NumberedCanvas


class Lockup(Flowable):
    """The cover's logo lockup: the mark beside the report title."""

    def __init__(self, title: str, size: float = 30):
        super().__init__()
        self.title, self.size = title, size

    def wrap(self, aw, ah):
        return aw, self.size

    def draw(self):
        c = self.canv
        draw_mark(c, 0, 0, self.size)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 19)
        c.drawString(self.size + 10, self.size / 2 - 6.5, self.title)


def render(flowables: list, report_id: str, title: str) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.8 * inch, title=title,
                            author=PRODUCT, subject=report_id, creator="wxreport", producer="wxreport")
    doc.build(list(flowables), canvasmaker=_numbered_canvas(report_id))
    return buf.getvalue()


__all__ = ["P", "esc", "table", "render", "Spacer", "STYLES", "PRODUCT", "inch"]
