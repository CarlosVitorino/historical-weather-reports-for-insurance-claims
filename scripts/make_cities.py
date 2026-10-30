"""Build wxreport/data/us_cities.csv: every US city of 50,000+ people, the places Storm Reports can have a page for.

Inputs, downloaded by hand:
  US Census Bureau (public domain): population and the place list
    https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/cities/totals/sub-est2024.csv
    https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_place_national.zip (unzipped)
  Wikidata (CC0): each city's coordinate, which is where people put the centre (downtown, city hall). The Census
  "internal point" is only somewhere inside the boundary: Phoenix's is 8.6 mi north of downtown, San Francisco's is
  offshore. Query https://query.wikidata.org with Accept: text/csv:
    SELECT ?item ?fips ?coord WHERE { ?item wdt:P774 ?fips ; wdt:P625 ?coord . }

  .venv/bin/python scripts/make_cities.py sub-est2024.csv 2024_Gaz_place_national.txt wikidata.csv
"""
import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

from timezonefinder import TimezoneFinder

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wxreport.geo import distance_mi  # noqa: E402

MIN_POP = 50_000
# A city's storms are the reports within this distance of its centre: the radius of a circle with the city's land area,
# plus 2 miles, so sprawling cities are covered (Phoenix, 518 sq mi: 15 mi) and compact ones keep 8 mi.
RADIUS_MIN_MI, RADIUS_MAX_MI, RADIUS_PAD_MI = 8.0, 20.0, 2.0
OUT = Path(__file__).resolve().parent.parent / "wxreport" / "data" / "us_cities.csv"

# Consolidated governments the Census names after the whole county; people search the city.
NAMES = {
    "Nashville-Davidson metropolitan government (balance)": "Nashville",
    "Louisville/Jefferson County metro government (balance)": "Louisville",
    "Lexington-Fayette urban county": "Lexington",
    "Augusta-Richmond County consolidated government (balance)": "Augusta",
    "Athens-Clarke County unified government (balance)": "Athens",
    "Macon-Bibb County": "Macon",
    "Columbus city": "Columbus",
    "San Buenaventura (Ventura) city": "Ventura",
    "Urban Honolulu CDP": "Honolulu",
    "Boise City city": "Boise",
}
SUFFIX = re.compile(r" (city|town|village|borough|municipality|CDP|city and borough|metropolitan government|"
                    r"consolidated government|unified government|urban county)( \(balance\))?$")


def clean(name: str) -> str:
    return NAMES.get(name) or SUFFIX.sub("", name.replace(" (balance)", "")).strip()


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("'", "")).strip("-")


def wikidata_points(path: str) -> dict[str, list[tuple[float, float]]]:
    """Census place code (state + place, 7 digits) -> Wikidata coordinates (some places have several items)."""
    out = defaultdict(list)
    for r in csv.DictReader(open(path, encoding="utf-8")):
        code, m = re.sub(r"\D", "", r["fips"]), re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", r["coord"])
        if m and len(code) == 7:
            out[code].append((float(m.group(2)), float(m.group(1))))
    return out


def main(pop_csv: str, gaz_txt: str, wikidata_csv: str) -> None:
    pop = {}
    for r in csv.DictReader(open(pop_csv, encoding="latin-1")):
        if r["SUMLEV"] == "162":
            pop[r["STATE"] + r["PLACE"]] = (int(r["POPESTIMATE2024"]), r["STNAME"])
    tf = TimezoneFinder()
    wd = wikidata_points(wikidata_csv)
    rows = []
    with open(gaz_txt, encoding="latin-1") as fh:
        rd = csv.reader(fh, delimiter="\t")
        head = [h.strip() for h in next(rd)]
        for raw in rd:
            g = dict(zip(head, (x.strip() for x in raw)))
            p, state_name = pop.get(g["GEOID"], (0, ""))
            if p < MIN_POP:
                continue
            lat, lon, centre = float(g["INTPTLAT"]), float(g["INTPTLONG"]), "census"
            if wd.get(g["GEOID"]):   # several items: the one nearest the Census point is the city, not a namesake
                lat, lon = min(wd[g["GEOID"]], key=lambda pt: distance_mi(lat, lon, *pt))
                centre = "wikidata"
            name = clean(g["NAME"])
            radius = math.sqrt(float(g["ALAND_SQMI"]) / math.pi) + RADIUS_PAD_MI
            rows.append({"geoid": g["GEOID"], "name": name, "slug": slug(name), "state": g["USPS"],
                         "state_name": state_name, "population": p, "lat": f"{lat:.5f}", "lon": f"{lon:.5f}",
                         "tz": tf.timezone_at(lat=lat, lng=lon), "centre": centre,
                         "radius_mi": round(min(max(radius, RADIUS_MIN_MI), RADIUS_MAX_MI))})
    rows.sort(key=lambda r: (r["state"], -r["population"]))
    keys = [(r["state"], r["slug"]) for r in rows]
    dups = {k for k in keys if keys.count(k) > 1}
    if dups:
        raise SystemExit(f"duplicate state/slug: {sorted(dups)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} cities ({sum(r['centre'] == 'wikidata' for r in rows)} centred on Wikidata) -> {OUT}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
