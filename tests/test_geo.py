from wxreport.geo import bearing_deg, compass, distance_mi, proximity


def test_distance_known_pair():
    # Indianapolis (IND) to Bloomington (BMG) airports: ~45 mi.
    d = distance_mi(39.7173, -86.2944, 39.1460, -86.6168)
    assert 42 < d < 46


def test_bearing_cardinals():
    assert round(bearing_deg(39, -86, 40, -86)) == 0
    assert round(bearing_deg(39, -86, 38, -86)) == 180
    assert 89 < bearing_deg(0, 0, 0, 1) < 91


def test_compass_boundaries():
    assert compass(0) == "N"
    assert compass(11.24) == "N"
    assert compass(11.26) == "NNE"
    assert compass(348.76) == "N"
    assert compass(202.5) == "SSW"


def test_proximity_text():
    assert proximity(39.0, -86.0, 39.0, -86.0) == "at the site"
    assert proximity(39.0, -86.0, 39.1, -86.0).endswith("mi N")
