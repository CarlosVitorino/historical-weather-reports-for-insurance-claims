"""Public pages: the landing/order page and the buyer's order pages, with one shared look.

Audience: adjusters, public adjusters, roofing contractors, attorneys and policyholders documenting a loss.
The look is "evidence file", not "startup": paper-white documents on a deep storm-navy ground, Geist for type
(Geist Mono for IDs, hashes and source references), tabular figures, and one warning-amber accent used sparingly. The product sells itself best by
being shown, so the real sample report is the hero image and the proof section.
"""
from datetime import date, timedelta
from html import escape

from .report import MIN_DATE

from . import BRAND, DOMAIN
PRICE = "$9.99"
SAMPLE = {
    "place": "Bloomington, IN",
    "date": "February 19, 2026",
    "pages": 25,
    "pdf": "/static/sample-report.pdf",
    "id": "WE-2026-02-19-8F0B0A49121B",
}

# Self-hosted (SIL OFL, see /static/fonts/OFL.txt): no third-party requests from buyers' browsers.
FONT_FACES = """
@font-face{font-family:Geist;src:url(/static/fonts/Geist-Variable.woff2) format("woff2");font-weight:100 900;
  font-style:normal;font-display:swap}
@font-face{font-family:"Geist Mono";src:url(/static/fonts/GeistMono-Variable.woff2) format("woff2");font-weight:100 900;
  font-style:normal;font-display:swap}
"""
FONTS = '<link rel="preload" href="/static/fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin>'

CSS = FONT_FACES + """
:root{
  --navy-950:#07111f;--navy-900:#0b1a2e;--navy-800:#12263f;--navy-700:#1c3554;--navy-100:#e6ecf3;
  --ink:#14202e;--body:#344254;--muted:#5d6b7c;--rule:#dfe4ea;--paper:#fbfaf7;--white:#fff;
  --amber:#f2a93b;--amber-ink:#8a5a0b;--amber-50:#fdf5e8;--green:#1f7a4d;--red:#a33a2b;
  --sans:Geist,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"Geist Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --radius:10px;--shadow:0 1px 2px rgba(7,17,31,.06),0 8px 24px rgba(7,17,31,.08);
  --doc-shadow:0 2px 4px rgba(0,0,0,.18),0 24px 60px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font:16px/1.6 var(--sans);color:var(--body);background:var(--paper);
  -webkit-font-smoothing:antialiased}
.fact .num,.case .v,.price-card .amount,.rid,.callout b{font-variant-numeric:tabular-nums}
a{color:var(--navy-700)}
img{max-width:100%;display:block}
.wrap{max-width:1160px;margin:0 auto;padding:0 24px}
h1,h2,h3{color:var(--ink);font-family:var(--sans);font-weight:600;margin:0}
h1,h2{text-wrap:balance}
h1{font-size:clamp(2.2rem,4.6vw,3.5rem);line-height:1.04;letter-spacing:-.04em}
h2{font-size:clamp(1.65rem,3vw,2.3rem);line-height:1.12;letter-spacing:-.03em}
h3{font-size:1.04rem;font-weight:600;letter-spacing:-.01em}
.eyebrow{font:500 .76rem/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--amber-ink)}
@media (max-width:520px){.eyebrow{font-size:.7rem;letter-spacing:.04em;line-height:1.35}
  .hero-actions .btn{flex:1 1 100%}}
.lede{font-size:1.12rem;line-height:1.6;color:var(--muted);max-width:40rem;text-wrap:pretty}

/* header */
.top{position:sticky;top:0;z-index:20;background:rgba(11,26,46,.92);backdrop-filter:saturate(1.4) blur(10px);
  border-bottom:1px solid rgba(255,255,255,.06)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;height:60px;gap:16px}
.brand{display:flex;align-items:center;gap:10px;color:#fff;text-decoration:none;font-weight:650;letter-spacing:-.01em;
  white-space:nowrap}
@media (max-width:420px){.top .brand span{font-size:.92rem}.top .wrap{padding:0 16px}}
.brand svg{flex:none}
.top nav{display:flex;align-items:center;gap:22px}
.top nav a{color:#c9d5e3;text-decoration:none;font-size:.92rem}
.top nav a:hover{color:#fff}
.top nav a.btn-amber,.top nav a.btn-amber:hover{color:#1b1205}
@media (max-width:720px){.top nav a.hide-sm{display:none}}

/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font:550 1rem/1 var(--sans);letter-spacing:-.01em;
  padding:14px 22px;border-radius:8px;border:0;cursor:pointer;text-decoration:none;transition:transform .08s,background .15s}
.btn:active{transform:translateY(1px)}
.btn-amber{background:var(--amber);color:#1b1205}.btn-amber:hover{background:#f5b754}
.btn-navy{background:var(--navy-800);color:#fff}.btn-navy:hover{background:var(--navy-700)}
.btn-ghost{background:transparent;color:var(--navy-800);border:1px solid #b9c5d3}.btn-ghost:hover{background:#fff}
.btn-ghost-dark{background:transparent;color:#e4ebf3;border:1px solid rgba(255,255,255,.28)}
.btn-ghost-dark:hover{background:rgba(255,255,255,.06)}
.top .btn{padding:9px 14px;font-size:.9rem}
.btn-block{width:100%}

/* hero */
.hero{position:relative;overflow:hidden;color:#cfdae6;
  background:radial-gradient(1200px 600px at 85% 10%,#1d3a5f 0%,rgba(29,58,95,0) 60%),
             radial-gradient(900px 500px at 0% 100%,#10243d 0%,rgba(16,36,61,0) 60%),var(--navy-900)}
.hero .isobars{position:absolute;inset:0;opacity:.13;pointer-events:none}
.hero .wrap{position:relative;display:grid;grid-template-columns:1.02fr .98fr;gap:56px;align-items:center;
  padding-top:64px;padding-bottom:72px}
.hero h1{color:#fff}
.hero .lede{color:#b9c7d6;margin:18px 0 26px}
.hero .eyebrow{color:var(--amber)}
.ticks{list-style:none;padding:0;margin:0 0 26px;display:grid;gap:8px}
.ticks li{display:flex;gap:10px;align-items:flex-start;color:#d8e1ea}
.ticks svg{flex:none;margin-top:4px}
.hero-actions{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.hero-note{font-size:.85rem;color:#8fa3b8;margin-top:14px}

/* the report stack */
.stack{position:relative;min-height:520px}
.stack .doc{position:absolute;background:#fff;border-radius:4px;box-shadow:var(--doc-shadow);overflow:hidden}
.stack .doc img{width:100%;height:auto}
.stack .d1{width:72%;right:0;top:0;transform:rotate(1.5deg)}
.stack .d2{width:62%;left:0;top:70px;transform:rotate(-3deg);opacity:.98}
.callout{position:absolute;background:#fff;color:var(--ink);border-radius:8px;padding:10px 12px;
  box-shadow:0 10px 30px rgba(0,0,0,.28);font-size:.82rem;line-height:1.35;max-width:220px;border-left:4px solid var(--amber)}
.callout b{display:block;font-size:1.15rem;font-weight:600;letter-spacing:-.02em;color:var(--ink);margin-bottom:2px}
.callout span{color:var(--muted)}
.c1{left:-14px;bottom:28px}.c2{right:-10px;bottom:-14px}.c3{left:-26px;top:38%}
@media (max-width:960px){
  .hero .wrap{grid-template-columns:1fr;gap:40px;padding-top:40px}
  .stack{min-height:0;height:min(118vw,560px)}
}
@media (max-width:520px){.c3{display:none}.callout{max-width:180px}}

/* sources strip */
.sources{background:var(--navy-950);color:#8fa3b8;font-size:.85rem}
.sources .wrap{display:flex;flex-wrap:wrap;gap:10px 28px;align-items:center;justify-content:center;padding:18px 24px}
.sources b{color:#dbe4ee;font-weight:600}

/* sections */
section{padding:88px 0}
section.alt{background:#fff;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.section-head{max-width:46rem;margin-bottom:44px}
.section-head h2{margin:10px 0 12px}

/* proof */
.proof{display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:start}
.facts{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.fact{background:var(--paper);border:1px solid var(--rule);border-radius:var(--radius);padding:18px 18px 16px}
.fact .num{font:600 2.1rem/1.05 var(--sans);color:var(--ink);letter-spacing:-.04em}
.fact .num small{font-size:1rem;font-weight:500;letter-spacing:-.01em;color:var(--muted);margin-left:4px}
.fact p{margin:8px 0 0;font-size:.9rem;color:var(--muted);line-height:1.45}
.fact .src{display:block;margin-top:10px;font:500 .72rem/1.3 var(--mono);color:#7b8899}
.case{background:var(--navy-900);color:#c9d5e3;border-radius:14px;padding:26px;box-shadow:var(--shadow)}
.case h3{color:#fff;font-size:1.3rem;letter-spacing:-.02em;margin-bottom:6px}
.case p{margin:0 0 16px;font-size:.95rem}
.case .meta{font:500 .8rem/1.5 var(--mono);color:#8fa3b8;border-top:1px solid rgba(255,255,255,.1);
  padding-top:14px;margin-top:6px;overflow-wrap:anywhere}
.case .row{display:flex;gap:12px;align-items:baseline;padding:10px 0;border-top:1px solid rgba(255,255,255,.08)}
.case .row .k{flex:1;color:#aebdcd;font-size:.9rem}.case .row .v{color:#fff;font-weight:600;text-align:right}

/* features */
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.feature{background:#fff;border:1px solid var(--rule);border-radius:var(--radius);padding:24px;box-shadow:0 1px 0 rgba(7,17,31,.02)}
.feature .icon{width:40px;height:40px;border-radius:9px;background:var(--navy-100);display:grid;place-items:center;margin-bottom:14px}
.feature h3{margin-bottom:6px;color:var(--ink)}
.feature p{margin:0;font-size:.94rem;color:var(--muted)}
.feature code{font:500 .8rem var(--mono);background:var(--paper);border:1px solid var(--rule);padding:1px 5px;border-radius:4px;color:var(--ink)}
@media (max-width:900px){.grid3{grid-template-columns:1fr 1fr}.proof{grid-template-columns:1fr}}
@media (max-width:600px){.grid3,.facts{grid-template-columns:1fr}section{padding:64px 0}}

/* sample gallery */
.gallery{display:grid;grid-template-columns:repeat(5,1fr);gap:18px}
.gallery a{display:block;text-decoration:none;color:var(--muted);font-size:.85rem}
.gallery .thumb{background:#fff;border:1px solid var(--rule);border-radius:4px;box-shadow:var(--shadow);overflow:hidden;
  aspect-ratio:8.5/11;transition:transform .15s,box-shadow .15s}
.gallery .thumb img{width:100%;height:100%;object-fit:cover;object-position:top}
.gallery a:hover .thumb{transform:translateY(-3px);box-shadow:0 2px 4px rgba(7,17,31,.08),0 16px 40px rgba(7,17,31,.16)}
.gallery span{display:block;margin-top:10px;font-weight:600;color:var(--ink)}
.gallery-cta{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin-top:34px}
@media (max-width:900px){.gallery{grid-template-columns:repeat(3,1fr)}}
@media (max-width:600px){.gallery{grid-template-columns:repeat(2,1fr)}}

/* steps + audience */
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;counter-reset:s}
.step{position:relative;padding:24px;border-radius:var(--radius);background:#fff;border:1px solid var(--rule)}
.step:before{counter-increment:s;content:counter(s);display:grid;place-items:center;width:32px;height:32px;border-radius:50%;
  background:var(--navy-800);color:#fff;font-weight:700;margin-bottom:14px}
.step h3{margin-bottom:6px}.step p{margin:0;color:var(--muted);font-size:.94rem}
.who{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}
.who span{background:#fff;border:1px solid var(--rule);border-radius:999px;padding:8px 14px;font-size:.9rem;color:var(--ink)}
@media (max-width:800px){.steps{grid-template-columns:1fr}}

/* pricing + order */
.order{display:grid;grid-template-columns:.9fr 1.1fr;gap:40px;align-items:start}
.price-card{background:var(--navy-900);color:#c9d5e3;border-radius:14px;padding:30px}
.price-card .amount{font:600 3.4rem/1 var(--sans);color:#fff;letter-spacing:-.05em}
.price-card .per{color:#8fa3b8;margin:6px 0 20px}
.price-card ul{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.price-card li{display:flex;gap:10px;align-items:flex-start;font-size:.95rem}
.price-card li svg{flex:none;margin-top:4px}
.price-card .vs{margin-top:22px;padding-top:16px;border-top:1px solid rgba(255,255,255,.1);font-size:.86rem;color:#8fa3b8}
.form-card{background:#fff;border:1px solid var(--rule);border-radius:14px;padding:30px;box-shadow:var(--shadow)}
.form-card h3{font-size:1.45rem;letter-spacing:-.025em;margin-bottom:4px}
.form-card .sub{color:var(--muted);margin:0 0 6px;font-size:.95rem}
label{display:block;margin-top:16px;font-weight:600;color:var(--ink);font-size:.95rem}
label small{font-weight:400;color:var(--muted)}
input{width:100%;padding:12px 14px;font:inherit;font-size:1rem;color:var(--ink);border:1px solid #c3ccd7;border-radius:8px;
  margin-top:6px;background:#fff;transition:border-color .15s,box-shadow .15s}
input:focus{outline:none;border-color:var(--navy-700);box-shadow:0 0 0 3px rgba(28,53,84,.15)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:600px){.row2{grid-template-columns:1fr;gap:0}}
.form-card .btn{margin-top:22px}
.fine{font-size:.82rem;color:var(--muted);margin-top:12px}
.err{background:var(--amber-50);border:1px solid #f0cf9c;color:var(--amber-ink);padding:12px 14px;border-radius:8px;margin:14px 0 0}
@media (max-width:900px){.order{grid-template-columns:1fr}}

/* faq */
.faq{max-width:780px}
.faq details{border-bottom:1px solid var(--rule);padding:18px 0}
.faq summary{cursor:pointer;font-weight:600;color:var(--ink);list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq summary::-webkit-details-marker{display:none}
.faq summary:after{content:"+";font-weight:400;font-size:1.4rem;line-height:1;color:var(--muted)}
.faq details[open] summary:after{content:"–"}
.faq p{margin:10px 0 0;color:var(--muted)}

/* footer */
footer{background:var(--navy-950);color:#8091a5;font-size:.86rem;padding:44px 0}
footer .wrap{display:grid;grid-template-columns:1.3fr 1fr;gap:32px}
footer a{color:#b6c4d4}
footer p{margin:0 0 10px}
@media (max-width:700px){footer .wrap{grid-template-columns:1fr}}

/* inner pages (confirm, status) */
.inner{max-width:620px;margin:0 auto;padding:56px 24px 88px}
.inner h1{font-size:clamp(1.9rem,4vw,2.4rem);margin:10px 0 18px}
.panel{background:#fff;border:1px solid var(--rule);border-radius:14px;padding:26px;box-shadow:var(--shadow)}
.panel dl{display:grid;grid-template-columns:8.5rem 1fr;gap:12px 16px;margin:0}
.panel dt{color:var(--muted);font-size:.92rem}.panel dd{margin:0;color:var(--ink)}
.panel .actions{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0 14px}
.status{display:flex;gap:14px;align-items:flex-start}
.status .dot{flex:none;width:12px;height:12px;border-radius:50%;margin-top:7px;background:var(--amber);
  box-shadow:0 0 0 0 rgba(242,169,59,.6);animation:pulse 1.6s infinite}
.status .dot.ok{background:var(--green);animation:none}
.status .dot.bad{background:var(--red);animation:none}
.status p{margin:0 0 8px}
@keyframes pulse{70%{box-shadow:0 0 0 10px rgba(242,169,59,0)}100%{box-shadow:0 0 0 0 rgba(242,169,59,0)}}
.rid{font:500 .92rem var(--mono);color:var(--ink);word-break:break-all}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto}}
"""

LOGO = """<svg width="26" height="26" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7"
fill="#f2a93b"/><path d="M8 21.5c3.2-5.4 6.4-5.4 9.6 0M11.2 21.5c1.9-2.9 3.8-2.9 5.7 0" stroke="#0b1a2e" stroke-width="2.4"
fill="none" stroke-linecap="round"/><path d="M19.5 9.5l-3.2 6h3.6l-2.4 5.5" stroke="#0b1a2e" stroke-width="2.2"
fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' "
           "height='32' rx='7' fill='%23f2a93b'/%3E%3Cpath d='M19.5 9.5l-3.2 6h3.6l-2.4 5.5' stroke='%230b1a2e' "
           "stroke-width='2.4' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")

CHECK = ('<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="8" fill="{bg}"/>'
         '<path d="M4.5 8.2l2.3 2.3 4.7-4.9" stroke="{fg}" stroke-width="1.8" fill="none" stroke-linecap="round" '
         'stroke-linejoin="round"/></svg>')
CHECK_DARK = CHECK.format(bg="rgba(242,169,59,.18)", fg="#f2a93b")

ISOBARS = """<svg class="isobars" viewBox="0 0 1200 700" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<g fill="none" stroke="#9fb6cf" stroke-width="1">
<path d="M-50 520C150 430 300 470 470 400S820 220 1010 260 1300 360 1300 360"/>
<path d="M-50 580C160 500 320 540 500 470S840 300 1030 330 1300 420 1300 420"/>
<path d="M-50 640C170 570 340 610 530 540S860 380 1050 400 1300 480 1300 480"/>
<path d="M-50 460C140 360 280 400 440 330S800 140 990 190 1300 300 1300 300"/>
<path d="M-50 400C130 290 260 330 410 260S780 60 970 120 1300 240 1300 240"/>
<ellipse cx="905" cy="180" rx="120" ry="58"/><ellipse cx="905" cy="180" rx="70" ry="32"/>
<ellipse cx="905" cy="180" rx="28" ry="12"/></g></svg>"""

ICONS = {
    "station": '<path d="M12 3v18M8 7h8M6 11h12" stroke="#1c3554" stroke-width="1.8" fill="none" stroke-linecap="round"/>',
    "compass": '<circle cx="12" cy="12" r="8.5" stroke="#1c3554" stroke-width="1.8" fill="none"/><path d="M14.8 9.2l-1.6 4-4 1.6 1.6-4z" fill="#1c3554"/>',
    "polygon": '<path d="M5 8l6-4 8 4-2 10-9 1z" stroke="#1c3554" stroke-width="1.8" fill="none" stroke-linejoin="round"/><circle cx="11" cy="12" r="2" fill="#f2a93b"/>',
    "db": '<ellipse cx="12" cy="6" rx="7" ry="2.6" stroke="#1c3554" stroke-width="1.8" fill="none"/><path d="M5 6v12c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6V6M5 12c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6" stroke="#1c3554" stroke-width="1.8" fill="none"/>',
    "hail": '<path d="M7 13a4 4 0 010-8 5 5 0 019.6 1.4A3.3 3.3 0 0117 13z" stroke="#1c3554" stroke-width="1.8" fill="none" stroke-linejoin="round"/><circle cx="8" cy="17" r="1.4" fill="#1c3554"/><circle cx="12" cy="19.5" r="1.4" fill="#1c3554"/><path d="M15.5 15l-1.5 3h2l-1.2 3" stroke="#f2a93b" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "hash": '<path d="M9 4L7 20M17 4l-2 16M4.5 9h15M3.5 15h15" stroke="#1c3554" stroke-width="1.8" fill="none" stroke-linecap="round"/>',
}


def icon(name: str) -> str:
    return f'<div class="icon"><svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg></div>'


def layout(title: str, body: str, refresh: int | None = None, description: str = "") -> str:
    meta = f'<meta http-equiv="refresh" content="{refresh}">' if refresh else ""
    desc = escape(description or "Address-specific historical weather report for insurance claims: station-measured "
                  "wind and rain, NWS warnings, storm reports, radar hail and lightning, with distance and direction "
                  f"from the loss site. {PRICE} PDF.", quote=True)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">{meta}
<title>{escape(title)}</title><meta name="description" content="{desc}">
<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{desc}">
<meta property="og:image" content="/static/sample-p1.webp"><meta name="theme-color" content="#0b1a2e">
<link rel="icon" href="{FAVICON}">{FONTS}<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><a class="brand" href="/">{LOGO}<span>{BRAND}</span></a>
<nav><a class="hide-sm" href="/#sample">Sample report</a><a class="hide-sm" href="/#how">How it works</a>
<a class="hide-sm" href="/#faq">FAQ</a><a class="btn btn-amber" href="/#order">Order · {PRICE}</a></nav></div></header>
<main>{body}</main>{FOOTER}</body></html>"""


FOOTER = f"""<footer><div class="wrap"><div><a class="brand" href="/" style="margin-bottom:14px">{LOGO}<span>{BRAND}</span></a>
<p>Address-specific historical weather reports compiled from public US government records: NOAA NCEI, the
National Weather Service and the US Census Bureau.</p>
<p>Not affiliated with or endorsed by NOAA, the National Weather Service or any government agency. Reports compile
public records; they are not certified government records or expert opinions, and records near a property do not
by themselves establish conditions at it.</p></div>
<div><p><a href="/#sample">Sample report</a> · <a href="/#faq">FAQ</a> · <a href="/#order">Order</a></p>
<p>{DOMAIN}</p>
<p>Payments are processed by Creem, our merchant of record.</p></div></div></footer>"""


def order_form(v: dict, error: str = "", ask_coords: bool = False, title: str = "Order your report") -> str:
    g = lambda k: escape(str(v.get(k) or ""), quote=True)  # noqa: E731
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    coords = ""
    if ask_coords or v.get("lat"):
        coords = f"""<div class="row2"><label>Latitude<input name="lat" inputmode="decimal" value="{g('lat')}"
placeholder="39.16955"></label><label>Longitude<input name="lon" inputmode="decimal" value="{g('lon')}"
placeholder="-86.53493"></label></div><p class="fine">Rural routes, PO boxes and new builds are often missing
from the Census address file. Right-click the property in Google Maps and copy the coordinates it shows.</p>"""
    err = f'<p class="err" role="alert">{escape(error)}</p>' if error else ""
    return f"""<div class="form-card" id="order-form"><h3>{escape(title)}</h3>
<p class="sub">Any US address · loss dates from {MIN_DATE.year} to yesterday</p>{err}
<form method="post" action="/order">
<label>Loss address<input name="address" required autocomplete="street-address" value="{g('address')}"
placeholder="401 N College Ave, Bloomington, IN 47404"></label>
<div class="row2"><label>Date of loss<input type="date" name="loss_date" required min="{MIN_DATE.isoformat()}"
max="{yesterday}" value="{g('loss_date')}"></label>
<label>Email for delivery<input type="email" name="email" required autocomplete="email" value="{g('email')}"
placeholder="you@company.com"></label></div>
{coords}<button class="btn btn-navy btn-block" type="submit">Check address</button>
<p class="fine">You'll confirm the matched location before paying {PRICE}. Nothing is charged until then.</p>
</form></div>"""


def landing(form: str) -> str:
    s = SAMPLE
    hero = f"""<section class="hero" style="padding:0">{ISOBARS}<div class="wrap">
<div><p class="eyebrow">Historical weather evidence · any US address</p>
<h1>What the weather did at the loss site.</h1>
<p class="lede">A PDF report for one address and one date of loss, built from NOAA and National Weather Service
records. Every number names the station that measured it and how far away it was.</p>
<ul class="ticks">
<li>{CHECK_DARK}<span>Peak wind gusts, rain and temperature from named weather stations, with distance and direction</span></li>
<li>{CHECK_DARK}<span>Whether the address was inside each NWS warning polygon</span></li>
<li>{CHECK_DARK}<span>Storm reports, NCEI Storm Events, NEXRAD radar hail and lightning</span></li>
</ul>
<div class="hero-actions"><a class="btn btn-amber" href="#order">Get a report — {PRICE}</a>
<a class="btn btn-ghost-dark" href="{s['pdf']}" target="_blank" rel="noopener">View sample PDF</a></div>
<p class="hero-note">Delivered in about a minute · Download link plus email copy</p></div>
<div class="stack" aria-label="Pages from the sample report">
<div class="doc d2"><img src="/static/sample-p2.webp" alt="Sample report: station-pinned measurements page" width="935" height="1210"></div>
<div class="doc d1"><img src="/static/sample-p1.webp" alt="Sample report: cover with key findings" width="935" height="1210"></div>
<div class="callout c3"><b>2 of 2</b><span>tornado warnings whose polygon contained the address</span></div>
<div class="callout c1"><b>70 mph gust</b><span>measured at KBMG, 4.7 mi WSW of the address, 7:01 PM EST</span></div>
<div class="callout c2"><b>1.50 in hail</b><span>radar-estimated 1.2 mi NNE · 7:07 PM</span></div>
</div></div></section>
<div class="sources"><div class="wrap"><span>Built from public records:</span><b>NOAA NCEI GHCN-hourly</b>
<b>NWS warnings &amp; storm reports</b><b>NCEI Storm Events</b><b>NEXRAD radar</b><b>US Census geocoder</b></div></div>"""

    proof = f"""<section class="alt" id="proof"><div class="wrap proof">
<div><p class="eyebrow">From the sample report</p>
<h2 style="margin:10px 0 12px">Measured, located and dated, not estimated.</h2>
<p class="lede" style="margin-bottom:28px">Weather sites often blend several stations into one smoothed number,
and that can miss the peak that did the damage. This report keeps every reading tied to the station that took
it, so the numbers hold up when someone checks them.</p>
<div class="facts">
<div class="fact"><div class="num">70<small>mph</small></div><p>Peak gust measured by the Monroe County Airport
station, 4.7 mi WSW of the address, at 7:01 PM.</p><span class="src">GHCNh · KBMG · PK WND 21061/0001</span></div>
<div class="fact"><div class="num">2.0<small>mi WSW</small></div><p>Closest approach of the EF2 tornado's
path to the address (3.73 mi long, 440 yd wide).</p><span class="src">NCEI Storm Events · event 1318047</span></div>
<div class="fact"><div class="num">Inside</div><p>The address lay inside the polygons of both tornado
warnings issued that evening.</p><span class="src">NWS VTEC · KIND TO.W 0008 &amp; 0009</span></div>
<div class="fact"><div class="num">1.50<small>in</small></div><p>Largest hail reported on the ground within
5 miles: 1.9 mi SE, 7:05 PM.</p><span class="src">NWS Local Storm Report</span></div>
</div></div>
<aside class="case"><h3>Sample: {s['place']}</h3><p>{s['date']} · tornado and hail outbreak. Real report,
built from live government data.</p>
<div class="row"><span class="k">Stations measured</span><span class="v">4 within 34 mi</span></div>
<div class="row"><span class="k">Storm reports within 25 mi</span><span class="v">19</span></div>
<div class="row"><span class="k">Storm Events records</span><span class="v">8</span></div>
<div class="row"><span class="k">Radar hail detections within 15 mi</span><span class="v">19</span></div>
<div class="row"><span class="k">Pages</span><span class="v">{s['pages']}</span></div>
<div class="meta">Report ID {s['id']}<br>Every source response is hashed (SHA-256), so the
report can be regenerated byte-for-byte and verified.</div>
<a class="btn btn-amber btn-block" style="margin-top:18px" href="{s['pdf']}" target="_blank" rel="noopener">Open the full sample PDF</a>
</aside></div></section>"""

    features = f"""<section id="what"><div class="wrap"><div class="section-head"><p class="eyebrow">What's in the report</p>
<h2>Everything the free sites leave out.</h2><p class="lede">Built for a claim file: each record carries its
source, its time in the local timezone, and its position relative to the loss site.</p></div>
<div class="grid3">
<div class="feature">{icon('station')}<h3>Station-pinned measurements</h3><p>Wind, gusts, rain, temperature,
visibility and present weather from the nearest stations, with every report of the day and its raw METAR text.</p></div>
<div class="feature">{icon('compass')}<h3>Distance and direction</h3><p>Every station, storm report, radar
detection and lightning cell is placed relative to the address, for example <code>1.9 mi SE</code>.</p></div>
<div class="feature">{icon('polygon')}<h3>Warning polygon check</h3><p>NWS watches and warnings in effect, with
the address tested against each bulletin's polygon and the full bulletin text included.</p></div>
<div class="feature">{icon('db')}<h3>NCEI Storm Events</h3><p>NOAA's reviewed record, with tornado path
distance, magnitudes, damage estimates and narratives. Months not yet published are labelled as such.</p></div>
<div class="feature">{icon('hail')}<h3>Hail and lightning</h3><p>NEXRAD radar hail size estimates scan by scan,
ground hail reports, and lightning strike counts for the grid cell containing the address.</p></div>
<div class="feature">{icon('hash')}<h3>Honest about gaps</h3><p>Missing station hours are marked missing, never
zero. Sources that were unavailable are listed on page one. Each source is hashed for verification.</p></div>
</div></div></section>"""

    pages = [("1", "Key findings"), ("2", "Station measurements"), ("4", "Warnings & storm reports"),
             ("6", "Storm Events"), ("7", "Hail & lightning")]
    thumbs = "".join(f'<a href="{s["pdf"]}#page={p}" target="_blank" rel="noopener"><div class="thumb">'
                     f'<img loading="lazy" src="/static/sample-p{p}.webp" alt="Sample report page {p}: {t}" '
                     f'width="935" height="1210"></div><span>{t}</span>Page {p}</a>' for p, t in pages)
    sample = f"""<section class="alt" id="sample"><div class="wrap"><div class="section-head">
<p class="eyebrow">Sample report</p><h2>See exactly what you'll receive.</h2>
<p class="lede">The full {s['pages']}-page report for {s['place']} on {s['date']}, unedited. Your report has
the same sections for your address and date.</p></div>
<div class="gallery">{thumbs}</div>
<div class="gallery-cta"><a class="btn btn-navy" href="{s['pdf']}" target="_blank" rel="noopener">Download the
sample PDF</a><a class="btn btn-ghost" href="#order">Get yours — {PRICE}</a></div></div></section>"""

    how = """<section id="how"><div class="wrap"><div class="section-head"><p class="eyebrow">How it works</p>
<h2>Three steps, about a minute.</h2></div>
<div class="steps">
<div class="step"><h3>Enter the address and date of loss</h3><p>Any US address. If the address isn't in the
Census address file, you can enter the property's coordinates instead.</p></div>
<div class="step"><h3>Confirm the location and pay</h3><p>We show the matched location first, so you only pay
for the right place. Secure checkout through Creem.</p></div>
<div class="step"><h3>Download the PDF</h3><p>The report is built from the government archives while you wait.
You get a download link and an emailed copy.</p></div></div>
<div class="who"><span>Independent adjusters</span><span>Public adjusters</span><span>Roofing &amp; restoration
contractors</span><span>Attorneys &amp; paralegals</span><span>Homeowners</span><span>Property managers</span></div>
</div></section>"""

    order = f"""<section class="alt" id="order"><div class="wrap order">
<div class="price-card"><p class="eyebrow" style="color:var(--amber)">One report</p>
<div class="amount">{PRICE}</div><div class="per">per address and date · no subscription</div>
<ul>
<li>{CHECK_DARK}<span>Station measurements with distance and direction</span></li>
<li>{CHECK_DARK}<span>NWS warnings with polygon check and full text</span></li>
<li>{CHECK_DARK}<span>Storm reports and NCEI Storm Events</span></li>
<li>{CHECK_DARK}<span>Radar hail and lightning</span></li>
<li>{CHECK_DARK}<span>Raw source records and verification hashes</span></li>
<li>{CHECK_DARK}<span>PDF download and email copy</span></li></ul>
<p class="vs">Single-address hail or wind verification reports are commonly sold for $40 or more.</p></div>
{form}</div></section>"""

    faq_items = [
        ("Is this a certified weather report?",
         "No. It compiles public records from NOAA, the National Weather Service and the US Census Bureau, and shows "
         "exactly where each record came from. It is not a certified government record or an expert opinion. If you "
         "need certified records or testimony, NOAA NCEI and forensic meteorologists provide those."),
        ("How close is the weather data to my address?",
         "It depends on where the nearest stations are. The report names each station and gives its distance and "
         "direction from the address, and it does the same for every storm report, radar detection and warning. "
         "Records near a property do not by themselves establish conditions at it, and the report says so."),
        ("Which dates can I order?",
         f"Any completed day from {MIN_DATE.year} to yesterday. NOAA publishes the Storm Events database a few months "
         "after each month ends; for recent dates that section says it has not been published yet, and everything else "
         "is included."),
        ("What if my address isn't found?",
         "Rural routes, PO boxes and new construction are sometimes missing from the Census address file. You can "
         "enter the property's latitude and longitude instead, and the report notes that the coordinates were supplied."),
        ("How fast do I get it?",
         "Usually within a minute or two of payment. The page updates by itself when the report is ready, and a copy "
         "is emailed to you."),
        ("What if the report can't be built?",
         "If a report fails after payment, we're notified immediately. We'll deliver the report or refund you."),
    ]
    faq = "".join(f"<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in faq_items)
    faq_html = f"""<section id="faq"><div class="wrap"><div class="section-head"><p class="eyebrow">FAQ</p>
<h2>Questions adjusters ask.</h2></div><div class="faq">{faq}</div></div></section>"""
    return hero + proof + features + sample + how + order + faq_html


def inner(body: str) -> str:
    return f'<div class="inner">{body}</div>'


def status_block(kind: str, title: str, text: str) -> str:
    dot = {"wait": "", "ok": " ok", "bad": " bad"}[kind]
    return f'<div class="status"><span class="dot{dot}"></span><div><p><b>{title}</b></p>{text}</div></div>'
