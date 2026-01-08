from django.contrib import admin

from timeblocks.models import SlotSeries


@admin.register(SlotSeries)
class SlotSeriesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "series_id",
        "start_date",
        "end_date",
        "interval",
        "recurrence_type",
        "end_type",
        "is_active",
    )
    list_filter = ("recurrence_type", "end_type", "is_active")
    readonly_fields = ("series_id", "created_at", "updated_at")
    search_fields = ("series_id",)
    fieldsets = (
        (
            "Ownership",
            {
                "fields": ("content_type", "object_id"),
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "start_date",
                    "start_time",
                    "end_time",
                    "timezone",
                ),
            },
        ),
        (
            "Recurrence",
            {
                "fields": (
                    "recurrence_type",
                    "interval",
                    "by_weekdays",
                    "week_of_month",
                    "month_of_year",
                ),
            },
        ),
        (
            "Termination",
            {
                "fields": (
                    "end_type",
                    "end_date",
                    "occurrence_count",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "System",
            {
                "fields": ("series_id", "created_at", "updated_at"),
            },
        ),
    )

    actions = ["cancel_series"]

    @admin.action(description="Cancel selected series (safe)")
    def cancel_series(self, request, queryset):
        from timeblocks.services.series_service import SeriesService

        for series in queryset:
            SeriesService.cancel_series(series)
