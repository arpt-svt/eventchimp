from django.db import models
from django.conf import settings

from commons.enums import NotificationType, NotificationChannel, NotificationStatus


class NotificationTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(
        choices=NotificationType.choices,
        max_length=30
    )
    subject = models.CharField(max_length=255)
    body_text = models.TextField()
    body_html = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Notification(models.Model):
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=255, blank=True)
    notification_type = models.CharField(
        choices=NotificationType.choices,
        max_length=30
    )
    channel = models.CharField(
        choices=NotificationChannel.choices,
        default=NotificationChannel.EMAIL,
        max_length=20
    )
    status = models.CharField(
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        max_length=20
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    error_message = models.TextField(blank=True, default="")
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
            models.Index(fields=["recipient_email"]),
        ]

    def mark_sent(self):
        from django.utils import timezone
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.save()

    def mark_failed(self, error):
        self.status = NotificationStatus.FAILED
        self.error_message = error
        self.retry_count += 1
        self.save()

    def can_retry(self):
        return self.retry_count < self.max_retries

    @classmethod
    def get_pending_notifications(cls):
        from django.utils import timezone
        return cls.objects.filter(
            status=NotificationStatus.PENDING,
            scheduled_at__lte=timezone.now()
        ).select_related()

    @classmethod
    def bulk_create_notifications(cls, notifications_data):
        notifications = [cls(**data) for data in notifications_data]
        return cls.objects.bulk_create(notifications)
