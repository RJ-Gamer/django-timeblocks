from enum import Enum


class Mode(str, Enum):
    """
    Enumeration for different modes of operation.
    """

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class SlotStatus(str, Enum):
    """
    Lifecycle status of an individual slot.
    """

    OPEN = "OPEN"
    BOOKED = "BOOKED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class RecurrenceType(str, Enum):
    """
    Rule that defines how slots recur over time.
    """

    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    WEEKDAYS = "WEEKDAYS"
    MONTH_NTH = "MONTH_NTH"
    MONTH_LAST = "MONTH_LAST"
    YEARLY = "YEARLY"
    WEEKDAY_MON_FRI = "WEEKDAY_MON_FRI"


class EndType(str, Enum):
    """
    Conditions under which slot generation ends.
    """

    NEVER = "NEVER"
    ON_DATE = "ON_DATE"
    AFTER_OCCURRENCES = "AFTER_OCCURRENCES"
