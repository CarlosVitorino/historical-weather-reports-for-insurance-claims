"""The /admin page: who came, how far they got, what sold, and every order's state."""
from datetime import datetime
from html import escape

from .config import Settings
from .store import FUNNEL, Store

CSS = """
:root{--ink:#1b2430;--muted:#5b6675;--rule:#e1e6ec;--accent:#1f4e79;--bg:#f7f9fb;--bad:#a33a2b;--good:#1e6b3a}
*{box-sizing:border-box}body{font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);
background:var(--bg);margin:0}main{max-width:72rem;margin:0 auto;padding:1.5rem 1rem 4rem}
h1{font-size:1.4rem;margin:0}h2{font-size:1.05rem;margin:2rem 0 .6rem}header{display:flex;flex-wrap:wrap;
gap:1rem;align-items:baseline;justify-content:space-between}nav a{margin-left:.6rem;color:var(--accent)}
nav a.on{font-weight:700;text-decoration:none;color:var(--ink)}
.kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(10.5rem,1fr));gap:.75rem;margin-top:1rem}
.kpi{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:.8rem 1rem}
.kpi b{display:block;font-size:1.5rem;font-variant-numeric:tabular-nums}.kpi span{color:var(--muted);font-size:.85rem}
.wrap{overflow-x:auto;background:#fff;border:1px solid var(--rule);border-radius:8px}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:.45rem .7rem;border-bottom:1px solid var(--rule);vertical-align:top;white-space:nowrap}
th{background:#eef2f6;font-weight:600}td.wrapok{white-space:normal;min-width:14rem}
.bar{height:.5rem;background:var(--accent);border-radius:3px;display:inline-block;vertical-align:middle}
.s-ready{color:var(--good);font-weight:600}.s-failed{color:var(--bad);font-weight:600}.muted{color:var(--muted)}
form.inline{display:inline}button{font:inherit;font-size:.8rem;padding:.15rem .5rem;cursor:pointer}
.warn{background:#fdf0e6;border:1px solid #f0c9a4;padding:.6rem .9rem;border-radius:6px;margin-top:1rem}
"""


def _money(cents) -> str:
    return f"${(cents or 0) / 100:,.2f}"


def _pct(a, b) -> str:
    return f"{100 * a / b:.0f}%" if b else "—"


def _ts(s: str | None) -> str:
    if not s:
        return ""
    return datetime.fromisoformat(s).strftime("%Y-%m-%d %H:%M")


def render_admin(cfg: Settings, store: Store, days: int) -> str:
    st = store.stats(days or None)
    c = st["counts"]
    n = lambda k: c.get(k, (0, 0))[0]  # noqa: E731
    label = {1: "last 24 hours", 7: "last 7 days", 30: "last 30 days", 90: "last 90 days", 0: "all time"}[days]
    nav = "".join(f'<a href="/admin?days={d}" class="{"on" if d == days else ""}">{t}</a>'
                  for d, t in ((1, "24h"), (7, "7d"), (30, "30d"), (90, "90d"), (0, "All")))
    warn = []
    if not cfg.payments_ready:
        warn.append("creem is not configured (CREEM_API_KEY, CREEM_PRODUCT_ID, CREEM_WEBHOOK_SECRET)"
                     + (" — DEV_FAKE_PAYMENTS is on" if cfg.fake_payments else ""))
    if not cfg.email_ready:
        warn.append("Resend is not configured (RESEND_API_KEY, RESEND_FROM): reports are not emailed")
    warn_html = "".join(f'<div class="warn">{escape(w)}</div>' for w in warn)

    kpis = [("Unique visitors", st["visitors"]), ("Page views", n("page_view")),
            ("Addresses checked", n("form_submit")), ("Went to payment", n("checkout_click")),
            ("Paid orders", st["paid_orders"]), ("Revenue", _money(st["revenue_cents"])),
            ("Visitor → paid", _pct(st["paid_orders"], st["visitors"])), ("Downloads", n("download")),
            ("Reports failed", n("report_failed")), ("Refunds", st["refunds"])]
    kpi_html = "".join(f'<div class="kpi"><b>{v}</b><span>{escape(k)}</span></div>' for k, v in kpis)

    # funnel: unique visitors at each step (orders for paid)
    steps = []
    for kind, text in FUNNEL:
        v = c.get(kind, (0, 0))[1] if kind != "paid" else st["paid_orders"]
        steps.append((text, v))
    top = steps[0][1] or 1
    funnel = "".join(
        f"<tr><td>{escape(t)}</td><td>{v}</td><td>{_pct(v, steps[i - 1][1]) if i else ''}</td>"
        f'<td><span class="bar" style="width:{max(2, 240 * v // top)}px"></span></td></tr>'
        for i, (t, v) in enumerate(steps))

    daily = "".join(
        f"<tr><td>{d['day']}</td><td>{d['visitors']}</td><td>{d['views']}</td><td>{d['submits']}</td>"
        f"<td>{d['clicks']}</td><td>{d['paid']}</td><td>{_money(d['revenue_cents'])}</td><td>{d['downloads']}</td></tr>"
        for d in st["daily"]) or '<tr><td colspan="8" class="muted">No activity yet.</td></tr>'
    refs = "".join(f"<tr><td>{escape(str(r['src']))}</td><td>{r['visitors']}</td><td>{r['views']}</td></tr>"
                   for r in st["referrers"]) or '<tr><td colspan="3" class="muted">No visits yet.</td></tr>'
    errs = "".join(f"<tr><td>{escape(str(r['reason']))}</td><td>{r['n']}</td></tr>"
                   for r in st["form_errors"]) or '<tr><td colspan="2" class="muted">None.</td></tr>'

    rows = []
    for o in store.orders(200):
        if o["status"] == "draft":
            continue
        act = ""
        if o["status"] == "failed":
            act = f'<form class="inline" method="post" action="/admin/orders/{o["id"]}/retry"><button>Retry</button></form>'
        if o["status"] == "ready":
            act = (f'<a href="/admin/orders/{o["id"]}/report.pdf">PDF</a> '
                   f'<form class="inline" method="post" action="/admin/orders/{o["id"]}/resend"><button>Re-send email</button></form>')
        err = f'<br><span class="muted">{escape((o["error"] or "").splitlines()[0][:160])}</span>' if o["error"] else ""
        rows.append(
            f"<tr><td>{_ts(o['created_at'])}</td><td class=\"s-{o['status']}\">{o['status']}{err}</td>"
            f"<td class=\"wrapok\">{escape(o['matched_address'] or o['address'])}"
            f"<br><span class=\"muted\">{escape(o['county'] or '')}</span></td><td>{o['loss_date']}</td>"
            f"<td>{escape(o['email'])}</td><td>{_money(o['amount_cents']) if o['amount_cents'] else ''}</td>"
            f"<td>{o['report_id'] or ''}</td><td>{o['email_status'] or ''}</td><td>{act}</td></tr>")
    orders = "".join(rows) or '<tr><td colspan="9" class="muted">No orders yet.</td></tr>'
    by_status = ", ".join(f"{k}: {v}" for k, v in sorted(st["orders_by_status"].items()) if k != "draft") or "none"

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Admin · Loss-Site Weather Report</title><style>{CSS}</style></head><body><main>
<header><h1>Sales and traffic <span class="muted" style="font-weight:400">· {label}</span></h1><nav>{nav}</nav></header>
{warn_html}<div class="kpis">{kpi_html}</div>
<h2>Funnel (unique visitors per step)</h2><div class="wrap"><table><tr><th>Step</th><th>Visitors</th>
<th>From previous</th><th></th></tr>{funnel}</table></div>
<h2>By day (UTC)</h2><div class="wrap"><table><tr><th>Day</th><th>Visitors</th><th>Views</th><th>Address checked</th>
<th>To payment</th><th>Paid</th><th>Revenue</th><th>Downloads</th></tr>{daily}</table></div>
<h2>Where visitors came from</h2><div class="wrap"><table><tr><th>Source (utm_source or referrer)</th><th>Visitors</th>
<th>Views</th></tr>{refs}</table></div>
<h2>Why order forms were rejected</h2><div class="wrap"><table><tr><th>Reason</th><th>Count</th></tr>{errs}</table></div>
<h2 id="orders">Orders <span class="muted" style="font-weight:400;font-size:.9rem">({escape(by_status)})</span></h2>
<div class="wrap"><table><tr><th>Created (UTC)</th><th>Status</th><th>Location</th><th>Loss date</th><th>Email</th>
<th>Paid</th><th>Report ID</th><th>Email</th><th></th></tr>{orders}</table></div>
<p class="muted">Visitors are counted by an anonymous first-party cookie; no IP addresses are stored.</p>
</main></body></html>"""
