"""Assemble one report: locate the site, gather sources into a snapshot, render the PDF."""
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from . import pdf
from .geocode import Location, locate
from .pdf import P, Spacer, esc, table
from .snapshot import DEFAULT_ROOT, Snapshot, report_id
from .timewin import LocalDay, fmt_local, local_day


class InvalidRequest(Exception):
    pass


@dataclass
class ReportContext:
    loc: Location
    day: LocalDay
    snap: Snapshot
    report_id: str


def _iso_to_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def gather(address: str, day_str: str, lat: float | None = None, lon: float | None = None,
           offline: bool = False, refresh: bool = False, root: Path = DEFAULT_ROOT, now: datetime | None = None) -> ReportContext:
    try:
        day = date.fromisoformat(day_str)
    except ValueError as e:
        raise InvalidRequest(f"Loss date must be YYYY-MM-DD, got {day_str!r}") from e
    if (lat is None) != (lon is None):
        raise InvalidRequest("Supply both latitude and longitude, or neither.")
    request = {"address": address.strip(), "date": day.isoformat(), "lat": lat, "lon": lon}
    snap = Snapshot.open(request, root=root, offline=offline, refresh=refresh)
    loc = locate(snap, request["address"], lat, lon)
    window = local_day(day, loc.tz)
    if not snap.frozen_at and window.end_utc > (now or datetime.now(timezone.utc)):
        raise InvalidRequest(f"{day} has not ended yet in {loc.tz}; reports cover completed past dates only.")
    # Source collectors are added here in Phase 3.
    snap.freeze()
    return ReportContext(loc, window, snap, report_id(day.isoformat(), snap))


def _cover(ctx: ReportContext) -> list:
    loc, day = ctx.loc, ctx.day
    place = loc.matched_address or loc.input_address
    gen = fmt_local(_iso_to_dt(ctx.snap.frozen_at), loc.tz, with_date=True)
    out = [P(pdf.PRODUCT, "title"),
           P(f"Report ID <b>{ctx.report_id}</b> · Data retrieved {esc(gen)}", "small"),
           Spacer(1, 14),
           P("Loss site and date", "h1"),
           P(esc(place), "big"),
           P(f"{day.day.strftime('%B')} {day.day.day}, {day.day.year} · local weather date "
             f"({day.hours} hours) · {esc(loc.tz)}", "body"),
           Spacer(1, 6),
           table([["Coordinates", f"{loc.lat:.5f}, {loc.lon:.5f}"],
                  ["County", f"{loc.county}, {loc.state}" if loc.county else "Not determined"],
                  ["Location method", "US Census Geocoder address match" if loc.method == "census"
                   else "Coordinates supplied by the requester; the address was not geocoded"],
                  ["Address as entered", loc.input_address],
                  ["Local day (UTC)", f"{day.start_utc:%Y-%m-%d %H:%M} to {day.end_utc:%Y-%m-%d %H:%M} UTC"]],
                 col_widths=[1.6 * pdf.inch, 5.2 * pdf.inch], header=False, zebra=False)]
    return out


def _sources(ctx: ReportContext) -> list:
    rows = [["Source", "Retrieved (UTC)", "Status", "SHA-256 (first 16)"]]
    for name in sorted(ctx.snap.sources):
        s = ctx.snap.sources[name]
        rows.append([name, s["retrieved_at"].replace("+00:00", "Z"),
                     "ok" if s["status"] == "ok" else "unavailable",
                     (s.get("sha256") or "")[:16]])
    return [Spacer(1, 18), P("Sources and retrieval", "h1"),
            P("Every source response used for this report is stored unmodified. The hashes below identify "
              "those exact bytes; the report ID is derived from them, so the same data always yields the same "
              "report and ID.", "body"), Spacer(1, 4),
            table(rows, col_widths=[2.2 * pdf.inch, 1.6 * pdf.inch, 0.9 * pdf.inch, 2.1 * pdf.inch]),
            Spacer(1, 10), P("What this report establishes", "h2"),
            P("This report compiles public US government weather records for the selected location and date. "
              "Nearby records do not by themselves establish conditions at the exact property. Missing values "
              "are not zero. It does not determine property damage, causation, insurance coverage or legal "
              "admissibility, and it is not a certified government record or expert opinion.", "body")]


def build_pdf(ctx: ReportContext) -> bytes:
    return pdf.render(_cover(ctx) + _sources(ctx), ctx.report_id,
                      title=f"{pdf.PRODUCT} {ctx.report_id}")


def generate(address: str, day_str: str, out_dir: Path = Path("reports"), **kw) -> tuple[Path, str]:
    ctx = gather(address, day_str, **kw)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ctx.report_id}.pdf"
    path.write_bytes(build_pdf(ctx))
    return path, ctx.report_id
