"""Email through Resend (https://resend.com): the report to the buyer, and alerts to the operator.

Sender: RESEND_FROM, default "Weather Evidence <report@weatherevidence.com>". Replies go to SUPPORT_EMAIL.
Alerts go to ALERT_EMAIL, default SUPPORT_EMAIL. weatherevidence.com must be a verified domain in Resend.
"""
import base64

import requests

from . import BRAND, PRODUCT, SUPPORT_EMAIL
from .config import Settings

RESEND = "https://api.resend.com/emails"


def _send(cfg: Settings, body: dict) -> tuple[bool, str]:
    if not cfg.email_ready:
        return False, "email not configured"
    try:
        r = requests.post(RESEND, json={"from": cfg.resend_from, "reply_to": SUPPORT_EMAIL, **body}, timeout=30,
                          headers={"Authorization": f"Bearer {cfg.resend_api_key}"})
    except requests.RequestException as e:
        return False, f"Resend unreachable: {e}"
    if r.status_code >= 300:
        return False, f"Resend {r.status_code}: {r.text[:300]}"
    return True, r.json().get("id", "")


def send_report(cfg: Settings, order: dict, pdf: bytes, link: str) -> tuple[bool, str]:
    where = order.get("matched_address") or order["address"]
    html = f"""<p>Your {PRODUCT} is ready.</p>
<p><b>{_esc(where)}</b> · loss date {order['loss_date']}<br>
Report ID: {order['report_id']}</p>
<p><a href="{link}">Download the report (PDF)</a> — the PDF is also attached.</p>
<p style="color:#5b6675;font-size:13px">The report compiles public US government weather records. It is not a
certified government record or expert opinion. Keep the report ID: the same ID always identifies the same file.</p>
<p style="color:#5b6675;font-size:13px">Questions or a problem with the report? Reply to this email or write to
<a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>.</p>"""
    text = f"""Your {PRODUCT} is ready.

{where} · loss date {order['loss_date']}
Report ID: {order['report_id']}

Download the report (PDF): {link}
The PDF is also attached.

The report compiles public US government weather records. It is not a certified government record or expert
opinion. Keep the report ID: the same ID always identifies the same file.

Questions or a problem with the report? Reply to this email or write to {SUPPORT_EMAIL}.
"""
    return _send(cfg, {"to": [order["email"]],
                       "subject": f"Your weather report for {order['loss_date']} — {order['report_id']}",
                       "html": html, "text": text,
                       "attachments": [{"filename": f"{order['report_id']}.pdf",
                                        "content": base64.b64encode(pdf).decode()}]})


def send_alert(cfg: Settings, subject: str, text: str) -> tuple[bool, str]:
    """A plain-text note to the operator: a failed report or email, a refund, a dispute, a new sale."""
    return _send(cfg, {"to": [cfg.alert_email or SUPPORT_EMAIL], "subject": f"[{BRAND}] {subject}",
                       "text": f"{text}\n\nAdmin: {cfg.base_url}/admin#orders\n"})


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
