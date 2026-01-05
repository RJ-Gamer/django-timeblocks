class TimeBlocksError(Exception):
    """
    Base exception for time block errors.
    Users may catch this exception to handle all time block related errors.
    """

    pass


class InvalidRecurrence(TimeBlocksError):
    """
    Exception raised for invalid recurrence patterns in time blocks.
    """

    pass


class SlotGenerationError(TimeBlocksError):
    """
    Exception raised when there is an error generating time slots.
    """

    pass


class ImmutableSlotError(TimeBlocksError):
    """
    Exception raised when an attempt is made to modify an immutable slot.
    """

    pass


class ConfigurationError(TimeBlocksError):
    """
    Exception raised for invalid configuration settings in time blocks.
    """

    pass
