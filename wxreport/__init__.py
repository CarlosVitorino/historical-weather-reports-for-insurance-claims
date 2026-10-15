"""Address-specific historical weather reports built from free US government data."""

BRAND = "Weather Evidence"
PRODUCT = "Weather Evidence Report"        # title printed on every report
DOMAIN = "weatherevidence.com"
ID_PREFIX = "WE"                           # report IDs: WE-<loss date>-<12 hex>

# Bump whenever report content or layout changes: it is part of the report ID, so one ID is one exact PDF.
RENDER_VERSION = "4"
