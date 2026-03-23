from django.contrib import admin

from .models import WaitlistEntry, WaitlistConfig


class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "email", "full_name", "status", "position", "is_active", "created_at")
    list_filter = ("status", "is_active", "priority")
    search_fields = ("email", "full_name")
    raw_id_fields = ("event",)


class WaitlistConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "is_enabled", "max_size", "auto_promote")
    raw_id_fields = ("event",)


admin.site.register(WaitlistEntry, WaitlistEntryAdmin)
admin.site.register(WaitlistConfig, WaitlistConfigAdmin)
