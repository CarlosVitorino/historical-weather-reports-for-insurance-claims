import gzip
import sqlite3
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from wxreport import config, housekeeping
from wxreport.fulfil import order_dir
from wxreport.ratelimit import DailyBudget, Limiter
from wxreport.store import Store


def setup(tmp_path):
    cfg = replace(config.load(), data_dir=tmp_path, backup_keep=2, draft_ttl_hours=24)
    return cfg, Store(tmp_path / "app.db")


def test_purges_old_drafts_only(tmp_path):
    cfg, store = setup(tmp_path)
    old = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()
    stale = store.create_order(email="a@b.co", address="x", loss_date="2026-02-19")
    fresh = store.create_order(email="a@b.co", address="x", loss_date="2026-02-19")
    at_checkout = store.create_order(email="a@b.co", address="x", loss_date="2026-02-19")
    store.update(stale["id"], created_at=old)
    store.update(at_checkout["id"], created_at=old, status="checkout")   # creem may still confirm it
    (order_dir(cfg, stale["id"]) / "snapshots").mkdir(parents=True)
    assert housekeeping.purge_drafts(cfg, store) == 1
    assert store.get(stale["id"]) is None and not order_dir(cfg, stale["id"]).exists()
    assert store.get(fresh["id"]) and store.get(at_checkout["id"])


def test_backup_is_a_readable_database_and_rotates(tmp_path):
    cfg, store = setup(tmp_path)
    store.create_order(email="a@b.co", address="x", loss_date="2026-02-19")
    target = housekeeping.backup_db(cfg, store)
    copy = tmp_path / "restored.db"
    copy.write_bytes(gzip.decompress(target.read_bytes()))
    assert sqlite3.connect(copy).execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1
    for day in ("20260101", "20260102", "20260103"):
        (tmp_path / "backups" / f"app-{day}.db.gz").write_bytes(b"")
    housekeeping.backup_db(cfg, store)
    assert len(list((tmp_path / "backups").glob("app-*.db.gz"))) == 2 and target.exists()


def test_limiter_window_slides():
    t = [0.0]
    lim = Limiter({"GET /api/x": (2, 60), "POST /order/": (1, 60)}, clock=lambda: t[0])
    assert [lim.allow("GET", "/api/x", "1.1.1.1") for _ in range(3)] == [True, True, False]
    assert lim.allow("GET", "/api/x", "2.2.2.2")          # per client
    assert lim.allow("POST", "/order/a/b/checkout", "1.1.1.1") and not lim.allow("POST", "/order/c/d/checkout", "1.1.1.1")
    t[0] = 61
    assert lim.allow("GET", "/api/x", "1.1.1.1")


def test_daily_budget_resets_at_midnight_utc():
    t = [86400 * 100 + 5]
    b = DailyBudget(2, clock=lambda: t[0])
    assert [b.take(), b.take(), b.take()] == [True, True, False]
    t[0] += 86400
    assert b.take()
