"""Trim a real snapshot into a small test fixture, keeping only what the report for that site/date uses.

    .venv/bin/python scripts/make_fixture.py <snapshot dir> <fixture root>
"""
import csv
import gzip
import io
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wxreport.geo import distance_mi  # noqa: E402
from wxreport.snapshot import Snapshot  # noqa: E402

src, root = Path(sys.argv[1]), Path(sys.argv[2])
m = json.loads((src / "manifest.json").read_text())
req = m["request"]
census = json.loads(gzip.decompress((src / m["sources"]["census_address"]["file"]).read_bytes()))
c = census["result"]["addressMatches"][0]["coordinates"]
lat, lon = c["y"], c["x"]
day = req["date"]
out = Snapshot.open(req, root=root)


def body(name):
    e = m["sources"][name]
    return gzip.decompress((src / e["file"]).read_bytes())


for name, e in sorted(m["sources"].items()):
    if e["status"] != "ok":
        out.sources[name] = e
        continue
    b = body(name)
    if name == "ghcnh_station_list":
        lines = b.decode().splitlines()
        keep = [lines[0]] + [ln for ln in lines[1:] if ln.startswith("US") and
                             distance_mi(lat, lon, float(ln.split(",")[1]), float(ln.split(",")[2])) < 80]
        b = ("\n".join(keep) + "\n").encode()
    elif name.startswith("ghcnh_"):
        lines = b.decode().splitlines(keepends=True)
        days = {(date.fromisoformat(day) + timedelta(days=k)).isoformat() for k in (-1, 0, 1)}
        b = "".join([lines[0]] + [ln for ln in lines[1:] if ln.split("|")[2][:10] in days]).encode()
    elif name.startswith("stormevents_details"):
        rows = list(csv.DictReader(io.StringIO(gzip.decompress(b).decode("latin-1"))))
        keep = [r for r in rows if r["STATE_FIPS"].zfill(2) == "18"] + [max(rows, key=lambda r: r["BEGIN_YEARMONTH"])]
        s = io.StringIO()
        w = csv.DictWriter(s, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(keep)
        b = gzip.compress(s.getvalue().encode("latin-1"), mtime=0)
    elif name == "iem_lsr":
        g = json.loads(b)
        g["features"] = [f for f in g["features"]
                         if distance_mi(lat, lon, float(f["properties"]["lat"]), float(f["properties"]["lon"])) < 40]
        b = json.dumps(g).encode()
    elif name.startswith("nldn_tiles"):
        t = gzip.decompress(b).decode().splitlines()
        d0 = date.fromisoformat(day)
        utc_days = {(d0 + timedelta(days=k)).strftime("%Y%m%d") for k in (0, 1)}
        data = [ln for ln in t if ln[:1].isdigit()]
        keep = [ln for ln in t if ln.startswith("#") or ln[:8] in utc_days]
        keep.append(max(data))  # keep the latest day so "published through" logic still sees it
        b = gzip.compress(("\n".join(keep) + "\n").encode(), mtime=0)
    out.put(name, b, url=e["url"], params=e.get("params"), retrieved_at=e["retrieved_at"])
out.freeze()
print(out.path, sum(f.stat().st_size for f in out.path.iterdir()) // 1024, "KB")
