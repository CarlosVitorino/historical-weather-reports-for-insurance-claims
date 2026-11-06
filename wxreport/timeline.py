"""One station's hours around a date, and what they add up to: pure functions over GHCNh observations.

Figures are for the air at the station. They are never estimates for the location, and a missing hour stays missing.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from . import units
from .sources.ghcnh import Obs

FREEZING_F = 32.0
_WET = ("rain", "drizzle", "snow", "ice pellets", "hail", "precipitation", "showers")


@dataclass
class Hour:
    t: datetime                         # UTC, start of the hour
    reports: int = 0
    temp_f: float | None = None
    vis_mi: float | None = None         # lowest in the hour
    gust_mph: float | None = None       # highest in the hour
    precip_mm: float | None = None      # hour-ending total of the routine report
    trace: bool = False
    weather: list[str] = field(default_factory=list)
    snow_depth_in: float | None = None

    @property
    def precipitating(self) -> list[str]:
        return [w for w in self.weather if any(x in w for x in _WET) and "blowing" not in w]

    @property
    def icy(self) -> bool:
        return any("freezing" in w or "snow" in w or "ice" in w for w in self.precipitating)


def hours(obs: list[Obs], start: datetime, end: datetime) -> list[Hour]:
    """Every hour from start to end, including hours with no report at all."""
    t = start.replace(minute=0, second=0, microsecond=0)
    out = {}
    while t < end:
        out[t] = Hour(t)
        t += timedelta(hours=1)
    grouped: dict[datetime, list[Obs]] = {}
    for o in obs:
        key = o.t.replace(minute=0, second=0, microsecond=0)
        if key in out:
            grouped.setdefault(key, []).append(o)
    for key, group in grouped.items():
        h, routine = out[key], [o for o in group if o.report_type == "FM15"]
        h.reports = len(group)
        rep = (routine or group)[-1]
        temps = [o.values.get("temperature") for o in [rep, *group] if o.values.get("temperature") is not None]
        h.temp_f = units.f(temps[0]) if temps else None
        vis = [o.values["visibility"] for o in group if o.values.get("visibility") is not None]
        h.vis_mi = units.mi(min(vis)) if vis else None
        gust = [o.values["wind_gust"] for o in group if o.values.get("wind_gust") is not None]
        h.gust_mph = units.mph(max(gust)) if gust else None
        if routine:
            h.precip_mm = rep.values.get("precipitation")
            h.trace = rep.codes.get("precipitation") in ("T", "2")
        depth = [o.values["snow_depth"] for o in group if o.values.get("snow_depth") is not None]
        h.snow_depth_in = units.inch(depth[-1]) if depth else None
        h.weather = list(dict.fromkeys(w for o in group for w in o.weather))
    return list(out.values())


def hour_at(hrs: list[Hour], t: datetime) -> Hour | None:
    key = t.replace(minute=0, second=0, microsecond=0)
    return next((h for h in hrs if h.t == key), None)


def at_or_below(hrs: list[Hour], f: float) -> int:
    return sum(1 for h in hrs if h.temp_f is not None and h.temp_f <= f)


def longest_run(hrs: list[Hour], f: float) -> int:
    """Longest unbroken run of hours at or below f. An hour with no reading ends the run, so this errs short."""
    best = run = 0
    for h in hrs:
        run = run + 1 if h.temp_f is not None and h.temp_f <= f else 0
        best = max(best, run)
    return best


def crossings(hrs: list[Hour]) -> int:
    """How many times the temperature passed through freezing, between readings."""
    temps = [h.temp_f for h in hrs if h.temp_f is not None]
    return sum(1 for a, b in zip(temps, temps[1:]) if (a <= FREEZING_F) != (b <= FREEZING_F))


def coldest(hrs: list[Hour]) -> Hour | None:
    known = [h for h in hrs if h.temp_f is not None]
    return min(known, key=lambda h: h.temp_f) if known else None


def last_precip(hrs: list[Hour]) -> Hour | None:
    return next((h for h in reversed(hrs) if h.precipitating or (h.precip_mm or 0) > 0), None)


def missing(hrs: list[Hour]) -> int:
    return sum(1 for h in hrs if not h.reports)
