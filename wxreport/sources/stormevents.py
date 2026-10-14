"""NCEI Storm Events Database — the reviewed, official record (published ~2–4 months after the month ends).

Delivered as per-year gzip CSVs whose filename carries the creation date (…_d2026_c20260918.csv.gz), so the
directory listing is part of the snapshot: it shows which edition was used and how far the year is covered.
"""
import csv
import gzip
import io
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ..geocode import STATE_FIPS as _STATE_ABBR
from ..geo import bearing_deg, compass, distance_mi, nearest_on_segment
from ..snapshot import Snapshot, SourceUnavailable
from ..timewin import LocalDay

LISTING = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
RADIUS_MI = 25.0
_FILE = re.compile(r'StormEvents_details-ftp_v1\.0_d(\d{4})_c(\d{8})\.csv\.gz')


@dataclass
class StormEvent:
    event_id: str
    episode_id: str
    event_type: str
    begin: datetime          # UTC
    end: datetime            # UTC
    tz_label: str            # as published, e.g. "EST-5"
    cz_name: str
    state: str
    wfo: str
    magnitude: str
    tor_scale: str
    tor_length_mi: str
    tor_width_yd: str
    damage_property: str
    source: str
    begin_loc: str
    begin_latlon: tuple | None
    end_latlon: tuple | None
    distance_mi: float | None   # nearest point of the event (path for tornadoes)
    bearing: float | None
    match: str                  # "radius" | "county" | "zone"
    narrative: str
    episode_narrative: str

    @property
    def proximity(self) -> str:
        if self.distance_mi is None:
            return f"{self.cz_name.title()} ({'county' if self.match == 'county' else 'forecast zone'})"
        if self.distance_mi < 0.05:
            return "at the site"
        return f"{self.distance_mi:.1f} mi {compass(self.bearing)}"


@dataclass
class StormEventsResult:
    status: str                 # ok | not_published | unavailable
    note: str
    events: list[StormEvent]
    edition: str | None = None  # file creation date YYYYMMDD
    covered_through: str | None = None   # latest YYYYMM present in the file


def _offset(tz_label: str) -> timedelta:
    m = re.search(r"([+-]\d+)$", tz_label or "")
    return timedelta(hours=int(m.group(1))) if m else timedelta(0)


def _dt(yearmonth: str, day: str, hhmm: str, tz_label: str) -> datetime:
    hhmm = hhmm.zfill(4)
    local = datetime(int(yearmonth[:4]), int(yearmonth[4:]), int(day), int(hhmm[:2]), int(hhmm[2:]))
    return (local - _offset(tz_label)).replace(tzinfo=timezone.utc)


def _latlon(lat: str, lon: str):
    try:
        return (float(lat), float(lon))
    except ValueError:
        return None


def collect(snap: Snapshot, lat: float, lon: float, window: LocalDay, county_fips: str | None,
            zones: list[str]) -> StormEventsResult:
    year = window.day.year
    try:
        listing = snap.fetch("stormevents_listing", LISTING).decode("utf-8", "replace")
    except SourceUnavailable as e:
        return StormEventsResult("unavailable", f"Storm Events file listing unavailable: {e}", [])
    files = sorted({(m.group(2), m.group(0)) for m in _FILE.finditer(listing) if m.group(1) == str(year)})
    if not files:
        return StormEventsResult("not_published", f"NCEI has not yet published a {year} Storm Events file.", [])
    edition, fname = files[-1]
    try:
        body = snap.fetch(f"stormevents_details_{year}", LISTING + fname)
    except SourceUnavailable as e:
        return StormEventsResult("unavailable", f"Storm Events file unavailable: {e}", [], edition)
    rows = list(csv.DictReader(io.StringIO(gzip.decompress(body).decode("latin-1"))))
    covered = max((r["BEGIN_YEARMONTH"] for r in rows), default=None)
    ym = f"{year}{window.day.month:02d}"
    if covered is None or ym > covered:
        return StormEventsResult(
            "not_published",
            f"The {year} Storm Events file (edition {edition}) covers events through "
            f"{covered[:4]}-{covered[4:]}; {window.day:%B %Y} has not been published yet. "
            "This means no reviewed record exists yet, not that no events occurred.", [], edition, covered)

    zone_keys = {(z[:2], z[3:]) for z in zones}   # ("IN", "062") from "INZ062"
    st_fips = county_fips[:2] if county_fips else None
    events = []
    for r in rows:
        tz = r["CZ_TIMEZONE"]
        try:
            begin = _dt(r["BEGIN_YEARMONTH"], r["BEGIN_DAY"], r["BEGIN_TIME"], tz)
            end = _dt(r["END_YEARMONTH"], r["END_DAY"], r["END_TIME"], tz)
        except ValueError:
            continue
        if end < window.start_utc or begin >= window.end_utc:
            continue
        a, b = _latlon(r["BEGIN_LAT"], r["BEGIN_LON"]), _latlon(r["END_LAT"], r["END_LON"])
        dist = brg = None
        match = None
        if a:
            p = nearest_on_segment(lat, lon, a, b or a)
            dist, brg = distance_mi(lat, lon, *p), bearing_deg(lat, lon, *p)
            if dist <= RADIUS_MI:
                match = "radius"
        if match is None and r["CZ_TYPE"] == "C" and county_fips and \
                r["STATE_FIPS"].zfill(2) == st_fips and r["CZ_FIPS"].zfill(3) == county_fips[2:]:
            match = "county"
        if match is None and r["CZ_TYPE"] == "Z" and zone_keys and \
                (_STATE_ABBR.get(r["STATE_FIPS"].zfill(2)), r["CZ_FIPS"].zfill(3)) in zone_keys:
            match = "zone"
        if match is None:
            continue
        events.append(StormEvent(
            r["EVENT_ID"], r["EPISODE_ID"], r["EVENT_TYPE"], begin, end, tz, r["CZ_NAME"], r["STATE"], r["WFO"],
            f"{r['MAGNITUDE']} {r['MAGNITUDE_TYPE']}".strip(), r["TOR_F_SCALE"], r["TOR_LENGTH"], r["TOR_WIDTH"],
            r["DAMAGE_PROPERTY"], r["SOURCE"],
            f"{r['BEGIN_RANGE']} {r['BEGIN_AZIMUTH']} {r['BEGIN_LOCATION']}".strip(), a, b,
            dist if match == "radius" else None, brg if match == "radius" else None, match,
            r["EVENT_NARRATIVE"], r["EPISODE_NARRATIVE"]))
    events.sort(key=lambda e: (e.begin, e.event_id))
    return StormEventsResult("ok", "", events, edition, covered)

