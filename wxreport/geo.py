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


def _xy(lat0: float, lon0: float, lat: float, lon: float) -> tuple[float, float]:
    """Local flat projection (miles) centred on lat0/lon0 — accurate to well under 1% within ~50 miles."""
    kx = 69.172 * cos(radians(lat0))
    return (lon - lon0) * kx, (lat - lat0) * 69.0


def nearest_on_segment(lat: float, lon: float, a: tuple[float, float], b: tuple[float, float]):
    """Closest point to (lat, lon) on the segment a→b, as (lat, lon). Used for tornado paths."""
    ax, ay = _xy(lat, lon, *a)
    bx, by = _xy(lat, lon, *b)
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L2))
    return a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])


def point_in_polygon(lat: float, lon: float, poly: list[tuple[float, float]]) -> bool:
    inside, n = False, len(poly)
    for i in range(n):
        (y1, x1), (y2, x2) = poly[i], poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def distance_to_polygon_mi(lat: float, lon: float, poly: list[tuple[float, float]]) -> float:
    """0 when inside; otherwise distance to the nearest edge."""
    if point_in_polygon(lat, lon, poly):
        return 0.0
    best = float("inf")
    for i in range(len(poly)):
        p = nearest_on_segment(lat, lon, poly[i], poly[(i + 1) % len(poly)])
        best = min(best, distance_mi(lat, lon, *p))
    return best
