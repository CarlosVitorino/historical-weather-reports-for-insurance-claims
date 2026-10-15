"""The whole purchase path: form → confirm → creem checkout → signed webhook → report → download, plus /admin."""
import hashlib
import hmac
import json
import re
from dataclasses import replace
from pathlib import Path

import pytest
import requests
from fastapi.testclient import TestClient

from wxreport import config, fulfil, web
from wxreport.geocode import AddressNotFound, Location
from wxreport.report import gather

FIXTURES = Path(__file__).parent / "fixtures" / "snapshots"
ADDR, DAY = "401 N College Ave, Bloomington, IN", "2026-02-19"
LOC = Location(ADDR, "401 N COLLEGE AVE, BLOOMINGTON, IN, 47404", 39.16955, -86.53493,
               "America/Indiana/Indianapolis", "Monroe County", "IN", "18105", "census")
SECRET = "whsec_test"


class FakeResp:
    def __init__(self, status, data):
        self.status_code, self._data, self.text = status, data, json.dumps(data)

    def json(self):
        return self._data


@pytest.fixture
def env(tmp_path, monkeypatch):
    cfg = replace(config.load(), base_url="https://reports.test", data_dir=tmp_path, creem_api_key="creem_test_k",
                  creem_product_id="prod_1", creem_webhook_secret=SECRET, creem_api_base="https://test-api.creem.io",
                  resend_api_key="re_k", resend_from="Reports <r@test>", admin_password="pw", fake_payments=False)
    posts = []

    def fake_post(url, json=None, headers=None, timeout=None):
        posts.append((url, json, headers))
        if "creem" in url:
            return FakeResp(200, {"id": "ch_1", "checkout_url": "https://checkout.creem.test/ch_1"})
        return FakeResp(200, {"id": "email_1"})

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(web, "locate", lambda snap, address, lat=None, lon=None: LOC)
    monkeypatch.setattr(fulfil, "gather", lambda *a, **k: gather(ADDR, DAY, root=FIXTURES, offline=True))
    app = web.create_app(cfg)
    return app, TestClient(app), posts


def sign(body: bytes) -> str:
    return hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


def place_order(client) -> tuple[str, str]:
    r = client.post("/order", data={"address": ADDR, "loss_date": DAY, "email": "adjuster@example.com"},
                    follow_redirects=False)
    assert r.status_code == 303
    oid, token = re.match(r"/order/(ord_\w+)/([\w-]+)", r.headers["location"]).groups()
    return oid, token


def test_purchase_path_end_to_end(env):
    app, client, posts = env
    store = app.state.store
    r = client.get("/?utm_source=adjuster-forum")
    assert r.status_code == 200 and "vid" in r.cookies

    oid, token = place_order(client)
    r = client.get(f"/order/{oid}/{token}")
    assert "401 N COLLEGE AVE, BLOOMINGTON, IN, 47404" in r.text and "Pay $9.99" in r.text

    r = client.post(f"/order/{oid}/{token}/checkout", follow_redirects=False)
    assert r.headers["location"] == "https://checkout.creem.test/ch_1"
    url, body, headers = posts[0]
    assert url == "https://test-api.creem.io/v1/checkouts" and headers["x-api-key"] == "creem_test_k"
    assert body["request_id"] == oid and body["success_url"] == f"https://reports.test/orders/{oid}/{token}"

    assert "Waiting for payment" in client.get(f"/orders/{oid}/{token}").text

    event = {"id": "evt_1", "eventType": "checkout.completed", "created_at": 1,
             "object": {"id": "ch_1", "request_id": oid, "order": {"id": "ord_creem", "amount": 999, "currency": "USD"},
                        "customer": {"email": "adjuster@example.com"}, "metadata": {"order_id": oid}}}
    raw = json.dumps(event).encode()
    assert client.post("/webhooks/creem", content=raw, headers={"creem-signature": "bad"}).status_code == 401
    assert client.post("/webhooks/creem", content=raw, headers={"creem-signature": sign(raw)}).json() == {"ok": True}
    assert client.post("/webhooks/creem", content=raw, headers={"creem-signature": sign(raw)}).json()["duplicate"]
    app.state.fulfiller.pool.shutdown(wait=True)

    o = store.get(oid)
    assert o["status"] == "ready" and o["amount_cents"] == 999 and o["email_status"] == "sent"
    assert o["report_id"].startswith("WE-2026-02-19-")
    email = posts[-1][1]
    assert posts[-1][0] == "https://api.resend.com/emails" and email["to"] == ["adjuster@example.com"]
    assert email["attachments"][0]["filename"] == f"{o['report_id']}.pdf"

    page = client.get(f"/orders/{oid}/{token}").text
    assert "Your report is ready" in page and o["report_id"] in page
    pdf = client.get(f"/orders/{oid}/{token}/report.pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    assert client.get(f"/orders/{oid}/wrong-token").status_code == 404

    assert client.get("/admin").status_code == 401
    assert client.get("/admin", auth=("admin", "nope")).status_code == 401
    admin = client.get("/admin", auth=("admin", "pw")).text
    for needle in ["Unique visitors", "$9.99", "adjuster-forum", o["report_id"], "adjuster@example.com"]:
        assert needle in admin, needle
    st = store.stats(None)
    assert st["paid_orders"] == 1 and st["revenue_cents"] == 999
    assert {k: st["counts"][k][0] for k in ("page_view", "form_submit", "checkout_click", "paid", "download")} == \
        {"page_view": 1, "form_submit": 1, "checkout_click": 1, "paid": 1, "download": 1}


def test_form_errors_are_logged_and_leave_no_order(env, monkeypatch):
    app, client, _ = env
    r = client.post("/order", data={"address": ADDR, "loss_date": DAY, "email": "not-an-email"})
    assert "valid email" in r.text

    def not_found(*a, **k):
        raise AddressNotFound("no")
    monkeypatch.setattr(web, "locate", not_found)
    r = client.post("/order", data={"address": "PO Box 1, Bettles, AK", "loss_date": DAY, "email": "a@b.co"})
    assert "match that address" in r.text and 'name="lat"' in r.text
    assert app.state.store.orders(10) == []
    reasons = {e["reason"]: e["n"] for e in app.state.store.stats(None)["form_errors"]}
    assert reasons == {"bad_email": 1, "address_not_found": 1}


def test_unfinished_day_rejected(env):
    _, client, _ = env
    from datetime import date
    r = client.post("/order", data={"address": ADDR, "loss_date": date.today().isoformat(), "email": "a@b.co"})
    assert "ended yet at that address" in r.text


def test_admin_disabled_without_password(env):
    app, _, _ = env
    cfg = replace(app.state.cfg, admin_password="")
    client = TestClient(web.create_app(cfg, app.state.store))
    assert client.get("/admin", auth=("admin", "")).status_code == 503


def test_fake_payments_for_local_testing(env):
    app, _, _ = env
    cfg = replace(app.state.cfg, creem_api_key="", fake_payments=True)
    app2 = web.create_app(cfg, app.state.store)
    client = TestClient(app2)
    oid, token = place_order(client)
    r = client.post(f"/order/{oid}/{token}/checkout", follow_redirects=False)
    assert r.headers["location"] == f"/orders/{oid}/{token}"
    app2.state.fulfiller.pool.shutdown(wait=True)
    assert app2.state.store.get(oid)["status"] == "ready"


def test_pin_only_order(env, monkeypatch):
    app, client, _ = env
    seen = {}

    def fake_locate(snap, address, lat=None, lon=None):
        seen.update(address=address, lat=lat, lon=lon)
        return Location(address, None, lat, lon, "America/Indiana/Indianapolis", "Monroe County", "IN", "18105",
                        "operator")
    monkeypatch.setattr(web, "locate", fake_locate)
    r = client.post("/order", data={"address": "", "lat": "39.17", "lon": "-86.53", "loss_date": DAY,
                                    "email": "a@b.co"}, follow_redirects=False)
    assert r.status_code == 303 and seen["lat"] == 39.17
    oid = r.headers["location"].split("/")[2]
    o = app.state.store.get(oid)
    assert o["address"].startswith("Map pin at 39.17") and o["site_lat"] == 39.17
    page = client.get(r.headers["location"]).text
    assert 'id="confirm-map"' in page and "map pin" in page


def test_landing_hook_and_order_page(env):
    app, client, _ = env
    html = client.get("/").text
    for needle in ['href="/order"', "/static/hero.js", 'id="hero-map"', 'id="compare"', "Sample report · page 1"]:
        assert needle in html, needle
    assert 'id="order-form"' not in html
    order = client.get("/order?address=401+N+College+Ave").text
    for needle in ['id="order-form"', 'role="combobox"', "/static/order.js", 'value="401 N College Ave"',
                   "1 · Location and date"]:
        assert needle in order, needle
    assert app.state.store.stats(None)["counts"]["order_view"][0] == 1


def test_geocode_and_reverse_endpoints(env, monkeypatch):
    _, client, _ = env
    monkeypatch.setattr(web, "find", lambda q: {"label": "5299 Dtc Blvd, Greenwood Village, CO 80111",
                                                "lat": 39.619946, "lon": -104.8899, "source": "census"}
                        if "Greenwood" in q else None)
    monkeypatch.setattr(web, "suggest", lambda q: ([], False))
    assert client.get("/api/geocode", params={"q": "5299 DTC Blvd, Greenwood Village, CO"}).json()["lat"] == 39.619946
    assert client.get("/api/geocode", params={"q": "5299 Dtc Blvd, Ste 550"}).json() == {"ok": False}

    monkeypatch.setattr(web, "where", lambda lat, lon: {"ok": True, "in_us": True, "county": "Arapahoe County",
                                                        "state": "CO"})
    monkeypatch.setattr(web, "reverse", lambda lat, lon: None)
    d = client.get("/api/reverse", params={"lat": 39.6198, "lon": -104.8904}).json()
    assert d["label"] == "Map pin in Arapahoe County, CO (39.61980, -104.89040)" and d["in_us"]
    monkeypatch.setattr(web, "reverse", lambda lat, lon: "5299 DTC Boulevard, Greenwood Village, CO 80111")
    assert client.get("/api/reverse", params={"lat": 39.6198, "lon": -104.8904}).json()["label"].startswith("5299")
    assert client.get("/api/reverse", params={"lat": 200, "lon": 0}).status_code == 400
