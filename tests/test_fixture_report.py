"""End to end on a real (trimmed) snapshot: Bloomington, IN, 2026-02-19 — the StormRecord sample's case."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from wxreport import units
from wxreport.report import build_pdf, gather

FIXTURES = Path(__file__).parent / "fixtures" / "snapshots"
ADDR, DAY = "401 N College Ave, Bloomington, IN", "2026-02-19"


@pytest.fixture(scope="module")
def ctx():
    return gather(ADDR, DAY, root=FIXTURES, offline=True)


def test_station_pinned_peak_gust(ctx):
    sd = ctx.primary
    assert sd.station.icao == "KBMG" and sd.station.proximity == "4.7 mi WSW"
    t, ms, _ = sd.peak_gust()
    assert round(units.mph(ms)) == 70 and t.strftime("%H:%M") == "00:01"


def test_precip_is_marked_incomplete(ctx):
    total, counted, missing, _ = ctx.primary.precipitation(ctx.day)
    assert missing == 2 and counted == 22


def test_site_inside_both_tornado_warning_polygons(ctx):
    inside = [w.vtec_id for w in ctx.warnings if w.site_inside]
    assert inside == ["2026-KIND-TO-W-0008", "2026-KIND-TO-W-0009"]
    watch = next(w for w in ctx.warnings if w.vtec_id == "2026-KIND-TO-A-0010")
    assert not watch.polygon_based and len(watch.bulletins) == 11


def test_storm_events_tornado_path_distance(ctx):
    tor = [e for e in ctx.storm_events.events if e.event_type == "Tornado"]
    assert len(tor) == 1 and tor[0].tor_scale == "EF2" and tor[0].proximity == "2.0 mi WSW"


def test_lsrs_hail_and_lightning(ctx):
    assert len(ctx.lsrs) == 19
    asos = next(r for r in ctx.lsrs if r.source == "ASOS")
    assert asos.magnitude == "70 mph"   # the competitor printed this as "70.0 kts"
    near = min((h for h in ctx.hail if h.max_size_in), key=lambda h: h.distance_mi)
    assert near.proximity == "1.2 mi NNE" and near.max_size_in == 1.5
    assert sum(x.count for x in ctx.lightning if x.contains_site) == 8


def test_pdf_is_deterministic_and_complete(ctx, tmp_path):
    a = build_pdf(ctx)
    assert a == build_pdf(gather(ADDR, DAY, root=FIXTURES, offline=True))
    if shutil.which("pdftotext"):
        p = tmp_path / "r.pdf"
        p.write_bytes(a)
        text = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
        for needle in ["Key findings", "70 mph (61 kt)", "Inside warning polygon", "NCEI Storm Events Database",
                       "NEXRAD radar hail", "Appendix B", ctx.report_id]:
            assert needle in text, needle


def test_sources_down_render_as_unavailable(tmp_path):
    root = tmp_path / "snaps"
    shutil.copytree(FIXTURES, root)
    mf = next(root.glob("*/manifest.json"))
    m = json.loads(mf.read_text())
    for name in list(m["sources"]):
        if name.startswith(("iem_", "stormevents", "swdi", "ghcnh_USW00003893")):
            m["sources"][name] = {"url": m["sources"][name]["url"], "retrieved_at": m["sources"][name]["retrieved_at"],
                                  "status": "error", "error": "ConnectionError: simulated outage"}
    mf.write_text(json.dumps(m))
    ctx = gather(ADDR, DAY, root=root, offline=True)
    assert ctx.warnings == [] and "unavailable" in ctx.warnings_note
    assert ctx.lsrs == [] and ctx.storm_events.status == "unavailable"
    assert ctx.hail_note and ctx.primary.station.icao != "KBMG"
    assert next(s for s in ctx.stations if s.station.id == "USW00003893").status == "unavailable"
    pdf = build_pdf(ctx)
    p = tmp_path / "down.pdf"
    p.write_bytes(pdf)
    if shutil.which("pdftotext"):
        text = " ".join(subprocess.run(["pdftotext", "-l", "1", str(p), "-"], capture_output=True, text=True).stdout.split())
        assert "Sources unavailable when this report was made" in text and "station KBMG" in text
