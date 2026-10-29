# International demand check — DE, ES, PT, FR, AU (2026-10-29)

Demand-only check (no data-sourcing questions) for the Weather Evidence concept outside the US.
Method: DataForSEO via OpenSEO, **one bulk `get_keyword_metrics` call per market** (location + language),
to stay economical. Volumes are Google Ads monthly searches; `—` = below the measurable floor.

US reference (for scale): `hail report by address` **140**, `hail history by address` **70**,
`hail verification report` **40**.

---

## Check 1 — general demand per market (claim + historical phrasings)

| Market | Keyword | Vol | KD | CPC |
|---|---|---|---|---|
| 🇩🇪 Germany | historische wetterdaten | **590** | 16 | 2.48 |
| 🇩🇪 Germany | wettergutachten | 20 | — | 5.13 |
| 🇩🇪 Germany | wettergutachten versicherung / hagelschaden / wetterrueckblick / wetterauskunft versicherung | 0 | — | — |
| 🇪🇸 Spain | datos meteorológicos históricos | 20 | 22 | — |
| 🇪🇸 Spain | certificado meteorológico | 10 | — | — |
| 🇪🇸 Spain | informe meteorológico | 10 | 92 | — |
| 🇵🇹 Portugal | relatório meteorológico (para seguro) / certificado / histórico | **0** | — | — |
| 🇫🇷 France | relevé météo | 140 | 47 | — |
| 🇫🇷 France | grêle assurance | 70 | 0 | — |
| 🇦🇺 Australia | historical weather data | **210** | 12 | 6.02 |
| 🇦🇺 Australia | hail map | 70 | 0 | — |

---

## Check 2 — the top 3 US keywords, in each market

The three strongest US keywords were `hail report by address`, `hail history by address`,
`hail verification report`. Their translated equivalents per market:

| Market | Keyword | Vol | KD | CPC |
|---|---|---|---|---|
| 🇩🇪 Germany | hagelgutachten | 10 | — | **11.19** |
| 🇩🇪 Germany | hagelbericht adresse / hagelhistorie adresse | 0 | — | — |
| 🇪🇸 Spain | informe de granizo / historial de granizo / informe verificación granizo | **0** | — | — |
| 🇵🇹 Portugal | relatório de granizo / histórico / verificação | **0** | — | — |
| 🇫🇷 France | relevé grêle / historique grêle / attestation grêle | **0** | — | — |
| 🇦🇺 Australia | hail report by address | 10 | — | — |
| 🇦🇺 Australia | hail history by address | 10 | — | — |
| 🇦🇺 Australia | hail verification report | 0 | — | — |

---

## Conclusion

**The "hail report by address" money term is a US phenomenon. It does not exist abroad.**

- In **DE, ES, PT, FR**, the translated "hail report by address" phrasings are all **zero**. Only
  Germany shows a faint insurance signal — `hagelgutachten` (10 vol, but CPC 11.19, the German
  legal/insurance term for a hail expert report).
- In **Australia**, the concept exists but is **7–14× smaller** than the US (10 vs 140).

Where international demand *does* exist, it is the **"historical weather data"** angle, not a claim
report:

1. **🇩🇪 Germany — the only market worth real consideration.** `historische wetterdaten` (590, KD 16)
   is genuinely winnable, plus a small-but-commercial `wettergutachten` signal.
2. **🇦🇺 Australia — second.** `historical weather data` (210, KD 12) is winnable; hail is a real
   Australian claim driver, but the specific report terms are tiny.
3. **🇫🇷 France — marginal.** `relevé météo` (140, KD 47) and `grêle assurance` (70, navigational).
4. **🇪🇸 Spain and 🇵🇹 Portugal — not worth it on search demand** (near zero).

**Two caveats:**

1. **Demand only.** The real gate for any expansion is data: the product is built on NOAA/NWS/NCEI/
   GHCN (US-only). Germany = DWD, France = Météo-France, Spain = AEMET, Portugal = IPMA, Australia =
   BoM — each a separate integration, and some (BoM especially) carry real access/licensing friction.
2. **The entry term abroad is "historical weather data", not a claim report.** Any future expansion
   lands on an informational "historical weather data" page that funnels to the report — the same
   top-of-funnel shape as the US plan.

**Bottom line:** expand to **Germany** first (if anywhere), then **Australia**. Skip Spain and
Portugal on organic-search demand.
