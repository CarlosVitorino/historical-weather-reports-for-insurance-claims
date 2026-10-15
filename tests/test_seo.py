"""Search-facing behaviour: what is indexed, what never is, structured data, and wording the brief rules out."""
import json
import re

from wxreport import content

from test_web import env, place_order  # noqa: F401  (fixture and helper)

PUBLIC = ["/", "/order", "/guides", *content.PAGES]
# Claims a compilation of public records can't make (see docs/reports/Competitor SEO and ads positioning.md).
BANNED = re.compile(r"court[- ]admissible|court[- ]approved|insurance[- ]approved|official (weather )?report|"
                    r"NOAA report|proves? (the )?damage|forensic report|guaranteed", re.I)


def ld(html: str) -> list[dict]:
    return [json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)]


def test_public_pages_are_indexable_with_canonical_urls(env):  # noqa: F811
    _, client, _ = env
    titles = set()
    for path in PUBLIC:
        r = client.get(path)
        assert r.status_code == 200, path
        assert '<meta name="robots" content="index,follow">' in r.text, path
        canon = "https://reports.test" + ("/" if path == "/" else path)
        assert f'<link rel="canonical" href="{canon}">' in r.text, path
        titles.add(re.search(r"<title>(.*?)</title>", r.text).group(1))
        assert not BANNED.search(re.sub(r"<[^>]+>", " ", r.text)), path
    assert len(titles) == len(PUBLIC)   # every page has its own title


def test_structured_data(env):  # noqa: F811
    _, client, _ = env
    blocks = {b["@type"]: b for b in ld(client.get("/").text)}
    assert blocks["Product"]["offers"]["price"] == "9.99" and blocks["Product"]["offers"]["priceCurrency"] == "USD"
    assert "aggregateRating" not in blocks["Product"] and {"Organization", "WebSite"} <= blocks.keys()
    guide = content.GUIDES[0]
    types = {b["@type"]: b for b in ld(client.get(guide.path).text)}
    assert types["Article"]["headline"] == guide.h1
    assert [i["name"] for i in types["BreadcrumbList"]["itemListElement"]] == ["Home", "Guides", guide.h1]


def test_personal_pages_are_never_indexed(env):  # noqa: F811
    _, client, _ = env
    oid, token = place_order(client)
    r = client.get(f"/order/{oid}/{token}")
    assert r.headers["X-Robots-Tag"] == "noindex, nofollow" and '<meta name="robots" content="noindex">' in r.text
    assert 'rel="canonical"' not in r.text
    assert client.get("/api/suggest?q=ab").headers["X-Robots-Tag"].startswith("noindex")


def test_sitemap_and_robots(env):  # noqa: F811
    _, client, _ = env
    sm = client.get("/sitemap.xml")
    assert sm.headers["content-type"].startswith("application/xml")
    locs = re.findall(r"<loc>(.*?)</loc>", sm.text)
    assert {f"https://reports.test{p}" for p in PUBLIC if p != "/"} <= set(locs)
    assert "https://reports.test/" in locs and not any("/orders/" in u or "/admin" in u for u in locs)
    for u in locs:
        assert client.get(u.replace("https://reports.test", "")).status_code == 200, u
    robots = client.get("/robots.txt").text
    assert "Disallow: /admin" in robots and "Sitemap: https://reports.test/sitemap.xml" in robots
    assert "Disallow: /order" not in robots   # noindex must stay readable, and /order is a public page


def test_trailing_slash_redirects_to_one_url(env):  # noqa: F811
    _, client, _ = env
    r = client.get("/guides/?utm_source=x", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == "/guides?utm_source=x"


def test_content_page_visits_are_counted_with_their_path(env):  # noqa: F811
    app, client, _ = env
    client.get("/methodology", headers={"referer": "https://www.google.com/"})
    st = app.state.store.stats(None)
    assert {"path": "/methodology", "views": 1, "visitors": 1} in st["pages"]
    assert any(r["src"] == "www.google.com" for r in st["referrers"])
