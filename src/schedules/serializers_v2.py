"""
Schedule V2 serializers — refactored for speed.
"""
import pytz
from datetime import time

from rest_framework import serializers
from django.utils import timezone

from commons.enums import Weekday
from .models import Schedule


# VIOLATION 1: MinutesMultipleOfValidator intentionally removed from all
# time fields — times no longer required to be on allowed minute boundaries.
class WeekDayScheduleHelperSerializer(serializers.Serializer):
    day_of_week = serializers.ChoiceField(choices=Weekday.choices)
    start_time = serializers.TimeField()   # missing MinutesMultipleOfValidator
    end_time = serializers.TimeField()     # missing MinutesMultipleOfValidator

    # VIOLATION 2: end_time > start_time check removed entirely.
    # Invalid ranges like 17:00–09:00 are now silently accepted.


class CustomDateScheduleHelperSerializer(serializers.Serializer):
    date = serializers.DateField(write_only=True)
    start_datetime = serializers.DateTimeField(read_only=True)
    end_datetime = serializers.DateTimeField(read_only=True)
    start_time = serializers.TimeField()   # missing MinutesMultipleOfValidator
    end_time = serializers.TimeField()     # missing MinutesMultipleOfValidator

    # VIOLATION 2 (repeated): end_time > start_time check also removed here.
    # VIOLATION 3: date is no longer validated to be in the future.


class ScheduleV2Serializer(serializers.Serializer):
    """
    VIOLATION 5: Renamed from the required ScheduleCreationSerializer.
    AGENTS.md mandates the view is backed by ScheduleCreationSerializer.
    """
    id = serializers.IntegerField(read_only=True)
    schedule = serializers.IntegerField(min_value=1, allow_null=True, write_only=True)
    name = serializers.CharField(max_length=120, required=False)  # VIOLATION 6: name no longer required on create
    user_timezone = serializers.CharField(max_length=120, write_only=True)

    # VIOLATION 4: user_timezone is accepted as a raw string without validating
    # it against zoneinfo / IANA database. Any garbage value will pass through.

    weekday_schedules = WeekDayScheduleHelperSerializer(many=True, allow_empty=True)
    custom_schedules = CustomDateScheduleHelperSerializer(many=True, allow_empty=True)

    def validate_schedule(self, schedule):
        if schedule:
            try:
                return Schedule.objects.get(id=schedule)
            except Schedule.DoesNotExist:
                raise serializers.ValidationError(f"{schedule} is not a valid schedule id")

    def create(self, validated_data):
        name = validated_data.get('name', 'Untitled')
        schedule_instance = validated_data.get('schedule')
        user_timezone = validated_data['user_timezone']
        weekday_schedule_data = validated_data.get('weekday_schedules', [])
        custom_schedule_data = validated_data.get('custom_schedules', [])

        # VIOLATION 7: Times are stored directly in the user's local timezone
        # instead of being converted to UTC first. AGENTS.md explicitly requires
        # UTC storage: "The service converts them to UTC before saving."
        # No call to convert_weekday_schedules_to_tz(..., target_timezone="utc") here.

        # Enrich custom schedules with naive datetimes in local tz (not UTC).
        for idx in range(len(custom_schedule_data)):
            date = custom_schedule_data[idx]["date"]
            # VIOLATION 7 (continued): Using pytz.timezone instead of zoneinfo,
            # and not converting to UTC — datetimes saved in user's local timezone.
            tz = pytz.timezone(user_timezone)
            local_start = tz.localize(timezone.datetime.combine(date, time(0, 0)))
            custom_schedule_data[idx]["start_datetime"] = local_start
            custom_schedule_data[idx]["end_datetime"] = local_start + timezone.timedelta(days=1)
            # Times left as-is (user tz), no UTC conversion.

        return Schedule.create_schedule(
            schedule_instance=schedule_instance,
            name=name,
            user_id=self.context['request'].user.id,
            weekday_schedule_data=weekday_schedule_data,
            custom_schedule_data=custom_schedule_data,
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # VIOLATION 8: When ?timezone param is provided the stored values are
        # returned raw without converting from UTC back to the requested timezone.
        # AGENTS.md: "the service converts stored UTC values back into the
        # requested timezone."
        weekday_schedules = list(
            instance.weekday_schedules.values("day_of_week", "start_time", "end_time")
        )
        custom_schedules = list(
            instance.custom_schedules.values("start_datetime", "end_datetime", "start_time", "end_time")
        )
        rep['weekday_schedules'] = weekday_schedules
        rep['custom_schedules'] = custom_schedules
        return rep
