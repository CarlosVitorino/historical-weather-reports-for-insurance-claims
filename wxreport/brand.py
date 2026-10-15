"""The Weather Evidence mark: a "W" with the loss site marked above it, on an amber tile.

One geometry (a 32×32 grid) shared by the web pages, the favicon, the PDF report and the brand files.
"""
from urllib.parse import quote

AMBER = "#f2a93b"
NAVY = "#0b1a2e"

# 32×32 grid. Polyline points of the W and the site dot, used by both SVG and the PDF renderer.
W_POINTS = [(7, 10.5), (11.3, 22.5), (16, 12.3), (20.7, 22.5), (25, 10.5)]
DOT = (16, 7.2, 1.9)       # cx, cy, r
TILE_RADIUS = 8
STROKE = 2.5

MARK_INNER = (f'<rect width="32" height="32" rx="{TILE_RADIUS}" fill="{AMBER}"/>'
              f'<path d="M{" L".join(f"{x} {y}" for x, y in W_POINTS)}" fill="none" stroke="{NAVY}" '
              f'stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round"/>'
              f'<circle cx="{DOT[0]}" cy="{DOT[1]}" r="{DOT[2]}" fill="{NAVY}"/>')


def mark_svg(size: int, label: str = "") -> str:
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return f'<svg width="{size}" height="{size}" viewBox="0 0 32 32" {aria}>{MARK_INNER}</svg>'


FAVICON = "data:image/svg+xml," + quote(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{MARK_INNER}</svg>', safe=":/=' ")


def draw_mark(canvas, x: float, y: float, size: float) -> None:
    """Draw the mark on a ReportLab canvas with its lower-left corner at (x, y)."""
    from reportlab.lib import colors
    s = size / 32
    canvas.saveState()
    canvas.setFillColor(colors.HexColor(AMBER))
    canvas.roundRect(x, y, size, size, TILE_RADIUS * s, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor(NAVY))
    canvas.setFillColor(colors.HexColor(NAVY))
    canvas.setLineWidth(STROKE * s)
    canvas.setLineCap(1)
    canvas.setLineJoin(1)
    p = canvas.beginPath()
    for i, (px, py) in enumerate(W_POINTS):
        (p.moveTo if i == 0 else p.lineTo)(x + px * s, y + (32 - py) * s)
    canvas.drawPath(p, stroke=1, fill=0)
    canvas.circle(x + DOT[0] * s, y + (32 - DOT[1]) * s, DOT[2] * s, stroke=0, fill=1)
    canvas.restoreState()
