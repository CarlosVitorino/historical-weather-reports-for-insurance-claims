"""Orders and the event log, in one SQLite file. Small, durable, and easy to inspect by hand."""
import json
import secrets
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    visitor TEXT,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    loss_date TEXT NOT NULL,
    lat REAL,
    lon REAL,
    matched_address TEXT,
    county TEXT,
    status TEXT NOT NULL,          -- draft | checkout | paid | generating | ready | failed | refunded
    checkout_id TEXT,
    creem_order_id TEXT,
    amount_cents INTEGER,
    currency TEXT,
    paid_at TEXT,
    report_id TEXT,
    pdf_path TEXT,
    ready_at TEXT,
    email_status TEXT,             -- sent | failed | skipped
    error TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    kind TEXT NOT NULL,            -- page_view | form_submit | form_error | checkout_click | paid | report_ready |
                                   -- report_failed | email_sent | email_failed | download | refund | webhook
    visitor TEXT,
    order_id TEXT,
    detail TEXT
);
CREATE INDEX IF NOT EXISTS events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS events_kind ON events(kind);
CREATE TABLE IF NOT EXISTS webhook_events (id TEXT PRIMARY KEY, received_at TEXT NOT NULL);
"""

FUNNEL = [("page_view", "Visited the home page"), ("order_view", "Opened the order page"),
          ("form_submit", "Address and date accepted"),
          ("checkout_click", "Went to payment"), ("paid", "Paid"), ("download", "Downloaded the report")]


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.Lock()
        with self._conn() as c:
            c.executescript(SCHEMA)
            cols = {r[1] for r in c.execute("PRAGMA table_info(orders)")}
            for col in ("site_lat REAL", "site_lon REAL"):      # added after v1: where the report is centred
                if col.split()[0] not in cols:
                    c.execute(f"ALTER TABLE orders ADD COLUMN {col}")

    @contextmanager
    def _conn(self):
        with self._lock:
            c = sqlite3.connect(self.path)
            c.row_factory = sqlite3.Row
            try:
                yield c
                c.commit()
            finally:
                c.close()

    # -- events ----------------------------------------------------------------------------
    def log(self, kind: str, visitor: str | None = None, order_id: str | None = None, **detail) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO events (ts, kind, visitor, order_id, detail) VALUES (?,?,?,?,?)",
                      (now(), kind, visitor, order_id, json.dumps(detail, sort_keys=True) if detail else None))

    def seen_webhook(self, event_id: str) -> bool:
        """Record a webhook event ID; True if it was already processed (creem may retry deliveries)."""
        with self._conn() as c:
            try:
                c.execute("INSERT INTO webhook_events (id, received_at) VALUES (?,?)", (event_id, now()))
                return False
            except sqlite3.IntegrityError:
                return True

    # -- orders ----------------------------------------------------------------------------
    def create_order(self, **fields) -> dict:
        oid = "ord_" + secrets.token_hex(8)
        row = {"id": oid, "token": secrets.token_urlsafe(24), "created_at": now(), "updated_at": now(),
               "status": "draft", **fields}
        with self._conn() as c:
            c.execute(f"INSERT INTO orders ({','.join(row)}) VALUES ({','.join('?' * len(row))})", list(row.values()))
        return row

    def get(self, oid: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
        return dict(r) if r else None

    def update(self, oid: str, **fields) -> None:
        fields["updated_at"] = now()
        with self._conn() as c:
            c.execute(f"UPDATE orders SET {','.join(f'{k}=?' for k in fields)} WHERE id=?", [*fields.values(), oid])

    def delete(self, oid: str) -> None:
        with self._conn() as c:
            c.execute("DELETE FROM orders WHERE id=? AND status='draft'", (oid,))

    def transition(self, oid: str, from_states: tuple, to: str, **fields) -> bool:
        """Atomic status change; False if the order wasn't in one of from_states (keeps webhooks idempotent)."""
        fields = {"status": to, "updated_at": now(), **fields}
        with self._conn() as c:
            cur = c.execute(f"UPDATE orders SET {','.join(f'{k}=?' for k in fields)} "
                            f"WHERE id=? AND status IN ({','.join('?' * len(from_states))})",
                            [*fields.values(), oid, *from_states])
            return cur.rowcount == 1

    def orders(self, limit: int = 100, status: str | None = None) -> list[dict]:
        q, args = "SELECT * FROM orders", []
        if status:
            q += " WHERE status=?"
            args.append(status)
        q += " ORDER BY created_at DESC LIMIT ?"
        with self._conn() as c:
            return [dict(r) for r in c.execute(q, [*args, limit]).fetchall()]

    def pending_work(self) -> list[str]:
        with self._conn() as c:
            return [r[0] for r in c.execute("SELECT id FROM orders WHERE status IN ('paid','generating')")]

    # -- stats -----------------------------------------------------------------------------
    def stats(self, days: int | None) -> dict:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0).isoformat() \
            if days else "0000"
        with self._conn() as c:
            counts = {r["kind"]: (r["n"], r["v"]) for r in c.execute(
                "SELECT kind, COUNT(*) n, COUNT(DISTINCT visitor) v FROM events WHERE ts>=? GROUP BY kind", (since,))}
            visitors = c.execute("SELECT COUNT(DISTINCT visitor) FROM events WHERE ts>=? AND kind='page_view'",
                                 (since,)).fetchone()[0]
            rev = c.execute("SELECT COUNT(*), COALESCE(SUM(amount_cents),0) FROM orders WHERE paid_at>=? AND "
                            "status!='refunded'", (since,)).fetchone()
            refunds = c.execute("SELECT COUNT(*) FROM orders WHERE status='refunded' AND updated_at>=?",
                                (since,)).fetchone()[0]
            daily = [dict(r) for r in c.execute(
                """SELECT substr(ts,1,10) day,
                          COUNT(DISTINCT CASE WHEN kind='page_view' THEN visitor END) visitors,
                          SUM(kind='page_view') views, SUM(kind='form_submit') submits,
                          SUM(kind='checkout_click') clicks, SUM(kind='paid') paid, SUM(kind='download') downloads
                   FROM events WHERE ts>=? GROUP BY day ORDER BY day DESC LIMIT 60""", (since,))]
            revenue_by_day = {r[0]: r[1] for r in c.execute(
                "SELECT substr(paid_at,1,10), SUM(amount_cents) FROM orders WHERE paid_at>=? AND status!='refunded' "
                "GROUP BY 1", (since,))}
            errors = [dict(r) for r in c.execute(
                "SELECT json_extract(detail,'$.reason') reason, COUNT(*) n FROM events WHERE ts>=? AND "
                "kind='form_error' GROUP BY 1 ORDER BY n DESC", (since,))]
            referrers = [dict(r) for r in c.execute(
                """SELECT COALESCE(json_extract(detail,'$.utm_source'), json_extract(detail,'$.referrer'), '(direct)') src,
                          COUNT(*) views, COUNT(DISTINCT visitor) visitors
                   FROM events WHERE ts>=? AND kind='page_view' GROUP BY 1 ORDER BY visitors DESC LIMIT 15""",
                (since,))]
            by_status = {r[0]: r[1] for r in c.execute(
                "SELECT status, COUNT(*) FROM orders WHERE created_at>=? GROUP BY 1", (since,))}
        for d in daily:
            d["revenue_cents"] = revenue_by_day.get(d["day"], 0)
        return {"counts": counts, "visitors": visitors, "paid_orders": rev[0], "revenue_cents": rev[1],
                "refunds": refunds, "daily": daily, "form_errors": errors, "referrers": referrers,
                "orders_by_status": by_status}
