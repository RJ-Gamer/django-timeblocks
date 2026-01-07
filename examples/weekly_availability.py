from datetime import date, time

from timeblocks.services.series_service import SeriesService


def create_weekly_availability(user):
    """
    Available every Monday, Wednesday, and Friday.
    """
    return SeriesService.create_series(
        owner=user,
        data={
            "start_date": date(2025, 1, 6),  # Monday
            "start_time": time(10, 0),
            "end_time": time(11, 0),
            "timezone": "UTC",
            "recurrence_type": "WEEKLY",
            "interval": 1,
            "by_weekdays": ["MON", "WED", "FRI"],
            "end_type": "AFTER_OCCURRENCES",
            "occurrence_count": 10,
        },
    )
