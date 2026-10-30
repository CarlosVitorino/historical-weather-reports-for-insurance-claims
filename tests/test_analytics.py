"""Umami: the tracker only on public pages, nothing in development, and the owner's own browser left out."""
from dataclasses import replace

from fastapi.testclient import TestClient

from wxreport import config, site, web

from test_web import env, place_order  # noqa: F401  (fixture and helper)

SITE_ID = "949170a6-74b3-48ae-bcf5-22c087abe3f5"


def client_with(tmp_path, website_id: str) -> TestClient:
    cfg = replace(config.load(), base_url="https://weatherevidence.com", data_dir=tmp_path, storm_sync=False,
                  umami_website_id=website_id)
    return TestClient(web.create_app(cfg))


def test_tracker_on_public_pages_only(tmp_path):
    client = client_with(tmp_path, SITE_ID)
    for path in ["/", "/order", "/guides", "/storm-reports", "/privacy"]:
        html = client.get(path).text
        assert f'data-website-id="{SITE_ID}"' in html, path
        assert 'src="/u/script.js"' in html and 'data-domains="weatherevidence.com"' in html, path
        assert html.index("/static/analytics.js") < html.index("/u/script.js"), path   # the scrub loads first
    assert "/u/script.js" not in client.get("/does-not-exist").text


def test_no_tracker_without_a_website_id(tmp_path):
    assert "/u/script.js" not in client_with(tmp_path, "").get("/").text
    assert "/u/script.js" not in client_with(tmp_path, "not-a-uuid").get("/").text
    site.configure_analytics("", "")   # leave the module as the other tests expect it


def test_order_pages_carry_no_tracker(env):  # noqa: F811
    _, client, _ = env
    site.configure_analytics(SITE_ID, "https://reports.test")
    try:
        oid, token = place_order(client)
        assert "/u/script.js" not in client.get(f"/order/{oid}/{token}").text   # the address holds the token
        assert "/u/script.js" not in client.get(f"/orders/{oid}/{token}").text
    finally:
        site.configure_analytics("", "")


def test_owner_browser_is_not_counted(env):  # noqa: F811
    app, client, _ = env
    store = app.state.store
    before = store.stats(None)["counts"].get("page_view", (0, 0))[0]
    client.cookies.set("nostats", "1")
    client.get("/")
    assert store.stats(None)["counts"].get("page_view", (0, 0))[0] == before
    client.cookies.delete("nostats")
    client.get("/")
    assert store.stats(None)["counts"].get("page_view", (0, 0))[0] == before + 1


def test_admin_offers_the_switch(env):  # noqa: F811
    _, client, _ = env
    html = client.get("/admin", auth=("admin", "pw")).text
    assert "Don't count this browser" in html and 'localStorage.setItem("umami.disabled", "1")' in html
