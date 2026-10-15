"""Public pages: the landing/order page and the buyer's order pages, with one shared look.

Audience: adjusters, public adjusters, roofing contractors, attorneys and policyholders documenting a loss.
Principles: say each thing once, in plain words; show the product with real data (the hero map and the wind
chart are drawn from the sample report by scripts/make_site_map.py); put the order form where people land.
"""
from datetime import date, timedelta
from html import escape
from pathlib import Path

from . import BRAND, DOMAIN
from .brand import FAVICON, mark_svg
from .report import MIN_DATE

PRICE = "$9.99"
STATIC = Path(__file__).parent / "static"
SAMPLE = {
    "place": "Bloomington, IN",
    "date": "February 19, 2026",
    "pages": 25,
    "pdf": "/static/sample-report.pdf",
    "id": "WE-2026-02-19-C37C7155922C",
}
WIND_CHART = (STATIC / "wind-chart.svg").read_text()

# Self-hosted (SIL OFL, see /static/fonts/OFL.txt): no third-party requests from buyers' browsers.
FONT_FACES = """
@font-face{font-family:Geist;src:url(/static/fonts/Geist-Variable.woff2) format("woff2");font-weight:100 900;
  font-style:normal;font-display:swap}
@font-face{font-family:"Geist Mono";src:url(/static/fonts/GeistMono-Variable.woff2) format("woff2");font-weight:100 900;
  font-style:normal;font-display:swap}
"""
FONTS = '<link rel="preload" href="/static/fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin>'
MAP_ASSETS = ('<link rel="stylesheet" href="/static/vendor/leaflet/leaflet.css">'
              '<script defer src="/static/vendor/leaflet/leaflet.js"></script>'
              '<script defer src="/static/order.js"></script><script defer src="/static/hero.js"></script>')

CSS = FONT_FACES + """
:root{
  --navy-950:#07111f;--navy-900:#0b1a2e;--navy-800:#12263f;--navy-700:#1c3554;--navy-100:#e8eef5;
  --ink:#14202e;--body:#3a4757;--muted:#5d6b7c;--faint:#8a96a5;--rule:#e1e6ec;--paper:#fbfaf7;--white:#fff;
  --amber:#f2a93b;--amber-ink:#8a5a0b;--amber-50:#fdf5e8;--green:#1f7a4d;--green-50:#e9f5ef;--red:#a33a2b;
  --sky:#3d7fc2;
  --sans:Geist,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"Geist Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --radius:12px;--shadow:0 1px 2px rgba(7,17,31,.05),0 10px 30px rgba(7,17,31,.07);
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-behavior:smooth}
body{margin:0;font:16px/1.6 var(--sans);color:var(--body);background:var(--paper);-webkit-font-smoothing:antialiased}
a{color:var(--navy-700)}
img{max-width:100%;display:block}
.wrap{max-width:1160px;margin:0 auto;padding:0 24px}
h1,h2,h3{color:var(--ink);font-family:var(--sans);font-weight:600;margin:0}
h1,h2{text-wrap:balance}
h1{font-size:clamp(2.3rem,4.8vw,3.6rem);line-height:1.03;letter-spacing:-.045em}
h2{font-size:clamp(1.75rem,3.2vw,2.5rem);line-height:1.1;letter-spacing:-.035em}
h3{font-size:1.1rem;font-weight:600;letter-spacing:-.015em;line-height:1.3}
.eyebrow{font:500 .74rem/1.3 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--amber-ink);margin:0}
.lede{font-size:1.1rem;line-height:1.6;color:var(--muted);max-width:38rem;text-wrap:pretty;margin:0}
.num{font-variant-numeric:tabular-nums}

/* header */
.top{position:sticky;top:0;z-index:1000;background:rgba(11,26,46,.94);backdrop-filter:saturate(1.4) blur(10px);
  border-bottom:1px solid rgba(255,255,255,.06)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;height:62px;gap:16px}
.brand{display:flex;align-items:center;gap:10px;color:#fff;text-decoration:none;font-weight:650;font-size:1.08rem;
  letter-spacing:-.025em;white-space:nowrap}
.brand svg{flex:none;border-radius:7px}
.top nav{display:flex;align-items:center;gap:24px}
.top nav a{color:#c3cfdc;text-decoration:none;font-size:.93rem}
.top nav a:hover{color:#fff}
.top nav a.btn-amber,.top nav a.btn-amber:hover{color:#1b1205}
@media (max-width:760px){.top nav a.hide-sm{display:none}}
@media (max-width:420px){.top .brand{font-size:.95rem}.top .wrap{padding:0 16px}}

/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font:560 1rem/1 var(--sans);
  letter-spacing:-.01em;padding:14px 22px;border-radius:9px;border:0;cursor:pointer;text-decoration:none;
  transition:background .15s,transform .08s}
.btn:active{transform:translateY(1px)}
.btn-amber{background:var(--amber);color:#1b1205}.btn-amber:hover{background:#f6b856}
.btn-navy{background:var(--navy-800);color:#fff}.btn-navy:hover{background:var(--navy-700)}
.btn-ghost{background:#fff;color:var(--navy-800);border:1px solid #c6d0db}.btn-ghost:hover{border-color:var(--navy-700)}
.top .btn{padding:9px 14px;font-size:.9rem}
.btn-block{width:100%}
.linkbtn{background:none;border:0;padding:0;font:500 .88rem var(--sans);color:var(--sky);cursor:pointer;
  display:inline-flex;align-items:center;gap:6px}
.linkbtn:hover{text-decoration:underline}

/* sections */
section{padding:104px 0}
section.alt{background:#fff;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.section-head{max-width:44rem;margin:0 0 48px;display:grid;gap:12px}
.section-head.center{margin-left:auto;margin-right:auto;text-align:center;justify-items:center}
@media (max-width:640px){section{padding:72px 0}.section-head{margin-bottom:32px}}

/* hero */
.hero{position:relative;color:#c9d5e3;padding:0;
  background:radial-gradient(1100px 620px at 88% 0%,#1d3a5f 0%,rgba(29,58,95,0) 62%),var(--navy-900)}
.hero .wrap{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:64px;align-items:start;
  padding-top:72px;padding-bottom:88px}
.hero h1{color:#fff;margin:14px 0 18px}
.hero .eyebrow{color:var(--amber)}
.hero .lede{color:#aebdcd;margin-bottom:28px}
.figure{margin:0}
.mapcard{background:#fff;color:var(--body);border-radius:16px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.3)}
.mapcard .mc-head{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid var(--rule)}
.mapcard .mc-head svg{flex:none;border-radius:6px}
.mapcard .mc-head b{display:block;color:var(--ink);font-size:.92rem;font-weight:600;letter-spacing:-.01em}
.mapcard .mc-head span{display:block;color:var(--muted);font-size:.8rem}
#hero-map{height:330px;background:#e9edf1}
#hero-map .leaflet-tile-pane{filter:grayscale(1) contrast(.92) brightness(1.06)}
#hero-map .leaflet-tooltip{font:600 .76rem/1.25 var(--sans);color:var(--ink);border-radius:6px;padding:4px 7px;
  border:1px solid var(--rule);box-shadow:0 2px 8px rgba(0,0,0,.12)}
.mc-legend{display:flex;flex-wrap:wrap;gap:6px 16px;margin:0;padding:10px 18px;list-style:none;font-size:.78rem;
  color:var(--muted);border-bottom:1px solid var(--rule)}
.mc-legend li{display:flex;align-items:center;gap:6px}
.findings{display:grid;grid-template-columns:1fr 1fr;margin:0}
.findings div{padding:12px 18px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.findings div:nth-child(2n){border-right:0}
.findings div:nth-last-child(-n+2){border-bottom:0}
.findings dt{font:500 .68rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
.findings dd{margin:3px 0 0;color:var(--ink);font-size:.9rem;line-height:1.35}
.findings dd b{font-weight:650;font-size:1.05rem;letter-spacing:-.02em}
.figure figcaption{margin-top:14px;font-size:.85rem;color:#8fa3b8;line-height:1.5}
.figure figcaption a{color:#cfd9e4}
@media (max-width:480px){.findings{grid-template-columns:1fr}.findings div{border-right:0}
  .findings div:nth-last-child(-n+2){border-bottom:1px solid var(--rule)}.findings div:last-child{border-bottom:0}}
.lg{display:inline-block;flex:none}
.lg-site{width:11px;height:11px;border-radius:50%;background:var(--amber);box-shadow:0 0 0 2px var(--navy-900) inset}
.lg-station{width:10px;height:10px;border-radius:2px;background:var(--navy-800)}
.lg-path{width:18px;height:4px;border-radius:2px;background:#d9442e}
.lg-warn{width:16px;height:11px;border:1.4px dashed #d68f1f;background:rgba(242,169,59,.15)}
.lg-hail{width:11px;height:11px;border-radius:50%;background:rgba(61,127,194,.25);border:1px solid var(--sky)}
.lg-report{width:8px;height:8px;background:var(--sky);transform:rotate(45deg);margin:0 2px}
@media (max-width:980px){.hero .wrap{grid-template-columns:1fr;gap:48px;padding-top:48px;padding-bottom:64px}}

/* order form */
.form-card{background:#fff;color:var(--body);border-radius:16px;padding:28px;box-shadow:0 24px 60px rgba(0,0,0,.28);
  scroll-margin-top:90px}
.inner .form-card{box-shadow:var(--shadow);border:1px solid var(--rule)}
.form-card h3{font-size:1.3rem;letter-spacing:-.025em;margin-bottom:4px}
.form-card .sub{color:var(--muted);margin:0;font-size:.92rem}
form label{display:block;margin-top:16px;font-weight:550;color:var(--ink);font-size:.92rem}
form input{width:100%;padding:12px 14px;font:inherit;font-size:1rem;color:var(--ink);border:1px solid #c3ccd7;
  border-radius:9px;margin-top:6px;background:#fff;transition:border-color .15s,box-shadow .15s}
form input:focus{outline:none;border-color:var(--navy-700);box-shadow:0 0 0 3px rgba(28,53,84,.14)}
/* map view toggle (replaces Leaflet's layer control) */
.mapview{display:inline-flex;background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.25);overflow:hidden}
.mapview button{border:0;background:#fff;font:500 .78rem var(--sans);color:var(--ink);padding:7px 11px;cursor:pointer}
.mapview button+button{border-left:1px solid var(--rule)}
.mapview button[aria-pressed=true]{background:var(--navy-800);color:#fff}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:600px){.row2{grid-template-columns:1fr;gap:0}}
.form-card .btn{margin-top:22px}
.fine{font-size:.82rem;color:var(--muted);margin:10px 0 0;line-height:1.5}
.fine.warn{color:var(--amber-ink)}.fine.ok{color:var(--green)}
#addr-hint:empty{display:none}
#addr-hint{margin-top:6px}
.err{background:var(--amber-50);border:1px solid #f0cf9c;color:var(--amber-ink);padding:12px 14px;border-radius:9px;margin:14px 0 0}
.ac{position:relative}
.ac ul{position:absolute;z-index:1100;left:0;right:0;top:calc(100% + 4px);margin:0;padding:6px;list-style:none;background:#fff;
  border:1px solid var(--rule);border-radius:10px;box-shadow:0 14px 40px rgba(7,17,31,.16);max-height:300px;overflow:auto}
.ac li{padding:9px 10px;border-radius:7px;cursor:pointer;font-size:.93rem;color:var(--ink);line-height:1.35}
.ac li small{display:block;color:var(--faint);font-size:.78rem}
.ac li[aria-selected=true],.ac li:hover{background:var(--navy-100)}
.ac li.attr{cursor:default;font-size:.7rem;color:var(--faint);padding:6px 10px 2px}
.ac li.attr:hover{background:none}
.locate{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:12px 0 8px;flex-wrap:wrap}
.pinned{font-size:.82rem;color:var(--green);display:none;align-items:center;gap:6px}
.pinned.on{display:inline-flex}
#map-wrap{margin-top:4px}
#map{height:260px;border-radius:10px;border:1px solid var(--rule);background:#e8eef5}
.leaflet-container{font-family:var(--sans)}
.pin{width:22px;height:22px;border-radius:50% 50% 50% 0;background:var(--amber);border:3px solid var(--navy-900);
  transform:rotate(-45deg);box-shadow:0 4px 10px rgba(0,0,0,.35)}

/* sources strip */
.sources{background:var(--navy-950);color:#7f93a8;font-size:.84rem}
.sources .wrap{display:flex;flex-wrap:wrap;gap:8px 26px;align-items:center;justify-content:center;padding:16px 24px}
.sources b{color:#cfd9e4;font-weight:500}

/* questions */
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
@media (max-width:960px){.grid3{grid-template-columns:1fr}}
.q{background:#fff;border:1px solid var(--rule);border-radius:16px;padding:22px;display:flex;flex-direction:column;gap:14px}
.q .vis{background:var(--paper);border:1px solid var(--rule);border-radius:12px;padding:14px;height:228px;
  display:flex;flex-direction:column;justify-content:center;overflow:hidden}
@media (max-width:960px){.q .vis{height:auto;min-height:0}}
.q .vis svg{width:100%;height:auto;display:block}
.q p{margin:0;color:var(--muted);font-size:.95rem}
.vis-cap{font:500 .72rem/1.3 var(--mono);color:var(--faint);letter-spacing:.02em;margin-top:8px}
.rows{display:grid;gap:8px}
.rowi{display:flex;justify-content:space-between;align-items:center;gap:10px;background:#fff;border:1px solid var(--rule);
  border-radius:9px;padding:9px 11px;font-size:.88rem;color:var(--ink)}
.rowi b{font-weight:600}
.chip{font:500 .74rem/1 var(--mono);color:var(--navy-700);background:var(--navy-100);border-radius:6px;padding:5px 7px;
  white-space:nowrap}
.inside{display:inline-flex;align-items:center;gap:7px;background:var(--green-50);color:var(--green);font-weight:600;
  font-size:.85rem;border-radius:999px;padding:6px 11px;align-self:flex-start;margin-top:10px}
.also{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:28px;color:var(--muted);font-size:.92rem}
.also span.t{background:#fff;border:1px solid var(--rule);border-radius:999px;padding:7px 13px;color:var(--ink);font-size:.88rem}

/* compare */
.compare{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid var(--rule);border-radius:16px;
  overflow:hidden;font-size:.95rem}
.compare th,.compare td{padding:15px 18px;text-align:left;border-bottom:1px solid var(--rule);vertical-align:middle}
.compare tr:last-child td{border-bottom:0}
.compare thead th{font-weight:600;color:var(--ink);background:var(--paper);font-size:.92rem}
.compare thead th.us{background:var(--navy-900);color:#fff}
.compare td.us{background:#f6f9fc;font-weight:550;color:var(--ink)}
.compare td:first-child{color:var(--ink);font-weight:500;width:34%}
.yes,.no{display:inline-flex;align-items:center;gap:8px}
.yes:before{content:"";width:18px;height:18px;border-radius:50%;flex:none;background:var(--green-50) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 18 18'%3E%3Cpath d='M5 9.3l2.6 2.6 5.4-5.6' fill='none' stroke='%231f7a4d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/18px}
.no{color:var(--faint)}
.no:before{content:"";width:18px;height:2px;background:#cfd6de;flex:none;margin:0 0 0 0}
@media (max-width:700px){
  .compare,.compare tbody,.compare tr,.compare td{display:block;width:100%!important}
  .compare thead{display:none}
  .compare tr{border-bottom:1px solid var(--rule);padding:14px 16px}
  .compare tr:last-child{border-bottom:0}
  .compare td{border:0;padding:4px 0;display:flex;justify-content:space-between;gap:12px;background:none!important}
  .compare td:first-child{font-weight:600;padding-bottom:8px}
  .compare td[data-label]:before{content:attr(data-label);color:var(--muted);font-weight:400}
  .compare td.us:before{color:var(--ink);font-weight:600}
}

/* steps */
.steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;counter-reset:s;margin:0;padding:0;list-style:none}
.steps li{display:flex;gap:14px;align-items:flex-start}
.steps li:before{counter-increment:s;content:counter(s);flex:none;display:grid;place-items:center;width:30px;height:30px;
  border-radius:50%;background:var(--navy-800);color:#fff;font-weight:600;font-size:.9rem}
.steps b{display:block;color:var(--ink);font-weight:600}
.steps span{color:var(--muted);font-size:.93rem}
@media (max-width:800px){.steps{grid-template-columns:1fr}}

/* sample gallery */
.gallery{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px}
.gallery a{display:block;text-decoration:none;color:var(--muted);font-size:.85rem}
.gallery .thumb{background:#fff;border:1px solid var(--rule);border-radius:6px;box-shadow:var(--shadow);overflow:hidden;
  aspect-ratio:8.5/11;transition:transform .15s,box-shadow .15s}
.gallery .thumb img{width:100%;height:100%;object-fit:cover;object-position:top}
.gallery a:hover .thumb{transform:translateY(-3px);box-shadow:0 2px 4px rgba(7,17,31,.08),0 16px 40px rgba(7,17,31,.16)}
.gallery span{display:block;margin-top:10px;font-weight:550;color:var(--ink)}
.actions-row{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:36px}
@media (max-width:900px){.gallery{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:600px){.gallery{grid-template-columns:repeat(2,minmax(0,1fr))}}

/* faq */
.faq{max-width:780px;margin:0 auto}
.faq details{border-bottom:1px solid var(--rule);padding:18px 0}
.faq summary{cursor:pointer;font-weight:550;color:var(--ink);list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq summary::-webkit-details-marker{display:none}
.faq summary:after{content:"+";font-weight:400;font-size:1.4rem;line-height:1;color:var(--faint)}
.faq details[open] summary:after{content:"–"}
.faq p{margin:10px 0 0;color:var(--muted)}

/* closing call to action */
.cta{background:var(--navy-900);color:#aebdcd;text-align:center;padding:88px 0}
.cta h2{color:#fff;margin:0 auto 14px;max-width:30rem}
.cta p{margin:0 auto 28px;max-width:34rem}

/* footer */
footer{background:var(--navy-950);color:#7f93a8;font-size:.85rem;padding:40px 0}
footer .wrap{display:flex;flex-wrap:wrap;gap:20px 40px;justify-content:space-between;align-items:flex-start}
footer a{color:#b6c4d4}
footer p{margin:0 0 8px;max-width:40rem}
footer .links{display:flex;gap:18px;flex-wrap:wrap}

/* inner pages (confirm, status) */
.inner{max-width:640px;margin:0 auto;padding:56px 24px 96px}
.inner h1{font-size:clamp(1.9rem,4vw,2.4rem);margin:10px 0 18px}
.panel{background:#fff;border:1px solid var(--rule);border-radius:16px;padding:26px;box-shadow:var(--shadow)}
.panel dl{display:grid;grid-template-columns:8.5rem 1fr;gap:12px 16px;margin:0}
.panel dt{color:var(--muted);font-size:.92rem}.panel dd{margin:0;color:var(--ink)}
@media (max-width:520px){.panel dl{grid-template-columns:1fr;gap:2px}.panel dd{margin-bottom:10px}}
.panel .actions{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0 14px}
#confirm-map{height:220px;border-radius:10px;border:1px solid var(--rule);margin:0 0 20px;background:#e8eef5}
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

LOGO = mark_svg(28)
PIN_ICON = ('<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s7-6.6 7-12a7 7 0 1 0-14 0c0 '
            '5.4 7 12 7 12z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="2.5" '
            'fill="currentColor"/></svg>')

WARNING_VIS = """<svg viewBox="0 0 300 150" role="img" aria-label="A property inside a warning area">
<rect width="300" height="150" fill="#f3f6f9"/>
<path d="M28 118 52 26 196 14 238 92 150 136z" fill="rgba(242,169,59,.14)" stroke="#d68f1f" stroke-width="2"
 stroke-dasharray="7 5" stroke-linejoin="round"/>
<path d="M182 140 210 58 292 70 296 140z" fill="rgba(61,127,194,.07)" stroke="#9db4cc" stroke-width="1.5" stroke-dasharray="5 5"/>
<circle cx="132" cy="76" r="17" fill="rgba(242,169,59,.25)"/>
<circle cx="132" cy="76" r="8" fill="#f2a93b" stroke="#0b1a2e" stroke-width="3"/>
<text x="146" y="100" font-family="Geist,sans-serif" font-size="12" font-weight="600" fill="#14202e">The property</text>
<text x="66" y="44" font-family="Geist Mono,monospace" font-size="10" fill="#8a5a0b">TORNADO WARNING AREA</text>
</svg>"""


def layout(title: str, body: str, refresh: int | None = None, description: str = "", map_assets: bool = False) -> str:
    meta = f'<meta http-equiv="refresh" content="{refresh}">' if refresh else ""
    desc = escape(description or "Historical weather report for one US address and date of loss: measured wind and "
                  "rain from named stations, NWS warnings, storm reports, hail and lightning, each with its distance "
                  f"from the property. {PRICE} PDF.", quote=True)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">{meta}
<title>{escape(title)}</title><meta name="description" content="{desc}">
<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{desc}">
<meta property="og:image" content="/static/sample-p1.webp"><meta name="theme-color" content="#0b1a2e">
<link rel="icon" href="{FAVICON}"><link rel="apple-touch-icon" href="/static/apple-touch-icon.png">{FONTS}
{MAP_ASSETS if map_assets else ""}<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><a class="brand" href="/">{LOGO}<span>{BRAND}</span></a>
<nav><a class="hide-sm" href="/#report">What you get</a><a class="hide-sm" href="/#compare">Compare</a>
<a class="hide-sm" href="/#sample">Sample report</a><a class="hide-sm" href="/#faq">FAQ</a>
<a class="btn btn-amber" href="/#order">Order · {PRICE}</a></nav></div></header>
<main>{body}</main>{FOOTER}</body></html>"""


FOOTER = f"""<footer><div class="wrap"><div><a class="brand" href="/" style="margin-bottom:14px">{LOGO}<span>{BRAND}</span></a>
<p>Not affiliated with NOAA, the National Weather Service or any government agency. Reports compile public records;
they are not certified records or expert opinions.</p></div>
<div><p class="links"><a href="/#sample">Sample report</a><a href="/#faq">FAQ</a><a href="/#order">Order</a></p>
<p>{DOMAIN} · Payments processed by Creem</p></div></div></footer>"""


def order_form(v: dict, error: str = "", ask_coords: bool = False, title: str = "Get the report") -> str:
    g = lambda k: escape(str(v.get(k) or ""), quote=True)  # noqa: E731
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    show_coords = ask_coords or bool(v.get("lat"))
    err = f'<p class="err" role="alert">{escape(error)}</p>' if error else ""
    return f"""<div class="form-card" id="order"><h3>{escape(title)}</h3>
<p class="sub">Any US address · dates of loss from {MIN_DATE.year} to yesterday</p>{err}
<form method="post" action="/order" id="order-form" novalidate>
<label for="address">Property address</label>
<div class="ac"><input id="address" name="address" autocomplete="off" value="{g('address')}" role="combobox"
 aria-autocomplete="list" aria-expanded="false" aria-controls="ac-list" placeholder="Start typing an address">
<ul id="ac-list" role="listbox" hidden></ul></div>
<p class="fine" id="addr-hint" aria-live="polite"></p>
<div id="map-wrap" hidden><div class="locate"><span class="fine" style="margin:0">Or click the map. The address and
the pin stay in sync.</span><span class="pinned" id="pinned">{PIN_ICON}<span>Pinned</span></span></div>
<div id="map"></div><p class="fine" id="map-note" aria-live="polite">Type the address above or click the property on
the map.</p></div>
<div id="coords" class="row2" {"" if show_coords else "hidden"}><label>Latitude<input name="lat" id="lat" inputmode="decimal"
 value="{g('lat')}" placeholder="39.16955"></label><label>Longitude<input name="lon" id="lon" inputmode="decimal"
 value="{g('lon')}" placeholder="-86.53493"></label></div>
<div class="row2"><label>Date of loss<input type="date" name="loss_date" required min="{MIN_DATE.isoformat()}"
max="{yesterday}" value="{g('loss_date')}"></label>
<label>Email for delivery<input type="email" name="email" required autocomplete="email" value="{g('email')}"
placeholder="you@company.com"></label></div>
<button class="btn btn-amber btn-block" type="submit">Continue</button>
<p class="fine">Next you'll see the exact location on a map before paying {PRICE}.</p>
</form></div>"""


def landing(form: str) -> str:
    s = SAMPLE
    hero = f"""<section class="hero"><div class="wrap">
<div><p class="eyebrow">Weather records · any US address</p>
<h1>What the weather did at the loss site.</h1>
<p class="lede">A report of what was measured, warned and reported around one address on one date: gusts, rain,
warnings, hail and tornadoes, each with its distance from the property. {PRICE}, delivered in about a minute.</p>
{form}</div>
<figure class="figure"><div class="mapcard">
<div class="mc-head">{mark_svg(24)}<div><b>Sample report: 401 N College Ave, {s['place']}</b><span>Date of loss:
{s['date']} · records within 9 miles</span></div></div>
<div id="hero-map" data-src="/static/site-map.json" role="img" aria-label="Map of weather records around the property"></div>
<ul class="mc-legend"><li><i class="lg lg-site"></i>Property</li><li><i class="lg lg-station"></i>Weather station</li>
<li><i class="lg lg-warn"></i>Tornado warning area</li><li><i class="lg lg-path"></i>Tornado path</li>
<li><i class="lg lg-hail"></i>Radar hail</li><li><i class="lg lg-report"></i>Hail report</li></ul>
<dl class="findings">
<div><dt>Peak wind gust</dt><dd><b>70 mph</b> at 7:01 PM<br>Airport station, 4.7 mi WSW</dd></div>
<div><dt>Tornado warning</dt><dd><b>Inside</b> the warning area<br>6:39 – 7:30 PM</dd></div>
<div><dt>Tornado</dt><dd><b>EF2</b>, path 2.0 mi WSW<br>at its closest</dd></div>
<div><dt>Largest hail nearby</dt><dd><b>1.5 in</b> reported<br>1.9 mi SE, 7:05 PM</dd></div>
</dl></div>
<figcaption>Real records from a real report. <a href="{s['pdf']}" target="_blank" rel="noopener">Open the full sample
PDF</a></figcaption></figure>
</div></section>
<div class="sources"><div class="wrap"><span>Built on public records from</span><b>NOAA</b><b>National Weather Service</b>
<b>NEXRAD radar</b><b>US Census Bureau</b></div></div>"""

    questions = f"""<section id="report"><div class="wrap">
<div class="section-head"><p class="eyebrow">What you get</p><h2>Answers to the three questions every weather claim asks.</h2></div>
<div class="grid3">
<article class="q"><div class="vis">{WIND_CHART}<div class="vis-cap">AIRPORT STATION KBMG · 4.7 MI FROM THE PROPERTY</div></div>
<h3>How strong was the wind?</h3><p>Gusts, sustained wind, rain and temperature measured at the nearest weather
stations through the day. Each reading names its station and how far away it is.</p></article>
<article class="q"><div class="vis">{WARNING_VIS}<span class="inside">✓ Inside the warning area</span></div>
<h3>Was the property under a warning?</h3><p>Every National Weather Service watch and warning for that day,
with the property's location checked against each warning's official area.</p></article>
<article class="q"><div class="vis"><div class="rows">
<div class="rowi"><span><b>1.5 in hail</b> · ground report</span><span class="chip">1.9 mi SE</span></div>
<div class="rowi"><span><b>EF2 tornado</b> · path</span><span class="chip">2.0 mi WSW</span></div>
<div class="rowi"><span><b>70 mph gust</b> · airport</span><span class="chip">4.7 mi WSW</span></div>
<div class="rowi"><span><b>1.5 in hail</b> · radar</span><span class="chip">1.2 mi NNE</span></div></div></div>
<h3>What was reported nearby?</h3><p>Storm reports, NOAA's reviewed Storm Events records and radar hail detections,
sorted by distance and direction from the property.</p></article>
</div>
<div class="also"><span>Also in every report:</span><span class="t">Lightning counts</span><span class="t">Full warning
text</span><span class="t">Raw station reports</span><span class="t">Local times with time zone</span><span class="t">Source
hashes for verification</span></div>
</div></section>"""

    rows = [
        ("Price", "Free", f"<b>{PRICE}</b> per report", "Hourly or project fees"),
        ("Turnaround", "Instant", "About a minute", "Days to weeks"),
        ("Readings tied to a named station", "Rarely", "yes", "yes"),
        ("Distance and direction to every record", "no", "yes", "yes"),
        ("Property checked against warning areas", "no", "yes", "yes"),
        ("Storm reports, Storm Events and radar hail", "Partly", "yes", "yes"),
        ("Expert analysis or testimony", "no", "no", "yes"),
    ]

    def cell(v):
        return {"yes": '<span class="yes">Yes</span>', "no": '<span class="no">No</span>'}.get(v, f"<span>{v}</span>")

    body = "".join(f"<tr><td>{a}</td><td data-label='Free sites'>{cell(b)}</td>"
                   f"<td class='us' data-label='{BRAND}'>{cell(c)}</td><td data-label='Expert'>{cell(d)}</td></tr>"
                   for a, b, c, d in rows)
    compare = f"""<section class="alt" id="compare"><div class="wrap">
<div class="section-head"><p class="eyebrow">Compare</p><h2>Between a free weather site and an expert.</h2>
<p class="lede">Detailed enough for a claim file, priced for every claim. If you later need an expert, the report
gives them every source to start from.</p></div>
<div><table class="compare"><thead><tr><th></th><th>Free weather sites</th><th class="us">{BRAND}</th>
<th>Forensic meteorologist</th></tr></thead><tbody>{body}</tbody></table></div>
</div></section>"""

    pages = [("1", "Key findings"), ("2", "Station measurements"), ("4", "Warnings & storm reports"),
             ("6", "Storm Events"), ("7", "Hail & lightning")]
    thumbs = "".join(f'<a href="{s["pdf"]}#page={p}" target="_blank" rel="noopener"><div class="thumb">'
                     f'<img loading="lazy" src="/static/sample-p{p}.webp" alt="Sample report page {p}: {t}" '
                     f'width="935" height="1210"></div><span>{t}</span>Page {p}</a>' for p, t in pages)
    sample = f"""<section id="sample"><div class="wrap">
<div class="section-head"><p class="eyebrow">Sample report</p><h2>Read a real report before you buy.</h2>
<p class="lede">The full {s['pages']}-page report for {s['place']} on {s['date']}, unedited.</p></div>
<div class="gallery">{thumbs}</div>
<div class="actions-row"><a class="btn btn-navy" href="{s['pdf']}" target="_blank" rel="noopener">Open the sample PDF</a></div>
</div></section>"""

    how = """<section class="alt" id="how"><div class="wrap">
<div class="section-head"><p class="eyebrow">How it works</p><h2>Ordered in a minute, delivered in another.</h2></div>
<ol class="steps">
<li><div><b>Enter the address and date</b><span>Pick the address from the suggestions, or place a pin on the map
for rural or new properties.</span></div></li>
<li><div><b>Confirm the location and pay</b><span>You see the exact spot on a map before paying. Secure checkout
by Creem.</span></div></li>
<li><div><b>Download the PDF</b><span>Built from the government archives while you wait, with a copy sent to your
email.</span></div></li></ol></div></section>"""

    faq_items = [
        ("Is this a certified weather report?",
         "No. It compiles public records from NOAA, the National Weather Service and the US Census Bureau and shows "
         "where each one came from. It is not a certified government record or an expert opinion."),
        ("How close is the weather data to the property?",
         "That depends on where the nearest stations are. The report names every station and gives its distance and "
         "direction, so you can judge how representative it is."),
        ("Which dates can I order?",
         f"Any completed day from {MIN_DATE.year} to yesterday. NOAA publishes its Storm Events database a few months "
         "after each month ends; for recent dates the report says so, and includes everything else."),
        ("What if the address isn't found?",
         "Place a pin on the map instead. The report notes that the location was set by pin."),
        ("What if the report can't be built?",
         "We're notified automatically and will deliver the report or refund you."),
    ]
    faq = "".join(f"<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in faq_items)
    faq_html = f"""<section id="faq"><div class="wrap">
<div class="section-head center"><p class="eyebrow">FAQ</p><h2>Common questions.</h2></div>
<div class="faq">{faq}</div></div></section>"""

    cta = f"""<section class="cta"><div class="wrap"><h2>Get the weather record for your date of loss.</h2>
<p>{PRICE} per report. Any US address.</p><a class="btn btn-amber" href="#order">Start your report</a></div></section>"""
    return hero + questions + compare + sample + how + faq_html + cta


def inner(body: str) -> str:
    return f'<div class="inner">{body}</div>'


def status_block(kind: str, title: str, text: str) -> str:
    dot = {"wait": "", "ok": " ok", "bad": " bad"}[kind]
    return f'<div class="status"><span class="dot{dot}"></span><div><p><b>{title}</b></p>{text}</div></div>'
