"""What search engines read: structured data (schema.org JSON-LD), sitemap.xml and robots.txt.

Indexed: the home page, the order page, the content pages and the sample PDF. Everything personal (orders, status,
downloads) is noindex, and /admin, /api and /webhooks are disallowed.
"""
from datetime import date
from xml.sax.saxutils import escape as xml_escape

from . import BRAND, DOMAIN
from .content import GUIDES, PAGES, Page
from .legal import PATHS as LEGAL_PATHS, UPDATED as LEGAL_UPDATED

SITE_UPDATED = date(2026, 10, 29)   # bump when the home or order page changes meaningfully


def organization(base: str) -> dict:
    return {"@context": "https://schema.org", "@type": "Organization", "@id": f"{base}/#org", "name": BRAND,
            "url": f"{base}/", "logo": f"{base}/static/apple-touch-icon.png"}


def website(base: str) -> dict:
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": f"{base}/#site", "name": BRAND,
            "alternateName": DOMAIN, "url": f"{base}/", "publisher": {"@id": f"{base}/#org"}}


def product(base: str, price_cents: int) -> dict:
    """The report as a product. No ratings or reviews: there are none yet, and fake ones break Google's rules."""
    return {"@context": "https://schema.org", "@type": "Product", "@id": f"{base}/#report",
            "name": f"{BRAND} report", "brand": {"@type": "Brand", "name": BRAND},
            "image": f"{base}/static/sample-p1.webp",
            "description": "Historical weather report for one US address and date of loss: measured wind and rain at "
                           "named stations, NWS warnings with a warning-area check, storm reports, NOAA Storm Events, "
                           "radar hail and lightning, each with its distance and direction from the property. PDF.",
            "offers": {"@type": "Offer", "price": f"{price_cents / 100:.2f}", "priceCurrency": "USD",
                       "availability": "https://schema.org/InStock", "url": f"{base}/order",
                       "seller": {"@id": f"{base}/#org"}}}


def breadcrumbs(base: str, trail: list[tuple[str, str]]) -> dict:
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i, "name": name, "item": f"{base}{path}"}
                                for i, (name, path) in enumerate(trail, 1)]}


def article(base: str, page: Page) -> list[dict]:
    trail = [("Home", "/")] + ([("Guides", "/guides")] if page.guide else []) + [(page.h1, page.path)]
    return [{"@context": "https://schema.org", "@type": "Article", "headline": page.h1,
             "description": page.description, "url": f"{base}{page.path}",
             "dateModified": page.updated.isoformat(), "image": f"{base}/static/sample-p1.webp",
             "author": {"@type": "Organization", "name": BRAND, "url": f"{base}/"},
             "publisher": {"@type": "Organization", "name": BRAND, "url": f"{base}/"}},
            breadcrumbs(base, trail)]


def sitemap(base: str, extra: list[tuple[str, date]] = ()) -> str:
    """extra: generated pages (Storm Reports) with their last change."""
    entries = [("/", SITE_UPDATED), ("/order", SITE_UPDATED), ("/guides", max(g.updated for g in GUIDES)),
               *((p.path, p.updated) for p in PAGES.values()), *((p, LEGAL_UPDATED) for p in LEGAL_PATHS),
               ("/static/sample-report.pdf", SITE_UPDATED), *extra]
    urls = "".join(f"<url><loc>{xml_escape(base + path)}</loc><lastmod>{d.isoformat()}</lastmod></url>"
                   for path, d in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')


def robots(base: str) -> str:
    return ("User-agent: *\nDisallow: /admin\nDisallow: /api/\nDisallow: /webhooks/\n"
            f"\nSitemap: {base}/sitemap.xml\n")
