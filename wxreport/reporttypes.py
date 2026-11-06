"""The kinds of report we sell, at one price. The default kind holds every record for an address and date. The others
are short: each answers one question, so it reads only the records that answer it (`reads`).

A kind with `before` or `after` also reads the nearest station's hours around the date (timeline.py). The default kind
adds nothing to a request, so its reports keep their IDs. Pages for each kind are in report_pages.py.
"""
import re
from dataclasses import dataclass
from datetime import timedelta

DEFAULT = "property"
EVERYTHING = frozenset({"stations", "warnings", "lsrs", "storm_events", "hail", "lightning", "map"})
_TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


@dataclass(frozen=True)
class ReportType:
    slug: str
    name: str                               # "Car hail damage"
    date_label: str = "Date of loss"
    place_label: str = "Property address"
    map_label: str = "Property"             # what the report's map calls the point
    time_label: str = ""                    # asked for only when set, and then required
    before: timedelta = timedelta(0)        # hours read before the moment (or the local day, with no time)
    after: timedelta = timedelta(0)
    reads: frozenset = EVERYTHING

    @property
    def short(self) -> bool:
        return self.reads != EVERYTHING

    @property
    def path(self) -> str:
        return "/" if self.slug == DEFAULT else f"/reports/{self.slug}"


TYPES = {t.slug: t for t in [
    ReportType(DEFAULT, "Property damage"),
    ReportType("car-hail-damage", "Car hail damage", date_label="Date of the hail",
               place_label="Where the car was parked", map_label="Location",
               reads=frozenset({"warnings", "lsrs", "hail"})),
    ReportType("car-accident", "Car accident", date_label="Date of the accident", time_label="Time of the accident",
               place_label="Where the accident happened", map_label="Location", before=timedelta(hours=3), after=timedelta(hours=3),
               reads=frozenset({"stations", "warnings"})),
    ReportType("slip-and-fall-on-ice", "Slip and fall on ice", date_label="Date of the fall",
               time_label="Time of the fall", place_label="Where the fall happened", map_label="Location", before=timedelta(hours=72), after=timedelta(hours=1),
               reads=frozenset({"stations", "warnings", "lsrs"})),
    ReportType("frozen-pipes", "Frozen pipes", date_label="Date you found the burst pipe", before=timedelta(days=7),
               reads=frozenset({"stations", "warnings"})),
]}


def get(slug: str | None) -> ReportType:
    return TYPES.get(slug or DEFAULT, TYPES[DEFAULT])


def valid_time(value: str | None) -> bool:
    return bool(value and _TIME.match(value))
