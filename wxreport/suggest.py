"""Address autocomplete for the order form, proxied so buyers' browsers never call a third party directly.

Suggestions come from Photon (OpenStreetMap data, https://photon.komoot.io). They only help the buyer find the
place: the report itself uses the US Census Geocoder, or the exact map pin the buyer confirms.
"""
import time
from functools import lru_cache

import requests

PHOTON = "https://photon.komoot.io/api/"
USER_AGENT = "weatherevidence.com order form"
_TTL = 3600


def _label(p: dict) -> str | None:
    street = " ".join(x for x in (p.get("housenumber"), p.get("street") or p.get("name")) if x)
    city = p.get("city") or p.get("town") or p.get("village") or p.get("county")
    tail = " ".join(x for x in (p.get("state"), p.get("postcode")) if x)
    parts = [x for x in (street, city, tail) if x]
    return ", ".join(parts) if len(parts) >= 2 else None


@lru_cache(maxsize=2048)
def _cached(q: str, bucket: int) -> tuple:
    r = requests.get(PHOTON, params={"q": q, "limit": 10, "lang": "en", "lat": 39.5, "lon": -98.35},
                     headers={"User-Agent": USER_AGENT}, timeout=4)
    r.raise_for_status()
    seen, out = set(), []
    for f in r.json().get("features", []):
        p = f.get("properties", {})
        if p.get("countrycode", "").upper() != "US":
            continue
        label = _label(p)
        if not label or label in seen:
            continue
        seen.add(label)
        lon, lat = f["geometry"]["coordinates"]
        exact = bool(p.get("housenumber"))
        out.append({"label": label, "lat": round(lat, 6), "lon": round(lon, 6), "exact": exact})
        if len(out) == 6:
            break
    return tuple(out)


def suggest(q: str) -> list[dict]:
    q = " ".join(q.split())[:120]
    if len(q) < 3:
        return []
    try:
        return list(_cached(q.lower(), int(time.time() // _TTL)))
    except (requests.RequestException, ValueError, KeyError):
        return []
