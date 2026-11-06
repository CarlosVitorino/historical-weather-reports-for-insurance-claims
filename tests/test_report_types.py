"""Kinds of report: the hours around a date, their pages in the PDF, and how they are ordered and shown on the site."""
import re
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from wxreport import report_pages, reporttypes, timeline
from wxreport.report import InvalidRequest, build_pdf, gather
from wxreport.sources import ghcnh
from wxreport.sources.ghcnh import Obs

from test_seo import BANNED
from test_web import env  # noqa: F401  (fixture)

FIXTURES = Path(__file__).parent / "fixtures" / "snapshots"
ADDR, DAY = "401 N College Ave, Bloomington, IN", "2026-02-19"
T0 = datetime(2026, 2, 19, 0, 53, tzinfo=timezone.utc)


def obs(hour: int, temp_c: float | None, weather=(), precip=None, vis=16.0, rtype="FM15") -> Obs:
    v = {"temperature": temp_c, "visibility": vis, "precipitation": precip, "wind_gust": None, "snow_depth": None}
    return Obs(T0 + timedelta(hours=hour), rtype, v, {}, {}, list(weather), [], "", None)


def test_hours_keep_gaps_and_use_the_routine_report():
    readings = [obs(0, 0.0), obs(0, -5.0, rtype="FM16", vis=1.0), obs(2, 1.0, ["light rain"], precip=2.5)]
    start = T0.replace(minute=0)
    hrs = timeline.hours(readings, start, start + timedelta(hours=4))
    assert [h.reports for h in hrs] == [2, 0, 1, 0] and timeline.missing(hrs) == 2
    assert hrs[0].temp_f == 32 and round(hrs[0].vis_mi, 1) == 0.6     # routine temperature, lowest visibility
    assert hrs[1].temp_f is None and hrs[2].precip_mm == 2.5


def test_freezing_figures():
    temps = [1.0, -1.0, -2.0, None, -1.0, 1.0, -8.0]
    start = T0.replace(minute=0)
    hrs = timeline.hours([obs(i, t) for i, t in enumerate(temps)], start, start + timedelta(hours=7))
    assert timeline.at_or_below(hrs, 32) == 4
    assert timeline.longest_run(hrs, 32) == 2                         # the missing hour ends the run
    assert timeline.crossings(hrs) == 3                               # down, up, down
    assert round(timeline.coldest(hrs).temp_f) == 18


def test_last_precipitation_ignores_blowing_snow():
    start = T0.replace(minute=0)
    hrs = timeline.hours([obs(0, -1.0, ["light freezing rain"]), obs(1, -1.0, ["blowing snow"])], start,
                         start + timedelta(hours=2))
    assert timeline.last_precip(hrs) is hrs[0] and hrs[0].icy and not hrs[1].precipitating


def test_history_crosses_new_year():
    class Snap:
        def __init__(self):
            self.asked = []

        def fetch(self, name, url, missing_ok=False):
            self.asked.append(name)
            return None
    snap = Snap()
    st = ghcnh.Station("USW1", "X", 0, 0, 0, "IN", "KX", 1, 0)
    ghcnh.history(snap, st, datetime(2025, 12, 30, tzinfo=timezone.utc), datetime(2026, 1, 2, tzinfo=timezone.utc))
    assert snap.asked == ["ghcnh_USW1_2025", "ghcnh_USW1_2026"]


def test_time_is_required_when_a_kind_asks_for_it():
    with pytest.raises(InvalidRequest):
        gather(ADDR, DAY, root=FIXTURES, offline=True, report_type="car-accident", event_time="25:00")


def test_the_plain_report_keeps_its_id():
    assert gather(ADDR, DAY, root=FIXTURES, offline=True).kind.slug == reporttypes.DEFAULT
    assert "report_type" not in gather(ADDR, DAY, root=FIXTURES, offline=True).snap.request


@pytest.mark.parametrize("slug", [s for s in reporttypes.TYPES if s != reporttypes.DEFAULT])
def test_every_kind_renders(slug):
    ctx = gather(ADDR, DAY, root=FIXTURES, offline=True)
    kind = reporttypes.TYPES[slug]
    event = datetime(2026, 2, 19, 13, 0, tzinfo=timezone.utc) if kind.time_label else None
    start = (event or ctx.day.start_utc) - kind.before
    readings = [obs(h, -2.0 + h / 10, ["light snow"]) for h in range(-80, 24)]
    full = replace(ctx, kind=kind, event_utc=event, hours=timeline.hours(readings, start, start + kind.before +
                                                                         kind.after + timedelta(hours=2)))
    pdf = build_pdf(full)
    assert pdf[:4] == b"%PDF" and pdf == build_pdf(full)   # same inputs, same bytes
    empty = replace(full, hours=[], history_note="No station reported on this date.")
    assert build_pdf(empty)[:4] == b"%PDF"


def test_report_pages_are_public_and_say_their_limits(env):  # noqa: F811
    _, client, _ = env
    assert client.get("/reports").status_code == 200
    home = client.get("/").text
    for slug, kind in reporttypes.TYPES.items():
        if slug == reporttypes.DEFAULT:
            continue
        r = client.get(kind.path)
        assert r.status_code == 200 and f'href="/order?type={slug}"' in r.text
        assert "What it doesn't show" in r.text and not BANNED.search(re.sub(r"<[^>]+>", " ", r.text))
        assert f'<link rel="canonical" href="https://reports.test{kind.path}">' in r.text
        assert f'href="{kind.path}"' in home                               # menu and home page
        assert kind.path in client.get("/sitemap.xml").text
    assert {s.sample for s in report_pages.SPECS} == {f"/static/sample-{s.slug}.pdf" for s in report_pages.SPECS}


def test_samples_exist():
    static = Path(report_pages.__file__).parent / "static"
    for s in report_pages.SPECS:
        assert (static / Path(s.sample).name).stat().st_size > 10_000, s.slug


def test_order_form_follows_the_kind(env):  # noqa: F811
    _, client, _ = env
    plain = client.get("/order").text
    assert 'name="type" value="property"' in plain and 'name="event_time"' not in plain
    fall = client.get("/order?type=slip-and-fall-on-ice&loss_date=2026-02-19").text
    assert 'name="type" value="slip-and-fall-on-ice"' in fall and "Date of the fall" in fall
    assert 'name="event_time"' in fall and "Time of the fall" in fall
    assert 'name="type" value="property"' in client.get("/order?type=nonsense").text


def test_a_kind_with_a_time_needs_one(env):  # noqa: F811
    _, client, _ = env
    r = client.post("/order", data={"address": "1 Main St", "loss_date": DAY, "email": "a@b.co",
                                    "type": "car-accident", "event_time": ""})
    assert "Enter the time of the accident." in r.text and 'name="event_time"' in r.text


def test_a_paid_order_builds_the_kind_it_was_ordered_as(env, monkeypatch):  # noqa: F811
    from test_web import ADDR as ORDER_ADDR
    from wxreport import fulfil
    app, client, _ = env
    asked = {}

    def capture(*a, **k):
        asked.update(k)
        return gather(ADDR, DAY, root=FIXTURES, offline=True)
    monkeypatch.setattr(fulfil, "gather", capture)
    r = client.post("/order", data={"address": ORDER_ADDR, "loss_date": DAY, "email": "a@example.com",
                                    "type": "car-accident", "event_time": "08:30"}, follow_redirects=False)
    assert r.status_code == 303
    oid, token = re.match(r"/order/(ord_\w+)/([\w-]+)", r.headers["location"]).groups()
    confirm = client.get(f"/order/{oid}/{token}").text
    assert "Car accident" in confirm and "Date of the accident" in confirm and "08:30" in confirm
    assert "type=car-accident" in confirm and "event_time=08%3A30" in confirm     # Change details keeps both
    app.state.store.update(oid, status="paid")
    app.state.fulfiller.run(oid)
    assert asked["report_type"] == "car-accident" and asked["event_time"] == "08:30"


def test_report_pages_show_their_sample_and_credit_the_photos(env):  # noqa: F811
    _, client, _ = env
    static = Path(report_pages.__file__).parent / "static"
    for s in report_pages.SPECS:
        html = client.get(reporttypes.TYPES[s.slug].path).text
        assert 'class="rp-chart"><svg' in html and report_pages.ART[s.slug]["facts"][0]["value"] in html
        assert (static / f"sample-{s.slug}-p2.webp").exists()
    for page in ("/", "/reports", "/reports/frozen-pipes"):
        html = client.get(page).text
        assert 'class="rt-credit"' in html and "Skakerman" in html
    for slug in report_pages.PHOTOS:
        assert (static / f"photo-{slug}.webp").exists()


def test_charts_survive_empty_data():
    from datetime import timezone as tz
    from wxreport import charts
    t = datetime(2024, 1, 15, 14, tzinfo=tz.utc)
    assert charts.hail([], "America/Chicago", str) is None
    assert charts.hour_columns([timeline.Hour(t)], t, "America/Chicago", "accident") is None
    assert charts.temperature([timeline.Hour(t)], "America/Chicago") is None
    warm = [timeline.Hour(t + timedelta(hours=i), reports=1, temp_f=70.0 + i) for i in range(4)]
    assert "32°F" in charts.temperature(warm, "America/Chicago").svg()     # freezing stays in view
    big = [{"t": t, "size": 4.5, "dist": 9.0, "what": "Ground report"}]
    fig = charts.hail(big, "America/Chicago", lambda v: "ball")
    assert "4.5 in, 9.0 mi away" in fig.svg() and fig.drawing(500).width == 500


def test_warnings_look_back_past_the_date():
    """A warning issued days before the date is still in force on it."""
    from wxreport.sources import nws
    from wxreport.timewin import local_day
    from datetime import date

    class Snap:
        params = None

        def fetch_json(self, name, url, params=None, **kw):
            if name == "iem_vtec_bypoint":
                self.params = params
                return {"events": [{"issue": "2023-01-30T15:00:00Z", "expire": "2023-02-02T16:00:00Z", "wfo": "EWX",
                                    "phenomena": "WS", "significance": "W", "eventid": 1, "name": "Winter Storm Warning",
                                    "ugc": "TXZ192"}]}
            return {}
    snap = Snap()
    found, _ = nws.collect_warnings(snap, 30.26, -97.74, local_day(date(2023, 2, 1), "America/Chicago"))
    assert [w.name for w in found] == ["Winter Storm Warning"] and snap.params["sdate"] <= "2023-01-30"


@pytest.mark.parametrize("slug", [s for s in reporttypes.TYPES if s != reporttypes.DEFAULT])
def test_a_short_report_leaves_out_the_rest(slug, monkeypatch):
    from wxreport import sections
    ctx = replace(gather(ADDR, DAY, root=FIXTURES, offline=True), kind=reporttypes.TYPES[slug],
                  event_utc=datetime(2026, 2, 19, 13, 0, tzinfo=timezone.utc))
    for part in ("stations", "warnings", "lsrs", "storm_events", "hail_lightning", "appendices", "findings", "sources"):
        monkeypatch.setattr(sections, part, lambda c: pytest.fail(f"{part} is in a short report"))
    assert build_pdf(ctx)[:4] == b"%PDF"
    assert reporttypes.TYPES[slug].short and not reporttypes.TYPES[reporttypes.DEFAULT].short


def test_marked_hail_rows_are_always_listed():
    from wxreport import focus
    records = [{"t": T0, "what": "Radar estimate", "size": 2.0 + i / 10, "dist": 9.0, "where": "", "detail": ""} for i in range(20)]
    records.append({"t": T0, "what": "Radar estimate", "size": 0.75, "dist": 0.8, "where": "", "detail": ""})
    big, close = focus._key_hail(records)
    assert close["dist"] == 0.8 and big is close   # the only record within 5 miles
    assert focus._key_hail([]) == (None, None)

    class Ctx:
        pass
    ctx = Ctx()
    focus_records = focus._hail_records
    focus._hail_records = lambda c: records
    try:
        assert close in focus._shown_hail(ctx)
    finally:
        focus._hail_records = focus_records


def test_a_badge_fits_inside_a_row():
    from wxreport.pdf import Badge, STYLES
    assert Badge.HEIGHT <= STYLES["tiny"].leading
    assert Badge("Largest, closest").wrap(58, 100) == (58, Badge.HEIGHT)
