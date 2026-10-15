"""Address autocomplete for the order form, proxied so buyers' browsers never call a third party directly.

Providers (only to help the buyer find the place; the report itself uses the US Census Geocoder or the exact
map pin the buyer confirms):
* Geoapify, when GEOAPIFY_API_KEY is set: OpenStreetMap plus OpenAddresses, i.e. good US house-number coverage.
  Free tier 3,000 requests/day; results may be stored.
* Photon (https://photon.komoot.io) otherwise: free, no key, but only OpenStreetMap's patchy US house numbers.
"""
import logging
import os
import time
from functools import lru_cache

import requests

log = logging.getLogger("wxreport.suggest")
PHOTON = "https://photon.komoot.io/api/"
GEOAPIFY = "https://api.geoapify.com/v1/geocode/autocomplete"
USER_AGENT = "weatherevidence.com order form"
_TTL = 3600


def provider() -> str:
    return "geoapify" if os.environ.get("GEOAPIFY_API_KEY") else "photon"


def _photon_label(p: dict) -> str | None:
    street = " ".join(x for x in (p.get("housenumber"), p.get("street") or p.get("name")) if x)
    city = p.get("city") or p.get("town") or p.get("village") or p.get("county")
    tail = " ".join(x for x in (p.get("state"), p.get("postcode")) if x)
    parts = [x for x in (street, city, tail) if x]
    return ", ".join(parts) if len(parts) >= 2 else None


def _photon(q: str) -> list[dict]:
    r = requests.get(PHOTON, params={"q": q, "limit": 10, "lang": "en", "lat": 39.5, "lon": -98.35},
                     headers={"User-Agent": USER_AGENT}, timeout=4)
    r.raise_for_status()
    out = []
    for f in r.json().get("features", []):
        p = f.get("properties", {})
        if p.get("countrycode", "").upper() != "US":
            continue
        label = _photon_label(p)
        if label:
            lon, lat = f["geometry"]["coordinates"]
            out.append({"label": label, "lat": lat, "lon": lon, "exact": bool(p.get("housenumber"))})
    return out


def _geoapify(q: str) -> list[dict]:
    r = requests.get(GEOAPIFY, params={"text": q, "filter": "countrycode:us", "format": "json", "limit": 8,
                                       "lang": "en", "apiKey": os.environ["GEOAPIFY_API_KEY"]},
                     headers={"User-Agent": USER_AGENT}, timeout=4)
    r.raise_for_status()
    out = []
    for p in r.json().get("results", []):
        line2 = (p.get("address_line2") or "").replace(", United States of America", "").replace(", United States", "")
        label = ", ".join(x for x in (p.get("address_line1"), line2) if x) or p.get("formatted")
        if label and p.get("lat") is not None:
            exact = bool(p.get("housenumber")) or p.get("result_type") in ("building", "amenity")
            out.append({"label": label, "lat": p["lat"], "lon": p["lon"], "exact": exact})
    return out


@lru_cache(maxsize=2048)
def _cached(q: str, prov: str, bucket: int) -> tuple:
    rows = _geoapify(q) if prov == "geoapify" else _photon(q)
    seen, out = set(), []
    for row in rows:
        if row["label"] in seen:
            continue
        seen.add(row["label"])
        out.append({**row, "lat": round(row["lat"], 6), "lon": round(row["lon"], 6)})
        if len(out) == 6:
            break
    return tuple(out)


def suggest(q: str) -> list[dict]:
    q = " ".join(q.split())[:120]
    if len(q) < 3:
        return []
    prov = provider()
    try:
        return list(_cached(q.lower(), prov, int(time.time() // _TTL)))
    except (requests.RequestException, ValueError, KeyError) as e:
        log.warning("address suggestions failed (%s): %s", prov, e)
        return []
