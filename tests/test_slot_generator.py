from datetime import date, time

import pytest

from timeblocks.constants import EndType, RecurrenceType
from timeblocks.models import SlotSeries
from timeblocks.services.slot_generator import iter_occurrence_dates

pytestmark = pytest.mark.django_db


def make_series(**overrides):
    defaults = {
        "start_date": date(2025, 1, 1),
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "timezone": "UTC",
        "recurrence_type": RecurrenceType.DAILY.value,
        "interval": 1,
        "end_type": EndType.AFTER_OCCURRENCES.value,
        "occurrence_count": 5,
        "by_weekdays": [],
    }
    defaults.update(overrides)
    return SlotSeries(**defaults)


def test_daily_generates_consecutive_dates():
    series = make_series(
        start_date=date(2025, 1, 1),
        occurrence_count=3,
    )

    dates = list(iter_occurrence_dates(series))

    assert dates == [
        date(2025, 1, 1),
        date(2025, 1, 2),
        date(2025, 1, 3),
    ]


def test_daily_respects_interval():
    series = make_series(
        start_date=date(2025, 1, 1),
        interval=2,
        occurrence_count=3,
    )

    dates = list(iter_occurrence_dates(series))

    assert dates == [
        date(2025, 1, 1),
        date(2025, 1, 3),
        date(2025, 1, 5),
    ]


def test_weekly_filters_by_weekdays():
    series = make_series(
        recurrence_type=RecurrenceType.WEEKLY.value,
        by_weekdays=["MON", "WED"],
        start_date=date(2025, 1, 1),  # Wednesday
        occurrence_count=3,
    )

    dates = list(iter_occurrence_dates(series))

    assert dates == [
        date(2025, 1, 1),  # Wed
        date(2025, 1, 6),  # Mon
        date(2025, 1, 8),  # Wed
    ]


def test_weekly_respects_interval():
    series = make_series(
        recurrence_type=RecurrenceType.WEEKLY.value,
        by_weekdays=["MON"],
        start_date=date(2025, 1, 6),  # Monday
        interval=2,
        occurrence_count=3,
    )

    dates = list(iter_occurrence_dates(series))

    assert dates == [
        date(2025, 1, 6),
        date(2025, 1, 20),
        date(2025, 2, 3),
    ]


def test_weekday_mon_fri_skips_weekends():
    series = make_series(
        recurrence_type=RecurrenceType.WEEKDAY_MON_FRI.value,
        start_date=date(2025, 1, 3),  # Friday
        occurrence_count=5,
    )

    dates = list(iter_occurrence_dates(series))

    assert dates == [
        date(2025, 1, 3),  # Fri
        date(2025, 1, 6),  # Mon
        date(2025, 1, 7),  # Tue
        date(2025, 1, 8),  # Wed
        date(2025, 1, 9),  # Thu
    ]
