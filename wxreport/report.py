"""Assemble one report: locate the site, gather every source into a snapshot, render the PDF."""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

from . import RENDER_VERSION
from .geocode import Location, locate
from .snapshot import DEFAULT_ROOT, Snapshot, report_id
from .sources import ghcnh, nws, stormevents, swdi
from .timewin import LocalDay, local_day


class InvalidRequest(Exception):
    pass


# NWS VTEC warnings and the IEM storm-report archive are complete from 2005; earlier dates would print
# gaps as if nothing happened.
MIN_DATE = date(2005, 1, 1)


@dataclass
class ReportContext:
    loc: Location
    day: LocalDay
    snap: Snapshot
    report_id: str = ""
    zones: list[str] = field(default_factory=list)
    wfo: str | None = None
    stations: list[ghcnh.StationDay] = field(default_factory=list)
    stations_note: str | None = None
    warnings: list[nws.Warning] = field(default_factory=list)
    warnings_note: str | None = None
    lsrs: list[nws.LSR] = field(default_factory=list)
    lsrs_note: str | None = None
    storm_events: stormevents.StormEventsResult | None = None
    hail: list[swdi.HailDetection] = field(default_factory=list)
    hail_note: str | None = None
    lightning: list[swdi.LightningTile] = field(default_factory=list)
    lightning_note: str | None = None

    @property
    def primary(self) -> ghcnh.StationDay | None:
        """Station for the observation log: the nearest airport (METAR) station unless another wind-measuring
        station is more than 5 miles closer; else the nearest that reported at all."""
        ok = [s for s in self.stations if s.status == "ok"]
        windy = [s for s in ok if s.has_wind]
        if not windy:
            return ok[0] if ok else None
        metar = [s for s in windy if "METAR" in s.network]
        if metar and metar[0].station.distance_mi <= windy[0].station.distance_mi + 5:
            return metar[0]
        return windy[0]


def gather(address: str, day_str: str, lat: float | None = None, lon: float | None = None,
           offline: bool = False, refresh: bool = False, root: Path = DEFAULT_ROOT,
           now: datetime | None = None) -> ReportContext:
    try:
        day = date.fromisoformat(day_str)
    except ValueError as e:
        raise InvalidRequest(f"Loss date must be YYYY-MM-DD, got {day_str!r}") from e
    if day < MIN_DATE:
        raise InvalidRequest(f"Reports cover loss dates from {MIN_DATE:%B %-d, %Y} onward.")
    if (lat is None) != (lon is None):
        raise InvalidRequest("Supply both latitude and longitude, or neither.")
    if not address.strip():
        raise InvalidRequest("An address is required.")
    request = {"address": address.strip(), "date": day.isoformat(), "lat": lat, "lon": lon}
    snap = Snapshot.open(request, root=root, offline=offline, refresh=refresh)
    loc = locate(snap, request["address"], lat, lon)
    if loc.method == "operator" and loc.county is None and \
            snap.sources.get("census_coordinates", {}).get("status") == "ok":
        raise InvalidRequest(f"{loc.lat}, {loc.lon} is not inside a US county; v1 covers US locations only.")
    window = local_day(day, loc.tz)
    if not snap.frozen_at and window.end_utc > (now or datetime.now(timezone.utc)):
        raise InvalidRequest(f"{day} has not ended yet in {loc.tz}; reports cover completed past dates only.")

    ctx = ReportContext(loc, window, snap)
    ctx.zones, ctx.wfo = nws.zones(snap, loc.lat, loc.lon)
    ctx.stations, ctx.stations_note = ghcnh.collect(snap, loc.lat, loc.lon, window)
    ctx.warnings, ctx.warnings_note = nws.collect_warnings(snap, loc.lat, loc.lon, window)
    ctx.lsrs, ctx.lsrs_note = nws.collect_lsrs(snap, loc.lat, loc.lon, window)
    ctx.storm_events = stormevents.collect(snap, loc.lat, loc.lon, window, loc.county_fips, ctx.zones)
    ctx.hail, ctx.hail_note = swdi.collect_hail(snap, loc.lat, loc.lon, window)
    ctx.lightning, ctx.lightning_note = swdi.collect_lightning(snap, loc.lat, loc.lon, window)
    snap.freeze()
    ctx.report_id = report_id(day.isoformat(), snap, RENDER_VERSION)
    return ctx


def build_pdf(ctx: ReportContext) -> bytes:
    from .sections import render_report
    return render_report(ctx)


def generate(address: str, day_str: str, out_dir: Path = Path("reports"), **kw) -> tuple[Path, str]:
    ctx = gather(address, day_str, **kw)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ctx.report_id}.pdf"
    path.write_bytes(build_pdf(ctx))
    return path, ctx.report_id
