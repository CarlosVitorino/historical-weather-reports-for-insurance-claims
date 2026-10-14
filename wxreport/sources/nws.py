"""NWS warnings (VTEC events, full bulletin text) and Local Storm Reports.

Archived NWS products come from the Iowa Environmental Mesonet (Iowa State University), which archives
NWS text products verbatim; current zone identifiers come from api.weather.gov.
"""
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ..geo import bearing_deg, compass, distance_mi, distance_to_polygon_mi
from ..snapshot import Snapshot, SourceUnavailable
from ..timewin import LocalDay

IEM = "https://mesonet.agron.iastate.edu"
NWS_POINTS = "https://api.weather.gov/points/{lat:.4f},{lon:.4f}"
LSR_RADIUS_MI = 25.0


def _utc(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# -- zones ---------------------------------------------------------------------------------------
def zones(snap: Snapshot, lat: float, lon: float) -> tuple[list[str], str | None]:
    """NWS county and forecast zone codes for the point (e.g. INC105, INZ062) and the forecast office."""
    try:
        p = snap.fetch_json("nws_points", NWS_POINTS.format(lat=lat, lon=lon))["properties"]
    except (SourceUnavailable, KeyError, ValueError):
        return [], None
    codes = [p[k].rsplit("/", 1)[-1] for k in ("county", "forecastZone") if p.get(k)]
    return codes, p.get("cwa")


# -- warnings ------------------------------------------------------------------------------------
@dataclass
class Bulletin:
    kind: str                  # "Issued" | "Update"
    issued: datetime | None
    text: str
    polygon: list[tuple[float, float]] | None
    inside: bool | None
    distance_mi: float | None


@dataclass
class Warning:
    vtec_id: str               # e.g. 2026-KIND-TO-W-0008
    name: str                  # Tornado Warning
    wfo: str
    issue: datetime
    expire: datetime
    ugc: str                   # UGC that put the site in the event
    ugc_names: list[str]
    bulletins: list[Bulletin] = field(default_factory=list)

    @property
    def polygon_based(self) -> bool:
        return any(b.polygon for b in self.bulletins)

    @property
    def site_inside(self) -> bool | None:
        vals = [b.inside for b in self.bulletins if b.inside is not None]
        return any(vals) if vals else None

    @property
    def min_distance(self) -> float | None:
        vals = [b.distance_mi for b in self.bulletins if b.distance_mi is not None]
        return min(vals) if vals else None


_LATLON = re.compile(r"LAT\.\.\.LON((?:\s+\d{4,5}\s+\d{4,5})+)")


def parse_polygon(text: str) -> list[tuple[float, float]] | None:
    m = _LATLON.search(text)
    if not m:
        return None
    nums = [int(n) for n in m.group(1).split()]
    return [(nums[i] / 100.0, -nums[i + 1] / 100.0) for i in range(0, len(nums) - 1, 2)]


def _product_time(text: str, near: datetime) -> datetime:
    """Issue time from the WMO header ("WFUS53 KIND 192339" = day 19, 23:39 UTC), resolved to the
    month closest to the event's issue time."""
    m = re.search(r"^\w{6} \w{4} (\d{2})(\d{2})(\d{2})", text, re.M)
    if not m:
        return near
    d, hh, mm = (int(x) for x in m.groups())
    cands = []
    for shift in (-1, 0, 1):
        y, mo = divmod(near.year * 12 + near.month - 1 + shift, 12)
        try:
            cands.append(near.replace(year=y, month=mo + 1, day=d, hour=hh, minute=mm, second=0))
        except ValueError:
            pass
    return min(cands, key=lambda t: abs(t - near)) if cands else near


def collect_warnings(snap: Snapshot, lat: float, lon: float, window: LocalDay) -> tuple[list[Warning], str | None]:
    sd = (window.start_utc - timedelta(days=1)).date().isoformat()
    ed = (window.end_utc + timedelta(days=1)).date().isoformat()
    try:
        data = snap.fetch_json("iem_vtec_bypoint", f"{IEM}/json/vtec_events_bypoint.py",
                               {"lat": f"{lat:.4f}", "lon": f"{lon:.4f}", "sdate": sd, "edate": ed})
    except (SourceUnavailable, ValueError) as e:
        return [], f"NWS warning archive unavailable: {e}"
    out = []
    for ev in data.get("events", []):
        issue, expire = _utc(ev["issue"]), _utc(ev["expire"])
        if expire <= window.start_utc or issue >= window.end_utc:
            continue
        year = issue.year
        wfo4 = ev["wfo"] if len(ev["wfo"]) == 4 else ("P" if ev["wfo"] in ("GUM", "HFO", "PPG") else "K") + ev["wfo"]
        vtec_id = f"{year}-{wfo4}-{ev['phenomena']}-{ev['significance']}-{int(ev['eventid']):04d}"
        w = Warning(vtec_id, ev["name"], ev["wfo"], issue, expire, ev.get("ugc", ""), [])
        try:
            det = snap.fetch_json(f"iem_vtec_{vtec_id}", f"{IEM}/json/vtec_event.py",
                                  {"wfo": ev["wfo"], "year": year, "phenomena": ev["phenomena"],
                                   "significance": ev["significance"], "etn": ev["eventid"]})
            w.ugc_names = sorted({f"{u['name']} ({u['ugc']})" for u in det.get("ugcs", [])})
            prods = [("Issued", det.get("report") or {})] + [("Update", s) for s in det.get("svs") or []]
            for kind, prod in prods:
                text = (prod.get("text") or "").replace("\r", "").strip()
                if not text:
                    continue
                poly = parse_polygon(text)
                dist = distance_to_polygon_mi(lat, lon, poly) if poly else None
                w.bulletins.append(Bulletin(kind, _product_time(text, issue), text, poly,
                                            None if poly is None else dist == 0.0, dist))
        except (SourceUnavailable, ValueError, KeyError):
            pass  # event still listed; the report says bulletin text was unavailable
        out.append(w)
    out.sort(key=lambda w: (w.issue, w.vtec_id))
    return out, None


# -- local storm reports -------------------------------------------------------------------------
@dataclass
class LSR:
    time: datetime
    type: str
    magnitude: str
    qualifier: str
    city: str
    county: str
    state: str
    source: str
    remark: str
    product_id: str
    wfo: str
    lat: float
    lon: float
    distance_mi: float
    bearing: float

    @property
    def proximity(self) -> str:
        return "at the site" if self.distance_mi < 0.05 else f"{self.distance_mi:.1f} mi {compass(self.bearing)}"


QUALIFIER = {"M": "measured", "E": "estimated", "U": "unknown"}
LSR_TYPES = {"TSTM WND GST": "Thunderstorm wind gust", "TSTM WND DMG": "Thunderstorm wind damage",
             "NON-TSTM WND GST": "Non-thunderstorm wind gust", "NON-TSTM WND DMG": "Non-thunderstorm wind damage",
             "FLASH FLOOD": "Flash flood", "HEAVY RAIN": "Heavy rain", "FUNNEL CLOUD": "Funnel cloud",
             "MARINE TSTM WIND": "Marine thunderstorm wind"}


def collect_lsrs(snap: Snapshot, lat: float, lon: float, window: LocalDay) -> tuple[list[LSR], str | None]:
    try:
        data = snap.fetch_json("iem_lsr", f"{IEM}/geojson/lsr.php",
                               {"sts": window.start_utc.strftime("%Y%m%d%H%M"),
                                "ets": window.end_utc.strftime("%Y%m%d%H%M")})
    except (SourceUnavailable, ValueError) as e:
        return [], f"Local Storm Report archive unavailable: {e}"
    out = []
    for f in data.get("features", []):
        p = f["properties"]
        try:
            plat, plon = float(p["lat"]), float(p["lon"])
        except (TypeError, ValueError, KeyError):
            continue
        d = distance_mi(lat, lon, plat, plon)
        if d > LSR_RADIUS_MI:
            continue
        mag = p.get("magnitude") or ""
        if mag and p.get("unit"):
            mag = f"{mag} {p['unit'].lower()}"
        typetext = (p.get("typetext") or "").upper()
        out.append(LSR(_utc(p["valid"]), LSR_TYPES.get(typetext, typetext.capitalize()), mag,
                       QUALIFIER.get(p.get("qualifier") or "", ""), p.get("city") or "", p.get("county") or "",
                       p.get("st") or p.get("state") or "", p.get("source") or "", (p.get("remark") or "").strip().strip("."),
                       p.get("product_id") or "", p.get("wfo") or "", plat, plon, d, bearing_deg(lat, lon, plat, plon)))
    out.sort(key=lambda r: (r.time, r.distance_mi, r.product_id))
    return out, None

