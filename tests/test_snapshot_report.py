import json
from datetime import datetime, timezone

import pytest

from wxreport.geocode import AddressNotFound
from wxreport.snapshot import Snapshot, SourceUnavailable
from wxreport.report import InvalidRequest, build_pdf, gather

ADDR = "401 N College Ave, Bloomington, IN"
# Synthetic geocoder response in the Census JSON shape, for exercising the pipeline offline.
CENSUS = {"result": {"addressMatches": [{
    "matchedAddress": "401 N COLLEGE AVE, BLOOMINGTON, IN, 47404",
    "coordinates": {"x": -86.5348, "y": 39.1700},
    "geographies": {"Counties": [{"NAME": "Monroe County", "STATE": "18", "GEOID": "18105"}]}}]}}


def seed(root, address=ADDR, day="2026-02-19", body=CENSUS):
    snap = Snapshot.open({"address": address, "date": day, "lat": None, "lon": None}, root=root)
    snap.put("census_address", json.dumps(body).encode(), url="https://example.invalid/census",
             retrieved_at="2026-10-14T12:00:00+00:00")
    return snap


def test_same_snapshot_gives_identical_pdf_and_id(tmp_path):
    seed(tmp_path)
    a = gather(ADDR, "2026-02-19", root=tmp_path, offline=True)
    pdf_a = build_pdf(a)
    b = gather(ADDR, "2026-02-19", root=tmp_path, offline=True)
    assert a.report_id == b.report_id
    assert pdf_a == build_pdf(b)
    assert a.loc.county == "Monroe County" and a.loc.state == "IN"
    assert a.loc.tz == "America/Indiana/Indianapolis"


def test_different_data_gives_different_id(tmp_path):
    seed(tmp_path / "a")
    other = json.loads(json.dumps(CENSUS))
    other["result"]["addressMatches"][0]["coordinates"]["y"] = 39.18
    seed(tmp_path / "b", body=other)
    a = gather(ADDR, "2026-02-19", root=tmp_path / "a", offline=True)
    b = gather(ADDR, "2026-02-19", root=tmp_path / "b", offline=True)
    assert a.report_id != b.report_id


def test_unmatched_address(tmp_path):
    seed(tmp_path, body={"result": {"addressMatches": []}})
    with pytest.raises(AddressNotFound):
        gather(ADDR, "2026-02-19", root=tmp_path, offline=True)


def test_offline_without_snapshot(tmp_path):
    with pytest.raises(SourceUnavailable):
        gather(ADDR, "2026-02-19", root=tmp_path, offline=True)


def test_future_or_unfinished_date_rejected(tmp_path):
    seed(tmp_path, day="2026-10-14")
    snap_now = datetime(2026, 10, 14, 20, 0, tzinfo=timezone.utc)  # 4 PM EDT, day not over
    with pytest.raises(InvalidRequest):
        gather(ADDR, "2026-10-14", root=tmp_path, offline=True, now=snap_now)


def test_bad_date_format(tmp_path):
    with pytest.raises(InvalidRequest):
        gather(ADDR, "02/19/2026", root=tmp_path)


def test_recorded_failure_replays_when_frozen_and_retries_when_open(tmp_path, monkeypatch):
    import requests
    snap = Snapshot.open({"address": "x", "date": "2026-01-01"}, root=tmp_path)
    calls = []

    def boom(*a, **k):
        calls.append(1)
        raise requests.ConnectionError("down")
    monkeypatch.setattr(requests, "get", boom)
    with pytest.raises(SourceUnavailable):
        snap.fetch("s", "https://example.invalid")
    with pytest.raises(SourceUnavailable):
        snap.fetch("s", "https://example.invalid")
    assert len(calls) == 2  # open snapshot retries
    snap.freeze()
    with pytest.raises(SourceUnavailable):
        snap.fetch("s", "https://example.invalid")
    assert len(calls) == 2  # frozen snapshot replays the failure
