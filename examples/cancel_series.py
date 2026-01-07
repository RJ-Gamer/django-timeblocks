from timeblocks.services.series_service import SeriesService


def cancel_availability(series):
    """
    Stops future availability without deleting history.
    """
    SeriesService.cancel_series(series=series)
