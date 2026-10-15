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
emailed through Resend. `/admin` (HTTP Basic auth, password `ADMIN_PASSWORD`) shows visitors, the funnel,
revenue, where visitors came from, why order forms were rejected, and every order, with retry and re-send buttons.

Configuration lives in environment variables; see `.env.example`. For a local dry run without creem, set
`ENVIRONMENT=development` and orders are marked paid at checkout, even if creem keys are set.

On your server:

1. Copy the repo to `/opt/wxreport`, then run `make setup`.
2. Create `.env` from `.env.example`.
3. Install `deploy/wxreport.service`.
4. Put HTTPS in front of it with a reverse proxy.
5. In the creem dashboard, set the webhook URL to `https://<your domain>/webhooks/creem`.

Everything is stored in `DATA_DIR`: `app.db` (orders and events) and `orders/<id>/` (snapshots and PDFs). Back it up.
