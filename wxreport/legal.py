"""Terms, privacy and refund pages: what creem's account review checks (docs.creem.io → Account Reviews).

The review wants Terms and Privacy reachable without signing in, the price visible, a support email that matches the
one in creem's Business Details, and buyers told before paying that creem is the merchant of record (creem merchant
terms 3.7). The owner's legal name and governing law come from LEGAL_OWNER and LEGAL_LAW; until LEGAL_OWNER is set
the pages say they are drafts, and the review would reject them. /imprint is the Impressum: the operator is in
Germany, so § 5 DDG applies even though buyers are in the US. It needs LEGAL_ADDRESS (a postal address).
"""
from datetime import date
from html import escape

from . import BRAND, DOMAIN, SUPPORT_EMAIL
from .config import Settings
from .content import Page

UPDATED = date(2026, 10, 30)
PATHS = ("/terms", "/privacy", "/refunds", "/imprint")
MAIL = f'<a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>'


def _price(cfg: Settings) -> str:
    return f"${cfg.price_cents / 100:.2f}"


def _owner(cfg: Settings) -> str:
    return cfg.legal_owner or "[legal name of the business]"


def _draft(cfg: Settings) -> str:
    return "" if cfg.legal_owner and cfg.legal_address else '<p class="err">Draft: not yet reviewed.</p>'


def _address(cfg: Settings) -> str:
    """LEGAL_ADDRESS, lines separated by "|": "Musterstr. 1 | 10115 Berlin | Germany"."""
    if not cfg.legal_address:
        return "[postal address]"
    parts = [x.strip() for x in cfg.legal_address.split("|") if x.strip()]
    return "<br>".join(escape(x) for x in parts)


def terms(cfg: Settings) -> Page:
    price = _price(cfg)
    return Page(
        path="/terms", title=f"Terms of service — {BRAND}", h1="Terms of service", eyebrow="Legal", updated=UPDATED,
        description=f"The terms for buying a {BRAND} report: one PDF for one US address and date of loss, {price}, "
                    "paid through Creem as merchant of record.",
        body=f"""{_draft(cfg)}
<p>These terms apply when you use {DOMAIN} or order a report. By ordering you agree to them, and to our
<a href="/privacy">Privacy policy</a> and <a href="/refunds">Refund policy</a>.</p>

<h2>Who we are</h2>
<p>{BRAND} ({DOMAIN}) is run by {_owner(cfg)}, {_address(cfg).replace("<br>", ", ")}. Support: {MAIL}. We answer within 3 business days.</p>

<h2>What you buy</h2>
<p>One PDF report for one US address and one date of loss. It compiles public US government weather records
(NOAA, the National Weather Service, NEXRAD radar and the US Census Bureau geocoder) and gives each record's distance
and direction from the location you confirmed before paying. The report is usually ready in about a minute; you
download it from your order page and we email a copy to the address you gave.</p>

<h2>What the report is not</h2>
<ul>
<li>It is not a certified government record, an expert opinion, or legal or insurance advice.</li>
<li>It does not decide a claim. Whether a claim is paid is up to the insurer and the policy.</li>
<li>It shows what the public records contain. Stations can be miles from the property, records can have gaps, and
NOAA publishes its Storm Events database a few months after each month ends. The report says when that applies.</li>
</ul>

<h2>Prices and payment</h2>
<ul>
<li>Each report costs {price} (US dollars), paid once. There is no subscription and nothing renews.</li>
<li>Our order process is conducted by our online reseller Creem (creem.io). Creem is the merchant of record for all
our orders: it processes the payment, calculates any sales tax or VAT, issues your receipt, and handles payment
questions and refunds together with us. Creem's own terms also apply to the purchase.</li>
</ul>

<h2>Using the report</h2>
<ul>
<li>You may use the report for your claim and share it with anyone involved in it, such as your insurer, adjuster,
attorney or contractor.</li>
<li>You must not resell the reports or offer them as your own product or service.</li>
<li>You must not use the site to break the law, or overload, scrape or attack it.</li>
</ul>

<h2>Liability</h2>
<p>The report is provided as is. To the extent the law allows, our total liability to you is limited to what you
paid for the report the claim is about. Nothing here limits rights you have as a consumer that can't be limited by
contract.</p>

<h2>Changes and governing law</h2>
<p>We may update these terms; the date above shows when. These terms are governed by the laws of {cfg.legal_law}.
If you buy as a consumer, you keep the protection of the mandatory consumer laws of the country where you live.</p>""")


def privacy(cfg: Settings) -> Page:
    rows = [
        ("Your email address", "To deliver the report and answer you about the order", "With the order"),
        ("The address, map pin and date of loss you enter", "To build the report", "With the order"),
        ("The report and the weather records it was built from", "So you can download it again, and so a report ID "
         "always identifies the same file", "With the order"),
        ("Your purchase: amount, time and Creem order number", "Our accounts", "As long as tax law requires"),
        ("A random visitor id, the pages you open, the site that sent you and any campaign tags in the link",
         "To see how people find the site and where ordering goes wrong", "Until we delete old statistics"),
    ]
    table = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return Page(
        path="/privacy", title=f"Privacy policy — {BRAND}", h1="Privacy policy", eyebrow="Legal", updated=UPDATED,
        description=f"What {BRAND} keeps about you and why: your email and order details, a random visitor id. "
                    "No advertising trackers, nothing sold.",
        body=f"""{_draft(cfg)}
<p>{_owner(cfg)} runs {DOMAIN} and is responsible for your data (the controller under the GDPR):</p>
<p>{_owner(cfg)}<br>{_address(cfg)}<br>{MAIL}</p>
<p> We collect what we need to
build and deliver your report, sell nothing, and use no advertising trackers.</p>

<h2>What we keep, and why</h2>
<table class="ctable"><thead><tr><th>What</th><th>Why</th><th>How long</th></tr></thead><tbody>{table}</tbody></table>
<p>We don't store your network (IP) address. The legal basis is our contract with you, plus our legitimate interest
in running and improving the site.</p>

<h2>Cookies</h2>
<p>One first-party cookie holding a random visitor id, kept for a year, so we can count visits and connect an order
to the visit it came from. No advertising or third-party tracking cookies.</p>

<h2>Visit statistics</h2>
<p>We count visits to our public pages with Umami, which we run on our own server. It sets no cookies and does not
store your network (IP) address. It records the page, the site that sent you, your browser, device type and country,
and a few clicks such as opening the order page. It never sees your address, email or order: order pages are not
counted, and anything typed into a link is removed before it is sent.</p>

<h2>Who else sees your data</h2>
<ul>
<li><strong>Creem</strong> processes payments as merchant of record. We never see your card details.</li>
<li><strong>Resend</strong> sends the email with your report.</li>
<li><strong>Address lookup:</strong> what you type in the address box is sent to Geoapify or Photon (komoot) for
suggestions, and to the US Census Bureau geocoder to find the location.</li>
<li><strong>Maps:</strong> your browser loads map tiles from OpenStreetMap and the US Geological Survey, which see
your network address as any website does.</li>
<li><strong>Weather data:</strong> public services such as NOAA and the Iowa Environmental Mesonet receive the
location and date of the report, never your email.</li>
<li><strong>Our hosting provider</strong> runs the server the site and your orders are stored on.</li>
</ul>

<h2>Your rights</h2>
<p>You can ask to see, correct, export or delete your data at any time by writing to {MAIL}. We keep purchase
records as long as tax law requires. You can also complain to your data protection authority.</p>""")


def refunds(cfg: Settings) -> Page:
    return Page(
        path="/refunds", title=f"Refund policy — {BRAND}", h1="Refund policy", eyebrow="Legal", updated=UPDATED,
        description=f"{BRAND} refunds: a report that can't be built is refunded, a broken report is redone or "
                    "refunded within 14 days.",
        body=f"""{_draft(cfg)}
<ul>
<li><strong>Report can't be built:</strong> we're notified automatically and will deliver the report or refund
you in full.</li>
<li><strong>Broken report:</strong> if the PDF won't open, is for a different location or date than the one you
confirmed, or is missing sections because of an error on our side, write to us within 14 days and we'll redo it or
refund it.</li>
<li>A report delivered as ordered can't be refunded. You see the exact location and date before paying, and the
report is built for you and delivered straight away, so the digital service has then been fully provided. A report
that finds little or no severe weather is still delivered as ordered.</li>
</ul>
<p>To ask for a refund, write to {MAIL} from the email address you ordered with, and include the report ID or the
link to your order. Refunds are paid by Creem, our merchant of record, to the card you paid with, usually within
5–10 days.</p>""")


def imprint(cfg: Settings) -> Page:
    """The Impressum a site run from Germany must carry (§ 5 DDG), whoever its buyers are."""
    phone = f"<br>Phone: {escape(cfg.legal_phone)}" if cfg.legal_phone else ""
    vat = (f"<h2>VAT ID</h2><p>VAT identification number under § 27a of the German VAT Act (UStG): "
           f"{escape(cfg.legal_vat_id)}</p>") if cfg.legal_vat_id else ""
    return Page(
        path="/imprint", title=f"Imprint (Impressum) — {BRAND}", h1="Imprint", eyebrow="Legal", updated=UPDATED,
        description=f"Who runs {BRAND} ({DOMAIN}) and how to reach them.",
        body=f"""{_draft(cfg)}
<p>Information under § 5 of the German Digital Services Act (DDG).</p>
<h2>Operator</h2>
<p>{_owner(cfg)}<br>{_address(cfg)}</p>
<h2>Contact</h2>
<p>Email: {MAIL}{phone}</p>
{vat}
<h2>Payments</h2>
<p>Orders are sold and invoiced by our reseller Creem (creem.io), the merchant of record. Receipts and tax come
from Creem.</p>""")


PAGES = {"/terms": terms, "/privacy": privacy, "/refunds": refunds, "/imprint": imprint}
