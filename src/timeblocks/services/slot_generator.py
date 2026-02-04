import calendar
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta

from timeblocks.conf import timeblocks_settings
from timeblocks.constants import EndType, RecurrenceType, SlotStatus
from timeblocks.exceptions import InvalidRecurrence
from timeblocks.models import Slot, SlotSeries
from timeblocks.utils.timezone import normalize_datetime

WEEKDAY_MAP = {
    "MON": 0,
    "TUE": 1,
    "WED": 2,
    "THU": 3,
    "FRI": 4,
    "SAT": 5,
    "SUN": 6,
}

WEEKDAY_MON_FRI_SET = {"MON", "TUE", "WED", "THU", "FRI"}


def validate_series(series: SlotSeries) -> None:
    if series.start_time >= series.end_time:
        raise InvalidRecurrence("Series start time must be before end time.")

    if series.recurrence_type == RecurrenceType.NONE.value:
        return

    if series.interval < 1:
        raise InvalidRecurrence("Recurrence interval must be at least 1.")

    if (
        series.end_type == EndType.AFTER_OCCURRENCES.value
        and not series.occurrence_count
    ):
        raise InvalidRecurrence(
            "Number of occurrences must be specified for 'after occurrences' end type."
        )

    if series.end_type == EndType.ON_DATE.value and not series.end_date:
        raise InvalidRecurrence("End date must be specified for 'on date' end type.")

    if series.recurrence_type == RecurrenceType.WEEKDAY_MON_FRI.value:
        if series.by_weekdays:
            raise InvalidRecurrence(
                "WEEKDAY_MON_FRI is a preset and does not accept by_weekdays. "
                "Use WEEKDAYS for custom weekday selection."
            )

        if series.interval != 1:
            raise InvalidRecurrence("WEEKDAY_MON_FRI does not support interval > 1.")

    if series.recurrence_type == RecurrenceType.WEEKDAYS.value:
        if not series.by_weekdays:
            raise InvalidRecurrence(
                "WEEKDAYS recurrence requires by_weekdays "
                "(e.g. ['MON', 'WED', 'FRI'])."
            )

    if series.recurrence_type == RecurrenceType.MONTH_NTH.value:
        if not series.by_weekdays or len(series.by_weekdays) != 1:
            raise InvalidRecurrence(
                "MONTH_NTH recurrence requires exactly one value in by_weekdays."
            )
        if series.week_of_month not in {1, 2, 3, 4}:
            raise InvalidRecurrence(
                "MONTH_NTH requires week_of_month to be 1, 2, 3, or 4."
            )

    if series.recurrence_type == RecurrenceType.MONTH_LAST.value:
        if not series.by_weekdays or len(series.by_weekdays) != 1:
            raise InvalidRecurrence(
                "MONTH_LAST recurrence requires exactly one value in by_weekdays."
            )
        series.week_of_month = -1

    if series.recurrence_type == RecurrenceType.YEARLY.value:
        if not series.month_of_year or not (1 <= series.month_of_year <= 12):
            raise InvalidRecurrence(
                "YEARLY recurrence requires month_of_year to be set and between 1 and 12."
            )

        if not series.by_weekdays or len(series.by_weekdays) != 1:
            raise InvalidRecurrence(
                "YEARLY recurrence requires exactly one value in by_weekdays."
            )
        if series.week_of_month not in {1, 2, 3, 4, -1}:
            raise InvalidRecurrence(
                "YEARLY recurrence requires week_of_month to be 1, 2, 3, 4, or -1(last week)."
            )


def should_stop(*, generated: int, current_date: date, series: SlotSeries) -> bool:
    if (
        series.end_type == EndType.AFTER_OCCURRENCES.value
        and generated >= series.occurrence_count
    ):
        return True

    if series.end_type == EndType.ON_DATE.value and current_date > series.end_date:
        return True

    return False


def iter_daily_dates(series: SlotSeries):
    current_date = series.start_date
    generated = 0

    while True:
        if should_stop(generated=generated, current_date=current_date, series=series):
            break

        yield current_date
        generated += 1
        current_date += timedelta(days=series.interval)


def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date | None:
    cal = calendar.Calendar()
    candidates = [
        day
        for day in cal.itermonthdates(year, month)
        if day.month == month and day.weekday() == weekday
    ]
    if not candidates:
        return None

    if n == -1:
        return candidates[-1]

    if 1 <= n <= len(candidates):
        return candidates[n - 1]

    return None


def iter_MONTH_NTH_dates(series):
    if not series.by_weekdays or len(series.by_weekdays) != 1:
        raise InvalidRecurrence("MONTH_NTH requires exactly one weekday")

    if series.week_of_month not in {1, 2, 3, 4, -1}:
        raise InvalidRecurrence("Invalid week_of_month value")

    weekday = WEEKDAY_MAP[series.by_weekdays[0]]
    interval = series.interval or 0

    current = series.start_date.replace(day=1)
    generated = 0
    iterations = 0
    max_guard = timeblocks_settings.MAX_OCCURENCES * 2

    while True:
        candidate = nth_weekday_of_month(
            current.year, current.month, weekday, series.week_of_month
        )
        probe_date = candidate or current
        if should_stop(generated=generated, current_date=probe_date, series=series):
            break

        candidate = nth_weekday_of_month(
            current.year, current.month, weekday, series.week_of_month
        )

        if candidate and candidate >= series.start_date:
            yield candidate
            generated += 1

        current += relativedelta(months=interval)
        iterations += 1

        if iterations > max_guard:
            raise InvalidRecurrence("MONTH_NTH exceeded safety bounds")


def iter_weekly_dates(series: SlotSeries, override_weekdays=None):
    max_guard = timeblocks_settings.MAX_OCCURENCES
    weekdays = override_weekdays or series.by_weekdays

    if not weekdays:
        raise InvalidRecurrence("Weekly recurrence requires by_weekdays to be set.")

    target_weekdays = {WEEKDAY_MAP[day] for day in weekdays}

    current_date = series.start_date

    generated = 0

    iterations = 0
    max_guard = timeblocks_settings.MAX_OCCURENCES * 7  # safety multiplier

    while True:
        if should_stop(
            generated=generated,
            current_date=current_date,
            series=series,
        ):
            break

        if iterations >= max_guard:
            raise InvalidRecurrence("Weekly recurrence exceeded safety bounds")

        if current_date.weekday() in target_weekdays:
            yield current_date
            generated += 1

        current_date += timedelta(days=1)
        iterations += 1

        if current_date.weekday() == 0 and series.interval > 1:
            current_date += timedelta(weeks=series.interval - 1)


def iter_yearly_nth_dates(series: SlotSeries):
    interval = series.interval or 1
    weekday = WEEKDAY_MAP[series.by_weekdays[0]]

    generated = 0
    iterations = 0
    max_guard = timeblocks_settings.MAX_OCCURENCES * 2
    year = series.start_date.year

    while True:
        candidate = nth_weekday_of_month(
            year, series.month_of_year, weekday, series.week_of_month
        )
        probe_date = candidate or date(year, series.month_of_year, 1)
        if should_stop(generated=generated, current_date=probe_date, series=series):
            break

        if candidate and candidate >= series.start_date:
            yield candidate
            generated += 1

        year += interval
        iterations += 1

        if iterations > max_guard:
            raise InvalidRecurrence("Yearly recurrence exceeded safety bounds")


def iter_occurrence_dates(series: SlotSeries):
    if series.recurrence_type == RecurrenceType.NONE.value:
        yield series.start_date
        return

    if series.recurrence_type == RecurrenceType.DAILY.value:
        yield from iter_daily_dates(series)
        return

    if series.recurrence_type == RecurrenceType.WEEKLY.value:
        yield from iter_weekly_dates(series)
        return

    if series.recurrence_type == RecurrenceType.WEEKDAY_MON_FRI.value:
        yield from iter_weekly_dates(
            series,
            override_weekdays=WEEKDAY_MON_FRI_SET,
        )
        return

    if series.recurrence_type == RecurrenceType.WEEKDAYS.value:
        yield from iter_weekly_dates(
            series,
            override_weekdays=set(series.by_weekdays),
        )
        return

    if series.recurrence_type == RecurrenceType.MONTH_NTH.value:
        yield from iter_MONTH_NTH_dates(series)
        return

    if series.recurrence_type == RecurrenceType.MONTH_LAST.value:
        series.week_of_month = -1
        yield from iter_MONTH_NTH_dates(series)
        return

    if series.recurrence_type == RecurrenceType.YEARLY.value:
        yield from iter_yearly_nth_dates(series)
        return

    raise InvalidRecurrence(f"Unsupported recurrence type: {series.recurrence_type}")


def build_slot_instances(series: SlotSeries):
    validate_series(series)

    # content_type = ContentType.objects.get_for_model(series.owner)

    max_guard = timeblocks_settings.MAX_OCCURENCES

    produced = 0

    for day in iter_occurrence_dates(series):
        if produced >= max_guard:
            raise InvalidRecurrence(
                f"{timeblocks_settings.MAX_OCCURENCES} occurrences limit reached."
            )

        start_dt = datetime.combine(day, series.start_time)
        end_dt = datetime.combine(day, series.end_time)

        start_utc = normalize_datetime(start_dt, series.timezone)
        end_utc = normalize_datetime(end_dt, series.timezone)

        yield Slot(
            series_id=series.series_id,
            start=start_utc,
            end=end_utc,
            status=SlotStatus.OPEN.value,
        )

        produced += 1
