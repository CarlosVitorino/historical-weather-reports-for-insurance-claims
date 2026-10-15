"""Report delivery by email through Resend (https://resend.com): a link plus the PDF attached."""
import base64

import requests

from . import PRODUCT
from .config import Settings


def send_report(cfg: Settings, order: dict, pdf: bytes, link: str) -> tuple[bool, str]:
    if not cfg.email_ready:
        return False, "email not configured"
    html = f"""<p>Your {PRODUCT} is ready.</p>
<p><b>{_esc(order.get('matched_address') or order['address'])}</b> · loss date {order['loss_date']}<br>
Report ID: {order['report_id']}</p>
<p><a href="{link}">Download the report (PDF)</a> — the PDF is also attached.</p>
<p style="color:#5b6675;font-size:13px">The report compiles public US government weather records. It is not a
certified government record or expert opinion. Keep the report ID: the same ID always identifies the same file.</p>"""
    body = {"from": cfg.resend_from, "to": [order["email"]],
            "subject": f"Your weather report for {order['loss_date']} — {order['report_id']}",
            "html": html,
            "attachments": [{"filename": f"{order['report_id']}.pdf", "content": base64.b64encode(pdf).decode()}]}
    try:
        r = requests.post("https://api.resend.com/emails", json=body, timeout=30,
                          headers={"Authorization": f"Bearer {cfg.resend_api_key}"})
    except requests.RequestException as e:
        return False, f"Resend unreachable: {e}"
    if r.status_code >= 300:
        return False, f"Resend {r.status_code}: {r.text[:300]}"
    return True, r.json().get("id", "")


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
