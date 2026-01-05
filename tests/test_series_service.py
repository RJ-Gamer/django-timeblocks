from datetime import date, time

import pytest
from django.contrib.auth import get_user_model

from timeblocks.constants import EndType, RecurrenceType
from timeblocks.models import Slot
from timeblocks.services.series_service import SeriesService


@pytest.fixture
def owner():
    User = get_user_model()
    return User.objects.create(username="owner")


def test_create_series_creates_slots(owner):
    series = SeriesService.create_series(
        owner=owner,
        data=dict(
            start_date=date(2025, 1, 1),
            start_time=time(9, 0),
            end_time=time(10, 0),
            timezone="UTC",
            recurrence_type=RecurrenceType.DAILY.value,
            interval=1,
            end_type=EndType.AFTER_OCCURRENCES.value,
            occurrence_count=3,
        ),
    )

    slots = Slot.objects.filter(series_id=series.series_id)

    assert slots.count() == 3


def test_create_series_is_idempotent_per_series(owner):
    data = dict(
        start_date=date(2025, 1, 1),
        start_time=time(9, 0),
        end_time=time(10, 0),
        timezone="UTC",
        recurrence_type=RecurrenceType.DAILY.value,
        interval=1,
        end_type=EndType.AFTER_OCCURRENCES.value,
        occurrence_count=3,
    )

    series1 = SeriesService.create_series(owner=owner, data=data)
    series2 = SeriesService.create_series(owner=owner, data=data)

    assert Slot.objects.filter(series_id=series1.series_id).count() == 3
    assert Slot.objects.filter(series_id=series2.series_id).count() == 3


def test_regeneration_preserves_locked_slots(owner):
    series = SeriesService.create_series(
        owner=owner,
        data=dict(
            start_date=date(2025, 1, 1),
            start_time=time(9, 0),
            end_time=time(10, 0),
            timezone="UTC",
            recurrence_type=RecurrenceType.DAILY.value,
            interval=1,
            end_type=EndType.AFTER_OCCURRENCES.value,
            occurrence_count=3,
        ),
    )

    slot = Slot.objects.filter(series_id=series.series_id).first()
    slot.is_locked = True
    slot.save()

    SeriesService.regenerate_series(series=series, scope="all")

    assert (
        Slot.objects.filter(
            series_id=series.series_id,
            is_deleted=False,
        ).count()
        == 3
    )


def test_cancel_series_deletes_future_unlocked_slots(owner):
    series = SeriesService.create_series(
        owner=owner,
        data=dict(
            start_date=date(2025, 1, 1),
            start_time=time(9, 0),
            end_time=time(10, 0),
            timezone="UTC",
            recurrence_type=RecurrenceType.DAILY.value,
            interval=1,
            end_type=EndType.AFTER_OCCURRENCES.value,
            occurrence_count=3,
        ),
    )

    SeriesService.cancel_series(series=series)

    assert (
        Slot.objects.filter(
            series_id=series.series_id,
            is_deleted=False,
        ).count()
        == 3
    )
