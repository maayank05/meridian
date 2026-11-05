"""D-017 timezone conversion: normal, DST gap, DST fall-back ambiguity, boundary seconds (rule T10)."""

from datetime import datetime

import pytest

from meridian.ingestion.timezones import to_utc


@pytest.mark.parametrize(
    ("local", "expected_utc"),
    [
        (datetime(2017, 3, 10, 10, 0, 0), datetime(2017, 3, 10, 13, 0, 0)),  # standard time, UTC-3
        (datetime(2017, 1, 15, 12, 0, 0), datetime(2017, 1, 15, 14, 0, 0)),  # DST, UTC-2
        (datetime(2017, 10, 15, 9, 0, 0), datetime(2017, 10, 15, 11, 0, 0)),  # DST start day, after the gap
        (datetime(2019, 6, 1, 12, 0, 0), datetime(2019, 6, 1, 15, 0, 0)),  # Brazil abolished DST in 2019
    ],
)
def test_normal_timestamps_convert(local, expected_utc):
    assert to_utc(local) == (expected_utc, "ok")


@pytest.mark.parametrize(
    "local",
    [
        datetime(2017, 10, 15, 0, 0, 0),  # first second of the skipped hour
        datetime(2017, 10, 15, 0, 30, 0),
        datetime(2017, 10, 15, 0, 59, 59),  # last second of the skipped hour
        datetime(2016, 10, 16, 0, 15, 0),
    ],
)
def test_dst_gap_is_nonexistent_and_not_converted(local):
    assert to_utc(local) == (None, "nonexistent")


@pytest.mark.parametrize(
    "local",
    [
        datetime(2018, 2, 17, 23, 0, 0),  # first second of the repeated hour
        datetime(2018, 2, 17, 23, 30, 0),
        datetime(2018, 2, 17, 23, 59, 59),  # last second of the repeated hour
        datetime(2017, 2, 18, 23, 45, 0),
    ],
)
def test_dst_fall_back_is_ambiguous_and_utc_not_invented(local):
    assert to_utc(local) == (None, "ambiguous")


def test_boundaries_around_transitions_are_unambiguous():
    assert to_utc(datetime(2017, 10, 14, 23, 59, 59)) == (datetime(2017, 10, 15, 2, 59, 59), "ok")  # UTC-3
    assert to_utc(datetime(2017, 10, 15, 1, 0, 0)) == (datetime(2017, 10, 15, 3, 0, 0), "ok")  # UTC-2
    assert to_utc(datetime(2018, 2, 17, 22, 59, 59)) == (datetime(2018, 2, 18, 0, 59, 59), "ok")  # UTC-2
    assert to_utc(datetime(2018, 2, 18, 0, 0, 0)) == (datetime(2018, 2, 18, 3, 0, 0), "ok")  # UTC-3


def test_aware_datetime_rejected():
    with pytest.raises(ValueError, match="naive"):
        to_utc(datetime.fromisoformat("2017-03-10T10:00:00+00:00"))
