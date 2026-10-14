"""Order page. Phase 2 skeleton: the form posts to /order; creem.io checkout and webhook fulfilment come next."""
from datetime import date

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Loss-Site Weather Report")

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Loss-Site Weather Report</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:34rem;margin:2rem auto;padding:0 1rem;color:#1b2430}}
label{{display:block;margin-top:1rem;font-weight:600}}input{{width:100%;padding:.5rem;font:inherit;box-sizing:border-box}}
button{{margin-top:1.5rem;padding:.6rem 1.2rem;font:inherit;background:#1f4e79;color:#fff;border:0;border-radius:4px}}
.note{{color:#5b6675;font-size:.9rem}}</style></head><body>
<h1>Loss-Site Weather Report</h1>
<p>A PDF of the US government weather records for one address and one past date: station measurements
with distance and bearing, NWS warnings and storm reports, NCEI Storm Events, hail and lightning. $9.99.</p>
{body}</body></html>"""

FORM = """<form method="post" action="/order">
<label>Loss address<input name="address" required placeholder="401 N College Ave, Bloomington, IN 47404"></label>
<label>Loss date<input type="date" name="loss_date" required max="{max}"></label>
<label>Email for delivery<input type="email" name="email" required></label>
<button type="submit">Continue to payment</button>
<p class="note">Not a certified government record or expert opinion. Records near the site do not by
themselves establish conditions at the property.</p></form>"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return PAGE.format(body=FORM.format(max=date.today().isoformat()))


@app.post("/order", response_class=HTMLResponse)
def order(address: str = Form(...), loss_date: str = Form(...), email: str = Form(...)) -> HTMLResponse:
    return HTMLResponse(PAGE.format(body="<p>Checkout is not enabled yet.</p>"), status_code=503)
