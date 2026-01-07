from timeblocks.services.series_service import SeriesService


def update_schedule(series):
    """
    Called when a user edits their availability.
    """
    # Example: change interval or weekdays
    series.interval = 2
    series.save(update_fields=["interval"])

    # Safely regenerate future slots only
    SeriesService.regenerate_series(
        series=series,
        scope="future",
    )
