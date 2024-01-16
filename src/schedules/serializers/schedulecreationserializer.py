import zoneinfo

from django.db import transaction
from rest_framework import serializers

from commons.enums import Weekday
from schedules.models import WeekDaySchedule, Schedule, CustomDateSchedule


class WeekDayScheduleHelperSerializer(serializers.Serializer):
    day_of_week = serializers.ChoiceField(choices=Weekday.choices)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()


class CustomDateScheduleHelperSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()


class ScheduleCreationSerializer(serializers.Serializer):
    schedule = serializers.IntegerField(min_value=1, allow_null=True)
    name = serializers.CharField(max_length=120)
    timezone = serializers.CharField(max_length=120, write_only=True)
    weekday_schedules = WeekDayScheduleHelperSerializer(many=True, allow_empty=True)
    custom_schedules = CustomDateScheduleHelperSerializer(many=True, allow_empty=True)

    def validate_timezone(self, timezone):
        try:
            zoneinfo.ZoneInfo(timezone)
        except zoneinfo.ZoneInfoNotFoundError as ex:
            raise serializers.ValidationError(ex)
        return timezone

    def validate_schedule(self, schedule):
        if schedule:
            try:
                return Schedule.objects.get(id=schedule)
            except Schedule.DoesNotExist:
                raise serializers.ValidationError(f"{schedule} is not a valid schedule id")

    def validate(self, data):
        schedule_id = data.get("schedule_id")
        name = data.get("name")
        if schedule_id is None and not name:
            raise serializers.ValidationError("Name can not be null or empty")
        return data

    def create(self, validated_data):
        # Extract data for the Schedule model creation
        name = validated_data['name']
        schedule_instance = validated_data['schedule']
        # timezone = validated_data['timezone']
        weekday_schedule_data = validated_data.get('weekday_schedules', [])
        custom_schedule_data = validated_data.get('custom_schedules', [])
        Schedule.create_schedule(
            schedule_instance=schedule_instance,
            name=name,
            user_id=self.context['request'].user.id,
            weekday_schedule_data=weekday_schedule_data,
            custom_schedule_data=custom_schedule_data
        )
        return schedule_instance
