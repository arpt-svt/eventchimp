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
