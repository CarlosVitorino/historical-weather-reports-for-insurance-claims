"""Order page → address confirmation → creem checkout → webhook → background report → download + email.

Plus /admin: visitors, funnel, sales and orders, behind ADMIN_PASSWORD (HTTP Basic auth).
"""
import json
from contextlib import asynccontextmanager
import re
import secrets
import shutil
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlencode, urlparse

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from . import config, payments, site
from .fulfil import Fulfiller, order_dir
from .geocode import AddressNotFound, locate
from .report import MIN_DATE
from .snapshot import Snapshot, SourceUnavailable
from .store import Store, now
from .timewin import local_day

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VISITOR_COOKIE = "vid"

def page(title: str, body: str, refresh: int | None = None) -> HTMLResponse:
    return HTMLResponse(site.layout(title, body, refresh))


def inner_page(title: str, heading: str, body: str, refresh: int | None = None, eyebrow: str = "") -> HTMLResponse:
    eb = f'<p class="eyebrow">{escape(eyebrow)}</p>' if eyebrow else ""
    return page(title, site.inner(f"{eb}<h1>{escape(heading)}</h1>{body}"), refresh)


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

    app = FastAPI(title=site.BRAND, docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.cfg, app.state.store, app.state.fulfiller = cfg, store, fulfiller
    security = HTTPBasic(realm="admin")
    app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


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
        return page(f"{site.BRAND} — weather records for any US address and date of loss",
                    site.landing(site.order_form(prefill)))

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
            return page("Check your details", site.inner(site.order_form(v, msg, ask_coords, "Check your details")))

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
        price = f"${cfg.price_cents / 100:.2f}"
        return inner_page("Confirm your report", "Confirm your report", f"""<div class="panel"><dl>
<dt>Location</dt><dd><b>{escape(o['matched_address'])}</b><br><span class="fine">{escape(o['county'] or '')} · {how}</span></dd>
<dt>Date of loss</dt><dd>{d:%B} {d.day}, {d.year}</dd><dt>Deliver to</dt><dd>{escape(o['email'])}</dd>
<dt>Price</dt><dd><b>{price}</b> · one report, no subscription</dd></dl>{unavailable}
<div class="actions"><form method="post" action="/order/{oid}/{token}/checkout">
<button class="btn btn-amber" type="submit">Pay {price} securely</button></form>
<a class="btn btn-ghost" href="{escape(back, quote=True)}#order">Change details</a></div>
<p class="fine">If this isn't the property, change the details and enter its coordinates instead. The report is built
for the location above. Checkout is handled by Creem.</p></div>""", eyebrow="Step 2 of 3")

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
            return inner_page("Payment unavailable", "Payment is temporarily unavailable", f"""<div class="panel">
<p class="err">We couldn't open the payment page. Nothing was charged. Please try again in a minute.</p>
<div class="actions"><a class="btn btn-navy" href="/order/{oid}/{token}">Try again</a></div></div>""")
        store.update(oid, status="checkout", checkout_id=co.get("id"))
        return RedirectResponse(co["checkout_url"], status_code=303)

    @app.get("/orders/{oid}/{token}", response_class=HTMLResponse)
    def status(oid: str, token: str):
        o = order_or_404(oid, token)
        s = o["status"]
        where = f'<p class="lede" style="margin:-6px 0 22px">{escape(o["matched_address"] or o["address"])} · {o["loss_date"]}</p>'

        def show(title, kind, head, text, refresh=None):
            return inner_page(title, "Your weather report", where + f'<div class="panel">'
                              f'{site.status_block(kind, head, text)}</div>', refresh, eyebrow="Step 3 of 3")

        if s in ("draft", "checkout"):
            return show("Waiting for payment", "wait", "Waiting for payment confirmation…",
                        '<p class="fine">This page refreshes by itself. If you closed the payment page before paying, '
                        'nothing was charged.</p>', refresh=5)
        if s in ("paid", "generating"):
            return show("Building your report", "wait", "Payment received — building your report",
                        f"<p>Pulling station records, warnings, storm reports, radar hail and lightning from the "
                        f"government archives. Usually under a minute.</p><p class=\"fine\">This page refreshes by "
                        f"itself, and we'll email the report to {escape(o['email'])}.</p>", refresh=5)
        if s == "ready":
            sent = {"sent": f" A copy was emailed to {escape(o['email'])}.", None: " We're emailing a copy to "
                    f"{escape(o['email'])}."}.get(o["email_status"], "")
            return show("Your report is ready", "ok", "Your report is ready",
                        f'<p>Report ID <span class="rid">{o["report_id"]}</span></p>'
                        f'<div class="actions"><a class="btn btn-amber" href="/orders/{oid}/{token}/report.pdf">'
                        f'Download PDF</a></div><p class="fine">Bookmark this page to download again.{sent}</p>')
        if s == "refunded":
            return show("Refunded", "bad", "This order was refunded", "")
        return show("We're on it", "bad", "Your payment is safe, but the report hit a problem",
                    f"<p>We've been notified and will email {escape(o['email'])} with the report or a refund.</p>")

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

