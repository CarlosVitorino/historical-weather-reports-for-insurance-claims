"""Build the Weather Evidence brand files in brand/: the mark, horizontal lockups (text as outlines), PNGs.

    .venv/bin/python scripts/make_brand.py

Needs the dev-only packages fonttools, brotli, uharfbuzz and playwright (not app dependencies).
"""
import io
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wxreport.brand import AMBER, MARK_INNER, NAVY  # noqa: E402

OUT = ROOT / "brand"
FONT = ROOT / "wxreport/static/fonts/Geist-Variable.woff2"
TEXT, WEIGHT, TRACK = "Weather Evidence", 650, -0.025   # tracking in em


def text_path(text: str, size: float) -> tuple[str, float, float]:
    """SVG path data for `text` set in Geist at `size` px, baseline at y=0. Returns (d, width, cap_height)."""
    font = TTFont(FONT)
    inst = instantiateVariableFont(font, {"wght": WEIGHT})
    buf = io.BytesIO()
    inst.flavor = None
    inst.save(buf)
    data = buf.getvalue()
    hbf = hb.Font(hb.Face(data))
    hbf.set_variations({"wght": WEIGHT})
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(hbf, b, {"kern": True, "liga": True})
    upem = inst["head"].unitsPerEm
    scale = size / upem
    gs = inst.getGlyphSet()
    order = inst.getGlyphOrder()
    pen = SVGPathPen(gs)
    x = 0.0
    for info, pos in zip(b.glyph_infos, b.glyph_positions):
        name = order[info.codepoint]
        tp = TransformPen(pen, (scale, 0, 0, -scale, (x + pos.x_offset) * scale, -pos.y_offset * scale))
        gs[name].draw(tp)
        x += pos.x_advance + TRACK * upem
    width = (x - TRACK * upem) * scale
    cap = inst["OS/2"].sCapHeight * scale
    return pen.getCommands(), width, cap


def mark_svg(size: int = 32) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 32 32">'
            f'{MARK_INNER}</svg>')


def lockup_svg(text_color: str) -> tuple[str, int, int]:
    mark, gap, size = 40, 13, 25.0
    d, tw, cap = text_path(TEXT, size)
    w, h = int(mark + gap + tw + 2), mark
    base = h / 2 + cap / 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
           f'<g transform="scale({mark / 32})">{MARK_INNER}</g>'
           f'<path transform="translate({mark + gap},{base:.2f})" fill="{text_color}" d="{d}"/></svg>')
    return svg, w, h


def main():
    OUT.mkdir(exist_ok=True)
    files = {"mark.svg": mark_svg(), "logo-on-dark.svg": lockup_svg("#ffffff")[0],
             "logo-on-light.svg": lockup_svg(NAVY)[0]}
    for name, svg in files.items():
        (OUT / name).write_text(svg)
    import re
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = b.new_page(viewport={"width": 2400, "height": 800})
        for name, px, bg in [("mark.svg", 512, None), ("mark.svg", 180, None), ("logo-on-dark.svg", 0, NAVY),
                             ("logo-on-light.svg", 0, None)]:
            svg = (OUT / name).read_text()
            w, h = (float(v) for v in re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
            k = px / w if px else 4
            svg = svg.replace(f'width="{w:g}" height="{h:g}"', f'width="{w * k:g}" height="{h * k:g}"', 1)
            pad = 24 * k / 4 if bg else 0
            pg.set_content(f'<html><body style="margin:0;background:transparent"><div id="x" style="display:inline-block;'
                           f'line-height:0;padding:{pad}px;background:{bg or "transparent"}">{svg}</div></body></html>')
            stem = name[:-4] + (f"-{px}" if px else "")
            pg.locator("#x").screenshot(path=str(OUT / f"{stem}.png"), omit_background=bg is None)
        b.close()
    print("\n".join(sorted(f.name for f in OUT.iterdir())))


if __name__ == "__main__":
    main()
