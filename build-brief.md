# Historical weather reports for insurance claims
## What this is

Someone buys an address-specific historical weather report confirming conditions at a loss site — e.g. a $9.99 paid PDF — instead of getting it from free weather data or an enterprise forensic engagement.

## What would make you stop

Legally issues

## The smallest thing worth building first

A deterministic PDF generator that takes one address + loss date and produces the $9.99 report for a single region, closing the four gaps the sample shows (station-pinned measurements, distance-and-bearing proximity, Storm Events database, hail/lightning feeds) — then sell a handful against the existing StormRecord report to see if claims adjusters pay.

## What this is not building

- Enterprise forensic meteorology engagements and expert-witness testimony
- International weather data — v1 is US government sources only
- Real-time or forecast data; the product is strictly historical reports
- Building or licensing proprietary data feeds beyond the three free public inputs
- Insurance-company integrations, APIs, or bulk claim-pipeline tooling
- A marketing site or pitch materials beyond the report itself

## Who buys this and why not free data

The buyer is someone settling an insurance claim who needs an address-specific record of conditions at a loss site. The price point is $9.99 — below a forensic engagement, above a random weather site — and the product's honesty framing (provenance, QC flags, retrieval and generation timestamps, canonical report IDs) is part of what they are paying for.

## What the report must contain

The StormRecord sample already does much of what the pitch implied was missing: 10 NWS Local Storm Reports with hail sizes, tornado path and winds, LSR IDs and reporters; geocoded coordinates and timezone/DST handling; retrieval and generation times; canonical report ID; full alert bulletins with VTEC event IDs. A competing report must match all of that and add what the sample lacks: station-pinned measurements, distance-and-bearing proximity from the loss address, the NCEI Storm Events database, and hail and lightning feeds. Those four are the differentiator.

## Data sources and the engineering problem

Every input is free, public US government data: GHCN hourly (GHCNh) for station observations — wind, gust, temperature, dew point, humidity, pressure, present weather, visibility, precipitation, snow — with ISD as legacy fallback. The work is not acquiring data; it is taming three awkward delivery formats: a legacy token API, a new hourly dataset, and per-year gzip CSVs, all wrapped in a deterministic PDF.

## What would kill this project

Legal issues. Nothing in the notes elaborates which — whether around republishing government data, presenting a report as authoritative for a claim, or something else — so the first thing to resolve before building is what, specifically, the legal exposure is and whether the honesty/provenance framing is sufficient mitigation.

## Evidence

_Nothing attached yet._
