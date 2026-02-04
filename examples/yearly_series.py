from datetime import date, time

from django.contrib.auth import get_user_model

from timeblocks.constants import EndType, RecurrenceType
from timeblocks.models import Slot
from timeblocks.services.series_service import SeriesService

User = get_user_model()
user = User.objects.first()

if not user:
    user = User.objects.create_user(
        username="test",
        email="test@example.com",
        password="test123",
    )


# 🧪 TEST 1 — First Monday of January every year
series = SeriesService.create_series(
    owner=user,
    data={
        "start_date": date(2025, 1, 1),
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "timezone": "UTC",
        "recurrence_type": RecurrenceType.YEARLY.value,
        "month_of_year": 1,  # January
        "by_weekdays": ["MON"],
        "week_of_month": 1,  # First Monday
        "end_type": EndType.AFTER_OCCURRENCES.value,
        "occurrence_count": 3,
    },
)

slots = Slot.objects.filter(series_id=series.series_id).order_by("start")
[(s.start.date(), s.start.weekday()) for s in slots]

# Expected output:
# [
#   (2025-01-06, 0),
#   (2026-01-05, 0),
#   (2027-01-04, 0),
# ]


# 🧪 TEST 2 — Last Friday of November every year

series = SeriesService.create_series(
    owner=user,
    data={
        "start_date": date(2025, 1, 1),
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "timezone": "UTC",
        "recurrence_type": RecurrenceType.YEARLY.value,
        "month_of_year": 11,  # November
        "by_weekdays": ["FRI"],
        "week_of_month": -1,  # LAST
        "end_type": EndType.AFTER_OCCURRENCES.value,
        "occurrence_count": 3,
    },
)

slots = Slot.objects.filter(series_id=series.series_id).order_by("start")
[(s.start.date(), s.start.weekday()) for s in slots]

# ✅ Expected
# 3 dates
# All November
# All Friday

# 🧪 TEST 3 — Every 2 years works

series = SeriesService.create_series(
    owner=user,
    data={
        "start_date": date(2025, 1, 1),
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "timezone": "UTC",
        "recurrence_type": RecurrenceType.YEARLY.value,
        "month_of_year": 3,  # March
        "by_weekdays": ["TUE"],
        "week_of_month": 2,  # Second Tuesday
        "interval": 2,  # Every 2 years
        "end_type": EndType.AFTER_OCCURRENCES.value,
        "occurrence_count": 3,
    },
)

slots = Slot.objects.filter(series_id=series.series_id).order_by("start")
[s.start.date() for s in slots]

# ✅ Expected
# Dates jump 2 years at a time
# All are March
# All are Tuesday
