"""Page-1 area map: the property and every nearby record, on a muted USGS basemap.

The basemap is USGS The National Map (public domain). Its tiles are fetched while the report's data is
gathered and stored in the snapshot like every other source, so the map is reproducible byte-for-byte.
If tiles can't be fetched, the records are drawn on a plain background and the map says so.
Records are drawn as vectors on top (crisp at any zoom).
"""
import io
from dataclasses import dataclass, field
from math import ceil, cos, log, log2, pi, radians, tan

from .snapshot import Snapshot, SourceUnavailable

TILE_URL = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}"
ATTRIBUTION = "Basemap: USGS The National Map"
MAP_W_PT, MAP_H_PT = 504.0, 324.0        # 7.0 × 4.5 in on the page
TARGET_PX = 1100                         # basemap pixels across the map (≈160 dpi)
MAX_ZOOM = 16


def _world(lat: float, lon: float, z: int) -> tuple[float, float]:
    n = 256 * 2 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1 - log(tan(radians(lat)) + 1 / cos(radians(lat))) / pi) / 2 * n
    return x, y


@dataclass
class Extent:
    lat: float
    lon: float
    radius_mi: float
    ring_step: float
    zoom: int
    x0: float
    y0: float
    x1: float
    y1: float
    basemap: object = None               # PIL image, or None
    note: str | None = None
    tiles: list = field(default_factory=list)

    def to_pt(self, lat: float, lon: float, w: float = MAP_W_PT, h: float = MAP_H_PT) -> tuple[float, float]:
        x, y = _world(lat, lon, self.zoom)
        return (x - self.x0) / (self.x1 - self.x0) * w, h - (y - self.y0) / (self.y1 - self.y0) * h

    def pt_per_mile(self, w: float = MAP_W_PT) -> float:
        mpp = 156543.03392 * cos(radians(self.lat)) / 2 ** self.zoom
        return w / ((self.x1 - self.x0) * mpp / 1609.344)


def plan(lat: float, lon: float, nearest_station_mi: float | None) -> Extent:
    """Show at least 4 miles around the property and enough to include the nearest weather station."""
    r = max(4.0, min(15.0, ceil((nearest_station_mi or 4.0) * 1.25)))
    step = 1.0 if r <= 4 else 2.0 if r <= 8 else 5.0
    aspect = MAP_W_PT / MAP_H_PT
    half_w_m, half_h_m = r * aspect * 1609.344, r * 1609.344
    mpp_target = 2 * half_w_m / TARGET_PX
    z = int(min(MAX_ZOOM, max(6, round(log2(156543.03392 * cos(radians(lat)) / mpp_target)))))
    mpp = 156543.03392 * cos(radians(lat)) / 2 ** z
    cx, cy = _world(lat, lon, z)
    return Extent(lat, lon, r, step, z, cx - half_w_m / mpp, cy - half_h_m / mpp, cx + half_w_m / mpp,
                  cy + half_h_m / mpp)


def collect(snap: Snapshot, ext: Extent) -> Extent:
    """Fetch the basemap tiles into the snapshot and compose a muted image. Never raises."""
    from PIL import Image, ImageOps
    tx0, ty0, tx1, ty1 = int(ext.x0 // 256), int(ext.y0 // 256), int(ext.x1 // 256), int(ext.y1 // 256)
    w, h = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256
    mosaic = Image.new("RGB", (w, h), (243, 245, 247))
    missing = 0
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            name = f"basemap_z{ext.zoom}_{tx}_{ty}"
            ext.tiles.append(name)
            try:
                body = snap.fetch(name, TILE_URL.format(z=ext.zoom, x=tx, y=ty), timeout=30)
                tile = Image.open(io.BytesIO(body)).convert("RGB")
                mosaic.paste(tile, ((tx - tx0) * 256, (ty - ty0) * 256))
            except (SourceUnavailable, OSError, ValueError):
                missing += 1
    if missing == len(ext.tiles):
        ext.note = "Basemap unavailable when this report was made; records are shown without it."
        return ext
    if missing:
        ext.note = f"{missing} basemap tile(s) were unavailable and appear blank."
    crop = mosaic.crop((round(ext.x0 - tx0 * 256), round(ext.y0 - ty0 * 256),
                        round(ext.x1 - tx0 * 256), round(ext.y1 - ty0 * 256)))
    target = (TARGET_PX, round(TARGET_PX * MAP_H_PT / MAP_W_PT))
    crop = crop.resize(target, Image.LANCZOS)
    gray = ImageOps.grayscale(crop).convert("RGB")
    ext.basemap = Image.blend(gray, Image.new("RGB", target, (255, 255, 255)), 0.45)   # muted, so records stand out
    return ext
