"""Snapshot store: every raw source response is kept byte-for-byte with its URL, retrieval time and SHA-256.

A report is a pure function of (request, snapshot), so the same snapshot always renders the same PDF and
any report can be re-verified later. Failed retrievals are recorded too, so "unavailable" is reproducible.
"""
import gzip
import hashlib
import json
import re
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import requests

USER_AGENT = "wxreport/0.1 (historical weather report generator)"
DEFAULT_ROOT = Path("data/snapshots")


class SourceUnavailable(Exception):
    """A source could not be retrieved (now, or at the time the snapshot was taken)."""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


RETRY_DELAYS = (2, 6)   # seconds between attempts on timeouts, connection errors and 5xx/429


def _get(url: str, params: dict | None, timeout: float) -> requests.Response:
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT})
            if r.status_code < 500 and r.status_code != 429:
                return r
            if attempt == len(RETRY_DELAYS):
                return r
        except (requests.ConnectionError, requests.Timeout):
            if attempt == len(RETRY_DELAYS):
                raise
        time.sleep(RETRY_DELAYS[attempt])
    raise AssertionError("unreachable")


def request_key(address: str, day: str, lat: float | None = None, lon: float | None = None) -> str:
    norm = re.sub(r"\s+", " ", address.strip().upper())
    coords = "" if lat is None else f"|{lat:.5f},{lon:.5f}"
    return hashlib.sha256(f"{norm}|{day}{coords}".encode()).hexdigest()[:16]


@dataclass
class Snapshot:
    path: Path
    request: dict
    offline: bool = False
    sources: dict = field(default_factory=dict)
    frozen_at: str | None = None

    @classmethod
    def open(cls, request: dict, root: Path = DEFAULT_ROOT, offline: bool = False,
             refresh: bool = False) -> "Snapshot":
        """Reuse the stored snapshot for this request (deterministic replay), or start over with refresh."""
        key = request_key(request["address"], request["date"], request.get("lat"), request.get("lon"))
        path = root / key
        manifest = path / "manifest.json"
        if refresh and not offline and path.exists():
            shutil.rmtree(path)
        if manifest.exists():
            m = json.loads(manifest.read_text())
            return cls(path, m["request"], offline, m["sources"], m.get("frozen_at"))
        if offline:
            raise SourceUnavailable(f"No stored snapshot for this request ({path})")
        path.mkdir(parents=True, exist_ok=True)
        return cls(path, request, offline)

    # -- retrieval ---------------------------------------------------------------------------
    def fetch(self, name: str, url: str, params: dict | None = None, timeout: float = 120,
              missing_ok: bool = False) -> bytes | None:
        """Return the stored bytes for `name`, retrieving them first if this snapshot doesn't have them."""
        entry = self.sources.get(name)
        if entry is not None and entry["status"] == "ok":
            return self._read(entry)
        if entry is not None and entry["status"] == "absent" and missing_ok:
            return None
        if self.offline or self.frozen_at:
            # A frozen snapshot replays its recorded failures; an open one retries them.
            raise SourceUnavailable(entry.get("error", "unavailable") if entry else
                                    f"{name} is not part of this snapshot")
        retrieved_at = _now()
        try:
            r = _get(url, params, timeout)
            retrieved_at = _now()
            final_url = r.url
            if missing_ok and r.status_code == 404:
                # A definite "no such file" (e.g. a station with no data that year) is recorded, not retried.
                self.sources[name] = {"url": final_url, "params": params, "retrieved_at": retrieved_at,
                                      "status": "absent", "error": "HTTP 404 Not Found"}
                self._write()
                return None
            r.raise_for_status()
            body = r.content
        except requests.RequestException as e:
            self.sources[name] = {"url": url, "params": params, "retrieved_at": retrieved_at,
                                  "status": "error", "error": f"{type(e).__name__}: {e}"[:500]}
            self._write()
            raise SourceUnavailable(self.sources[name]["error"]) from e
        return self.put(name, body, url=final_url, params=params, retrieved_at=retrieved_at)

    def put(self, name: str, body: bytes, url: str, params: dict | None = None,
            retrieved_at: str | None = None) -> bytes:
        fname = re.sub(r"[^A-Za-z0-9_.-]", "_", name) + ".raw.gz"
        (self.path / fname).write_bytes(gzip.compress(body, mtime=0))
        self.sources[name] = {"url": url, "params": params, "retrieved_at": retrieved_at or _now(),
                              "status": "ok", "file": fname, "bytes": len(body),
                              "sha256": hashlib.sha256(body).hexdigest()}
        self._write()
        return body

    def _read(self, entry: dict) -> bytes:
        raw = (self.path / entry["file"]).read_bytes()
        return gzip.decompress(raw) if entry["file"].endswith(".gz") else raw

    def fetch_json(self, name: str, url: str, params: dict | None = None, **kw):
        return json.loads(self.fetch(name, url, params, **kw))

    # -- identity ----------------------------------------------------------------------------
    def freeze(self) -> None:
        """Close the snapshot. The printed 'retrieved' time is the latest retrieval, not the wall clock."""
        if not self.frozen_at:
            times = [s["retrieved_at"] for s in self.sources.values()]
            self.frozen_at = max(times) if times else _now()
            self._write()

    def digest(self) -> str:
        """SHA-256 over the request, freeze time and every source's retrieval time and content hash (or error).

        Retrieval times are printed in the report, so they are part of its identity: same ID ⇔ same PDF."""
        h = hashlib.sha256(json.dumps(self.request, sort_keys=True).encode())
        h.update(f"\nfrozen|{self.frozen_at}".encode())
        for name in sorted(self.sources):
            s = self.sources[name]
            h.update(f"\n{name}|{s['retrieved_at']}|{s['status']}|{s.get('sha256') or s.get('error')}".encode())
        return h.hexdigest()

    def _write(self) -> None:
        m = {"request": self.request, "frozen_at": self.frozen_at, "sources": self.sources}
        (self.path / "manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True))


def report_id(day: str, snap: Snapshot, render_version: str = "") -> str:
    """Canonical report ID: loss date + 12 hex of SHA-256(snapshot digest, renderer version).
    Same data and same renderer → same ID → byte-identical PDF."""
    h = hashlib.sha256(f"{snap.digest()}|render:{render_version}".encode()).hexdigest()
    return f"LWR-{day}-{h[:12].upper()}"
