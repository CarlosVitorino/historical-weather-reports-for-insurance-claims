"""Distance and bearing from the loss site — every record in the report is placed relative to it."""
from math import asin, atan2, cos, degrees, radians, sin, sqrt

EARTH_RADIUS_MI = 3958.7613
COMPASS_16 = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
              "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def distance_mi(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle (haversine) distance in statute miles."""
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = p2 - p1, radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_MI * asin(sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial bearing from point 1 to point 2, degrees clockwise from true north, in [0, 360)."""
    p1, p2 = radians(lat1), radians(lat2)
    dl = radians(lon2 - lon1)
    x = sin(dl) * cos(p2)
    y = cos(p1) * sin(p2) - sin(p1) * cos(p2) * cos(dl)
    return (degrees(atan2(x, y)) + 360.0) % 360.0


def compass(bearing: float) -> str:
    return COMPASS_16[int((bearing % 360) / 22.5 + 0.5) % 16]


def proximity(site_lat: float, site_lon: float, lat: float, lon: float) -> str:
    """Human-readable position of a record relative to the loss site, e.g. '4.6 mi SSW'."""
    d = distance_mi(site_lat, site_lon, lat, lon)
    if d < 0.05:
        return "at the site"
    return f"{d:.1f} mi {compass(bearing_deg(site_lat, site_lon, lat, lon))}"
