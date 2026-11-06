"""Crop and tone the card photos so they read as one set: same shape, same navy grade as the site's maps.

    .venv/bin/python scripts/make_report_photos.py
      → wxreport/static/photo-<slug>.webp

Sources and licences are in wxreport/report_pages.py (PHOTOS), and shown wherever the photos appear.
"""
import io
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

OUT = Path(__file__).resolve().parents[1] / "wxreport/static"
SIZE = (800, 500)
# slug: (url, horizontal focus, vertical focus), focus 0 to 1 within the source
SOURCES = {
    "car-hail-damage": ("https://upload.wikimedia.org/wikipedia/commons/7/79/"
                        "FEMA_-_44376_-_truck_windshield_with_hail_damage_in_OK.jpg", .5, .45),
    "car-accident": ("https://upload.wikimedia.org/wikipedia/commons/2/2f/Police-car-snowy-road.jpg", .5, .55),
    "slip-and-fall-on-ice": ("https://live.staticflickr.com/3066/3127743450_18efda5b7c_b.jpg", .6, .7),
    "frozen-pipes": ("https://live.staticflickr.com/3435/3324523470_6371323795_b.jpg", .5, .5),
}


def grade(im: Image.Image, keep: float = .28) -> Image.Image:
    """A navy duotone over a little of the original colour, so very different photos sit together."""
    im = ImageOps.autocontrast(im, cutoff=1)
    tone = ImageOps.colorize(ImageOps.grayscale(im), black="#0b1a2e", mid="#5f7a99", white="#f4f1ea")
    return ImageEnhance.Contrast(Image.blend(tone, im, keep)).enhance(1.06)


def fetch(url: str) -> Image.Image:
    req = urllib.request.Request(url, headers={"User-Agent": "weather-site-image-build/1.0"})
    return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=40).read())).convert("RGB")


def main():
    for slug, (url, fx, fy) in SOURCES.items():
        im = ImageOps.fit(fetch(url), SIZE, Image.Resampling.LANCZOS, centering=(fx, fy))
        path = OUT / f"photo-{slug}.webp"
        grade(im).save(path, quality=74, method=6)
        print(path, path.stat().st_size)


if __name__ == "__main__":
    main()
