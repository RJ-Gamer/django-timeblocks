from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.utils import timezone as dj_timezone

from timeblocks.conf import timeblocks_settings
from timeblocks.exceptions import ConfigurationError


def get_timezone(tz_name: str | None = None) -> ZoneInfo:
    """
    Resolve a timezone name to a ZoneInfo object.
    """
    name = tz_name or timeblocks_settings.DEFAULT_TIMEZONE

    if name.upper() == "UTC":
        return dj_timezone.utc

    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        raise ConfigurationError(f"Invalid timezone name: {name}")


def ensure_aware(dt: datetime, tz: ZoneInfo | None = None) -> datetime:
    """
    Ensure a datetime is timezone-aware.
    """
    if dj_timezone.is_aware(dt):
        return dt
    tz_info = tz or get_timezone()
    return dj_timezone.make_aware(dt, tz_info)


def to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC.
    """
    if dj_timezone.is_naive(dt):
        return ValueError("Cannot convert naive datetime to UTC.")
    return dt.astimezone(dj_timezone.utc)


def normalize_datetime(dt: datetime, tz: ZoneInfo | None = None) -> datetime:
    """
    Normalize a datetime:
    - make it aware if naive
    - apply the specified timezone
    - convert to utc
    """
    tz_info = get_timezone(tz)
    ensure = ensure_aware(dt, tz_info)
    return to_utc(ensure)
