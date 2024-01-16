from datetime import time

from rest_framework import serializers
from django.utils import timezone

from commons.serializerfields import TimeZoneField, AutoTzDateTimeField
from commons.enums import ReservationStatus
from .models import Reservation
from .availability_helper import get_available_slots


class ReservationSerializer(serializers.ModelSerializer):
    start_datetime = AutoTzDateTimeField()
    end_datetime = AutoTzDateTimeField(read_only=True)
    created_at = AutoTzDateTimeField(read_only=True)
    updated_at = AutoTzDateTimeField(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "event",
            "status",
            "start_datetime",
            "end_datetime",
            "attendee_full_name",
            "attendee_email",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "is_active", "end_datetime", "created_at", "updated_at")

    def validate_start_datetime(self, start_datetime):
        if timezone.now() > start_datetime:
            raise serializers.ValidationError("Start date should be in future")
        return start_datetime

    def validate(self, data):
        return data

    def save(self, *args, **kwargs):
        event_start = self.validated_data['start_datetime']
        event_duration_in_mins = timezone.timedelta(minutes=self.validated_data['event'].duration_in_minutes)
        self.validated_data['end_datetime'] = event_start + event_duration_in_mins
        self.validated_data['status'] = ReservationStatus.RESERVED
        # TODO: Use distributed locking
        available_slots = get_available_slots(
            event_id=self.validated_data["event"].id,
            start_datetime=event_start,
            end_datetime=self.validated_data['end_datetime']
        )
        available_slots = [slot for slot in available_slots if slot["start_datetime"] == event_start]
        if not available_slots:
            raise serializers.ValidationError("Requested slot is not available, please try again")
        resp = super().save(*args, **kwargs)
        return resp


class AvailabilityRequestSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    start_datetime = serializers.DateTimeField(read_only=True)
    end_datetime = serializers.DateTimeField(read_only=True)
    timezone = TimeZoneField()

    def validate(self, data):
        start_date = data["start_date"]
        end_date = data["end_date"]
        user_timezone = data["timezone"]
        if start_date < timezone.localtime(timezone.now(), user_timezone).date():
            raise serializers.ValidationError("Start date can not be a past date")
        if start_date > end_date:
            raise serializers.ValidationError("Start date should be before or same as end date")

        start_datetime = timezone.datetime.combine(start_date, time(0, 0), user_timezone)
        end_datetime = timezone.datetime.combine(end_date, time(0, 0), user_timezone) + timezone.timedelta(days=1)
        data["start_datetime"] = timezone.localtime(start_datetime)
        data["end_datetime"] = timezone.localtime(end_datetime)
        return data


# class AvailableSlotSerializer(serializers.Serializer):
#     start_datetime = serializers.DateTimeField()


# class AvailabilityResponseSerializer(serializers.Serializer):
#     date = serializers.DateField()
#     available_slots = AvailableSlotSerializer(many=True)
