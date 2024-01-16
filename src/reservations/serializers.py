import zoneinfo
from rest_framework import serializers
from django.utils import timezone

from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
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
        read_only_fields = ("status", "is_active", "end_datetime")

    def validate_start_datetime(self, start_datetime):
        if timezone.now() > start_datetime:
            raise serializers.ValidationError("Start date should be in future")
        return start_datetime

    def validate(self, data):
        return data

    def to_representation(self, instance):
        user_timezone = zoneinfo.ZoneInfo(self.context.get('request').query_params.get('timezone'))
        if user_timezone:
            start_datetime = timezone.localtime(instance.start_datetime, user_timezone)
            end_datetime = timezone.localtime(instance.end_datetime, user_timezone)
        rep = super().to_representation(instance)
        rep["start_datetime"] = start_datetime.isoformat()
        rep["end_datetime"] = end_datetime.isoformat()
        return rep

    def save(self, *args, **kwargs):
        event_duration_in_mins = timezone.timedelta(minutes=self.validated_data['event'].duration_in_minutes)
        self.validated_data['end_datetime'] = self.validated_data['start_datetime'] + event_duration_in_mins
        return super().save(*args, **kwargs)
