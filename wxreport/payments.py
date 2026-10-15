"""creem.io: hosted checkout sessions and signed webhooks.

Checkout: POST {base}/v1/checkouts with the x-api-key header → {checkout_url, id}.
Webhooks: the `creem-signature` header is the hex HMAC-SHA256 of the raw body keyed with the webhook secret;
the envelope is {"id", "eventType", "created_at", "object"}; for checkout.completed the object is the checkout,
carrying our request_id, metadata, order (amount in cents) and customer.
"""
import hashlib
import hmac

import requests

from .config import Settings


class PaymentError(Exception):
    pass


def create_checkout(cfg: Settings, order: dict) -> dict:
    body = {
        "product_id": cfg.creem_product_id,
        "request_id": order["id"],
        "success_url": f"{cfg.base_url}/orders/{order['id']}/{order['token']}",
        "customer": {"email": order["email"]},
        "metadata": {"order_id": order["id"], "loss_date": order["loss_date"]},
    }
    try:
        r = requests.post(f"{cfg.creem_api_base}/v1/checkouts", json=body, timeout=30,
                          headers={"x-api-key": cfg.creem_api_key, "Accept": "application/json"})
    except requests.RequestException as e:
        raise PaymentError(f"creem unreachable: {e}") from e
    if r.status_code >= 300:
        raise PaymentError(f"creem returned {r.status_code}: {r.text[:300]}")
    data = r.json()
    if not data.get("checkout_url"):
        raise PaymentError(f"creem response had no checkout_url: {str(data)[:300]}")
    return data


def verify_signature(raw_body: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.strip())


def order_ref(obj: dict) -> str | None:
    """Our order id from a checkout object (request_id first, then metadata)."""
    return obj.get("request_id") or (obj.get("metadata") or {}).get("order_id")
