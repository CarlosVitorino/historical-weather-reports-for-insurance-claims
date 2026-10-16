# Weather Evidence: one process serves the site, takes creem's webhook and builds reports in a thread pool.
# SQLite, snapshots, PDFs and backups live in /data (a volume). See deploy/README.md.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DATA_DIR=/data
WORKDIR /app

# Dependencies first, read from pyproject.toml, so a code change doesn't reinstall them.
COPY pyproject.toml ./
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))" \
        > /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Code root-owned and read-only to the app user; only /data is written.
COPY wxreport ./wxreport
RUN useradd --system --uid 10001 --home-dir /data wxreport \
    && mkdir -p /data && chown wxreport:wxreport /data
USER wxreport
VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4).status == 200 else 1)"
# One worker on purpose: rate limits, the report thread pool and SQLite all assume a single process.
# The edge Caddy overwrites X-Forwarded-For, so the client address uvicorn reports is the real visitor.
CMD ["uvicorn", "wxreport.web:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", \
     "--forwarded-allow-ips", "*", "--workers", "1"]
