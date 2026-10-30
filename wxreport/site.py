"""Public pages: the landing/order page and the buyer's order pages, with one shared look.

Audience: adjusters, public adjusters, roofing contractors, attorneys and policyholders documenting a loss.
Principles: say each thing once, in plain words; show the product with real data (the hero map and the wind
chart are drawn from the sample report by scripts/make_site_map.py); put the order form where people land.
"""
import json
import re
from datetime import date, timedelta
from html import escape
from pathlib import Path

from . import BRAND, DOMAIN, SUPPORT_EMAIL
from .brand import FAVICON, mark_svg
from .geocode import _pretty
from .report import MIN_DATE

PRICE = "$9.99"
STATIC = Path(__file__).parent / "static"
SAMPLE = {
    "place": "Bloomington, IN",
    "date": "February 19, 2026",
    "pages": 26,
    "pdf": "/static/sample-report.pdf",
    "id": "WE-2026-02-19-4486E5C490DC",
}
WIND_CHART = (STATIC / "wind-chart.svg").read_text()
SAMPLE_PAGE1 = json.loads((STATIC / "site-map.json").read_text())   # built from the sample report's page 1

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
              '<script defer src="/static/order.js"></script><script defer src="/static/hero.js"></script>'
              '<script defer src="/static/storms.js"></script>')

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
.mnav{display:none}
@media (max-width:760px){
  .top nav{gap:12px}
  .mnav{display:block}
  .mnav summary{list-style:none;cursor:pointer;width:40px;height:40px;display:grid;place-content:center;gap:5px;border-radius:9px;
    border:1px solid rgba(255,255,255,.18)}
  .mnav summary::-webkit-details-marker{display:none}
  .mnav summary span{display:block;width:18px;height:2px;border-radius:1px;background:#e4ebf3;transition:transform .15s,opacity .15s}
  .mnav[open] summary span:nth-child(1){transform:translateY(7px) rotate(45deg)}
  .mnav[open] summary span:nth-child(2){opacity:0}
  .mnav[open] summary span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
  .mnav-panel{position:fixed;top:62px;left:0;right:0;display:flex;flex-direction:column;padding:8px 16px 18px;
    background:var(--navy-900);border-bottom:1px solid rgba(255,255,255,.08);box-shadow:0 18px 40px rgba(7,17,31,.35);
    max-height:calc(100vh - 62px);overflow:auto}
  .top nav .mnav-panel a{color:#e4ebf3;font-size:1rem;padding:13px 4px;border-bottom:1px solid rgba(255,255,255,.07)}
  .top nav .mnav-panel a:hover{color:#fff}
  .top nav .mnav-panel a:last-child{border-bottom:0}
}
@media (max-width:420px){.top .btn{padding:8px 11px;font-size:.84rem}}
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

/* hero: one message, one action, one product visual; always fits the window on desktop */
.hero{--pad:clamp(20px,4.5vh,56px);--strip:52px;display:flex;flex-direction:column;
  min-height:calc(100svh - 62px);color:#c9d5e3;padding:0;
  background:radial-gradient(1000px 600px at 80% 10%,#1f3d63 0%,rgba(31,61,99,0) 65%),var(--navy-900)}
.hero-main{flex:1;display:grid;grid-template-columns:minmax(0,1fr) minmax(360px,460px);gap:clamp(32px,5vw,72px);
  align-items:center;padding-top:var(--pad);padding-bottom:var(--pad)}
.hero .eyebrow{color:var(--amber)}
.hero h1{color:#fff;margin:16px 0 18px;font-size:clamp(2.3rem,min(5.2vw,8vh),4.1rem)}
.hero .lede{color:#aebdcd;max-width:32rem;font-size:clamp(1rem,1.1vw + .4rem,1.15rem)}
.cta-row{display:flex;flex-wrap:wrap;gap:12px;margin-top:clamp(20px,4vh,32px)}
.cta-row .btn{padding:15px 24px;font-size:1rem}
.btn-ghost-dark{background:transparent;color:#e4ebf3;border:1px solid rgba(255,255,255,.25)}
.btn-ghost-dark:hover{background:rgba(255,255,255,.06)}
.assure{display:flex;flex-wrap:wrap;gap:8px 20px;margin:18px 0 0;padding:0;list-style:none;font-size:.86rem;color:#8fa3b8}
.assure li{display:flex;align-items:center;gap:7px}
.assure li:before{content:"";width:6px;height:6px;border-radius:50%;background:var(--amber)}
.hero-strip{flex:none;height:var(--strip);border-top:1px solid rgba(255,255,255,.07);background:rgba(7,17,31,.55)}
.hero-strip .wrap{height:100%;display:flex;flex-wrap:wrap;gap:6px 26px;align-items:center;justify-content:center;
  font-size:.84rem;color:#7f93a8}
.hero-strip b{color:#cfd9e4;font-weight:500}

/* the report card (page 1 of the sample report), sized to the space the hero leaves */
.rp{background:#fff;color:var(--body);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;
  height:clamp(430px,calc(100svh - 62px - var(--strip) - 2 * var(--pad)),700px);
  box-shadow:0 30px 70px -20px rgba(0,0,0,.5),0 10px 24px rgba(0,0,0,.18)}
.rp-head{flex:none;display:flex;gap:10px;align-items:center;padding:12px 16px;border-bottom:1px solid var(--rule)}
.rp-head svg{flex:none;border-radius:6px}
.rp-head .k{font:500 .64rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
.rp-head b{display:block;color:var(--ink);font-size:.9rem;font-weight:600;letter-spacing:-.015em}
.rp-head span{color:var(--muted);font-size:.8rem}
#hero-map{flex:1;min-height:120px;background:#eef1f4}
#hero-map .leaflet-tile-pane{filter:grayscale(1) contrast(.92) brightness(1.06)}
#hero-map .leaflet-tooltip{font:600 .72rem/1.25 var(--sans);color:var(--ink);border-radius:6px;padding:3px 6px;
  border:1px solid var(--rule);box-shadow:0 2px 8px rgba(0,0,0,.12)}
.mc-legend{flex:none;display:flex;flex-wrap:wrap;gap:4px 12px;margin:0;padding:8px 16px;list-style:none;font-size:.72rem;
  color:var(--muted);border-top:1px solid var(--rule)}
.mc-legend li{display:flex;align-items:center;gap:5px}
.facts{flex:none;display:grid;grid-template-columns:1fr 1fr;margin:0;border-top:1px solid var(--rule)}
.facts div{padding:10px 16px;border-bottom:1px solid var(--rule)}
.facts div:nth-child(odd){border-right:1px solid var(--rule)}
.facts dt{font:500 .62rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
.facts dd{margin:2px 0 0;color:var(--muted);font-size:.76rem;line-height:1.35}
.facts dd b{display:block;color:var(--ink);font-weight:650;font-size:1.15rem;letter-spacing:-.03em;line-height:1.2}
.rp-foot{flex:none;display:flex;justify-content:space-between;align-items:center;padding:10px 16px;font-size:.8rem;
  color:var(--muted);background:var(--paper)}
.rp-foot a{color:var(--navy-700);font-weight:550;text-decoration:none}
.rp-foot a:hover{text-decoration:underline}
@media (max-height:700px) and (min-width:961px){.mc-legend{display:none}.rp-head{padding:9px 14px}}
@media (max-width:960px){
  .hero{min-height:0}
  .hero-main{grid-template-columns:1fr;padding-top:48px;padding-bottom:48px}
  .rp{height:auto}#hero-map{flex:none;height:300px}
  .hero-strip{height:auto}.hero-strip .wrap{padding:14px 24px}
}
@media (max-width:520px){.cta-row .btn{flex:1 1 100%}.hero h1{font-size:2.35rem}}
.lg{display:inline-block;flex:none}
.lg-site{width:11px;height:11px;border-radius:50%;background:var(--amber);box-shadow:0 0 0 2px var(--navy-900) inset}
.lg-station{width:10px;height:10px;border-radius:2px;background:var(--navy-800)}
.lg-path{width:18px;height:4px;border-radius:2px;background:#d9442e}
.lg-warn{width:16px;height:11px;border:1.4px dashed #d68f1f;background:rgba(242,169,59,.15)}
.lg-hail{width:11px;height:11px;border-radius:50%;background:rgba(61,127,194,.25);border:1px solid var(--sky)}
.lg-report{width:8px;height:8px;background:var(--sky);transform:rotate(45deg);margin:0 2px}
.lg-wind{width:9px;height:9px;border-radius:50%;background:#6b4fa0}

/* order page */
.order-wrap{max-width:680px;margin:0 auto;padding:48px 24px 96px}
.order-wrap h1{font-size:clamp(1.9rem,4vw,2.5rem);margin:0 0 8px}
.order-wrap .lede{margin-bottom:24px;font-size:1rem}
.stepper{display:flex;gap:8px;margin:0 0 28px;padding:0;list-style:none;font-size:.82rem;color:var(--faint)}
.stepper li{flex:1;border-top:3px solid var(--rule);padding-top:8px}
.stepper li.on{border-color:var(--amber);color:var(--ink);font-weight:550}
.stepper li.done{border-color:var(--navy-700);color:var(--muted)}
.order-wrap .form-card{box-shadow:var(--shadow);border:1px solid var(--rule)}
.includes{display:flex;flex-wrap:wrap;gap:8px 18px;margin:20px 0 0;padding:0;list-style:none;font-size:.85rem;color:var(--muted)}
.includes li:before{content:"✓ ";color:var(--green);font-weight:700}

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
.cmp-cards{display:none}
@media (max-width:700px){
  .compare{display:none}
  .cmp-cards{display:grid;gap:14px}
  .cmp-card{background:#fff;border:1px solid var(--rule);border-radius:16px;overflow:hidden}
  .cmp-card h3{margin:0;padding:14px 16px;font-size:1rem;background:var(--paper);border-bottom:1px solid var(--rule)}
  .cmp-card.us{border-color:var(--navy-900);box-shadow:0 0 0 1px var(--navy-900)}
  .cmp-card.us h3{background:var(--navy-900);color:#fff}
  .cmp-card ul{list-style:none;margin:0;padding:4px 16px}
  .cmp-card li{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:11px 0;
    border-bottom:1px solid var(--rule);font-size:.93rem}
  .cmp-card li:last-child{border-bottom:0}
  .cmp-card .k{color:var(--muted)}
  .cmp-card .v{text-align:right;color:var(--ink);font-weight:550;flex:none;max-width:48%}
  .cmp-card.us .v{font-weight:600}
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
/* articles: methodology, certified records, guides */
.article{max-width:720px;margin:0 auto;padding:48px 24px 96px}
.crumbs{font-size:.85rem;color:var(--muted);margin:0 0 22px}.crumbs a{color:var(--muted)}
.article h1{font-size:clamp(1.9rem,4vw,2.5rem);line-height:1.15;letter-spacing:-.03em;margin:10px 0 18px}
.article .lede{margin:0 0 8px}
.article .updated{font-size:.82rem;color:var(--faint);margin:0 0 18px}
.article h2{font-size:1.25rem;letter-spacing:-.02em;margin:34px 0 10px}
.article p,.article li{line-height:1.7;color:var(--body)}
.article p{margin:0 0 14px}.article ul{padding-left:1.2rem;margin:0 0 14px}.article li{margin:0 0 6px}
.article .fine{font-size:.88rem;color:var(--muted)}
.ctable{width:100%;border-collapse:collapse;margin:20px 0 14px;font-size:.92rem}
.ctable th,.ctable td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--rule);vertical-align:top}
.ctable th{color:var(--ink);font-weight:600}.ctable td:first-child{color:var(--muted)}
@media (max-width:620px){.ctable{display:block;overflow-x:auto}}
.cta-box{display:flex;gap:18px 24px;align-items:center;justify-content:space-between;flex-wrap:wrap;margin:40px 0 0;
  padding:22px 24px;background:#fff;border:1px solid var(--rule);border-radius:14px;box-shadow:var(--shadow)}
.cta-box b{display:block;color:var(--ink);margin:0 0 4px}.cta-box span{color:var(--muted);font-size:.92rem;line-height:1.5}
.cta-box div{flex:1 1 300px}
.glist,.article .glist{list-style:none;padding:0;margin:24px 0 0;display:grid;gap:14px}
.glist a{display:block;padding:20px 22px;background:#fff;border:1px solid var(--rule);border-radius:14px;
  text-decoration:none;color:var(--body)}
.glist a:hover{border-color:#c6d0db}
.glist b{display:block;color:var(--ink);font-size:1.08rem;margin:0 0 6px;letter-spacing:-.015em}
.glist span{font-size:.92rem;line-height:1.55}
.more{margin:48px 0 0;padding:28px 0 0;border-top:1px solid var(--rule)}
.more h2{margin-top:0}
/* storm reports */
.sr-wrap{max-width:960px;margin:0 auto;padding:44px 24px 96px}
.sr-wrap section{padding:0}
.sr-intro h1{font-size:clamp(1.9rem,4vw,2.6rem);line-height:1.12;letter-spacing:-.035em;margin:10px 0 14px}
.sr-intro .lede{max-width:46rem;margin:0 0 22px}
.sr-checked{font:500 .76rem/1.4 var(--mono);color:var(--faint);margin:-6px 0 12px}
.sr-block{margin:48px 0 0}
.sr-block h2{font-size:1.35rem;letter-spacing:-.02em;margin:0 0 14px}
.sr-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin:0 0 14px}
.sr-head h2{margin:0}
.sr-note{color:var(--muted);font-size:.92rem;margin:-6px 0 16px;max-width:44rem}
.sr-badge{display:inline-block;flex:none;font:600 .66rem/1 var(--mono);letter-spacing:.05em;text-transform:uppercase;
  border-radius:999px;padding:5px 8px;white-space:nowrap}
.sr-badge.pre{background:var(--amber-50);color:var(--amber-ink);border:1px solid #f0cf9c}
.sr-badge.rev{background:var(--green-50);color:var(--green);border:1px solid #bfe0cd}
.sr-wide{max-width:1040px}
.sr-tbl{margin-top:28px}
.sr-filters{display:grid;grid-template-columns:minmax(220px,1.6fr) repeat(3,minmax(130px,1fr)) auto;gap:12px;align-items:end;
  padding:16px;background:#fff;border:1px solid var(--rule);border-radius:14px}
.sr-filters.js{grid-template-columns:minmax(220px,1.6fr) repeat(3,minmax(130px,1fr))}
.sr-fsheet{display:contents}
.sr-filters .sr-fsh,.sr-filters .sr-fsort,.sr-factions .btn-ghost,.sr-filters .sr-fbtn{display:none}
.sr-filters.js .sr-factions{display:none}
.sr-factions{display:flex;gap:10px}
.sr-f{display:flex;flex-direction:column;gap:5px;margin:0;font-weight:400}
.sr-f span{font:500 .68rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
.sr-f input,.sr-f select{width:100%;margin:0;padding:10px 12px;font:inherit;font-size:.95rem;color:var(--ink);background:#fff;
  border:1px solid #c3ccd7;border-radius:9px;min-height:44px}
.sr-f select{appearance:none;padding-right:30px;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' fill='none' stroke='%235d6b7c' stroke-width='1.5'/%3E%3C/svg%3E") right 12px center no-repeat}
.sr-f input:focus,.sr-f select:focus{outline:none;border-color:var(--navy-700);box-shadow:0 0 0 3px rgba(28,53,84,.14)}
.sr-filters .btn{min-height:44px;padding:10px 18px}
.sr-vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.sr-backdrop{position:fixed;inset:0;z-index:1500;background:rgba(7,17,31,.45)}
.sr-fclose{border:0;background:none;font-size:1.6rem;line-height:1;color:var(--muted);cursor:pointer;padding:0 4px}
@media (max-width:820px){.sr-filters,.sr-filters.js{grid-template-columns:1fr 1fr}.sr-fq{grid-column:1/-1}
  .sr-factions{grid-column:1/-1}}
/* phones with JavaScript: search + filter button; the other filters open as a bottom sheet */
@media (max-width:640px){
  .sr-filters.js{grid-template-columns:1fr auto;padding:0;background:none;border:0;align-items:end}
  .sr-filters.js .sr-fq{grid-column:1}.sr-filters.js .sr-fq span{display:none}
  .sr-filters.js .sr-fbtn{display:inline-flex;position:relative;align-items:center;justify-content:center;width:48px;height:44px;
    border:1px solid #c3ccd7;border-radius:9px;background:#fff;color:var(--ink);cursor:pointer}
  .sr-fcount{position:absolute;top:-6px;right:-6px;min-width:18px;height:18px;border-radius:9px;background:var(--navy-800);
    color:#fff;font:600 .68rem/18px var(--sans);text-align:center;padding:0 4px}
  .sr-filters.js .sr-fsheet{display:none}
  .sr-filters.js.open .sr-fsheet{display:grid;gap:14px;position:fixed;left:0;right:0;bottom:0;z-index:1600;background:#fff;
    padding:16px 18px calc(18px + env(safe-area-inset-bottom));border-radius:18px 18px 0 0;box-shadow:0 -10px 40px rgba(7,17,31,.25)}
  .sr-filters.js.open .sr-fsh{display:flex;justify-content:space-between;align-items:center}
  .sr-filters.js.open .sr-f.sr-fsort{display:flex}
  .sr-filters.js.open .sr-factions{display:flex}.sr-filters.js.open .sr-factions .btn{flex:1;display:inline-flex}
}
.sr-count{margin:14px 2px 10px;font-size:.88rem;color:var(--muted)}
.sr-count a{font-weight:550}
.sr-tw{background:#fff;border:1px solid var(--rule);border-radius:14px;overflow:hidden}
.sr-table{width:100%;border-collapse:collapse;font-size:.94rem}
.sr-table th{text-align:left;font:500 .68rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--faint);
  padding:12px 16px;background:var(--paper);border-bottom:1px solid var(--rule);white-space:nowrap}
.sr-table th a{color:inherit;text-decoration:none}.sr-table th a:hover,.sr-table th a.on{color:var(--ink)}
.sr-table td{padding:12px 16px;border-bottom:1px solid var(--rule);vertical-align:middle}
.sr-table tr:last-child td{border-bottom:0}
.sr-table .sr-cn{text-align:right;white-space:nowrap}
.sr-table td.sr-cn b{display:block;color:var(--ink);font-weight:600}
.sr-table td.sr-cn small{display:block;color:var(--faint);font-size:.76rem}
.sr-table tbody tr{position:relative}
.sr-rl{color:var(--ink);font-weight:600;text-decoration:none}
.sr-rl:after{content:"";position:absolute;inset:0}
.sr-rl:focus-visible{outline:none}.sr-table tbody tr:focus-within{box-shadow:inset 3px 0 0 var(--navy-700)}
.sr-table tbody tr:hover{background:#f7f9fb;cursor:pointer}.sr-table tbody tr:hover .sr-rl{color:var(--navy-700)}
.sr-table tr.sr-on{background:var(--navy-100)}.sr-table tr.sr-on .sr-rl{color:var(--navy-800)}
.sr-table tr.sr-on td:first-child{box-shadow:inset 3px 0 0 var(--navy-700)}
.sr-cd{white-space:nowrap;color:var(--muted);font-variant-numeric:tabular-nums}
.sr-cc .sr-tag,.sr-cc .sr-badge{margin-left:8px}
.sr-table tr.sr-yr th{background:var(--paper);color:var(--ink);font:600 .9rem/1.3 var(--sans);letter-spacing:0;text-transform:none;
  padding:10px 16px}
.sr-table tr.sr-yr th span{color:var(--faint);font-weight:400;font-size:.82rem;margin-left:6px}
/* city page: the city's record (fixed), then the workspace: storm card + list of storm days */
.sr-wrap .sr-record{margin:26px 0 0;padding:14px 16px 16px;background:var(--navy-100);border-radius:16px}
.sr-rk{margin:0 0 10px;font:500 .7rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--navy-700)}
.sr-record .sr-tiles{margin:0;border-color:#d3dde8}
.sr-work{display:grid;grid-template-columns:280px minmax(0,1fr);grid-template-areas:"days storm";gap:24px;
  align-items:start;margin:36px 0 0}
.sr-panel{grid-area:storm;background:#fff;border:1px solid var(--rule);border-radius:18px;box-shadow:var(--shadow);
  overflow:hidden;scroll-margin-top:80px;outline:none}
.sr-panel[aria-busy=true]{opacity:.55;transition:opacity .15s}
.sr-ph{display:flex;flex-wrap:wrap;align-items:flex-end;gap:6px 14px;padding:18px 22px;background:var(--navy-900);color:#fff}
.sr-pk{flex-basis:100%;margin:0;font:500 .7rem/1.3 var(--mono);letter-spacing:.07em;text-transform:uppercase;color:var(--amber)}
.sr-ph h2{color:#fff;font-size:1.45rem;letter-spacing:-.025em;margin:0}
.sr-pills{display:flex;gap:6px;margin-left:auto}
.sr-pill{display:inline-block;font:600 .66rem/1 var(--mono);letter-spacing:.05em;text-transform:uppercase;border-radius:999px;
  padding:5px 8px;background:var(--amber);color:#1b1205}
.sr-ph .sr-tag{background:#fbeae7}
.sr-tolatest{color:#cfd9e4;font-size:.85rem;font-weight:550;text-decoration:none;align-self:center}
.sr-tolatest:hover{color:#fff}
.sr-pb{padding:20px 22px 6px}
.sr-pb .sr-tiles{margin:0 0 16px}
.sr-pt{font-size:1rem;margin:20px 0 10px}
.sr-pb .sr-block{margin-top:28px}.sr-pb .sr-block h2{font-size:1.1rem}
.sr-pf{display:grid;grid-template-columns:1fr auto;gap:12px 20px;align-items:center;margin-top:18px;padding:18px 22px;
  background:var(--paper);border-top:1px solid var(--rule)}
.sr-porder b{display:block;color:var(--ink);font-size:.98rem}.sr-porder span{color:var(--muted);font-size:.88rem;line-height:1.5}
.sr-pf .sr-pager{grid-column:1/-1;margin:0;padding-top:12px;border-top:1px solid var(--rule)}
.sr-pf .sr-pager a{color:var(--navy-700)}
.sr-dlist{grid-area:days;position:sticky;top:80px;background:#fff;border:1px solid var(--rule);border-radius:16px;overflow:hidden}
.sr-dlist h2{font-size:1rem;margin:0;padding:14px 16px;border-bottom:1px solid var(--rule)}
.sr-dlist h2 span{color:var(--faint);font-weight:400;font-size:.88rem;margin-left:4px}
.sr-dscroll{position:relative;max-height:calc(100vh - 160px);overflow:auto;overscroll-behavior:contain}
.sr-dlist h3{position:sticky;top:0;z-index:1;margin:0;padding:8px 16px;background:var(--paper);font-size:.82rem;
  border-bottom:1px solid var(--rule)}
.sr-dlist h3 span{color:var(--faint);font-weight:400;margin-left:4px}
.sr-dlist ul{list-style:none;margin:0;padding:0}
.sr-dlist li+li{border-top:1px solid var(--rule)}
.sr-dlist a{display:grid;grid-template-columns:1fr auto;gap:2px 8px;padding:10px 16px;text-decoration:none;color:var(--body)}
.sr-dlist a:hover{background:#f7f9fb}
.sr-dlist a[aria-current]{background:var(--navy-100);box-shadow:inset 3px 0 0 var(--navy-700)}
.sr-ld{color:var(--ink);font-weight:600;font-size:.9rem}
.sr-ls{grid-column:1/-1;color:var(--muted);font-size:.82rem}
.sr-dlist .sr-tag{grid-column:2;grid-row:1;align-self:center;font-size:.6rem;padding:4px 6px}
/* the day strip (phones and tablets): chips that scroll sideways, plus "All days" for the full list */
.sr-strip{display:none}
@media (max-width:900px){
  .sr-work{grid-template-columns:1fr;grid-template-areas:"storm" "days";gap:20px;margin-top:24px}
  .sr-dlist{position:static}.sr-dscroll{max-height:none}
  .sr-ph{padding:14px 16px}.sr-ph h2{font-size:1.2rem}.sr-pb{padding:14px 16px 4px}
  .sr-pf{grid-template-columns:1fr;padding:14px 16px}.sr-pf .btn{justify-self:start}
  .sr-strip{display:flex;align-items:center;gap:8px;padding:10px 0 10px 16px;background:var(--navy-800);
    border-top:1px solid rgba(255,255,255,.08)}
  .sr-chips-x{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x proximity;scrollbar-width:none;flex:1;min-width:0}
  .sr-chips-x::-webkit-scrollbar{display:none}
  .sr-chip{flex:none;scroll-snap-align:center;display:flex;flex-direction:column;gap:1px;padding:7px 11px;border-radius:10px;
    background:rgba(255,255,255,.08);color:#cfd9e4;text-decoration:none;font-size:.72rem;line-height:1.25}
  .sr-chip b{color:#fff;font-size:.84rem;font-weight:600;white-space:nowrap}
  .sr-chip span{white-space:nowrap}
  .sr-chip.major b:after{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:#f07a68;
    margin-left:6px;vertical-align:2px}
  .sr-chip[aria-current]{background:var(--amber);color:#3a2604}.sr-chip[aria-current] b{color:#1b1205}
  .sr-all{flex:none;margin-right:12px;padding:9px 11px;border-radius:10px;border:1px solid rgba(255,255,255,.25);color:#fff;
    font-size:.78rem;font-weight:600;text-decoration:none;white-space:nowrap}
  /* with JavaScript the full list is a bottom sheet, opened from "All days" */
  .sr-js .sr-dlist{display:none}
  .sr-js .sr-sheet-open .sr-dlist{display:block;position:fixed;top:auto;left:0;right:0;bottom:0;z-index:1600;max-height:80vh;
    padding-bottom:env(safe-area-inset-bottom);
    border-radius:18px 18px 0 0;border:0;box-shadow:0 -10px 40px rgba(7,17,31,.25)}
  .sr-js .sr-sheet-open .sr-dscroll{max-height:calc(80vh - 52px)}
  .sr-dlist h2{display:flex;align-items:center;gap:6px}.sr-dlist h2 .sr-fclose{margin-left:auto}
}
@media (max-width:640px){
  .sr-intro .lede{font-size:1rem}
  .sr-wrap .sr-record{margin-top:18px;padding:10px 10px 10px}.sr-rk{margin:0 4px 8px}
  .sr-rk span{display:none}
  .sr-wrap .sr-record .sr-tiles,.sr-wrap .sr-pb .sr-tiles{grid-template-columns:repeat(4,minmax(0,1fr))}
  .sr-wrap .sr-record .sr-tiles div,.sr-wrap .sr-pb .sr-tiles div{padding:9px 8px;border-bottom:0;border-right:1px solid var(--rule)}
  .sr-wrap .sr-record .sr-tiles div:last-child,.sr-wrap .sr-pb .sr-tiles div:last-child{border-right:0}
  .sr-wrap .sr-record .sr-tiles dt,.sr-wrap .sr-pb .sr-tiles dt{font-size:.54rem;letter-spacing:.02em;min-height:2.6em}
  .sr-wrap .sr-record .sr-tiles dd b,.sr-wrap .sr-pb .sr-tiles dd b{font-size:1.02rem;white-space:nowrap}
  .sr-wrap .sr-record .sr-tiles dd span,.sr-wrap .sr-pb .sr-tiles dd span{display:none}
  .sr-pb .sr-tiles{margin-bottom:12px}
  .sr-pt{margin:14px 0 8px}
}
.sr-st{color:var(--faint);font-size:.82rem;margin:0 8px 0 6px}
.sr-none{color:#c3ccd7}
.sr-empty{padding:28px;text-align:center;background:#fff;border:1px solid var(--rule);border-radius:14px;color:var(--muted)}
.sr-pager{display:flex;justify-content:space-between;align-items:center;margin:14px 2px 0;font-size:.9rem;color:var(--muted)}
.sr-pager a{font-weight:550;text-decoration:none}
/* phones: each row becomes its own card, with space between cards: date and tag, the city, then the figures */
@media (max-width:640px){
  .sr-tw{background:none;border:0;border-radius:0;overflow:visible}
  .sr-table thead{display:none}
  .sr-table{display:block}
  .sr-table tbody{display:grid;gap:12px}
  .sr-table tbody tr{display:grid;grid-template-columns:repeat(3,1fr);background:#fff;border:1px solid var(--rule);
    border-radius:14px;box-shadow:0 1px 2px rgba(7,17,31,.04),0 4px 14px rgba(7,17,31,.05);overflow:hidden}
  .sr-table td{display:block;padding:0;border:0}
  .sr-table td.sr-cd{grid-column:1/-1;grid-row:1;padding:14px 16px 0;font:500 .68rem/1.4 var(--mono);letter-spacing:.05em;
    text-transform:uppercase;color:var(--faint)}
  .sr-table td.sr-cc{grid-column:1/-1;grid-row:2;padding:2px 16px 12px;font-size:1.12rem;letter-spacing:-.015em}
  .sr-cc .sr-st{margin-left:5px;font-size:.85rem}
  .sr-cc .sr-tag{position:absolute;top:12px;right:14px;margin:0;font-size:.58rem;padding:3px 6px}
  /* the figures: smaller than the header, inside the same card, under a short inset rule */
  .sr-table td.sr-cn{grid-row:3;text-align:left;padding:10px 0 14px 16px;position:relative}
  .sr-table td.sr-cn:nth-of-type(3):after{content:"";position:absolute;top:0;left:16px;width:calc(300% - 32px);height:1px;
    background:var(--rule)}
  .sr-table td.sr-cn:last-child{padding-right:16px}
  .sr-table td.sr-cn b{font-size:.9rem;font-weight:600}
  .sr-table td.sr-cn small{font-size:.7rem}
  .sr-table td.sr-cn:before{content:attr(data-label);display:block;font:500 .56rem/1.3 var(--mono);letter-spacing:.05em;
    text-transform:uppercase;color:var(--faint);margin-bottom:3px}
  .sr-table tbody tr:hover{background:#fff}.sr-table tbody tr:active{background:#f7f9fb}
}
.sr-tag{display:inline-block;flex:none;font:600 .66rem/1 var(--mono);letter-spacing:.05em;text-transform:uppercase;
  border-radius:999px;padding:5px 8px;white-space:nowrap;background:#fbeae7;color:var(--red);border:1px solid #efc4bc}
.sr-chips{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px}
.sr-chips a{display:inline-flex;gap:6px;align-items:center;padding:7px 12px;background:#fff;border:1px solid var(--rule);
  border-radius:999px;font-size:.88rem;text-decoration:none;color:var(--ink)}
.sr-chips a:hover{border-color:var(--navy-700)}
.sr-chips span{color:var(--faint);font-size:.8rem}
.sr-status{padding:9px 12px;border-radius:10px;margin:0 0 14px;font-size:.84rem}
.sr-status summary{display:flex;gap:10px;align-items:center;cursor:pointer;list-style:none;color:var(--amber-ink)}
.sr-status summary::-webkit-details-marker{display:none}
.sr-status summary:after{content:"i";flex:none;margin-left:auto;display:grid;place-items:center;width:18px;height:18px;
  border:1.4px solid currentColor;border-radius:50%;font:700 .68rem/1 Georgia,serif;opacity:.75}
.sr-status p{margin:8px 0 0;color:var(--body);line-height:1.5}
.sr-status.pre{background:var(--amber-50);border:1px solid #f0cf9c}
.sr-tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin:0 0 8px;background:#fff;border:1px solid var(--rule);
  border-radius:14px;overflow:hidden}
.sr-tiles div{padding:14px 16px;border-right:1px solid var(--rule)}
.sr-tiles div:last-child{border-right:0}
.sr-tiles dt{font:500 .66rem/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
.sr-tiles dd{margin:4px 0 0;color:var(--muted);font-size:.82rem;line-height:1.35}
.sr-tiles dd b{display:block;color:var(--ink);font-size:1.35rem;font-weight:650;letter-spacing:-.03em}
.sr-tiles dd span{display:block}
@media (max-width:700px){.sr-tiles{grid-template-columns:1fr 1fr}.sr-tiles div:nth-child(2){border-right:0}
  .sr-tiles div:nth-child(-n+2){border-bottom:1px solid var(--rule)}}
.sr-map{margin:0 0 16px;background:#fff;border:1px solid var(--rule);border-radius:14px;overflow:hidden}
#storm-map{height:400px;background:#e8eef5}
#storm-map .leaflet-tile-pane{filter:grayscale(1) contrast(.92) brightness(1.06)}
#storm-map .leaflet-tooltip{font:500 .76rem/1.35 var(--sans);color:var(--ink);border-radius:6px;padding:4px 7px;
  border:1px solid var(--rule);box-shadow:0 2px 8px rgba(0,0,0,.12)}
@media (max-width:700px){#storm-map{height:240px}}
.sr-mleg{display:flex;flex-wrap:wrap;gap:6px 16px;padding:9px 16px;font-size:.78rem;color:var(--muted);
  border-top:1px solid var(--rule)}
.sr-mleg span{display:inline-flex;align-items:center;gap:6px}
.lg-ring{width:14px;height:14px;border-radius:50%;border:1.4px dashed #4b5868}
.sr-panel .sr-list,.sr-group .sr-list{background:#fff;border:1px solid var(--rule);border-radius:12px}
.sr-group{margin:0 0 18px;scroll-margin-top:80px}
.sr-gh{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap;margin:0 0 8px}
.sr-gh h3{font-size:1.02rem}
.sr-list{list-style:none;margin:0;padding:0 18px}
.sr-list li{display:grid;grid-template-columns:5.4rem 1fr;gap:12px;padding:12px 0;border-bottom:1px solid var(--rule)}
.sr-list li:last-child{border-bottom:0}
.sr-t{font:500 .82rem/1.55 var(--mono);color:var(--muted);white-space:nowrap}
.sr-list b{color:var(--ink);font-weight:600;display:block;padding-left:16px;position:relative}
.sr-list b:before{content:"";position:absolute;left:0;top:.45em;width:8px;height:8px}
.k-hail b:before{background:var(--sky);transform:rotate(45deg)}
.k-wind b:before{background:#6b4fa0;border-radius:50%}
.k-tornado b:before{background:#d9442e}
.sr-pl{display:block;font-size:.9rem;color:var(--ink);padding-left:16px}
.sr-ml{display:block;font-size:.8rem;color:var(--faint);padding-left:16px}
.sr-remark{margin:6px 0 0 16px;font-size:.86rem;color:var(--body);line-height:1.55}
@media (max-width:520px){.sr-list li{grid-template-columns:1fr;gap:2px}.sr-list{padding:0 14px}}
.sr-more{margin:8px 0 0}
.sr-more summary{display:inline-flex;align-items:center;gap:6px;cursor:pointer;list-style:none;font-weight:550;
  font-size:.9rem;color:var(--navy-700);padding:6px 2px}
.sr-more summary::-webkit-details-marker{display:none}
.sr-more summary:before{content:"+";font-weight:400;font-size:1.1rem;line-height:1}
.sr-more[open] summary:before{content:"–"}
.sr-more[open] summary{margin-bottom:8px}
.sr-also{margin:12px 0 0;font-size:.9rem}.sr-also a{font-weight:550;text-decoration:none}
.sr-quote p{margin:0 0 10px}.sr-quote p:last-child{margin:0}.sr-quote .sr-more{margin:6px 0 0}
.sr-quote{margin:0 0 12px;padding:14px 18px;background:#fff;border-left:3px solid var(--navy-700);border-radius:0 10px 10px 0;
  color:var(--body);font-size:.93rem;line-height:1.65}
.sr-src{margin-top:32px}
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


# Umami (self-hosted at stats.huntingapps.io, cookieless). The edge Caddy serves it on our own origin at /u/script.js
# and /u/api/send. Set once at start-up by configure_analytics(); empty means no tracker (development, tests).
# analytics.js loads first: it holds the scrub that runs on every payload, and the click events.
ANALYTICS = ""


def configure_analytics(website_id: str, base_url: str) -> None:
    global ANALYTICS
    host = base_url.split("//", 1)[-1].split("/", 1)[0].split(":", 1)[0]
    ANALYTICS = "" if not re.fullmatch(r"[0-9a-f-]{36}", website_id or "") else (
        '<script defer src="/static/analytics.js"></script>'
        f'<script defer src="/u/script.js" data-website-id="{website_id}" data-domains="{escape(host, quote=True)}" '
        'data-exclude-hash="true" data-before-send="weScrub"></script>')


def layout(title: str, body: str, refresh: int | None = None, description: str = "", map_assets: bool = False,
           url: str = "", index: bool = False, jsonld: list | None = None) -> str:
    """url: the page's canonical absolute URL (public pages only). index=False marks the page noindex, which is the
    default so personal pages (orders, status) never reach a search index. Only public pages (with a url) carry the
    analytics tracker: order and status pages hold the order token in their address."""
    meta = f'<meta http-equiv="refresh" content="{refresh}">' if refresh else ""
    if url:
        origin = url[:url.index("/", url.index("//") + 2)] if url.count("/") > 2 else url
        meta += (f'<link rel="canonical" href="{escape(url, quote=True)}"><meta property="og:url" '
                 f'content="{escape(url, quote=True)}"><meta property="og:image" content="{origin}/static/sample-p1.webp">')
    meta += '<meta name="robots" content="index,follow">' if index else '<meta name="robots" content="noindex">'
    for block in jsonld or ():
        meta += ('<script type="application/ld+json">' + json.dumps(block, separators=(",", ":")).replace("</", "<\\/")
                 + "</script>")
    desc = escape(description or "Historical weather report for one US address and date of loss: measured wind and "
                  "rain from named stations, NWS warnings, storm reports, hail and lightning, each with its distance "
                  f"from the property. {PRICE} PDF.", quote=True)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">{meta}
<title>{escape(title)}</title><meta name="description" content="{desc}">
<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{desc}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#0b1a2e">
<link rel="icon" href="{FAVICON}"><link rel="apple-touch-icon" href="/static/apple-touch-icon.png">{FONTS}
{MAP_ASSETS if map_assets else ""}{ANALYTICS if url else ""}<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><a class="brand" href="/">{LOGO}<span>{BRAND}</span></a>
<nav>{NAV_LINKS.replace("<a ", '<a class="hide-sm" ')}<a class="btn btn-amber" href="/order">Order · {PRICE}</a>
{MOBILE_MENU}</nav></div></header>
<main>{body}</main>{FOOTER}</body></html>"""


# The site's pages, in the header and the phone menu alike. Only pages: the landing page's own sections are reached
# by scrolling it, not from the navigation.
NAV_LINKS = ('<a href="/storm-reports">Storm Reports</a><a href="/guides">Guides</a>'
             '<a href="/methodology">How it\'s built</a><a href="/static/sample-report.pdf">Sample report</a>')
# Phones: the header links don't fit, so they live in a menu. <details> opens and closes without JavaScript.
MOBILE_MENU = """<details class="mnav"><summary aria-label="Menu"><span></span><span></span><span></span></summary>
<div class="mnav-panel">""" + NAV_LINKS + """</div></details>
<script>document.addEventListener("click",function(e){var m=document.querySelector(".mnav[open]");
if(m&&(!m.contains(e.target)||e.target.closest(".mnav-panel a")))m.removeAttribute("open")});
document.addEventListener("keydown",function(e){var m=document.querySelector(".mnav[open]");
if(m&&e.key==="Escape"){m.removeAttribute("open");m.querySelector("summary").focus()}});</script>"""

FOOTER = f"""<footer><div class="wrap"><div><a class="brand" href="/" style="margin-bottom:14px">{LOGO}<span>{BRAND}</span></a>
<p>Not affiliated with NOAA, the National Weather Service or any government agency. Reports compile public records;
they are not certified records or expert opinions.</p></div>
<div><p class="links"><a href="/#sample">Sample report</a><a href="/methodology">How it's built</a>
<a href="/certified-weather-records">Certified records</a><a href="/storm-reports">Storm Reports</a>
<a href="/guides">Guides</a><a href="/#faq">FAQ</a>
<a href="/order">Order</a></p>
<p class="links"><a href="/terms">Terms</a><a href="/privacy">Privacy</a><a href="/refunds">Refunds</a><a href="/imprint">Imprint</a></p>
<p>Support: <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></p>
<p>{DOMAIN} · Payments processed by Creem, our merchant of record</p></div></div></footer>"""


def order_form(v: dict, error: str = "", ask_coords: bool = False, title: str = "") -> str:
    g = lambda k: escape(str(v.get(k) or ""), quote=True)  # noqa: E731
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    show_coords = ask_coords or bool(v.get("lat"))
    err = f'<p class="err" role="alert">{escape(error)}</p>' if error else ""
    head = f"<h3>{escape(title)}</h3>" if title else ""
    return f"""<div class="form-card" id="order">{head}{err}
<form method="post" action="/order" id="order-form" novalidate>
<label for="address" style="margin-top:0">Property address</label>
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
<p class="fine">Any US address, dates of loss from {MIN_DATE.year} to yesterday. Next you'll see the exact location
before paying {PRICE}.</p>
</form></div>"""


def landing() -> str:
    s = SAMPLE
    facts = "".join(f'<div><dt>{escape(f["label"])}</dt><dd><b>{escape(f["value"])}</b>{escape(f["detail"])}</dd></div>'
                    for f in SAMPLE_PAGE1["facts"])
    hero = f"""<section class="hero"><div class="wrap hero-main">
<div><p class="eyebrow">Weather reports · any US address</p>
<h1>What the weather did at the loss site.</h1>
<p class="lede">Measured gusts, warnings, hail and tornado reports for one address and date of loss, each with its
distance from the property.</p>
<div class="cta-row"><a class="btn btn-amber" href="/order">Get a report — {PRICE}</a>
<a class="btn btn-ghost-dark" href="#sample">View a sample report</a></div>
<ul class="assure"><li>Any US address</li><li>Delivered in about a minute</li><li>No subscription</li></ul></div>
<div class="rp">
<div class="rp-head">{mark_svg(24)}<div><div class="k">Sample report · page 1</div>
<b>{escape(_pretty(SAMPLE_PAGE1["address"]))}</b><span>Date of loss: {SAMPLE_PAGE1["date"]}</span></div></div>
<div id="hero-map" data-src="/static/site-map.json" role="img" aria-label="Map of weather records around the property"></div>
<ul class="mc-legend"><li><i class="lg lg-site"></i>Property</li><li><i class="lg lg-station"></i>Station</li>
<li><i class="lg lg-warn"></i>Warning area</li><li><i class="lg lg-path"></i>Tornado path</li>
<li><i class="lg lg-hail"></i>Radar hail</li><li><i class="lg lg-report"></i>Hail report</li></ul>
<dl class="facts">{facts}</dl>
<div class="rp-foot"><span>Real records, real report</span><a href="{s['pdf']}" target="_blank" rel="noopener">Open the
full sample →</a></div>
</div></div>
<div class="hero-strip"><div class="wrap"><span>Built on public records from</span><b>NOAA</b><b>National Weather
Service</b><b>NEXRAD radar</b><b>US Census Bureau</b></div></div>
</section>
"""

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
    # Mobile: one card per solution, features listed inside it (the table is hidden at <=700px).
    def card(idx, title, us=False):
        items = "".join(f"<li><span class='k'>{r[0]}</span><span class='v'>{cell(r[idx])}</span></li>" for r in rows)
        return f"<article class='cmp-card{' us' if us else ''}'><h3>{title}</h3><ul>{items}</ul></article>"

    cards = (card(1, "Free weather sites") + card(2, BRAND, us=True) + card(3, "Forensic meteorologist"))
    compare = f"""<section class="alt" id="compare"><div class="wrap">
<div class="section-head"><p class="eyebrow">Compare</p><h2>Between a free weather site and an expert.</h2>
<p class="lede">Detailed enough for a claim file, priced for every claim. If you later need an expert, the report
gives them every source to start from.</p></div>
<div><table class="compare"><thead><tr><th></th><th>Free weather sites</th><th class="us">{BRAND}</th>
<th>Forensic meteorologist</th></tr></thead><tbody>{body}</tbody></table>
<div class="cmp-cards">{cards}</div></div>
</div></section>"""

    pages = [("1", "Map & key facts"), ("3", "Station measurements"), ("5", "Warnings & storm reports"),
             ("7", "Storm Events"), ("8", "Hail & lightning")]
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
         "where each one came from. It is not a certified government record or an expert opinion. "
         '<a href="/certified-weather-records">When you need a certified record</a>.'),
        ("How close is the weather data to the property?",
         "That depends on where the nearest stations are. The report names every station and gives its distance and "
         "direction, so you can judge how representative it is."),
        ("Which dates can I order?",
         f"Any completed day from {MIN_DATE.year} to yesterday. NOAA publishes its Storm Events database a few months "
         "after each month ends; for recent dates the report says so, and includes everything else."),
        ("What if the address isn't found?",
         "Place a pin on the map instead. The report notes that the location was set by pin."),
        ("What if the report can't be built?",
         'We\'re notified automatically and will deliver the report or refund you. See the <a href="/refunds">refund '
         "policy</a>."),
        ("Who processes the payment?",
         "Creem (creem.io), our reseller and merchant of record. It takes the payment, calculates any sales tax and "
         f'emails your receipt. Questions about an order: <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>.'),
    ]
    faq = "".join(f"<details><summary>{escape(q)}</summary><p>{a}</p></details>" for q, a in faq_items)  # trusted HTML
    faq_html = f"""<section id="faq"><div class="wrap">
<div class="section-head center"><p class="eyebrow">FAQ</p><h2>Common questions.</h2></div>
<div class="faq">{faq}</div></div></section>"""

    cta = f"""<section class="cta"><div class="wrap"><h2>Get the weather record for your date of loss.</h2>
<p>{PRICE} per report. Any US address.</p><a class="btn btn-amber" href="/order">Start your report</a></div></section>"""
    return hero + questions + compare + sample + how + faq_html + cta


def order_page(form: str) -> str:
    return f"""<div class="order-wrap"><ol class="stepper"><li class="on">1 · Location and date</li>
<li>2 · Confirm and pay</li><li>3 · Download</li></ol>
<h1>Where and when was the loss?</h1>
<p class="lede">Enter the property address or place a pin on the map, then the date of loss.</p>
{form}
<ul class="includes"><li>Station measurements</li><li>Warning-area check</li><li>Storm reports and hail</li>
<li>PDF in about a minute</li></ul></div>"""


def inner(body: str) -> str:
    return f'<div class="inner">{body}</div>'


def status_block(kind: str, title: str, text: str) -> str:
    dot = {"wait": "", "ok": " ok", "bad": " bad"}[kind]
    return f'<div class="status"><span class="dot{dot}"></span><div><p><b>{title}</b></p>{text}</div></div>'


def article(page, related: list) -> str:
    """A content page: breadcrumbs, heading, body, then links to the other guides."""
    crumbs = '<a href="/">Home</a> / '
    if page.guide:
        crumbs += '<a href="/guides">Guides</a> / '
    more = ""
    if related:
        items = "".join(f'<li><a href="{r.path}"><b>{escape(r.h1)}</b><span>{escape(r.description)}</span></a></li>'
                        for r in related)
        more = f'<div class="more"><h2>Related</h2><ul class="glist">{items}</ul></div>'
    return f"""<article class="article"><nav class="crumbs" aria-label="Breadcrumb">{crumbs}{escape(page.h1)}</nav>
<p class="eyebrow">{escape(page.eyebrow)}</p><h1>{escape(page.h1)}</h1>
<p class="updated">Updated {page.updated:%B} {page.updated.day}, {page.updated.year}</p>{page.body}{more}</article>"""


def guides_index(pages: list) -> str:
    items = "".join(f'<li><a href="{p.path}"><b>{escape(p.h1)}</b><span>{escape(p.description)}</span></a></li>'
                    for p in pages)
    return f"""<div class="article"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Guides</nav>
<p class="eyebrow">Guides</p><h1>Weather records for insurance claims</h1>
<p class="lede">Plain-language guides to finding and reading public weather records for a property and a date of
loss.</p><ul class="glist">{items}</ul></div>"""
