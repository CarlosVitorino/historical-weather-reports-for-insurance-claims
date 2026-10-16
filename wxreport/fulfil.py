"""Turn a paid order into a delivered report. Runs in a small background thread pool."""
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import mailer
from .config import Settings
from .report import build_pdf, gather
from .store import Store, now

log = logging.getLogger("wxreport.fulfil")


def order_dir(cfg: Settings, oid: str) -> Path:
    return cfg.data_dir / "orders" / oid


class Fulfiller:
    def __init__(self, cfg: Settings, store: Store, workers: int = 2):
        self.cfg, self.store = cfg, store
        self.pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="fulfil")

    def submit(self, oid: str):
        return self.pool.submit(self.run, oid)

    def resume(self) -> None:
        """Re-queue orders interrupted by a restart."""
        for oid in self.store.pending_work():
            self.store.update(oid, status="paid")
            self.submit(oid)

    def run(self, oid: str) -> None:
        if not self.store.transition(oid, ("paid",), "generating"):
            return
        o = self.store.get(oid)
        try:
            ctx = gather(o["address"], o["loss_date"], lat=o["lat"], lon=o["lon"],
                         root=order_dir(self.cfg, oid) / "snapshots")
            pdf = build_pdf(ctx)
            path = order_dir(self.cfg, oid) / f"{ctx.report_id}.pdf"
            path.write_bytes(pdf)
        except Exception as e:  # noqa: BLE001 — any failure must reach the admin page, not vanish in a thread
            log.exception("report failed for %s", oid)
            self.store.update(oid, status="failed", error=f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}")
            self.store.log("report_failed", order_id=oid, error=f"{type(e).__name__}: {e}"[:300])
            self.alert(oid, "Report failed", f"The report for a paid order could not be built.\n\n"
                       f"{type(e).__name__}: {e}\n\nRetry it from the admin page, or refund it in creem.")
            return
        self.store.update(oid, status="ready", report_id=ctx.report_id, pdf_path=str(path), ready_at=now(), error=None)
        self.store.log("report_ready", order_id=oid, report_id=ctx.report_id)
        self.email(oid)

    def email(self, oid: str) -> None:
        o = self.store.get(oid)
        link = f"{self.cfg.base_url}/orders/{oid}/{o['token']}"
        ok, info = mailer.send_report(self.cfg, o, Path(o["pdf_path"]).read_bytes(), link)
        status = "sent" if ok else ("skipped" if info == "email not configured" else "failed")
        self.store.update(oid, email_status=status)
        self.store.log("email_sent" if ok else "email_failed", order_id=oid, info=info[:300])
        if status == "failed":
            self.alert(oid, "Report email failed", f"The report is ready but the email to {o['email']} failed.\n\n"
                       f"{info}\n\nThe buyer can still download it from the order page. Re-send it from the admin page.")

    def alert(self, oid: str | None, subject: str, text: str) -> None:
        """Tell the operator. Never raises: an alert that can't be sent is logged and shown on /admin."""
        o = self.store.get(oid) if oid else None
        if o:
            text = (f"{text}\n\nOrder {oid} · {o['status']}\n{o.get('matched_address') or o['address']} · "
                    f"loss date {o['loss_date']}\nBuyer: {o['email']}")
        ok, info = mailer.send_alert(self.cfg, subject, text)
        if not ok:
            log.warning("alert not sent (%s): %s", info, subject)
        self.store.log("alert_sent" if ok else "alert_failed", order_id=oid, subject=subject, info=info[:300])

    def alert_later(self, oid: str | None, subject: str, text: str) -> None:
        """Same, off the request thread (webhooks must answer creem quickly)."""
        self.pool.submit(self.alert, oid, subject, text)
