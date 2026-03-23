from django.contrib import admin

from .models import Notification, NotificationTemplate


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient_email", "notification_type", "status", "sent_at", "created_at")
    list_filter = ("status", "notification_type", "channel")
    search_fields = ("recipient_email", "subject")


class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "notification_type", "is_active")
    list_filter = ("notification_type", "is_active")


admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationTemplate, NotificationTemplateAdmin)
