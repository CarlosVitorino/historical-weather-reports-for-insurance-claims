"""Local-date windows. A loss date is a local calendar day; a day can be 23, 24 or 25 hours long."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class LocalDay:
    day: date
    tz_name: str
    start_utc: datetime
    end_utc: datetime  # exclusive

    @property
    def hours(self) -> int:
        return int((self.end_utc - self.start_utc).total_seconds() // 3600)

    def to_local(self, t: datetime) -> datetime:
        return t.astimezone(ZoneInfo(self.tz_name))


@lru_cache(maxsize=1)
def _finder():
    from timezonefinder import TimezoneFinder
    return TimezoneFinder()


def timezone_for(lat: float, lon: float) -> str:
    tz = _finder().timezone_at(lat=lat, lng=lon)
    if tz is None:
        raise ValueError(f"No timezone found for {lat}, {lon}")
    return tz


def local_day(day: date, tz_name: str) -> LocalDay:
    tz = ZoneInfo(tz_name)
    start = datetime.combine(day, time(0), tzinfo=tz).astimezone(timezone.utc)
    end = datetime.combine(day + timedelta(days=1), time(0), tzinfo=tz).astimezone(timezone.utc)
    return LocalDay(day, tz_name, start, end)


def fmt_local(t: datetime, tz_name: str, with_date: bool = False) -> str:
    """'6:57 PM EST' or 'Feb 19, 2026, 6:57 PM EST' — always with the zone abbreviation, so DST is explicit."""
    lt = t.astimezone(ZoneInfo(tz_name))
    s = lt.strftime("%I:%M %p %Z").lstrip("0")
    if with_date:
        s = f"{lt.strftime('%b')} {lt.day}, {lt.year}, {s}"
    return s
