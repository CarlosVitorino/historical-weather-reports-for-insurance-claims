import requests

from wxreport import suggest


class R:
    def __init__(self, data):
        self._d = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._d


def feature(lon, lat, **p):
    return {"geometry": {"coordinates": [lon, lat]}, "properties": p}


def test_us_only_labels_and_exactness(monkeypatch):
    monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
    data = {"features": [
        feature(-86.5349, 39.1696, countrycode="US", housenumber="401", street="North College Avenue",
                city="Bloomington", state="Indiana", postcode="47404"),
        feature(-79.4, 43.7, countrycode="CA", housenumber="401", street="College St", city="Toronto", state="Ontario"),
        feature(-86.53, 39.17, countrycode="US", name="College Avenue", city="Bloomington", state="Indiana"),
    ]}
    monkeypatch.setattr(requests, "get", lambda *a, **k: R(data))
    suggest._cached.cache_clear()
    out, ok = suggest.suggest("401 college bloomington")
    assert ok
    assert [o["label"] for o in out] == ["401 North College Avenue, Bloomington, Indiana 47404",
                                         "College Avenue, Bloomington, Indiana"]
    assert out[0]["exact"] and not out[1]["exact"]
    assert out[0]["lat"] == 39.1696


def test_geoapify_when_key_set(monkeypatch):
    monkeypatch.setenv("GEOAPIFY_API_KEY", "k")
    seen = {}
    data = {"results": [
        {"address_line1": "5299 DTC Boulevard", "address_line2": "Greenwood Village, CO 80111, United States of America",
         "lat": 39.6202, "lon": -104.8932, "housenumber": "5299", "result_type": "building"},
        {"address_line1": "DTC Boulevard", "address_line2": "Greenwood Village, CO, United States of America",
         "lat": 39.62, "lon": -104.89, "result_type": "street"}]}

    def get(url, params=None, **k):
        seen.update(url=url, params=params)
        return R(data)
    monkeypatch.setattr(requests, "get", get)
    suggest._cached.cache_clear()
    out, _ = suggest.suggest("5299 dtc blvd")
    assert seen["url"] == suggest.GEOAPIFY and seen["params"]["filter"] == "countrycode:us"
    assert out[0] == {"label": "5299 DTC Boulevard, Greenwood Village, CO 80111", "lat": 39.6202, "lon": -104.8932,
                      "exact": True}
    assert out[1]["exact"] is False


def test_short_query_and_outage(monkeypatch):
    assert suggest.suggest("ab") == ([], True)

    def boom(*a, **k):
        raise requests.ConnectionError("down")
    monkeypatch.setattr(requests, "get", boom)
    suggest._cached.cache_clear()
    assert suggest.suggest("401 college ave") == ([], False)
