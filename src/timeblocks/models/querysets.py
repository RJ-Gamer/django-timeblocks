from django.db import models
from django.utils import timezone


class SlotQueryset(models.QuerySet):
    def active(self):
        return self.filter(
            is_deleted=False,
            start__gte=timezone.now(),
        )

    def available(self):
        return self.active().filter(
            is_deleted=False, is_locked=False, start__gte=timezone.now()
        )

    def for_series(self, series):
        return self.filter(series_id=series.series_id)
