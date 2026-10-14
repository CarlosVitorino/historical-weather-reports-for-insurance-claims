"""NOAA Severe Weather Data Inventory: NEXRAD radar hail signatures and NLDN lightning tile counts.

* Hail: NEXRAD Level-III hail detections (nx3hail) — radar-estimated maximum hail size per storm cell,
  every volume scan. A radar estimate aloft, not a ground observation.
* Lightning: point-level NLDN strike data is licensed by Vaisala and not public. NCEI publishes daily
  counts of strikes per 0.1° grid cell (~6–7 miles) per UTC day; that is what is reported here.
"""
import csv
import gzip
import io
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ..geo import bearing_deg, compass, distance_mi
from ..snapshot import Snapshot, SourceUnavailable
from ..timewin import LocalDay

SWDI = "https://www.ncei.noaa.gov/swdiws/csv"
TILES = "https://www.ncei.noaa.gov/pub/data/swdi/database-csv/v2/nldn-tiles-{ym}.csv.gz"
HAIL_RADIUS_MI = 15.0
LIGHTNING_RADIUS_MI = 15.0


@dataclass
class HailDetection:
    time: datetime
    radar: str
    cell: str
    prob: int | None          # probability of hail, %
    severe_prob: int | None   # probability of severe hail, %
    max_size_in: float | None
    lat: float
    lon: float
    distance_mi: float
    bearing: float

    @property
    def proximity(self) -> str:
        return f"{self.distance_mi:.1f} mi {compass(self.bearing)}"


@dataclass
class LightningTile:
    utc_day: str               # YYYYMMDD
    lat: float
    lon: float
    count: int
    distance_mi: float
    bearing: float
    contains_site: bool

    @property
    def proximity(self) -> str:
        return "contains the site" if self.contains_site else f"{self.distance_mi:.1f} mi {compass(self.bearing)}"


def _int(s):
    try:
        v = int(float(s))
        return None if v == -999 else v
    except (TypeError, ValueError):
        return None


def collect_hail(snap: Snapshot, lat: float, lon: float, window: LocalDay):
    d0 = window.start_utc.strftime("%Y%m%d")
    d1 = (window.end_utc + timedelta(days=1)).strftime("%Y%m%d")
    pad_lat, pad_lon = 0.3, 0.4
    bbox = f"{lon - pad_lon:.3f},{lat - pad_lat:.3f},{lon + pad_lon:.3f},{lat + pad_lat:.3f}"
    try:
        text = snap.fetch("swdi_nx3hail", f"{SWDI}/nx3hail/{d0}:{d1}", {"bbox": bbox}).decode()
    except SourceUnavailable as e:
        return [], f"NEXRAD hail detections unavailable: {e}"
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        try:
            t = datetime.strptime(r["ZTIME"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            hlat, hlon = float(r["LAT"]), float(r["LON"])
        except (KeyError, ValueError):
            continue   # trailing summary lines
        if not (window.start_utc <= t < window.end_utc):
            continue
        d = distance_mi(lat, lon, hlat, hlon)
        if d > HAIL_RADIUS_MI:
            continue
        size = r.get("MAXSIZE")
        size_f = None if size in (None, "", "-999") else float(size)
        out.append(HailDetection(t, r["WSR_ID"], r["CELL_ID"], _int(r["PROB"]), _int(r["SEVPROB"]), size_f,
                                 hlat, hlon, d, bearing_deg(lat, lon, hlat, hlon)))
    out.sort(key=lambda h: (h.time, h.radar, h.cell))
    return out, None


def collect_lightning(snap: Snapshot, lat: float, lon: float, window: LocalDay):
    """Tiles within the radius for every UTC day the local day touches (one or two days)."""
    days, t = [], window.start_utc
    while t < window.end_utc:
        days.append(t.strftime("%Y%m%d"))
        t = (t + timedelta(days=1)).replace(hour=0, minute=0)
    out, notes = [], []
    for ym in sorted({d[:6] for d in days}):
        try:
            body = snap.fetch(f"nldn_tiles_{ym}", TILES.format(ym=ym), missing_ok=True)
        except SourceUnavailable as e:
            notes.append(f"Lightning tiles for {ym[:4]}-{ym[4:]} unavailable: {e}")
            continue
        if body is None:
            notes.append(f"NCEI has not published lightning tiles for {ym[:4]}-{ym[4:]} yet.")
            continue
        text = gzip.decompress(body).decode("utf-8", "replace")
        latest = max((ln.split(",", 1)[0] for ln in text.splitlines() if ln[:1].isdigit()), default="")
        for d in (d for d in days if d[:6] == ym and d > latest):
            notes.append(f"Lightning tiles for {d[:4]}-{d[4:6]}-{d[6:]} (UTC) are not yet in the published file.")
        for row in csv.reader(io.StringIO(text)):
            if not row or not row[0][:1].isdigit() or row[0] not in days:
                continue
            tlon, tlat, n = float(row[1]), float(row[2]), int(row[3])
            d = distance_mi(lat, lon, tlat, tlon)
            if d > LIGHTNING_RADIUS_MI:
                continue
            inside = abs(tlat - lat) <= 0.05 and abs(tlon - lon) <= 0.05
            out.append(LightningTile(row[0], tlat, tlon, n, d, bearing_deg(lat, lon, tlat, tlon), inside))
    out.sort(key=lambda x: (x.utc_day, x.distance_mi))
    return out, (" ".join(notes) or None)
