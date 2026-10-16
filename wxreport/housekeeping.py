"""Nightly chores, run in a daemon thread inside the one server process: delete stale drafts, copy the database.

The database copy lands in DATA_DIR/backups/. It protects against a bad write or a mistaken delete, not against
losing the disk: deploy/backup-offsite.sh copies DATA_DIR (these copies plus every order's PDF and snapshot) off
the machine.
"""
import gzip
import logging
import shutil
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .fulfil import order_dir
from .store import Store

log = logging.getLogger("wxreport.housekeeping")
INTERVAL = 24 * 3600


def purge_drafts(cfg: Settings, store: Store) -> int:
    ids = store.stale_drafts(cfg.draft_ttl_hours)
    for oid in ids:
        store.delete(oid)
        shutil.rmtree(order_dir(cfg, oid), ignore_errors=True)
    return len(ids)


def backup_db(cfg: Settings, store: Store) -> Path:
    folder = cfg.data_dir / "backups"
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")   # one per day: a restart replaces today's copy
    raw = folder / f"app-{stamp}.db"
    store.backup(raw)
    target = raw.with_suffix(".db.gz")
    with raw.open("rb") as f, gzip.open(target, "wb") as g:
        shutil.copyfileobj(f, g)
    raw.unlink()
    for old in sorted(folder.glob("app-*.db.gz"))[:-cfg.backup_keep]:
        old.unlink()
    return target


def run_once(cfg: Settings, store: Store) -> dict:
    out = {"drafts_deleted": purge_drafts(cfg, store), "backup": backup_db(cfg, store).name}
    store.log("housekeeping", **out)
    return out


def start(cfg: Settings, store: Store) -> threading.Thread:
    def loop():
        while True:
            try:
                log.info("housekeeping: %s", run_once(cfg, store))
            except Exception:  # noqa: BLE001 — a failed chore must not kill the thread; it retries tomorrow
                log.exception("housekeeping failed")
            time.sleep(INTERVAL)

    t = threading.Thread(target=loop, name="housekeeping", daemon=True)
    t.start()
    return t
