import argparse
import sys
from pathlib import Path

from . import config, mailer, payments
from .geocode import AddressNotFound
from .report import InvalidRequest, generate
from .snapshot import SourceUnavailable


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="wxreport", description="Historical loss-site weather report (PDF).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="Generate a report for one address and loss date.")
    r.add_argument("--address", required=True)
    r.add_argument("--date", required=True, help="Local loss date, YYYY-MM-DD")
    r.add_argument("--lat", type=float)
    r.add_argument("--lon", type=float)
    r.add_argument("--out", type=Path, default=Path("reports"))
    r.add_argument("--offline", action="store_true", help="Use only the stored snapshot; never fetch.")
    r.add_argument("--refresh", action="store_true", help="Discard the stored snapshot and re-retrieve all sources.")
    c = sub.add_parser("check", help="Check the production settings: creem key and product, Resend, legal pages.")
    c.add_argument("--email-to", help="Also send a test email to this address through Resend.")
    sub.add_parser("backup", help="Copy the database to DATA_DIR/backups now (also runs daily inside the server).")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        return check(a.email_to)
    if a.cmd == "backup":
        from .housekeeping import backup_db
        from .store import Store
        cfg = config.load()
        print(backup_db(cfg, Store(cfg.data_dir / "app.db")))
        return 0
    try:
        path, rid = generate(a.address, a.date, out_dir=a.out, lat=a.lat, lon=a.lon,
                             offline=a.offline, refresh=a.refresh)
    except (InvalidRequest, AddressNotFound, SourceUnavailable) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"{rid}\n{path}")
    return 0


def check(email_to: str | None) -> int:
    """Every setting a live sale depends on, with what is wrong. Exit 1 if anything would break a sale."""
    cfg = config.load()
    problems, notes = [], []
    if cfg.fake_payments:
        problems.append("ENVIRONMENT=development: every order is marked paid without charging")
    if not cfg.base_url.startswith("https://"):
        problems.append(f"BASE_URL is {cfg.base_url}; creem's redirect and webhook need the public https origin")
    if not cfg.payments_ready:
        problems.append("CREEM_API_KEY, CREEM_PRODUCT_ID and CREEM_WEBHOOK_SECRET must all be set")
    else:
        mode = "TEST mode" if "test-api" in cfg.creem_api_base else "LIVE"
        try:
            prod = payments.get_product(cfg)
            notes.append(f"creem {mode}: product {prod.get('name')!r} {prod.get('price')} {prod.get('currency')} "
                         f"({prod.get('billing_type')}, {prod.get('status')})")
            if prod.get("billing_type") not in (None, "onetime"):
                problems.append(f"the creem product is {prod.get('billing_type')}, not a one-time payment")
            if prod.get("price") != cfg.price_cents:
                problems.append(f"the creem product costs {prod.get('price')} but the site shows PRICE_CENTS="
                                f"{cfg.price_cents}")
        except payments.PaymentError as e:
            problems.append(f"creem {mode}: {e}")
    if not cfg.email_ready:
        problems.append("RESEND_API_KEY is not set: reports and alerts are not emailed")
    else:
        notes.append(f"email from {cfg.resend_from}, replies to {mailer.SUPPORT_EMAIL}, alerts to "
                     f"{cfg.alert_email or mailer.SUPPORT_EMAIL}")
        if email_to:
            ok, info = mailer._send(cfg, {"to": [email_to], "subject": "Weather Evidence test email",
                                          "text": "If you can read this, Resend accepts the key and the sender."})
            (notes if ok else problems).append(f"test email to {email_to}: {'sent, id ' + info if ok else info}")
    if not (cfg.legal_owner and cfg.legal_address):
        problems.append("LEGAL_OWNER and LEGAL_ADDRESS must be set, or the legal pages and imprint say Draft")
    if cfg.admin_password in ("", "change-me"):
        problems.append("ADMIN_PASSWORD is empty or still the example value")
    for n in notes:
        print(f"ok    {n}")
    for p in problems:
        print(f"FAIL  {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
