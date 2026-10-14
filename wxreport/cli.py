import argparse
import sys
from pathlib import Path

from .geocode import AddressNotFound
from .report import InvalidRequest, generate
from .snapshot import SourceUnavailable


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="wxreport", description="Historical loss-site weather report (PDF).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="Generate a report for one address and loss date.")
    r.add_argument("--address", required=True)
    r.add_argument("--date", required=True, help="Local loss date, YYYY-MM-DD")
    r.add_argument("--lat", type=float)
    r.add_argument("--lon", type=float)
    r.add_argument("--out", type=Path, default=Path("reports"))
    r.add_argument("--offline", action="store_true", help="Use only the stored snapshot; never fetch.")
    r.add_argument("--refresh", action="store_true", help="Discard the stored snapshot and re-retrieve all sources.")
    a = ap.parse_args(argv)
    try:
        path, rid = generate(a.address, a.date, out_dir=a.out, lat=a.lat, lon=a.lon,
                             offline=a.offline, refresh=a.refresh)
    except (InvalidRequest, AddressNotFound, SourceUnavailable) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"{rid}\n{path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
