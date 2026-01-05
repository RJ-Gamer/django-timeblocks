from django.conf import settings

DEFAULTS = {
    # how far in the future slots are generated when end_type = NEVER
    "GENERATION_WINDOW_DAYS": 180,
    # Fallback timezone if none is provided
    "DEFAULT_TIMEZONE": "UTC",
    # Whether slots are soft-deleted or hard-deleted
    "SOFT_DELETE": True,
    # Safety guard to prevent generating an excessive number of slots at once
    "MAX_OCCURENCES": 1000,
    # Whether booked slots are strictly immutable
    "BOOKED_SLOTS_IMMUTABLE": True,
}


class TimeblocksSettings:
    """
    Read-only resolved settings for timeblocks.

    usage:
        from timeblocks.conf import timeblocks_settings
        print(timeblocks_settings.DEFAULT_TIMEZONE)
    """

    def __init__(self):
        user_settings = getattr(settings, "TIMEBLOCKS", {})

        for key, default in DEFAULTS.items():
            setattr(self, key, user_settings.get(key, default))


timeblocks_settings = TimeblocksSettings()
