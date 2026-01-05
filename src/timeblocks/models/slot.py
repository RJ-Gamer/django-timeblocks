from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from timeblocks.constants import Mode, SlotStatus


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Slot(TimeStampModel):
    """
    A concrete, persistent representation of a time block.
    """

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="timeblocks_slot"
    )
    object_id = models.CharField(max_length=255)
    owner = GenericForeignKey("content_type", "object_id")

    # Recurrence link
    series_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Identifier for the series this slot belongs to, if any.",
    )
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(db_index=True)

    mode = models.CharField(
        max_length=20,
        choices=[(m.value, m.name) for m in Mode],
    )

    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in SlotStatus],
        default=SlotStatus.OPEN.value,
        db_index=True,
    )

    is_locked = models.BooleanField(
        default=False, help_text="blocked slots must not be modified or deleted"
    )

    is_deleted = models.BooleanField(default=False, help_text="soft delete flag")

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["start"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "start"]),
            models.Index(fields=["series_id", "start"]),
        ]
        verbose_name = "Slot"
        verbose_name_plural = "Slots"
