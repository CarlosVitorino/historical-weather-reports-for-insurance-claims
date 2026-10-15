"""Order page → address confirmation → creem checkout → webhook → background report → download + email.

Plus /admin: visitors, funnel, sales and orders, behind ADMIN_PASSWORD (HTTP Basic auth).
"""
import json
from contextlib import asynccontextmanager
import re
import secrets
import shutil
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlencode, urlparse

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import config, payments
from .fulfil import Fulfiller, order_dir
from .geocode import AddressNotFound, locate
from .report import MIN_DATE
from .snapshot import Snapshot, SourceUnavailable
from .store import Store, now
from .timewin import local_day

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VISITOR_COOKIE = "vid"

CSS = """
:root{--ink:#1b2430;--muted:#5b6675;--rule:#d9dee5;--accent:#1f4e79;--bg:#f7f9fb;--warn:#8a4b08;--ok:#1e6b3a}
*{box-sizing:border-box}body{font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);
background:var(--bg);margin:0}main{max-width:36rem;margin:0 auto;padding:2rem 1rem 4rem}
h1{font-size:1.6rem;line-height:1.25;margin:.2rem 0 1rem}h2{font-size:1.1rem;margin:1.6rem 0 .5rem}
.card{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:1.25rem;margin:1rem 0}
label{display:block;margin-top:1rem;font-weight:600}label small{font-weight:400;color:var(--muted)}
input{width:100%;padding:.6rem;font:inherit;border:1px solid #b9c2cd;border-radius:6px;margin-top:.3rem;background:#fff}
button,.btn{display:inline-block;margin-top:1.25rem;padding:.7rem 1.3rem;font:inherit;font-weight:600;
background:var(--accent);color:#fff;border:0;border-radius:6px;text-decoration:none;cursor:pointer}
.btn.secondary{background:#fff;color:var(--accent);border:1px solid var(--accent);margin-left:.5rem}
.note{color:var(--muted);font-size:.88rem}.err{background:#fdf0e6;border:1px solid #f0c9a4;color:var(--warn);
padding:.75rem 1rem;border-radius:6px}.ok{color:var(--ok)}ul.feat{padding-left:1.1rem}ul.feat li{margin:.25rem 0}
dl{display:grid;grid-template-columns:8rem 1fr;gap:.35rem .75rem;margin:0}dt{color:var(--muted)}dd{margin:0}
.row{display:flex;gap:.75rem}.row>label{flex:1}
"""


def page(title: str, body: str, refresh: int | None = None) -> HTMLResponse:
    meta = f'<meta http-equiv="refresh" content="{refresh}">' if refresh else ""
    return HTMLResponse(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">{meta}<title>{escape(title)}</title>
<style>{CSS}</style></head><body><main>{body}</main></body></html>""")


INTRO = """<h1>Loss-Site Weather Report</h1>
<p>One PDF of the US government weather records for one address and one past date — $9.99.</p>
<ul class="feat">
<li>Wind gusts, rain and temperature <b>measured at named NOAA stations</b>, each with its distance and direction
from the address. Nothing is blended or estimated.</li>
<li>NWS warnings, with a check of <b>whether the address was inside each warning polygon</b>.</li>
<li>NWS storm reports, the NCEI Storm Events database, NEXRAD radar hail and lightning counts.</li>
<li>Source retrieval times and hashes, so the report can be reproduced and verified.</li>
</ul>"""

DISCLAIMER = """<p class="note">Compiles public records; it is not a certified government record or expert opinion,
and records near the address do not by themselves establish conditions at the property.</p>"""


def form_html(v: dict, error: str = "", ask_coords: bool = False) -> str:
    g = lambda k: escape(str(v.get(k) or ""), quote=True)  # noqa: E731
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    coords = ""
    if ask_coords or v.get("lat"):
        coords = f"""<div class="row"><label>Latitude<input name="lat" inputmode="decimal" value="{g('lat')}"
placeholder="39.16955"></label><label>Longitude<input name="lon" inputmode="decimal" value="{g('lon')}"
placeholder="-86.53493"></label></div><p class="note">Rural routes, PO boxes and new builds often aren't in the
Census address file. Right-click the property in Google Maps and copy the coordinates shown.</p>"""
    err = f'<p class="err">{escape(error)}</p>' if error else ""
    return f"""{INTRO}<div class="card"><form method="post" action="/order">{err}
<label>Loss address<input name="address" required autocomplete="street-address" value="{g('address')}"
placeholder="401 N College Ave, Bloomington, IN 47404"></label>
<label>Loss date <small>(a completed past day, local time at the address)</small>
<input type="date" name="loss_date" required min="{MIN_DATE.isoformat()}" max="{yesterday}" value="{g('loss_date')}"></label>
<label>Email for delivery<input type="email" name="email" required autocomplete="email" value="{g('email')}"></label>
{coords}<button type="submit">Check address</button></form></div>{DISCLAIMER}"""


def _float(s: str | None) -> float | None:
    try:
        return float(s) if s not in (None, "") else None
    except ValueError:
        raise ValueError("Latitude and longitude must be numbers, e.g. 39.16955 and -86.53493.")


def create_app(cfg: config.Settings | None = None, store: Store | None = None) -> FastAPI:
    cfg = cfg or config.load()
    store = store or Store(cfg.data_dir / "app.db")
    fulfiller = Fulfiller(cfg, store)
    @asynccontextmanager
    async def lifespan(_app):
        fulfiller.resume()   # orders interrupted by a restart
        yield

    app = FastAPI(title="Loss-Site Weather Report", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.cfg, app.state.store, app.state.fulfiller = cfg, store, fulfiller
    security = HTTPBasic(realm="admin")


    @app.middleware("http")
    async def visitor(request: Request, call_next):
        vid = request.cookies.get(VISITOR_COOKIE)
        request.state.new_visitor = vid is None
        request.state.vid = vid or secrets.token_hex(8)
        resp = await call_next(request)
        if request.state.new_visitor and not request.url.path.startswith(("/webhooks", "/admin", "/healthz")):
            resp.set_cookie(VISITOR_COOKIE, request.state.vid, max_age=365 * 86400, httponly=True, samesite="lax")
        return resp

    def order_or_404(oid: str, token: str) -> dict:
        o = store.get(oid)
        if not o or not secrets.compare_digest(o["token"], token):
            raise HTTPException(404)
        return o

    # -- public pages -----------------------------------------------------------------------
    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        ref = request.headers.get("referer") or ""
        host = urlparse(ref).hostname or ""
        detail = {}
        if host and host != request.url.hostname:
            detail["referrer"] = host
        for k in ("utm_source", "utm_medium", "utm_campaign"):
            if request.query_params.get(k):
                detail[k] = request.query_params[k][:100]
        store.log("page_view", request.state.vid, **detail)
        prefill = {k: request.query_params.get(k) for k in ("address", "loss_date", "email", "lat", "lon")}
        return page("Loss-Site Weather Report", form_html(prefill))

    @app.post("/order", response_class=HTMLResponse)
    def order(request: Request, address: str = Form(""), loss_date: str = Form(""), email: str = Form(""),
              lat: str = Form(None), lon: str = Form(None)):
        v = {"address": address.strip(), "loss_date": loss_date, "email": email.strip(), "lat": lat, "lon": lon}

        created: list[str] = []

        def fail(reason: str, msg: str, ask_coords: bool = False):
            for oid in created:   # an order only exists once its location checks out
                store.delete(oid)
                shutil.rmtree(order_dir(cfg, oid), ignore_errors=True)
            store.log("form_error", request.state.vid, reason=reason)
            return page("Check your details", form_html(v, msg, ask_coords))

        if not v["address"]:
            return fail("no_address", "Enter the address of the loss.")
        if not EMAIL.match(v["email"]):
            return fail("bad_email", "Enter a valid email address — the report is delivered there.")
        try:
            day = date.fromisoformat(loss_date)
        except ValueError:
            return fail("bad_date", "Enter the loss date.")
        if day < MIN_DATE:
            return fail("date_too_old", f"Reports cover loss dates from {MIN_DATE:%B %-d, %Y} onward.")
        try:
            flat, flon = _float(lat), _float(lon)
        except ValueError as e:
            return fail("bad_coords", str(e), True)
        if (flat is None) != (flon is None):
            return fail("bad_coords", "Enter both latitude and longitude, or neither.", True)

        o = store.create_order(visitor=request.state.vid, email=v["email"], address=v["address"],
                               loss_date=day.isoformat(), lat=flat, lon=flon)
        created.append(o["id"])
        request_ = {"address": v["address"], "date": day.isoformat(), "lat": flat, "lon": flon}
        snap = Snapshot.open(request_, root=order_dir(cfg, o["id"]) / "snapshots")
        try:
            loc = locate(snap, v["address"], flat, flon)
        except AddressNotFound:
            return fail("address_not_found", "We couldn't find that address in the US Census address file. Check "
                        "the street, city and state (adding the ZIP code helps), or enter the property's "
                        "coordinates below.", True)
        except SourceUnavailable:
            return fail("geocoder_down", "The US Census address service didn't respond. Please try again in a "
                        "minute, or enter the property's coordinates below.", True)
        if loc.county is None:
            return fail("outside_us", "Those coordinates aren't inside a US county. Reports cover US locations only.",
                        True)
        if local_day(day, loc.tz).end_utc > datetime.now(timezone.utc):
            return fail("date_not_over", "That date hasn't ended yet at that address. Reports cover completed "
                        "past days only.")
        store.update(o["id"], lat=loc.lat if flat is not None else None, lon=loc.lon if flon is not None else None,
                     matched_address=loc.matched_address or f"{loc.lat:.5f}, {loc.lon:.5f}",
                     county=f"{loc.county}, {loc.state}")
        store.log("form_submit", request.state.vid, o["id"], method=loc.method)
        return RedirectResponse(f"/order/{o['id']}/{o['token']}", status_code=303)

    @app.get("/order/{oid}/{token}", response_class=HTMLResponse)
    def confirm(oid: str, token: str):
        o = order_or_404(oid, token)
        if o["status"] not in ("draft", "checkout"):
            return RedirectResponse(f"/orders/{oid}/{token}", status_code=303)
        d = date.fromisoformat(o["loss_date"])
        back = "/?" + urlencode({k: o[k] for k in ("address", "loss_date", "email") if o[k]} |
                                ({"lat": o["lat"], "lon": o["lon"]} if o["lat"] is not None else {}))
        how = "coordinates you entered" if o["lat"] is not None else "US Census Geocoder match"
        unavailable = "" if (cfg.payments_ready or cfg.fake_payments) else \
            '<p class="err">Payments are not configured on this server yet.</p>'
        return page("Confirm your report", f"""<h1>Confirm your report</h1><div class="card"><dl>
<dt>Location</dt><dd><b>{escape(o['matched_address'])}</b><br><span class="note">{escape(o['county'] or '')} · {how}</span></dd>
<dt>Loss date</dt><dd>{d:%B} {d.day}, {d.year}</dd><dt>Deliver to</dt><dd>{escape(o['email'])}</dd>
<dt>Price</dt><dd>${cfg.price_cents / 100:.2f}</dd></dl>{unavailable}
<form method="post" action="/order/{oid}/{token}/checkout" style="display:inline">
<button type="submit">Pay ${cfg.price_cents / 100:.2f}</button></form>
<a class="btn secondary" href="{escape(back, quote=True)}">Change</a></div>
<p class="note">If the location isn't the property, go back and enter its coordinates instead. The report is built
from the location above.</p>{DISCLAIMER}""")

    @app.post("/order/{oid}/{token}/checkout")
    def checkout(request: Request, oid: str, token: str):
        o = order_or_404(oid, token)
        if o["status"] not in ("draft", "checkout"):
            return RedirectResponse(f"/orders/{oid}/{token}", status_code=303)
        store.log("checkout_click", request.state.vid, oid)
        if cfg.fake_payments and not cfg.payments_ready:
            if store.transition(oid, ("draft", "checkout"), "paid", paid_at=now(), amount_cents=cfg.price_cents,
                                currency="USD", creem_order_id="fake"):
                store.log("paid", o["visitor"], oid, amount_cents=cfg.price_cents, fake=True)
                fulfiller.submit(oid)
            return RedirectResponse(f"/orders/{oid}/{token}", status_code=303)
        if not cfg.payments_ready:
            raise HTTPException(503, "Payments are not configured.")
        try:
            co = payments.create_checkout(cfg, o)
        except payments.PaymentError as e:
            store.log("checkout_error", request.state.vid, oid, error=str(e)[:300])
            return page("Payment unavailable", f"""<h1>Payment is temporarily unavailable</h1>
<p class="err">We couldn't open the payment page. Nothing was charged. Please try again in a minute.</p>
<a class="btn" href="/order/{oid}/{token}">Try again</a>""")
        store.update(oid, status="checkout", checkout_id=co.get("id"))
        return RedirectResponse(co["checkout_url"], status_code=303)

    @app.get("/orders/{oid}/{token}", response_class=HTMLResponse)
    def status(oid: str, token: str):
        o = order_or_404(oid, token)
        s = o["status"]
        head = f"""<h1>Your weather report</h1><p>{escape(o['matched_address'] or o['address'])} · {o['loss_date']}</p>"""
        if s in ("draft", "checkout"):
            return page("Waiting for payment", head + """<div class="card"><p><b>Waiting for payment confirmation…</b>
</p><p class="note">This page refreshes by itself. If you closed the payment page before paying, nothing was
charged.</p></div>""", refresh=5)
        if s in ("paid", "generating"):
            return page("Building your report", head + f"""<div class="card"><p class="ok"><b>Payment received.</b></p>
<p>Building your report from the government archives — usually under a minute. This page refreshes by itself, and
we'll email it to {escape(o['email'])}.</p></div>""", refresh=5)
        if s == "ready":
            sent = {"sent": f" A copy was emailed to {escape(o['email'])}.", None: " We're emailing a copy to "
                    f"{escape(o['email'])}."}.get(o["email_status"], "")
            return page("Your report is ready", head + f"""<div class="card"><p class="ok"><b>Your report is ready.</b></p>
<p>Report ID <b>{o['report_id']}</b></p><a class="btn" href="/orders/{oid}/{token}/report.pdf">Download PDF</a>
<p class="note">Bookmark this page to download again.{sent}</p></div>""")
        if s == "refunded":
            return page("Refunded", head + '<div class="card"><p>This order was refunded.</p></div>')
        return page("We're on it", head + f"""<div class="card"><p><b>Your payment is safe, but the report hit a
problem.</b></p><p>We've been notified and will email {escape(o['email'])} with the report or a refund.</p></div>""")

    @app.get("/orders/{oid}/{token}/report.pdf")
    def download(request: Request, oid: str, token: str):
        o = order_or_404(oid, token)
        if o["status"] != "ready" or not o["pdf_path"] or not Path(o["pdf_path"]).exists():
            raise HTTPException(404)
        store.log("download", request.state.vid, oid)
        return FileResponse(o["pdf_path"], media_type="application/pdf", filename=f"{o['report_id']}.pdf")

    # -- creem webhook ----------------------------------------------------------------------
    @app.post("/webhooks/creem")
    async def creem_webhook(request: Request):
        raw = await request.body()
        if not cfg.creem_webhook_secret:
            raise HTTPException(503, "webhook secret not configured")
        if not payments.verify_signature(raw, request.headers.get("creem-signature"), cfg.creem_webhook_secret):
            raise HTTPException(401, "bad signature")
        try:
            ev = json.loads(raw)
            etype, obj = ev["eventType"], ev.get("object") or {}
        except (ValueError, KeyError):
            raise HTTPException(400, "malformed event")
        if ev.get("id") and store.seen_webhook(ev["id"]):
            return {"ok": True, "duplicate": True}
        oid = payments.order_ref(obj) if etype == "checkout.completed" else \
            payments.order_ref(obj.get("checkout") or {}) or (obj.get("metadata") or {}).get("order_id")
        store.log("webhook", order_id=oid, event=etype)
        if etype == "checkout.completed" and oid and store.get(oid):
            order = obj.get("order") or {}
            amount = order.get("amount_paid", order.get("amount"))
            if store.transition(oid, ("draft", "checkout"), "paid", paid_at=now(), amount_cents=amount,
                                currency=order.get("currency"), creem_order_id=order.get("id"),
                                checkout_id=obj.get("id")):
                store.log("paid", store.get(oid)["visitor"], oid, amount_cents=amount)
                fulfiller.submit(oid)
        elif etype == "refund.created" and oid and store.get(oid):
            store.update(oid, status="refunded")
            store.log("refund", order_id=oid)
        return {"ok": True}

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "payments": cfg.payments_ready, "email": cfg.email_ready}

    # -- admin ------------------------------------------------------------------------------
    def admin_auth(creds: HTTPBasicCredentials = Depends(security)):
        if not cfg.admin_password:
            raise HTTPException(503, "Set ADMIN_PASSWORD to enable the admin page.")
        if not secrets.compare_digest(creds.password.encode(), cfg.admin_password.encode()):
            raise HTTPException(401, headers={"WWW-Authenticate": 'Basic realm="admin"'})

    @app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
    def admin(days: int = 30):
        from .admin import render_admin
        return HTMLResponse(render_admin(cfg, store, days if days in (1, 7, 30, 90) else 0))

    @app.post("/admin/orders/{oid}/retry", dependencies=[Depends(admin_auth)])
    def admin_retry(oid: str):
        if store.transition(oid, ("failed",), "paid", error=None):
            fulfiller.submit(oid)
        return RedirectResponse("/admin#orders", status_code=303)

    @app.post("/admin/orders/{oid}/resend", dependencies=[Depends(admin_auth)])
    def admin_resend(oid: str):
        o = store.get(oid)
        if o and o["status"] == "ready":
            fulfiller.pool.submit(fulfiller.email, oid)
        return RedirectResponse("/admin#orders", status_code=303)

    @app.get("/admin/orders/{oid}/report.pdf", dependencies=[Depends(admin_auth)])
    def admin_download(oid: str):
        o = store.get(oid)
        if not o or not o["pdf_path"] or not Path(o["pdf_path"]).exists():
            raise HTTPException(404)
        return FileResponse(o["pdf_path"], media_type="application/pdf", filename=f"{o['report_id']}.pdf")

    return app


def __getattr__(name: str):
    # `uvicorn wxreport.web:app` — build the app lazily so importing this module (e.g. in tests) has no side effects.
    if name == "app":
        globals()["app"] = create_app()
        return globals()["app"]
    raise AttributeError(name)

