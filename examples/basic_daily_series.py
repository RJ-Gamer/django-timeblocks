from datetime import date, time

from timeblocks.services.series_service import SeriesService


def create_daily_availability(user):
    """
    Therapist / instructor / resource is available
    every day from 9–10 AM for 5 days.
    """
    return SeriesService.create_series(
        owner=user,
        data={
            "start_date": date(2025, 1, 1),
            "start_time": time(9, 0),
            "end_time": time(10, 0),
            "timezone": "UTC",
            "recurrence_type": "DAILY",
            "interval": 1,
            "end_type": "AFTER_OCCURRENCES",
            "occurrence_count": 5,
        },
    )
