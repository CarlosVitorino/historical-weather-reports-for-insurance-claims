# Weather Evidence brand files

| File | Use |
|---|---|
| `mark.svg`, `mark-512.png`, `mark-180.png` | The mark on its own: favicon, social avatars, creem checkout logo, app icons |
| `logo-on-dark.svg` / `.png` | Mark plus wordmark on navy or dark backgrounds (PNG includes the navy background) |
| `logo-on-light.svg` / `.png` | Mark plus wordmark on white or light backgrounds: email signature, Resend emails, documents |

The wordmark is set in Geist 650 and converted to outlines, so it looks the same without the font installed.

Colours: amber `#F2A93B`, navy `#0B1A2E`. The mark geometry lives in `wxreport/brand.py`.
Rebuild these files with `.venv/bin/python scripts/make_brand.py`.
