"""Loss-site location via the US Census Geocoder (free, government, no key), or operator-supplied coordinates."""
from dataclasses import dataclass

from .snapshot import Snapshot, SourceUnavailable
from .timewin import timezone_for

CENSUS = "https://geocoding.geo.census.gov/geocoder"
BENCHMARK = "Public_AR_Current"
VINTAGE = "Current_Current"

STATE_FIPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
    "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
    "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
    "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY", "72": "PR",
}


class AddressNotFound(Exception):
    pass


@dataclass(frozen=True)
class Location:
    input_address: str
    matched_address: str | None
    lat: float
    lon: float
    tz: str
    county: str | None        # e.g. "Monroe County"
    state: str | None         # e.g. "IN"
    county_fips: str | None   # 5-digit GEOID, e.g. "18105"
    method: str               # "census" | "operator"


def _county(geos: dict) -> tuple[str | None, str | None, str | None]:
    counties = (geos or {}).get("Counties") or []
    if not counties:
        return None, None, None
    c = counties[0]
    return c.get("NAME"), STATE_FIPS.get(c.get("STATE")), c.get("GEOID")


def locate(snap: Snapshot, address: str, lat: float | None = None, lon: float | None = None) -> Location:
    params = {"benchmark": BENCHMARK, "vintage": VINTAGE, "layers": "Counties", "format": "json"}
    if lat is not None and lon is not None:
        try:
            data = snap.fetch_json("census_coordinates", f"{CENSUS}/geographies/coordinates",
                                   {**params, "x": f"{lon:.6f}", "y": f"{lat:.6f}"})
            county, state, fips = _county(data["result"].get("geographies"))
        except (SourceUnavailable, KeyError, ValueError):
            county = state = fips = None
        return Location(address, None, lat, lon, timezone_for(lat, lon), county, state, fips, "operator")

    data = snap.fetch_json("census_address", f"{CENSUS}/geographies/onelineaddress",
                           {**params, "address": address})
    matches = data.get("result", {}).get("addressMatches") or []
    if not matches:
        raise AddressNotFound(
            f"The Census Geocoder found no match for {address!r}. Check the address, or supply coordinates.")
    m = matches[0]
    mlat, mlon = float(m["coordinates"]["y"]), float(m["coordinates"]["x"])
    county, state, fips = _county(m.get("geographies"))
    return Location(address, m.get("matchedAddress"), mlat, mlon, timezone_for(mlat, mlon),
                    county, state, fips, "census")


def where(lat: float, lon: float) -> dict:
    """County and state for a point, straight from the Census service (no snapshot: used by the order form)."""
    import requests
    try:
        r = requests.get(f"{CENSUS}/geographies/coordinates", timeout=8,
                         params={"benchmark": BENCHMARK, "vintage": VINTAGE, "layers": "Counties", "format": "json",
                                 "x": f"{lon:.6f}", "y": f"{lat:.6f}"})
        r.raise_for_status()
        county, state, _ = _county(r.json()["result"].get("geographies"))
    except (requests.RequestException, ValueError, KeyError):
        return {"ok": False}
    return {"ok": True, "in_us": county is not None, "county": county, "state": state}


def _pretty(matched: str) -> str:
    """'5299 DTC BLVD, GREENWOOD VILLAGE, CO, 80111' → '5299 Dtc Blvd, Greenwood Village, CO 80111'."""
    parts = [p.strip() for p in matched.split(",")]
    if len(parts) >= 4:
        return f"{', '.join(p.title() for p in parts[:-2])}, {parts[-2].upper()} {parts[-1]}"
    return matched.title()


def find(q: str) -> dict | None:
    """Best Census match for free text (used live by the order form), or None."""
    import requests
    q = " ".join(q.split())[:200]
    if len(q) < 6:
        return None
    try:
        r = requests.get(f"{CENSUS}/locations/onelineaddress", timeout=8,
                         params={"address": q, "benchmark": BENCHMARK, "format": "json"})
        r.raise_for_status()
        m = (r.json().get("result") or {}).get("addressMatches") or []
    except (requests.RequestException, ValueError):
        return None
    if not m:
        return None
    c = m[0]["coordinates"]
    return {"label": _pretty(m[0]["matchedAddress"]), "lat": round(float(c["y"]), 6),
            "lon": round(float(c["x"]), 6), "source": "census"}
