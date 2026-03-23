from django.db import models
from django.conf import settings

from events.models import Event
from commons.enums import WaitlistStatus, WaitlistPriority


class WaitlistEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="waitlist_entries")
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(
        choices=WaitlistStatus.choices,
        default=WaitlistStatus.WAITING,
        max_length=20
    )
    priority = models.CharField(
        choices=WaitlistPriority.choices,
        default=WaitlistPriority.NORMAL,
        max_length=20
    )
    position = models.PositiveIntegerField(default=0)
    preferred_start_datetime = models.DateTimeField(null=True, blank=True)
    preferred_end_datetime = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    max_wait_days = models.PositiveIntegerField(default=30)
    notification_count = models.PositiveIntegerField(default=0)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    offered_at = models.DateTimeField(null=True, blank=True)
    offer_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "position", "created_at"]
        unique_together = ["event", "email"]

    def get_owner_id(self):
        return self.event.organiser_id

    def soft_delete(self):
        self.is_active = False
        self.save(force_update=True, update_fields=["is_active", "updated_at"])

    def promote(self):
        self.status = WaitlistStatus.OFFERED
        self.offered_at = models.functions.Now()
        self.save()

    def accept_offer(self):
        self.status = WaitlistStatus.ACCEPTED
        self.save()

    def decline_offer(self):
        self.status = WaitlistStatus.DECLINED
        self.save()

    def expire_offer(self):
        self.status = WaitlistStatus.EXPIRED
        self.save()

    def calculate_position(self):
        return WaitlistEntry.objects.filter(
            event=self.event,
            status=WaitlistStatus.WAITING,
            created_at__lt=self.created_at,
            is_active=True
        ).count() + 1

    @classmethod
    def get_next_in_line(cls, event_id):
        return cls.objects.filter(
            event_id=event_id,
            status=WaitlistStatus.WAITING,
            is_active=True
        ).first()

    @classmethod
    def get_waitlist_count(cls, event_id):
        return cls.objects.filter(
            event_id=event_id,
            is_active=True
        ).count()

    @classmethod
    def cleanup_expired_entries(cls, event_id):
        from django.utils import timezone
        from datetime import timedelta
        entries = cls.objects.filter(
            event_id=event_id,
            status=WaitlistStatus.WAITING,
            is_active=True
        )
        for entry in entries:
            if entry.created_at + timedelta(days=entry.max_wait_days) < timezone.now():
                entry.status = WaitlistStatus.EXPIRED
                entry.save()


class WaitlistConfig(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="waitlist_config")
    is_enabled = models.BooleanField(default=False)
    max_size = models.PositiveIntegerField(default=100)
    auto_promote = models.BooleanField(default=True)
    offer_expiry_hours = models.PositiveIntegerField(default=24)
    allow_priority_upgrade = models.BooleanField(default=False)
    notify_on_join = models.BooleanField(default=True)
    notify_on_promotion = models.BooleanField(default=True)
    notify_position_change = models.BooleanField(default=False)
    admin_email = models.EmailField(blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
