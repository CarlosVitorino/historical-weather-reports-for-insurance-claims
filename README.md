# Historical weather reports for insurance claims

Someone buys an address-specific historical weather report confirming conditions at a loss site — e.g. a $9.99 paid PDF — instead of getting it from free weather data or an enterprise forensic engagement.

- **Start here.** A deterministic PDF generator that takes one address + loss date and produces the $9.99 report for a single region, closing the four gaps the sample shows (station-pinned measurements, distance-and-bearing proximity, Storm Events database, hail/lightning feeds) — then sell a handful against the existing StormRecord report to see if claims adjusters pay.
- **Stop if.** Legally issues

This repository was handed off from BuildCase. Open it in Cursor, Claude Code, Replit, Bolt or any coding tool and ask it to start.

- `build-brief.md` — the full brief
- `AGENTS.md` — how to work on it
- `docs/build-plan.md` — the phases
- `docs/materials/` — files gathered along the way, each with a text reading beside it
## Running it

```sh
make setup                                   # create .venv and install
make report ADDRESS="401 N College Ave, Bloomington, IN" DATE=2026-02-19
make report ADDRESS="..." DATE=... LAT=39.1696 LON=-86.5386   # when the geocoder can't match the address
make test
make serve                                   # order page on http://localhost:8000 (+ /admin)
```

Reports are written to `reports/<report-id>.pdf`. Raw source responses are kept in `data/snapshots/` with
retrieval times and SHA-256 hashes. Re-running the same request replays the stored snapshot and gives a
byte-identical PDF. Use `.venv/bin/python -m wxreport.cli report ... --refresh` to re-retrieve everything.

## Selling it

`make serve` runs the order page. A buyer enters the address, loss date and email, confirms the geocoded location,
pays through creem.io, and is sent back to a status page that turns into a download link. The report is also
emailed through Resend from `report@weatherevidence.com`, with replies going to `support@weatherevidence.com`.
`/admin` (HTTP Basic auth, password `ADMIN_PASSWORD`) shows visitors, the funnel, revenue, where visitors came from,
why order forms were rejected, and every order, with retry and re-send buttons.

The operator is emailed (`ALERT_EMAIL`, default the support address) about every new sale, failed report, failed
report email, refund and dispute. creem's `refund.created` marks the order refunded; refunds themselves are issued
in the creem dashboard.

Configuration lives in environment variables; see `.env.example`. For a local dry run without creem, set
`ENVIRONMENT=development` and orders are marked paid at checkout, even if creem keys are set.

`.venv/bin/python -m wxreport.cli check` tests a filled-in `.env`: it fetches the creem product with the key (and
compares its price with `PRICE_CENTS`), and with `--email-to you@example.com` sends a test email through Resend.

### Testing a real creem payment locally

1. creem test mode: create a one-time $9.99 product, copy a `creem_test_…` API key and the product ID into `.env`,
   set `ENVIRONMENT=production` and `BASE_URL=http://localhost:8000`.
2. `npx @creem_io/cli listen --forward-to http://localhost:8000/webhooks/creem` and put the signing secret it prints
   in `CREEM_WEBHOOK_SECRET`. No public URL needed.
3. `make serve`, order a report, pay with card `4111 1111 1111 1111` (any future date, any CVC). The webhook
   arrives through the CLI, the report builds, and `/admin` shows the order as paid and ready.

### Limits and housekeeping

- Per-IP rate limits (`wxreport/ratelimit.py`): 10 order forms, 20 checkout clicks, 120 address suggestions,
  30 geocodes and 60 map-pin lookups per 10 minutes. Above that the visitor gets a 429.
- Geoapify (autocomplete) is used for at most `GEOAPIFY_DAILY_LIMIT` calls a UTC day (default 2,500 of the free
  3,000); after that suggestions come from Photon until midnight UTC.
- At start-up and then daily, the server deletes unpaid drafts older than `DRAFT_TTL_HOURS` (default 24) with
  their snapshots, and writes a consistent copy of the database to `DATA_DIR/backups/app-<date>.db.gz`
  (`BACKUP_KEEP`, default 14). Orders that reached checkout are never deleted: creem may still confirm them.

### Visit statistics (Umami)

Public pages load Umami (self-hosted at stats.huntingapps.io, cookieless) when `UMAMI_WEBSITE_ID` is set; empty in
development, so nothing is sent from localhost. The tracker is served from our own origin: the edge Caddy
(`huntingApps/deploy/edge/Caddyfile`) sends `/u/script.js` and `/u/api/send` on weatherevidence.com to Umami.
Order, status and admin pages carry no tracker (their addresses hold order tokens), and `static/analytics.js` strips
every query key but the filters, `day`, `loss_date` and `utm_*` before anything is sent. It also holds the events:
`order_cta`, `order_submit`, `sample_report`, `storm_day`, `storm_filter`. To leave your own visits out, open /admin
on each browser and device and press "Don't count this browser" (Umami's `umami.disabled` plus our `nostats` cookie).

### Storm Reports

Public pages at `/storm-reports`: an index with a city search and a feed of recent storms, state hubs and city pages
("Plano, TX hail storm history") (`wxreport/storms.py` for data and rules, `wxreport/storm_pages.py` for pages, plan in
`docs/storm-reports-plan.md`). Data covers the whole US; pages exist only where a storm earned one:

- A city of 50,000+ (`wxreport/data/us_cities.csv`, 817 cities, built by `scripts/make_cities.py` from Census files
  and Wikidata) gets a page on its first hail of 1 inch or more, or tornado, within its radius on or after
  `PAGES_SINCE` (2026-10-21). The page shows the city's history since 2021 and is indexed once it has 3+ storm days.
- A city's centre is its Wikidata coordinate (downtown, where people put it), not the Census internal point. Its
  radius is 8 mi for most cities, more for sprawling ones (land area → equivalent circle + 2 mi, at most 20 mi:
  Phoenix 15, Dallas 12). Changing the city list re-links stored reports on the next sync (`wxreport storms relink`).
- Hail of 2 inches or more, or a tornado, tags that storm day "Major storm".

Data lives in `DATA_DIR/storms.db` (about 180 MB for 2021 to today), rebuilt from the sources whenever needed, so it
is not backed up.

- The server keeps it current: on first start with an empty database it loads every reviewed NCEI Storm Events year
  (about a minute), then fetches NWS Local Storm Reports for the last 3 days every hour and checks NCEI for a new
  edition daily. `STORM_SYNC=0` turns this off.
- `wxreport storms backfill | refresh | status` does the same by hand; `status` lists the pages that exist.

## Deploying

It runs on the shared host with huntingapps.io and narrator.guru: one container on the `edge` Docker network,
behind the shared Caddy in `huntingApps/deploy/edge/` (which already has the `weatherevidence.com` block). Budget:
`cpus: 1`, `mem_limit: 768m`; the core came out of the narrator's worker (`huntingApps/docs/18-the-shared-host.md`).

1. Point `weatherevidence.com` and `www.weatherevidence.com` at the host. Let DNS settle first: Caddy requests a
   certificate as soon as it reloads, and failures count against Let's Encrypt's rate limits.
2. Clone the repo to `~/weatherevidence` (next to `~/narrator`), `cp .env.example deploy/.env`, fill it in with live creem keys and
   `ENVIRONMENT=production`.
3. `docker compose -f deploy/compose.yml up -d --build`, then
   `docker compose -f deploy/compose.yml exec web python -m wxreport.cli check --email-to you@example.com`.
4. Reload the edge Caddy: `docker compose -f ~/huntingApps/deploy/edge/compose.yml restart caddy`.
5. In the creem dashboard, set the webhook URL to `https://weatherevidence.com/webhooks/creem`.
6. Before creem's account review: set `LEGAL_OWNER` and `LEGAL_ADDRESS` (the legal pages and `/imprint` say Draft
   until you do), make sure `support@weatherevidence.com` receives mail, and enter the same address in creem →
   Settings → Business Details. The review checks /terms, /privacy, the visible price and that email.
7. Off-host backups: root's cron runs `deploy/backup-offsite.sh` nightly with `BACKUP_REMOTE` set (instructions in
   the script). Until that runs, the only copies are on the same disk.

Everything is stored in the `weatherevidence_data` volume (`/data` in the container): `app.db` (orders and events),
`orders/<id>/` (snapshots and PDFs, ~12 MB per paid order) and `backups/`.
