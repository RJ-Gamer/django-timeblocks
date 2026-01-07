from datetime import datetime, timezone

from django.utils import timezone as dj_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from timeblocks.conf import timeblocks_settings
from timeblocks.exceptions import ConfigurationError


def get_timezone(tz_name: str | None = None):
    """
    Resolve a timezone name to a tzinfo object.
    """
    name = tz_name or timeblocks_settings.DEFAULT_TIMEZONE

    if name.upper() == "UTC":
        return timezone.utc  # stdlib, always exists

    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        raise ConfigurationError(f"Invalid timezone name: {name}")


def ensure_aware(dt: datetime, tzinfo) -> datetime:
    """
    Ensure a datetime is timezone-aware.
    """
    if dj_timezone.is_aware(dt):
        return dt

    return dj_timezone.make_aware(dt, tzinfo)


def to_utc(dt: datetime) -> datetime:
    """
    Convert an aware datetime to UTC.
    """
    if dj_timezone.is_naive(dt):
        raise ValueError("Cannot convert naive datetime to UTC.")

    return dt.astimezone(timezone.utc)


def normalize_datetime(dt: datetime, tz_name: str | None = None) -> datetime:
    """
    Normalize a datetime:
    - make it aware if naive
    - apply the specified timezone
    - convert to UTC
    """
    tzinfo = get_timezone(tz_name)
    aware = ensure_aware(dt, tzinfo)
    return to_utc(aware)
