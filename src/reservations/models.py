from django.db import models

from events.models import Event
from commons.enums import ReservationStatus


class Reservation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="reservations")
    status = models.CharField(choices=ReservationStatus.choices, default=ReservationStatus.SOFT_RESERVED)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    attendee_full_name = models.CharField(max_length=255)
    attendee_email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_owner_id(self):
        return self.event.organiser_id

    def soft_delete(self):
        self.is_active = False
        self.save(
            force_update=True,
            update_fields=["is_active", "updated_at"]
        )

    @classmethod
    def get_active_reservations(cls, event_id, start_datetime, end_datetime):
        return cls.objects.exclude(
            status=ReservationStatus.CANCELLED
        ).filter(
            event_id=event_id,
            start_datetime__lte=end_datetime,
            end_datetime__gte=start_datetime,
            is_active=True,
        )
