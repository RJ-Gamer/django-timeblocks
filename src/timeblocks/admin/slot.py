from django.contrib import admin

from timeblocks.models import Slot


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "series_id",
        "start",
        "end",
        "is_locked",
        "is_deleted",
    )

    list_filter = (
        "is_locked",
        "is_deleted",
        "start",
    )

    search_fields = ("series_id",)

    readonly_fields = [f.name for f in Slot._meta.fields]

    ordering = ("start",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
