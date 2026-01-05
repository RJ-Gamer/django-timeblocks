import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from timeblocks.constants import EndType, RecurrenceType


def generate_series_id():
    return uuid.uuid4().hex


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlotSeries(TimeStampModel):
    """
    Declarative definition of a series of time blocks.
    """

    series_id = models.CharField(
        max_length=255,
        default=generate_series_id,
        unique=True,
        editable=False,
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="timeblocks_series"
    )
    object_id = models.CharField(max_length=255)
    owner = GenericForeignKey("content_type", "object_id")

    start_date = models.DateField(help_text="Date of first occurrence in the series.")
    start_time = models.TimeField(help_text="Start time of each slot.")
    end_time = models.TimeField(help_text="End time of each slot.")
    timezone = models.CharField(
        max_length=65,
        help_text="IANA timezone name for the series.",
    )

    recurrence_type = models.CharField(
        max_length=20,
        choices=[(r.value, r.name) for r in RecurrenceType],
        default=RecurrenceType.NONE.value,
    )
    interval = models.PositiveIntegerField(
        default=1,
        help_text="Repeat every N units (days/weeks/months/years).",
    )

    by_weekdays = models.JSONField(
        default=list,
        blank=True,
        help_text="List of weekdays. ex: ['Mon', 'Wed', 'Fri']",
    )

    week_of_month = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Week of the month for monthly recurrences (1..4, -1 for last week).",
    )

    month_of_year = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Month of the year for yearly recurrences (1..12).",
    )

    end_type = models.CharField(
        max_length=20,
        choices=[(e.value, e.name) for e in EndType],
        default=EndType.NEVER.value,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date is used when end_type is ON_DATE.",
    )

    occurrence_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Used when end_type = AFTER_OCCURRENCES",
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, help_text="soft delete flag")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Slot Series"
        verbose_name_plural = "Slot Series"
        verbose_name_plural = "Slot Series"
