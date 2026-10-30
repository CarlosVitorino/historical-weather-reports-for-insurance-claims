"""Storm Reports: parsing both sources, the preliminary → reviewed lifecycle, which cities and storms get a page,
and the public pages."""
import csv
import io
import re
from dataclasses import replace
from datetime import date, datetime, timezone

from fastapi.testclient import TestClient

from wxreport import config, storm_pages, storms, web
from wxreport.storms import StormDB

from test_seo import BANNED

NCEI_COLS = ["BEGIN_YEARMONTH", "BEGIN_DAY", "BEGIN_TIME", "EPISODE_ID", "EVENT_ID", "STATE", "CZ_NAME",
             "CZ_TIMEZONE", "EVENT_TYPE", "MAGNITUDE", "MAGNITUDE_TYPE", "TOR_F_SCALE", "BEGIN_RANGE",
             "BEGIN_AZIMUTH", "BEGIN_LOCATION", "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON", "SOURCE",
             "EVENT_NARRATIVE", "EPISODE_NARRATIVE"]
PLANO = (33.07, -96.77)          # 1.4 mi N of the Census centre point of Plano, TX
PHOENIX = (33.60, -112.10)
T0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
T1 = datetime(2030, 1, 1, tzinfo=timezone.utc)


def ncei_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, NCEI_COLS)
    w.writeheader()
    for r in rows:
        w.writerow({c: "" for c in NCEI_COLS} | r)
    return buf.getvalue()


def ncei_row(**kw) -> dict:
    base = dict(BEGIN_YEARMONTH="202605", BEGIN_DAY="2", BEGIN_TIME="2250", EPISODE_ID="9", EVENT_ID="100",
                STATE="TEXAS", CZ_NAME="COLLIN", CZ_TIMEZONE="CST-6", EVENT_TYPE="Hail", MAGNITUDE="1.75",
                BEGIN_RANGE="2", BEGIN_AZIMUTH="NW", BEGIN_LOCATION="PLANO", BEGIN_LAT=str(PLANO[0]),
                BEGIN_LON=str(PLANO[1]), SOURCE="Trained Spotter", EVENT_NARRATIVE="Golf ball hail.",
                EPISODE_NARRATIVE="Storms moved across North Texas.")
    return base | kw


def lsr(valid: str, at=PHOENIX, **kw) -> dict:
    p = dict(valid=valid, typetext="HAIL", magnitude="1.75", unit="INCH", qualifier="E", county="Maricopa", st="AZ",
             city="4 NE Glendale", source="Trained Spotter", remark="Golf ball hail.", lat=at[0], lon=at[1])
    return {"properties": p | kw}


def test_ncei_rows_are_converted():
    reports, covered = storms.parse_ncei(ncei_csv([
        ncei_row(),
        ncei_row(EVENT_ID="101", EVENT_TYPE="Thunderstorm Wind", MAGNITUDE="52", MAGNITUDE_TYPE="MG"),
        ncei_row(EVENT_ID="102", EVENT_TYPE="Flash Flood"),
        ncei_row(EVENT_ID="103", EVENT_TYPE="Tornado", MAGNITUDE="", TOR_F_SCALE="EF1", BEGIN_YEARMONTH="202606"),
    ]))
    assert covered == "202606"
    by_id = {r.id: r for r in reports}
    assert set(by_id) == {"ncei:100", "ncei:101", "ncei:103"}
    hail = by_id["ncei:100"]
    assert hail.time_utc == datetime(2026, 5, 3, 4, 50, tzinfo=timezone.utc)   # 22:50 CST
    assert (hail.state, hail.county, hail.place, hail.significant) == ("TX", "Collin", "2 NW Plano", True)
    assert by_id["ncei:101"].magnitude == 60 and by_id["ncei:101"].detail == "measured"   # 52 kt
    assert by_id["ncei:103"].detail == "EF1" and by_id["ncei:103"].magnitude is None


def test_lsr_parsing_and_significance():
    reports = storms.parse_lsr({"features": [
        lsr("2026-10-21T22:30:00Z"),
        lsr("2026-10-21T22:31:00Z", magnitude="0.75"),
        lsr("2026-10-21T22:32:00Z", typetext="TSTM WND DMG", magnitude=""),
        lsr("2026-10-21T22:33:00Z", typetext="TSTM WND GST", magnitude="45", unit="MPH"),
        lsr("2026-10-21T22:34:00Z", typetext="FLOOD"),
    ]})
    assert [(r.kind, r.magnitude, r.detail, r.significant) for r in reports] == [
        ("hail", 1.75, "estimated", True), ("hail", 0.75, "estimated", False), ("wind", None, "damage", True),
        ("wind", 45.0, "estimated", False)]


def test_reports_are_linked_to_nearby_cities(tmp_path):
    db = StormDB(tmp_path / "storms.db")
    db.replace(("lsr",), T0, T1, storms.parse_lsr({"features": [lsr("2026-10-21T22:30:00Z")]}))
    az = {c.name: c for c in storms.CITIES.values() if c.state == "AZ"}
    phoenix, glendale = db.city_reports(az["Phoenix"].geoid), db.city_reports(az["Glendale"].geoid)
    assert len(phoenix) == len(glendale) == 1 and phoenix[0]["id"] == glendale[0]["id"]   # one report, two cities
    assert phoenix[0]["distance_mi"] < az["Phoenix"].radius_mi and glendale[0]["distance_mi"] < az["Glendale"].radius_mi
    assert db.city_reports(az["Tucson"].geoid) == []


def test_reviewed_records_replace_preliminary(tmp_path):
    db = StormDB(tmp_path / "storms.db")
    db.replace(("lsr",), T0, T1, storms.parse_lsr({"features": [lsr("2026-05-03T04:00:00Z", at=PLANO)]}))
    reviewed, _ = storms.parse_ncei(ncei_csv([ncei_row()]))
    db.replace(("ncei", "lsr"), datetime(2026, 1, 1, tzinfo=timezone.utc), storms._after_month("202605"), reviewed)
    plano = next(c for c in storms.CITIES.values() if c.slug == "plano")
    assert [r["source"] for r in db.city_reports(plano.geoid)] == ["ncei"]


def test_which_cities_get_pages(tmp_path):
    db = StormDB(tmp_path / "storms.db")
    db.replace(("lsr",), T0, T1, storms.parse_lsr({"features": [
        lsr("2026-10-20T22:30:00Z"),                                        # Oct 20 in Arizona: before PAGES_SINCE
        lsr("2026-10-22T03:30:00Z", at=PLANO, magnitude="1.00", st="TX", county="Collin"),   # Oct 21 CDT
        lsr("2026-10-23T03:30:00Z", at=PLANO, typetext="TSTM WND GST", magnitude="70", st="TX"),  # wind: no page
        lsr("2026-10-25T22:30:00Z", magnitude="2.50"),                      # Phoenix
    ]}))
    live = {storms.CITIES[g].name: d for g, d in storms.live_cities(db, since=date(2026, 10, 21)).items()}
    assert live["Plano"] == date(2026, 10, 21) and live["Phoenix"] == date(2026, 10, 25)
    assert "Mesa" not in live


def test_storm_days_group_by_local_day():
    plano = next(c for c in storms.CITIES.values() if c.slug == "plano")
    rows = [dict(time_utc="2026-05-03T04:50:00Z", kind="hail", magnitude=1.75, significant=1, source="ncei"),
            dict(time_utc="2026-05-03T04:55:00Z", kind="wind", magnitude=None, significant=1, source="lsr"),
            dict(time_utc="2026-05-09T20:00:00Z", kind="hail", magnitude=0.75, significant=0, source="lsr")]
    days = storms.storm_days(rows, plano.tz)
    assert [d["day"] for d in days] == [date(2026, 5, 2)]   # May 9 had no significant report
    assert days[0]["max_hail"] == 1.75 and days[0]["n_damage"] == 1 and not days[0]["reviewed"]
    assert days[0]["trigger"] and not days[0]["major"]   # 1.75 in hail: a page, but not a major storm


def test_wording():
    assert storm_pages.place({"place": "3.12 NNE Cottondale", "county": "Wise"}) == "3.1 mi NNE of Cottondale"
    assert storm_pages.place({"place": ".58 E Cleburne Muni Arpt", "county": "Johnson"}) == \
        "0.6 mi E of Cleburne Muni Arpt"
    assert storm_pages.place({"place": "", "county": "Wise"}) == "Wise County"
    assert storm_pages.hail_name(1.75) == "golf ball" and storm_pages.hail_name(0.5) == ""
    assert storm_pages.summary({"n": 1, "max_wind": 49}) == "wind damage"   # NOAA's damage-estimated speed
    assert storm_pages.summary({"n": 3, "max_hail": 2.0, "n_tornado": 2, "max_wind": 70}) == \
        "2.00 in hail (hen egg) · 2 tornadoes · 70 mph wind"


def make_client(tmp_path):
    db = StormDB(tmp_path / "storms.db")
    reviewed, _ = storms.parse_ncei(ncei_csv([
        ncei_row(EVENT_ID="1", BEGIN_YEARMONTH="202204"), ncei_row(EVENT_ID="2", BEGIN_YEARMONTH="202305"),
        ncei_row(EVENT_ID="3", BEGIN_YEARMONTH="202406", MAGNITUDE="2.75")]))
    db.replace(("ncei",), T0, T1, reviewed)
    db.replace(("lsr",), datetime(2026, 10, 1, tzinfo=timezone.utc), T1, storms.parse_lsr({"features": [
        lsr("2026-10-22T03:30:00Z", at=PLANO, magnitude="2.00", st="TX", county="Collin", city="2 N Plano"),
        lsr("2026-10-25T22:30:00Z", magnitude="1.00")]}))
    db.set_meta("synced", "2026-10-30T11:00:00+00:00")
    cfg = replace(config.load(), base_url="https://reports.test", data_dir=tmp_path, storm_sync=False)
    return TestClient(web.create_app(cfg, storm_db=db))


def test_storm_pages(tmp_path):
    client = make_client(tmp_path)
    for path in ["/storm-reports", "/storm-reports/tx", "/storm-reports/tx/plano", "/storm-reports/az/phoenix"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert f'<link rel="canonical" href="https://reports.test{path}">' in r.text
        assert not BANNED.search(re.sub(r"<[^>]+>", " ", r.text)), path
        assert "not affiliated with NOAA" in r.text
    plano = client.get("/storm-reports/tx/plano").text
    assert "<title>Plano, TX hail storm history: 4 storm days since 2022 — Storm Reports</title>" in plano
    assert "The largest hail was 2.75 inches (baseball size) on June 2, 2024." in plano
    assert '<h2 id="storm-title">Wednesday, October 21, 2026</h2>' in plano and '<span class="sr-pill">Latest</span>' in plano
    assert 'href="/order?loss_date=2026-10-21"' in plano
    assert "Plano since 2022<span> · within 8 mi of the center</span>" in re.sub(r"\s+", " ", plano)   # city record
    # Oct 21, 2026 (2.00 in: latest-storm heading and history row) and Jun 2, 2024 (2.75 in)
    assert plano.count("Major storm") == 3
    assert 'Also hit that day: <a href="/storm-reports/tx/frisco">Frisco, TX</a>' in plano
    assert '<meta name="robots" content="index,follow">' in plano   # 4 storm days >= CITY_MIN_DAYS
    phoenix = client.get("/storm-reports/az/phoenix").text
    assert '<meta name="robots" content="noindex">' in phoenix      # 1 storm day: page, but not indexed
    for missing in ["/storm-reports/tx/dallas", "/storm-reports/tx/nowhere", "/storm-reports/co",
                    "/storm-reports/storms/2026-10-21-plano-tx"]:
        assert client.get(missing).status_code == 404, missing


def table(html: str) -> list[tuple[str, str]]:
    """(city link, date) for each table row, in order."""
    return re.findall(r'<td class="sr-cd" data-label="Date">\w+, (\w+ \d+, \d+)</td><td class="sr-cc" data-label="City">'
                      r'<a class="sr-rl" href="([^"]+)"', html)


def test_storm_table(tmp_path):
    client = make_client(tmp_path)
    index = client.get("/storm-reports").text                 # default: last 30 days, newest first, indexed
    rows = table(index)
    assert rows[0] == ("Oct 25, 2026", "/storm-reports/az/phoenix")   # the latest storm links to the plain page
    assert ("Oct 21, 2026", "/storm-reports/tx/plano") in rows and {d for d, _ in rows} == {"Oct 25, 2026",
                                                                                            "Oct 21, 2026"}
    assert '<meta name="robots" content="index,follow">' in index and "Preliminary" not in index
    assert '<option value="Plano, TX">' in index and "Clear filters" not in index

    everything = table(client.get("/storm-reports", params={"period": "all", "sort": "hail"}).text)
    plano = [href for _, href in everything if "/plano" in href]
    assert plano[0] == "/storm-reports/tx/plano?day=2024-06-02"       # 2.75 in, the largest, first
    assert len(plano) == 4

    major = table(client.get("/storm-reports", params={"period": "all", "kind": "major", "q": "plano"}).text)
    assert [href for _, href in major if "/plano" in href] == ["/storm-reports/tx/plano",
                                                                "/storm-reports/tx/plano?day=2024-06-02"]
    assert "No storm days match" in client.get("/storm-reports", params={"q": "nowhere"}).text
    filtered = client.get("/storm-reports", params={"period": "all"}).text
    assert '<meta name="robots" content="noindex">' in filtered and "Clear filters" in filtered

    r = client.get("/storm-reports", params={"state": "tx", "period": "all"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/storm-reports/tx?period=all"
    texas = client.get("/storm-reports/tx").text
    assert all(href.startswith("/storm-reports/tx/") for _, href in table(texas))
    assert "<h1>Texas hail storms by city</h1>" in texas
    weird = client.get("/storm-reports", params={"period": "bogus", "page": "x"})
    assert weird.status_code == 200 and "Last 30 days" in weird.text


def test_city_page_shows_any_storm_day(tmp_path):
    client = make_client(tmp_path)
    page = client.get("/storm-reports/tx/plano", params={"day": "2024-06-02"})
    assert page.status_code == 200 and '<h2 id="storm-title">Sunday, June 2, 2024</h2>' in page.text
    assert '<meta name="robots" content="noindex">' in page.text
    assert '<link rel="canonical" href="https://reports.test/storm-reports/tx/plano">' in page.text
    assert 'href="/order?loss_date=2024-06-02"' in page.text
    assert '<a class="sr-tolatest" href="/storm-reports/tx/plano#storm" data-day>Latest storm →</a>' in page.text
    assert '<a href="/storm-reports/tx/plano?day=2024-06-02#storm" data-day aria-current="true">' in page.text
    assert page.text.count('aria-current="true"') == 1
    r = client.get("/storm-reports/tx/plano", params={"day": "2019-01-01"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/storm-reports/tx/plano"


def test_narrative_text_is_cleaned():
    assert storm_pages.paragraphs("about 2\u00ef\u00bf\u00bd inches.||Second   paragraph.") == \
        ["about 2 inches.", "Second paragraph."]


def test_storm_sitemap(tmp_path):
    xml = make_client(tmp_path).get("/sitemap.xml").text
    assert "<loc>https://reports.test/storm-reports/tx/plano</loc><lastmod>2026-10-21</lastmod>" in xml
    assert "/storm-reports/az</loc>" in xml and "/storm-reports/az/phoenix" not in xml
    assert "/storm-reports/storms/" not in xml and "?period" not in xml
