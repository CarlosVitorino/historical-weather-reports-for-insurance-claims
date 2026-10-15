"""Unit tests for the source parsers, using real report text where it matters."""
from datetime import date, datetime, timezone

from wxreport import units
from wxreport.geo import distance_to_polygon_mi, point_in_polygon
from wxreport.sources import ghcnh, stormevents, nws
from wxreport.timewin import local_day

UTC = timezone.utc
DAY = local_day(date(2026, 2, 19), "America/Indiana/Indianapolis")
HEADER = ("STATION|DATE|temperature|temperature_Report_Type|temperature_Source_Code|wind_speed|wind_gust|"
          "precipitation|precipitation_Measurement_Code|REM")


def psv(*rows):
    return "\n".join([HEADER] + ["|".join(r) for r in rows]) + "\n"


def test_decode_weather_real_reports():
    assert ghcnh.decode_weather("METAR KBMG 192353Z 09011KT 10SM -TSRA SCT065 BKN075 18/12 A2943 RMK AO2")[0] == \
        ["light thunderstorm with rain"]
    assert ghcnh.decode_weather("SPECI KBMG 200001Z 21038G61KT 7SM -TSRA SQ FEW033 17/12 RMK AO2")[1] == ["-TSRA", "SQ"]
    phrases, _ = ghcnh.decode_weather("METAR KXXX 011253Z 30008G28KT 3/4SM +TSRAGR BR FC OVC009 21/20 RMK AO2")
    assert phrases == ["heavy thunderstorm with rain and hail", "mist", "funnel cloud"]
    assert ghcnh.decode_weather("METAR KBMG 190553Z AUTO 12005KT 8SM CLR 09/08 A2971 RMK AO2")[0] == []


def test_peak_wind_remark():
    t = datetime(2026, 2, 20, 0, 30, tzinfo=UTC)
    assert ghcnh._peak_wind("SPECI KBMG 200030Z VCTS RMK AO2 PK WND 21061/0001 WSHFT 2344", t) == \
        (210, 61, datetime(2026, 2, 20, 0, 1, tzinfo=UTC))
    # minutes only: same hour as the report
    assert ghcnh._peak_wind("METAR KXXX 201453Z RMK AO2 PK WND 27045/32", datetime(2026, 2, 20, 14, 53, tzinfo=UTC))[2] \
        == datetime(2026, 2, 20, 14, 32, tzinfo=UTC)


def test_precip_metar_periods_missing_not_zero():
    text = psv(
        ("USW1", "2026-02-19T21:53:00", "18.9", "FM15", "343", "3.1", "", "0.5", "", "METAR K 192153Z RMK AO2 P0002"),
        ("USW1", "2026-02-19T22:20:00", "18.0", "FM16", "343", "3.1", "", "1.0", "", "SPECI K 192220Z RMK AO2 P0004"),
        ("USW1", "2026-02-19T22:53:00", "18.3", "FM15", "343", "6.7", "10.8", "2.0", "", "METAR K 192253Z RMK AO2 P0008"),
        ("USW1", "2026-02-19T23:53:00", "17.8", "FM15", "343", "5.7", "", "", "", "METAR K 192353Z RMK AO2 PNO"),
        ("USW1", "2026-02-20T00:53:00", "17.0", "FM15", "343", "2.0", "", "", "", "METAR K 200053Z RMK AO2"),
    )
    obs = ghcnh.parse_psv(text, DAY)
    sd = ghcnh.StationDay(None, obs, edge=obs)
    total, counted, missing, trace = sd.precipitation(DAY)
    # 21:53 (0.5) + 22:53 (2.0, the SPECI's running total is superseded) + 00:53 (0); 23:53 PNO is missing;
    # every other hour of the day has no report at all, so it is missing too.
    assert total == 2.5
    assert counted == 3 and missing == 21


def test_precip_hourly_gauge_uses_hour_ending_totals():
    rows = [("USC1", f"2026-02-{d}T{h:02d}:00:00", "", "", "382", "", "", p, "", "")
            for d, h, p in [("19", 5, "9.9"), ("19", 6, "1.0"), ("20", 0, "2.0"), ("20", 5, "0.5"), ("20", 6, "7.0")]]
    obs = ghcnh.parse_psv(psv(*rows), DAY)
    in_day = [o for o in obs if o.t < DAY.end_utc]
    sd = ghcnh.StationDay(None, in_day, edge=obs)
    total, counted, missing, _ = sd.precipitation(DAY)
    # hours ending 06Z, 00Z and 05Z (next day) belong to the local day; 05Z on the 19th and 06Z on the 20th do not
    assert round(total, 2) == 3.5 and counted == 3 and missing == 21
    assert sd.network.startswith("Hourly precipitation gauge")


def test_polygon_from_warning_text():
    text = "TORIND\n...\nLAT...LON 3920 8698 3926 8668 3905 8653 3899 8699\nTIME...MOT...LOC 2339Z 266DEG 35KT 3922 8687\n"
    poly = nws.parse_polygon(text)
    assert poly[0] == (39.20, -86.98) and len(poly) == 4
    assert point_in_polygon(39.10, -86.80, poly)
    assert not point_in_polygon(39.17, -86.53, poly)
    assert 3.5 < distance_to_polygon_mi(39.17, -86.53, poly) < 4.5  # nearest edge ~4 mi west


def test_product_time_crosses_month():
    near = datetime(2026, 3, 1, 0, 30, tzinfo=UTC)
    assert nws._product_time("WFUS53 KIND 282339\nTORIND", near) == datetime(2026, 2, 28, 23, 39, tzinfo=UTC)


def test_storm_events_time_is_local_standard():
    assert stormevents._dt("202602", "19", "1857", "EST-5") == datetime(2026, 2, 19, 23, 57, tzinfo=UTC)
    assert stormevents._dt("202607", "4", "30", "AKST-9") == datetime(2026, 7, 4, 9, 30, tzinfo=UTC)


def test_units():
    assert units.fmt_precip_in(0.1) == "<0.01"
    assert units.fmt_precip_in(0.0, trace=True) == "<0.01"
    assert units.fmt_precip_in(0.0) == "0.00"
    assert units.fmt_precip_in(None) == "—"
    assert round(units.mph(31.4)) == 70 and round(units.kt(31.4)) == 61
