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
