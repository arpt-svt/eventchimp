from django.db import models


class Weekday(models.IntegerChoices):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class ReservationStatus(models.TextChoices):
    SOFT_RESERVED = "SOFT_RESERVED"
    RESERVED = "RESERVED"
    CANCELLED = "CANCELLED"


class WaitlistStatus(models.TextChoices):
    WAITING = "WAITING"
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class WaitlistPriority(models.TextChoices):
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class NotificationType(models.TextChoices):
    WAITLIST_JOINED = "WAITLIST_JOINED"
    WAITLIST_OFFER = "WAITLIST_OFFER"
    WAITLIST_UPDATE = "WAITLIST_UPDATE"
    WAITLIST_EXPIRED = "WAITLIST_EXPIRED"
    RESERVATION_CONFIRMED = "RESERVATION_CONFIRMED"
    RESERVATION_CANCELLED = "RESERVATION_CANCELLED"
    RESERVATION_REMINDER = "RESERVATION_REMINDER"
    EVENT_UPDATED = "EVENT_UPDATED"
    EVENT_CANCELLED = "EVENT_CANCELLED"


class NotificationChannel(models.TextChoices):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WEBHOOK = "WEBHOOK"
    IN_APP = "IN_APP"


class NotificationStatus(models.TextChoices):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"
