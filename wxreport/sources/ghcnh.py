"""Station-pinned measurements from NOAA GHCNh (Global Historical Climatology Network – hourly).

Every value in the report names the one station that measured it. Nothing is blended or interpolated.
Units in the source are metric (°C, m/s, mm, km); conversion happens only at display time.
"""
import csv
import io
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from ..geo import bearing_deg, compass, distance_mi
from ..snapshot import Snapshot, SourceUnavailable
from ..timewin import LocalDay

BASE = "https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly"
STATION_LIST = f"{BASE}/doc/ghcnh-station-list.csv"
MAX_STATIONS = 4          # stations reported
MAX_CANDIDATES = 8        # nearest stations tried before giving up
MAX_RADIUS_MI = 60.0

ELEMENTS = ["temperature", "dew_point_temperature", "relative_humidity", "wind_direction", "wind_speed",
            "wind_gust", "precipitation", "visibility", "sea_level_pressure", "snow_depth"]
# Quality codes that mean "passed" (GHCNh documentation, Table 3). Anything else is printed as a flag.
PASS_QC = {"", "0", "1", "4", "5", "9"}

WX_CODES = {
    "TS": "thunderstorm", "VCTS": "thunderstorm in vicinity", "RA": "rain", "DZ": "drizzle", "SN": "snow",
    "GR": "hail", "GS": "small hail / snow pellets", "PL": "ice pellets", "SG": "snow grains",
    "UP": "unknown precipitation", "FZRA": "freezing rain", "FZDZ": "freezing drizzle", "FG": "fog",
    "FZFG": "freezing fog", "BR": "mist", "HZ": "haze", "FU": "smoke", "DU": "dust", "SA": "sand",
    "SQ": "squall", "FC": "funnel cloud", "+FC": "tornado / waterspout", "SH": "showers", "BLSN": "blowing snow",
}
_WX_TOKEN = re.compile(r"^(\+|-|VC)?(MI|PR|BC|DR|BL|SH|TS|FZ)?((?:DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|"
                       r"PY|PO|SQ|FC|SS|DS)+)?$")
# Remarks meaning the precipitation sensor or amount was not available (FMH-1): sensor not operating,
# hourly amount missing, 3/6-hour amount missing.
PRECIP_MISSING = ("PNO", "P////", "6////")
_PK_WND = re.compile(r"PK WND (\d{3})(\d{2,3})/(\d{2})?(\d{2})")


@dataclass
class Station:
    id: str
    name: str
    lat: float
    lon: float
    elev_m: float | None
    state: str
    icao: str
    distance_mi: float
    bearing: float

    @property
    def proximity(self) -> str:
        return f"{self.distance_mi:.1f} mi {compass(self.bearing)}"


@dataclass
class Obs:
    t: datetime                 # UTC
    report_type: str            # FM15 routine METAR, FM16 special, …
    values: dict                # element → float | None (metric)
    codes: dict                 # element → measurement code
    qc: dict                    # element → quality code (only non-passing kept)
    weather: list[str]          # decoded present-weather phrases
    wx_raw: list[str]           # present-weather tokens as reported
    metar: str                  # raw report text (REM)
    peak_wind: tuple | None     # (direction°, speed kt, UTC time) from "PK WND" remark
    source: str = ""            # GHCNh data source code (343 METAR, 345 USCRN, 382 HPD, …)

    @property
    def flags(self) -> list[str]:
        return [f"{k}:{v}" for k, v in self.qc.items()]


@dataclass
class StationDay:
    station: Station
    obs: list[Obs]
    status: str = "ok"                       # ok | no_data | unavailable
    note: str = ""
    source_names: list[str] = field(default_factory=list)
    edge: list[Obs] = field(default_factory=list)   # obs plus the hour after the day (hour-ending totals)

    @property
    def network(self) -> str:
        if any(o.report_type in ("FM15", "FM16") for o in self.obs):
            return "ASOS/AWOS airport station (METAR)"
        if any(o.source == "345" for o in self.obs):
            return "US Climate Reference Network (USCRN)"
        if any(o.source == "382" for o in self.obs):
            return "Hourly precipitation gauge (NOAA HPD)"
        return "Other network"

    @property
    def has_wind(self) -> bool:
        return any(o.values.get("wind_speed") is not None for o in self.obs)

    @property
    def log_obs(self) -> list[Obs]:
        """Rows for the printed log: every METAR/SPECI, or top-of-hour rows for 5-minute networks."""
        if any(o.report_type in ("FM15", "FM16") for o in self.obs):
            return self.obs
        return [o for o in self.obs if o.t.minute == 0]

    # -- derived summaries (metric) ----------------------------------------------------------
    def _vals(self, el):
        return [(o.t, o.values[el]) for o in self.obs if o.values.get(el) is not None]

    def max_of(self, el):
        v = self._vals(el)
        return max(v, key=lambda x: x[1]) if v else None

    def min_of(self, el):
        v = self._vals(el)
        return min(v, key=lambda x: x[1]) if v else None

    def peak_gust(self):
        """Highest gust from the gust field or a 'PK WND' remark, as (UTC time, m/s, origin)."""
        cands = [(t, v, "gust") for t, v in self._vals("wind_gust")]
        for o in self.obs:
            if o.peak_wind:
                cands.append((o.peak_wind[2], o.peak_wind[1] * 0.514444, "PK WND remark"))
        return max(cands, key=lambda x: (x[1], -x[0].timestamp())) if cands else None

    def routine_reports(self):
        return [o for o in self.obs if o.report_type == "FM15"]

    def precipitation(self, day: LocalDay):
        """Liquid precipitation total (mm) from METAR hourly periods ending inside the local day.

        METAR precipitation is a running total since the last routine (FM15) report, so each routine
        report closes one period; SPECIs inside a period carry the running total. A period with no
        routine report, or whose report says the sensor was not operating (PNO), is missing — not zero.
        Returns (total_mm, periods_counted, periods_missing, trace).
        """
        routine = sorted(self.routine_reports(), key=lambda o: o.t)
        if not routine:
            return self._hourly_precipitation(day)
        minute = Counter(o.t.minute for o in routine).most_common(1)[0][0]
        # Expected period ends: every hour at the station's routine minute inside the day.
        first = day.start_utc.replace(minute=minute, second=0)
        if first < day.start_utc:
            first += timedelta(hours=1)
        ends, t = [], first
        while t < day.end_utc:
            ends.append(t)
            t += timedelta(hours=1)
        total, counted, missing, trace = 0.0, 0, 0, False
        for end in ends:
            rep = next((o for o in routine if abs((o.t - end).total_seconds()) <= 600), None)
            rmk = rep.metar.split("RMK")[-1] if rep else ""
            if rep is None or any(m in rmk for m in PRECIP_MISSING):
                # No routine report: use a SPECI in the period only if one carries the running total.
                inside = [o for o in self.obs if end - timedelta(hours=1) < o.t <= end
                          and o.values.get("precipitation") is not None]
                if rep is None and inside:
                    total += inside[-1].values["precipitation"]
                    counted += 1
                else:
                    missing += 1
                continue
            v = rep.values.get("precipitation")
            if rep.codes.get("precipitation") in ("T", "2"):
                trace = True
            total += v or 0.0
            counted += 1
        return total, counted, missing, trace

    def _hourly_precipitation(self, day: LocalDay):
        """Networks that publish hour-ending totals at :00 (USCRN, HPD): sum the hours ending in the day."""
        hourly = {o.t: o for o in self.edge if o.t.minute == 0 and day.start_utc < o.t <= day.end_utc
                  and o.values.get("precipitation") is not None}
        if not hourly:
            return None
        total = sum(o.values["precipitation"] for o in hourly.values())
        trace = any(o.codes.get("precipitation") == "T" for o in hourly.values())
        return total, len(hourly), max(0, day.hours - len(hourly)), trace


def _f(s: str):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def decode_weather(metar: str) -> tuple[list[str], list[str]]:
    body = metar.split(" RMK")[0]
    tokens, phrases = [], []
    for tok in body.split()[3:]:
        if tok in ("AUTO", "COR", "CLR", "SKC", "CAVOK", "NSW") or re.match(r"^\d", tok):
            continue
        m = _WX_TOKEN.match(tok)
        if not m or not (m.group(2) or m.group(3)):
            continue
        tokens.append(tok)
        intensity, desc, phen = m.group(1) or "", m.group(2) or "", m.group(3) or ""
        if tok in WX_CODES:
            phrases.append(WX_CODES[tok])
            continue
        if f"{intensity}{phen}" == "+FC":
            phrases.append(WX_CODES["+FC"])
            continue
        parts = []
        if intensity == "+":
            parts.append("heavy")
        elif intensity == "-":
            parts.append("light")
        if desc == "TS":
            parts.append("thunderstorm with")
        elif desc == "FZ":
            parts.append("freezing")
        elif desc == "SH":
            parts.append("showers of")
        elif desc == "BL":
            parts.append("blowing")
        names = [WX_CODES.get(phen[i:i + 2], phen[i:i + 2]) for i in range(0, len(phen), 2)]
        parts.append(" and ".join(names) if names else "")
        if intensity == "VC":
            parts.append("in vicinity")
        phrases.append(" ".join(p for p in parts if p).replace("thunderstorm with ", "thunderstorm with ")
                       .strip() or tok)
    return phrases, tokens


def _peak_wind(metar: str, t: datetime):
    m = _PK_WND.search(metar)
    if not m:
        return None
    d, spd, hh, mm = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4))
    hour = int(hh) if hh else t.hour
    pt = t.replace(hour=hour, minute=mm, second=0)
    if pt > t:
        pt -= timedelta(hours=1 if not hh else 24)
    return (d, spd, pt)


def parse_psv(text: str, window: LocalDay, after: timedelta = timedelta(hours=1)) -> list[Obs]:
    """Rows from the start of the local day to `after` past its end (hour-ending totals need the extra hour)."""
    out = []
    for row in csv.DictReader(io.StringIO(text), delimiter="|"):
        t = datetime.fromisoformat(row["DATE"]).replace(tzinfo=timezone.utc)
        if not (window.start_utc <= t <= window.end_utc + after):
            continue
        values = {el: _f(row.get(el)) for el in ELEMENTS}
        # REM carries an archive prefix ("MET101" = METAR record, 101 chars) before the report itself.
        metar = re.sub(r"^MET\d{3}", "", (row.get("REM") or "").strip())
        rtype = next((row.get(f"{el}_Report_Type") for el in ELEMENTS if row.get(f"{el}_Report_Type")), "")
        if not metar and all(v is None for v in values.values()):
            continue  # empty 5-minute placeholder rows
        if not rtype and metar:
            rtype = "FM16" if "SPECI" in metar[:12] else ("FM15" if "METAR" in metar[:12] else "")
        codes = {el: row.get(f"{el}_Measurement_Code", "") for el in ELEMENTS}
        qc = {el: row.get(f"{el}_Quality_Code", "") for el in ELEMENTS
              if values[el] is not None and row.get(f"{el}_Quality_Code", "") not in PASS_QC}
        phrases, tokens = decode_weather(metar) if metar else ([], [])
        src = next((row.get(f"{el}_Source_Code") for el in ELEMENTS if row.get(f"{el}_Source_Code")), "")
        out.append(Obs(t, rtype, values, codes, qc, phrases, tokens, metar, _peak_wind(metar, t), src))
    out.sort(key=lambda o: o.t)
    return out


def nearest_stations(snap: Snapshot, lat: float, lon: float) -> list[Station]:
    text = snap.fetch("ghcnh_station_list", STATION_LIST).decode("utf-8", "replace")
    found = []
    for row in csv.DictReader(io.StringIO(text)):
        if not row["GHCN_ID"].startswith("US"):
            continue
        slat, slon = _f(row["LATITUDE"]), _f(row["LONGITUDE"])
        if slat is None or slon is None or abs(slat - lat) > 1.5 or abs(slon - lon) > 2.0:
            continue
        d = distance_mi(lat, lon, slat, slon)
        if d <= MAX_RADIUS_MI:
            found.append(Station(row["GHCN_ID"], row["NAME"].strip(), slat, slon, _f(row["ELEVATION"]),
                                 row["STATE"], row["ICAO"], d, bearing_deg(lat, lon, slat, slon)))
    found.sort(key=lambda s: (s.distance_mi, s.id))
    return found


def collect(snap: Snapshot, lat: float, lon: float, window: LocalDay) -> tuple[list[StationDay], str | None]:
    """Up to MAX_STATIONS nearest stations that actually reported during the local day."""
    try:
        cands = nearest_stations(snap, lat, lon)
    except SourceUnavailable as e:
        return [], f"GHCNh station inventory unavailable: {e}"
    years = sorted({window.start_utc.year, (window.end_utc - timedelta(seconds=1)).year})
    days: list[StationDay] = []
    for st in cands[:MAX_CANDIDATES]:
        obs, names, failed = [], [], False
        for y in years:
            name = f"ghcnh_{st.id}_{y}"
            try:
                body = snap.fetch(name, f"{BASE}/access/by-year/{y}/psv/GHCNh_{st.id}_{y}.psv", missing_ok=True)
            except SourceUnavailable:
                failed = True
                continue
            names.append(name)
            if body:
                obs += parse_psv(body.decode("utf-8", "replace"), window)
        edge = sorted(obs, key=lambda o: o.t)
        in_day = [o for o in edge if o.t < window.end_utc]
        if in_day:
            days.append(StationDay(st, in_day, source_names=names, edge=edge))
        elif failed:
            days.append(StationDay(st, [], "unavailable", "Station file could not be retrieved.", names))
        if sum(1 for d in days if d.status == "ok") >= MAX_STATIONS:
            break
    if not cands:
        return [], f"No GHCNh station within {MAX_RADIUS_MI:.0f} miles."
    return days, None
