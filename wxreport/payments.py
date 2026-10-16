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


def get_product(cfg: Settings) -> dict:
    """GET /v1/products/{id}: proves the key works against this base URL and shows what buyers will be charged."""
    try:
        r = requests.get(f"{cfg.creem_api_base}/v1/products/{cfg.creem_product_id}", timeout=30,
                         headers={"x-api-key": cfg.creem_api_key, "Accept": "application/json"})
    except requests.RequestException as e:
        raise PaymentError(f"creem unreachable: {e}") from e
    if r.status_code >= 300:
        raise PaymentError(f"creem returned {r.status_code}: {r.text[:300]}")
    return r.json()


def verify_signature(raw_body: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.strip())


def order_ref(obj: dict) -> str | None:
    """Our order id from a checkout object (request_id first, then metadata)."""
    return obj.get("request_id") or (obj.get("metadata") or {}).get("order_id")


def order_id_for(event_type: str, obj: dict, store) -> str | None:
    """Our order id for a webhook object.

    checkout.completed: the object is the checkout. refund.created and dispute.created: the object nests the
    checkout and creem's order, but creem's own dispute sample has a checkout without request_id or metadata, so
    fall back to the creem order id we stored when the checkout completed.
    """
    if event_type == "checkout.completed":
        return order_ref(obj)
    oid = order_ref(obj.get("checkout") or {}) or (obj.get("metadata") or {}).get("order_id")
    if oid:
        return oid
    creem_order = obj.get("order") or (obj.get("transaction") or {}).get("order")
    creem_order = creem_order.get("id") if isinstance(creem_order, dict) else creem_order
    hit = store.by_creem_order(creem_order) if creem_order else None
    return hit["id"] if hit else None


def money(cents, currency: str | None) -> str:
    if cents is None:
        return "an unknown amount"
    return f"{int(cents) / 100:.2f} {(currency or 'USD').upper()}"
