"""Storm Reports: US hail, thunderstorm-wind and tornado reports, and which cities get a public page.

Data is national; pages are not (docs/storm-reports-plan.md):
* A **city page** (every US city of 50,000+, wxreport/data/us_cities.csv) exists once the city has hail of 1 inch or
  more, or a tornado, within its radius (City.radius_mi) on or after PAGES_SINCE. It then shows its whole history.
* A storm day with hail of 2 inches or more, or a tornado, near a city is tagged a **major storm** on its page.

Two sources, one lifecycle:
* NWS Local Storm Reports via the Iowa Environmental Mesonet: minutes after a storm, labelled preliminary.
* NCEI Storm Events: the reviewed record, 2–4 months later. Once NCEI covers a month, its records replace that
  month's Local Storm Reports.

Everything lives in DATA_DIR/storms.db and can be rebuilt from the sources, so it is not backed up.
"""
import csv
import gzip
import hashlib
import io
import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .geo import bearing_deg, distance_mi
from .snapshot import _get
from .sources.nws import IEM
from .sources.stormevents import LISTING, _FILE, _dt

log = logging.getLogger("wxreport.storms")

PAGES_SINCE = date(2026, 10, 21)   # pages are created for storms from this day on (founder decision, 2026-10-30)
HISTORY_FROM = 2021                # a page shows reports from this year on
HAIL_MIN_IN = 1.0                  # "significant": hail of 1 inch or more (the NWS severe threshold) ...
WIND_MIN_MPH = 58                  # ... thunderstorm wind of 58 mph or more, or wind damage, or any tornado
MAJOR_HAIL_IN = 2.0                # a "major storm" tag: hail of 2 inches or more, or a tornado
# A report belongs to every listed city within that city's radius_mi of its centre (8 mi for most; more for sprawling
# cities, see scripts/make_cities.py). Centres are where people put them (Wikidata), not the Census internal point.
CITY_MIN_DAYS = 3                  # a city page is indexed once the city has this many storm days
KT_TO_MPH = 1.15078
CITIES_CSV = Path(__file__).parent / "data" / "us_cities.csv"


@dataclass(frozen=True)
class City:
    geoid: str
    name: str
    slug: str
    state: str          # "TX"
    state_name: str     # "Texas"
    population: int
    lat: float
    lon: float
    tz: str
    radius_mi: float

    @property
    def path(self) -> str:
        return f"/storm-reports/{self.state.lower()}/{self.slug}"

    @property
    def label(self) -> str:
        return f"{self.name}, {self.state}"


def load_cities(path: Path = CITIES_CSV) -> dict[str, City]:
    with path.open() as f:
        return {r["geoid"]: City(r["geoid"], r["name"], r["slug"], r["state"], r["state_name"], int(r["population"]),
                                 float(r["lat"]), float(r["lon"]), r["tz"], float(r["radius_mi"]))
                for r in csv.DictReader(f)}


CITIES = load_cities()
CITIES_VERSION = hashlib.sha256(CITIES_CSV.read_bytes()).hexdigest()[:12]   # reports are re-linked when it changes
_GRID: dict[tuple[int, int], list[City]] = {}
for _c in CITIES.values():
    _GRID.setdefault((round(_c.lat), round(_c.lon)), []).append(_c)


def cities_near(lat: float, lon: float) -> list[tuple[City, float, float]]:
    """Listed cities whose radius covers a point: (city, distance from the city centre, bearing from it).
    Grid cells are 1° (≈ 69 mi), so the 3×3 block around the point covers every radius (≤ 20 mi)."""
    out = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for c in _GRID.get((round(lat) + i, round(lon) + j), ()):
                d = distance_mi(c.lat, c.lon, lat, lon)
                if d <= c.radius_mi:
                    out.append((c, d, bearing_deg(c.lat, c.lon, lat, lon)))
    return out


def _near_rows(points) -> list[tuple]:
    """(report id, lat, lon) -> rows for the near table: one per listed city whose radius covers the report."""
    out = []
    for rid, lat, lon in points:
        if lat is not None and lon is not None:
            out += [(rid, city.geoid, round(d, 2), round(b, 1)) for city, d, b in cities_near(lat, lon)]
    return out


def significant(kind: str, magnitude: float | None, detail: str = "") -> bool:
    if kind == "tornado":
        return True
    if kind == "hail":
        return magnitude is not None and magnitude >= HAIL_MIN_IN
    return magnitude is None or magnitude >= WIND_MIN_MPH or detail == "damage"


def triggers_page(r: dict) -> bool:
    """What creates a city page: what people search for (hail and tornadoes), not every wind report."""
    return r["kind"] == "tornado" or (r["kind"] == "hail" and (r["magnitude"] or 0) >= HAIL_MIN_IN)


def is_major(r: dict) -> bool:
    return r["kind"] == "tornado" or (r["kind"] == "hail" and (r["magnitude"] or 0) >= MAJOR_HAIL_IN)


@dataclass
class Report:
    id: str
    time_utc: datetime
    kind: str               # hail | wind | tornado
    magnitude: float | None  # inches (hail), mph (wind); None for damage-only and tornado reports
    detail: str             # EF rating, "measured"/"estimated", "damage"
    place: str              # as published, e.g. "2 NW Godley"
    county: str
    state: str              # "TX"
    lat: float | None
    lon: float | None
    end_lat: float | None
    end_lon: float | None
    source: str             # ncei | lsr
    reporter: str
    remark: str
    episode: str
    episode_narrative: str
    significant: bool


SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY, time_utc TEXT NOT NULL, kind TEXT NOT NULL, magnitude REAL, detail TEXT, place TEXT,
    county TEXT, state TEXT, lat REAL, lon REAL, end_lat REAL, end_lon REAL, source TEXT NOT NULL, reporter TEXT,
    remark TEXT, episode TEXT, episode_narrative TEXT, significant INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS reports_time ON reports(source, time_utc);
CREATE TABLE IF NOT EXISTS near (               -- report within a listed city's radius
    report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    city TEXT NOT NULL, distance_mi REAL NOT NULL, bearing REAL NOT NULL,
    PRIMARY KEY (city, report_id)
);
CREATE INDEX IF NOT EXISTS near_report ON near(report_id);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

_COLS = ("id", "time_utc", "kind", "magnitude", "detail", "place", "county", "state", "lat", "lon", "end_lat",
         "end_lon", "source", "reporter", "remark", "episode", "episode_narrative", "significant")


def _iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class StormDB:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.Lock()
        with self._conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def _conn(self):
        with self._lock:
            c = sqlite3.connect(self.path)
            c.row_factory = sqlite3.Row
            c.execute("PRAGMA foreign_keys=ON")
            try:
                yield c
                c.commit()
            finally:
                c.close()

    def get_meta(self, key: str) -> str | None:
        with self._conn() as c:
            r = c.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return r["value"] if r else None

    def set_meta(self, key: str, value: str) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                      (key, value))

    def replace(self, sources: tuple, start: datetime, end: datetime, reports: list[Report]) -> None:
        """Delete `sources` reports with start <= time < end and insert `reports`, in one transaction."""
        with self._conn() as c:
            for s in sources:
                c.execute("DELETE FROM reports WHERE source=? AND time_utc >= ? AND time_utc < ?",
                          (s, _iso(start), _iso(end)))
            c.executemany(f"INSERT OR REPLACE INTO reports VALUES ({','.join('?' * len(_COLS))})",
                          [(r.id, _iso(r.time_utc), r.kind, r.magnitude, r.detail, r.place, r.county, r.state,
                            r.lat, r.lon, r.end_lat, r.end_lon, r.source, r.reporter, r.remark, r.episode,
                            r.episode_narrative, int(r.significant)) for r in reports])
            c.executemany("INSERT OR REPLACE INTO near VALUES (?,?,?,?)",
                          _near_rows((r.id, r.lat, r.lon) for r in reports))

    def relink(self) -> int:
        """Link every stored report to the cities around it again, after the city list (or a centre) changed."""
        with self._conn() as c:
            c.execute("DELETE FROM near")
            rows = c.execute("SELECT id, lat, lon FROM reports WHERE lat IS NOT NULL").fetchall()
            near = _near_rows((r["id"], r["lat"], r["lon"]) for r in rows)
            c.executemany("INSERT INTO near VALUES (?,?,?,?)", near)
            c.execute("INSERT INTO meta(key,value) VALUES('cities_version',?) "
                      "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (CITIES_VERSION,))
        return len(near)

    def ensure_linked(self) -> int | None:
        """Re-link if the reports were linked to a different city list. Returns the links made, or None."""
        if self.count() and self.get_meta("cities_version") != CITIES_VERSION:
            return self.relink()
        if not self.get_meta("cities_version"):
            self.set_meta("cities_version", CITIES_VERSION)
        return None

    # -- reads -----------------------------------------------------------------------------------
    def city_reports(self, geoid: str) -> list[dict]:
        """Every report near a city, with its distance and bearing from the city centre, oldest first."""
        with self._conn() as c:
            rows = c.execute("SELECT r.*, n.distance_mi, n.bearing FROM near n JOIN reports r ON r.id = n.report_id "
                             "WHERE n.city=? ORDER BY r.time_utc, r.id", (geoid,)).fetchall()
        return [dict(r) for r in rows]

    def trigger_reports(self, since: date) -> list[dict]:
        """Hail of 1 in+ and tornadoes near any listed city from `since` on (a day early: local days lag UTC)."""
        start = datetime.combine(since - timedelta(days=1), datetime.min.time(), timezone.utc)
        with self._conn() as c:
            rows = c.execute(
                "SELECT r.id, r.time_utc, r.kind, r.magnitude, n.city FROM near n JOIN reports r ON r.id = n.report_id "
                "WHERE r.time_utc >= ? AND (r.kind='tornado' OR (r.kind='hail' AND r.magnitude >= ?))",
                (_iso(start), HAIL_MIN_IN)).fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        with self._conn() as c:
            return c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]


# -- what has a page -------------------------------------------------------------------------------
def local_day(time_utc: str, tz: str) -> date:
    return datetime.fromisoformat(time_utc.replace("Z", "+00:00")).astimezone(ZoneInfo(tz)).date()


def live_cities(db: StormDB, since: date = PAGES_SINCE) -> dict[str, date]:
    """Cities with a page: geoid -> local day of their first hail of 1 in+ or tornado on or after `since`."""
    first: dict[str, date] = {}
    for r in db.trigger_reports(since):
        day = local_day(r["time_utc"], CITIES[r["city"]].tz)
        if day >= since and (r["city"] not in first or day < first[r["city"]]):
            first[r["city"]] = day
    return first


def storm_days(reports: list[dict], tz: str) -> list[dict]:
    """Group a city's reports by local day; keep days with a significant report. Newest first."""
    days: dict[date, list[dict]] = {}
    for r in reports:
        days.setdefault(local_day(r["time_utc"], tz), []).append(r)
    out = []
    for day, rs in days.items():
        if not any(r["significant"] for r in rs):
            continue
        hail = [r["magnitude"] for r in rs if r["kind"] == "hail" and r["magnitude"]]
        wind = [r["magnitude"] for r in rs if r["kind"] == "wind" and r["magnitude"]]
        out.append({"day": day, "reports": rs, "n": len(rs), "max_hail": max(hail, default=None),
                    "max_wind": max(wind, default=None), "n_tornado": sum(r["kind"] == "tornado" for r in rs),
                    "n_damage": sum(r["kind"] == "wind" and r["magnitude"] is None for r in rs),
                    "reviewed": all(r["source"] == "ncei" for r in rs), "trigger": any(triggers_page(r) for r in rs),
                    "major": any(is_major(r) for r in rs)})
    out.sort(key=lambda d: d["day"], reverse=True)
    return out


# -- NCEI Storm Events -----------------------------------------------------------------------------
NCEI_KINDS = {"Hail": "hail", "Thunderstorm Wind": "wind", "Tornado": "tornado"}
STATE_ABBR = {"ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR", "CALIFORNIA": "CA", "COLORADO": "CO",
              "CONNECTICUT": "CT", "DELAWARE": "DE", "DISTRICT OF COLUMBIA": "DC", "FLORIDA": "FL", "GEORGIA": "GA",
              "HAWAII": "HI", "IDAHO": "ID", "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS",
              "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD", "MASSACHUSETTS": "MA",
              "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS", "MISSOURI": "MO", "MONTANA": "MT",
              "NEBRASKA": "NE", "NEVADA": "NV", "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM",
              "NEW YORK": "NY", "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
              "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
              "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT", "VERMONT": "VT",
              "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV", "WISCONSIN": "WI", "WYOMING": "WY",
              "PUERTO RICO": "PR"}


def _num(s) -> float | None:
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def parse_ncei(text) -> tuple[list[Report], str | None]:
    """Hail, thunderstorm-wind and tornado rows of one yearly details file, and the latest month it covers.
    `text` is the CSV as a string or an open text stream; a stream is read row by row (a year is ~100 MB unpacked)."""
    out, covered = [], None
    for r in csv.DictReader(io.StringIO(text) if isinstance(text, str) else text):
        ym = r["BEGIN_YEARMONTH"]
        covered = max(covered or ym, ym)
        kind = NCEI_KINDS.get(r["EVENT_TYPE"])
        if kind is None:
            continue
        try:
            t = _dt(ym, r["BEGIN_DAY"], r["BEGIN_TIME"], r["CZ_TIMEZONE"])
        except ValueError:
            continue
        mag = _num(r["MAGNITUDE"])
        detail = ""
        if kind == "wind":
            mag = round(mag * KT_TO_MPH) if mag is not None else None
            detail = {"MG": "measured", "MS": "measured", "EG": "estimated", "ES": "estimated"}.get(
                r["MAGNITUDE_TYPE"], "")
        elif kind == "tornado":
            mag, detail = None, r["TOR_F_SCALE"]
        rng = r["BEGIN_RANGE"] if r["BEGIN_RANGE"] not in ("", "0", "0.0") else ""
        place = " ".join(x for x in (rng, r["BEGIN_AZIMUTH"] if rng else "", r["BEGIN_LOCATION"].title()) if x)
        out.append(Report(
            f"ncei:{r['EVENT_ID']}", t, kind, mag, detail, place, r["CZ_NAME"].title(),
            STATE_ABBR.get(r["STATE"], r["STATE"][:2]), _num(r["BEGIN_LAT"]), _num(r["BEGIN_LON"]),
            _num(r["END_LAT"]), _num(r["END_LON"]), "ncei", r["SOURCE"], r["EVENT_NARRATIVE"].strip(),
            r["EPISODE_ID"], r["EPISODE_NARRATIVE"].strip(),
            significant(kind, mag, detail) or kind == "wind"))   # every NCEI thunderstorm wind met severe criteria
    return out, covered


def ncei_files(listing: str) -> dict[int, tuple[str, str]]:
    """year -> (edition YYYYMMDD, filename), newest edition per year."""
    out = {}
    for m in _FILE.finditer(listing):
        y, ed = int(m.group(1)), m.group(2)
        if y not in out or ed > out[y][0]:
            out[y] = (ed, m.group(0))
    return out


def _after_month(ym: str) -> datetime:
    """Start of the month after YYYYMM, plus 12 h so Alaska–Hawaii local evenings stay inside the month."""
    y, m = int(ym[:4]), int(ym[4:])
    return datetime(y + (m == 12), m % 12 + 1, 1, 12, tzinfo=timezone.utc)


def sync_ncei(db: StormDB, force: bool = False) -> list[str]:
    """Load every yearly file whose edition is new. Returns what changed."""
    r = _get(LISTING, None, 60)
    r.raise_for_status()
    changed = []
    for year, (edition, fname) in sorted(ncei_files(r.text).items()):
        if year < HISTORY_FROM or (not force and db.get_meta(f"ncei_edition:{year}") == edition):
            continue
        body = _get(LISTING + fname, None, 300)
        body.raise_for_status()
        with gzip.open(io.BytesIO(body.content), "rt", encoding="utf-8", errors="replace", newline="") as rows:
            reports, covered = parse_ncei(rows)
        del body
        if covered is None:
            continue
        # Reviewed records replace everything (preliminary reports too) from Jan 1 through the month NCEI covers.
        db.replace(("ncei", "lsr"), datetime(year, 1, 1, tzinfo=timezone.utc) - timedelta(hours=12),
                   _after_month(covered), reports)
        db.set_meta(f"ncei_edition:{year}", edition)
        if covered > (db.get_meta("ncei_through") or ""):
            db.set_meta("ncei_through", covered)
        changed.append(f"{year}: edition {edition}, {len(reports)} reports through {covered}")
    return changed


# -- Local Storm Reports (IEM) ---------------------------------------------------------------------
LSR_KINDS = {"HAIL": "hail", "TSTM WND GST": "wind", "TSTM WND DMG": "wind", "TORNADO": "tornado"}


def parse_lsr(data: dict) -> list[Report]:
    out = []
    for f in data.get("features", []):
        p = f.get("properties") or {}
        typetext = (p.get("typetext") or "").upper()
        kind = LSR_KINDS.get(typetext)
        if kind is None:
            continue
        try:
            t = datetime.fromisoformat(p["valid"].replace("Z", "+00:00"))
            lat, lon = float(p["lat"]), float(p["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        mag = _num(p.get("magnitude"))
        detail = {"M": "measured", "E": "estimated"}.get(p.get("qualifier") or "", "")
        if typetext == "TSTM WND DMG":
            mag, detail = None, "damage"
        elif kind == "tornado":
            mag = None
        key = f"{p['valid']}|{lat:.3f}|{lon:.3f}|{typetext}|{p.get('magnitude')}|{p.get('city')}"
        out.append(Report(
            "lsr:" + hashlib.sha1(key.encode()).hexdigest()[:16], t, kind, mag, detail, (p.get("city") or "").strip(),
            (p.get("county") or "").strip(), p.get("st") or p.get("state") or "", lat, lon, None, None, "lsr",
            p.get("source") or "", (p.get("remark") or "").strip(), "", "", significant(kind, mag, detail)))
    return out


def sync_lsr(db: StormDB, start: datetime, end: datetime) -> int:
    """Local Storm Reports for start..end (UTC), skipping what NCEI has already reviewed."""
    through = db.get_meta("ncei_through")
    if through:
        start = max(start, _after_month(through))
    total = 0
    while start < end:
        stop = min(end, start + timedelta(days=10))
        r = _get(f"{IEM}/geojson/lsr.php", {"sts": start.strftime("%Y%m%d%H%M"), "ets": stop.strftime("%Y%m%d%H%M")},
                 180)
        r.raise_for_status()
        reports = [x for x in parse_lsr(r.json()) if start <= x.time_utc < stop]
        db.replace(("lsr",), start, stop, reports)
        total += len(reports)
        start = stop
    return total


# -- jobs ------------------------------------------------------------------------------------------
def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def backfill(db: StormDB) -> dict:
    """First load: every reviewed year, then preliminary reports from where NCEI stops to now."""
    ncei = sync_ncei(db, force=True)
    lsr = sync_lsr(db, datetime(HISTORY_FROM, 1, 1, tzinfo=timezone.utc), _now())
    db.set_meta("synced", _now().isoformat())
    return {"ncei": ncei, "lsr_reports": lsr}


def refresh(db: StormDB, days: int = 3) -> int:
    n = sync_lsr(db, _now() - timedelta(days=days), _now())
    db.set_meta("synced", _now().isoformat())
    return n


LSR_EVERY = 3600          # recent Local Storm Reports: hourly
NCEI_EVERY = 24 * 3600    # NCEI's file listing: daily


def start(db: StormDB) -> threading.Thread:
    """Keep the data current from inside the server process. A failed run retries at the next tick."""
    def loop():
        last_ncei = 0.0
        while True:
            try:
                linked = db.ensure_linked()
                if linked is not None:
                    log.info("storms: city list changed, %d report-city links rebuilt", linked)
                if db.get_meta("ncei_through") is None:
                    log.info("storms backfill: %s", backfill(db))
                    last_ncei = time.time()
                elif time.time() - last_ncei >= NCEI_EVERY:
                    log.info("storms ncei: %s", sync_ncei(db) or "no new edition")
                    last_ncei = time.time()
                log.info("storms lsr: %d reports in the last 3 days", refresh(db))
            except Exception:  # noqa: BLE001 — sources go down; the next tick retries
                log.exception("storms sync failed")
            time.sleep(LSR_EVERY)

    t = threading.Thread(target=loop, name="storms", daemon=True)
    t.start()
    return t
