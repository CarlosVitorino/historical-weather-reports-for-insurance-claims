from datetime import date, datetime, timezone

from wxreport.timewin import fmt_local, local_day, timezone_for


def test_dst_day_lengths():
    assert local_day(date(2026, 3, 8), "America/New_York").hours == 23
    assert local_day(date(2026, 11, 1), "America/New_York").hours == 25
    assert local_day(date(2026, 2, 19), "America/Indiana/Indianapolis").hours == 24
    assert local_day(date(2026, 3, 8), "America/Phoenix").hours == 24  # no DST in Arizona


def test_window_bounds_utc():
    d = local_day(date(2026, 2, 19), "America/Indiana/Indianapolis")
    assert d.start_utc == datetime(2026, 2, 19, 5, tzinfo=timezone.utc)
    assert d.end_utc == datetime(2026, 2, 20, 5, tzinfo=timezone.utc)


def test_timezone_lookup_nationwide():
    assert timezone_for(39.1696, -86.5386) == "America/Indiana/Indianapolis"
    assert timezone_for(61.2181, -149.9003) == "America/Anchorage"
    assert timezone_for(21.3069, -157.8583) == "Pacific/Honolulu"
    assert timezone_for(33.4484, -112.0740) == "America/Phoenix"


def test_fmt_local_labels_zone():
    t = datetime(2026, 2, 19, 23, 57, tzinfo=timezone.utc)
    assert fmt_local(t, "America/Indiana/Indianapolis") == "6:57 PM EST"
    assert fmt_local(t, "America/Indiana/Indianapolis", with_date=True) == "Feb 19, 2026, 6:57 PM EST"
