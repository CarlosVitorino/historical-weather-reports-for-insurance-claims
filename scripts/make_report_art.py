"""Build what the report pages show from the four real sample reports (the requests behind static/sample-<slug>.pdf).

    PYTHONPATH=<dir with pypdfium2> .venv/bin/python scripts/make_report_art.py [--refresh]
      → wxreport/static/sample-<slug>.pdf           the sample report itself
      → wxreport/static/sample-<slug>-p{1,2}.webp   its page one and its own section
      → wxreport/static/report-art.json             where and when, page count, page-one facts, and the report's chart

The chart on a report's page is the one in its PDF (focus.figure, charts.py). It replays data/snapshots; --refresh retrieves the records again.
pypdfium2 renders the pages and isn't a dependency of the app.
"""
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wxreport import focus  # noqa: E402
from wxreport.report import build_pdf, gather  # noqa: E402

STATIC = ROOT / "wxreport/static"
SAMPLES = {
    "car-hail-damage": dict(address="1819 Farnam St, Omaha, NE", day="2024-04-26"),
    "car-accident": dict(address="Metro Courthouse, 1 Public Square, Nashville, TN", day="2024-01-15", lat=36.1663,
                         lon=-86.7784, time="08:00"),
    "slip-and-fall-on-ice": dict(address="301 W 2nd St, Austin, TX", day="2023-02-01", time="08:00"),
    "frozen-pipes": dict(address="1500 Marilla St, Dallas, TX", day="2021-02-17"),
}
def pages(pdf: Path, slug: str) -> int:
    import pypdfium2
    doc = pypdfium2.PdfDocument(str(pdf))
    for i in (0, 1):
        img = doc[i].render(scale=1.53).to_pil().convert("RGB")
        img.save(STATIC / f"sample-{slug}-p{i + 1}.webp", quality=72, method=6)
    return len(doc)


def main():
    art = {}
    for slug, s in SAMPLES.items():
        ctx = gather(s["address"], s["day"], lat=s.get("lat"), lon=s.get("lon"), offline="--refresh" not in sys.argv, refresh="--refresh" in sys.argv,
                     root=ROOT / "data/snapshots", report_type=slug, event_time=s.get("time"))
        pdf = STATIC / f"sample-{slug}.pdf"
        pdf.write_bytes(build_pdf(ctx))
        fig, caption = focus.figure(ctx)
        d = ctx.day.day
        when = ctx.event_utc.astimezone(ZoneInfo(ctx.loc.tz)).strftime(" · %-I:%M %p") if ctx.event_utc else ""
        art[slug] = {"place": ", ".join(s["address"].split(", ")[-2:]), "date": f"{d:%B} {d.day}, {d.year}{when}",
                     "pages": pages(pdf, slug), "report_id": ctx.report_id, "caption": caption, "chart": fig.svg(),
                     "facts": [{"label": a, "value": b, "detail": c} for a, b, c in focus.key_facts(ctx)]}
        print(slug, ctx.report_id, art[slug]["pages"])
    path = STATIC / "report-art.json"
    path.write_text(json.dumps(art, ensure_ascii=False, separators=(",", ":")))
    print(path)


if __name__ == "__main__":
    main()
