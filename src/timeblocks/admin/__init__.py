from django.contrib import admin

from .series import SlotSeriesAdmin
from .slot import SlotAdmin

admin.site.disable_action("delete_selected")
