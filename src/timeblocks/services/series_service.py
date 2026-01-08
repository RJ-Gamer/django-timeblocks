from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from timeblocks.models import Slot, SlotSeries
from timeblocks.services.slot_generator import build_slot_instances


def _get_regeneration_cutoff(scope: str):
    if scope == "future":
        return timezone.now()
    if scope == "all":
        return None
    raise ValueError(f"Invalid scope: {scope}")


class SeriesService:
    """
    Orchestrates operations related to SlotSeries.
    """

    @staticmethod
    @transaction.atomic
    def create_series(*, owner, data: dict) -> SlotSeries:
        """
        Creates a new SlotSeries instance.

        Args:
            owner: The owner object for the series.
            data (dict): Data for creating the SlotSeries.

        Returns:
            SlotSeries: The created SlotSeries instance.

        Raises:
            InvalidRecurrence: If the recurrence data is invalid.
        """
        content_type = ContentType.objects.get_for_model(owner)

        series = SlotSeries.objects.create(
            content_type=content_type, object_id=str(owner.pk), **data
        )

        slot_candidates = list(build_slot_instances(series=series))

        existing_keys = set(
            Slot.objects.filter(
                series_id=series.series_id,
                start__in=[slot.start for slot in slot_candidates],
            ).values_list("start", flat=True)
        )

        slots_to_create = [
            slot for slot in slot_candidates if slot.start not in existing_keys
        ]

        if slots_to_create:
            content_type = ContentType.objects.get_for_model(owner)

            for slot in slots_to_create:
                slot.content_type = content_type
                slot.object_id = str(owner.pk)

            Slot.objects.bulk_create(slots_to_create)

        return series

    @staticmethod
    @transaction.atomic
    def regenerate_series(*, series: SlotSeries, scope: str = "future") -> None:
        """
        Regenerates time blocks for the given series.

        Args:
            series (SlotSeries): The SlotSeries instance to regenerate.
            scope (str): Scope of regeneration ('future' or 'all').
                Defaults to 'future'.
                future - Regenerate from today onwards.
                all - all unlocked slots in the series.
        Raises:
            ImmutableSlotError: If attempting to modify immutable slots.
        """
        cutoff = _get_regeneration_cutoff(scope)

        slots_qs = Slot.objects.filter(
            series_id=series.series_id, is_deleted=False, is_locked=False
        )

        if cutoff:
            slots_qs = slots_qs.filter(start__gte=cutoff)

        slots_qs.select_for_update().update(is_deleted=True)

        slot_candidates = list(build_slot_instances(series=series))

        locked_starts = set(
            Slot.objects.filter(
                series_id=series.series_id,
                is_locked=True,
            ).values_list("start", flat=True)
        )

        safe_candidates = [
            slot for slot in slot_candidates if slot.start not in locked_starts
        ]

        if safe_candidates:
            content_type = ContentType.objects.get_for_model(series.owner)

            for slot in safe_candidates:
                slot.content_type = content_type
                slot.object_id = str(series.object_id)

            Slot.objects.bulk_create(safe_candidates)

    @staticmethod
    @transaction.atomic
    def cancel_series(*, series: SlotSeries) -> None:
        """
        Cancels all time blocks in the given series.
        """
        now = timezone.now()

        series.is_active = False
        series.save(update_fields=["is_active"])

        Slot.objects.select_for_update().filter(
            series_id=series.series_id,
            is_deleted=False,
            is_locked=False,
            start__gte=now,
        ).update(is_deleted=True)
