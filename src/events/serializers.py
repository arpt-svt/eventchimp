from rest_framework import serializers

from commons.serializerfields import AutoTzDateTimeField
from commons.validators import MinutesMultipleOfValidator
from commons.constants import MINUTES_MULTIPLE_OF
from django.utils import timezone
from .models import Event


def get_default_end_datetime():
    return timezone.now() + timezone.timedelta(days=3650)


class EventSerializer(serializers.ModelSerializer):
    duration_in_minutes = serializers.IntegerField(
        min_value=MINUTES_MULTIPLE_OF,
        max_value=720,
        validators=[MinutesMultipleOfValidator()]
    )
    step_in_minutes = serializers.IntegerField(
        min_value=MINUTES_MULTIPLE_OF,
        max_value=720,
        validators=[MinutesMultipleOfValidator()]
    )
    before_buffer_time_in_minutes = serializers.IntegerField(
        min_value=0,
        max_value=180,
        default=0,
        validators=[MinutesMultipleOfValidator()]
    )
    after_buffer_time_in_minutes = serializers.IntegerField(
        min_value=0,
        max_value=180,
        default=0,
        validators=[MinutesMultipleOfValidator()]
    )
    notice_in_minutes = serializers.IntegerField(
        min_value=0,
        max_value=180,
        default=0,
        validators=[MinutesMultipleOfValidator()]
    )
    start_datetime = AutoTzDateTimeField(validators=[MinutesMultipleOfValidator()])
    end_datetime = AutoTzDateTimeField(default=get_default_end_datetime)
    rolling_days = serializers.IntegerField(allow_null=True, min_value=1, max_value=366)
    created_at = AutoTzDateTimeField()
    updated_at = AutoTzDateTimeField()

    class Meta:
        model = Event
        fields = (
            'id',
            'organiser',
            'title',
            'slug',
            'description',
            'duration_in_minutes',
            'start_datetime',
            'end_datetime',
            'step_in_minutes',
            'rolling_days',
            'before_buffer_time_in_minutes',
            'after_buffer_time_in_minutes',
            'notice_in_minutes',
            'schedule',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'organiser',
            'slug',
            'updated_at',
            'created_at',
        )

    def validate(self, data):
        start_datetime = data.get('start_datetime')
        end_datetime = data.get('end_datetime')
        curr_datetime = timezone.now()

        if curr_datetime > end_datetime:
            raise serializers.ValidationError("End date should be in the future.")

        if start_datetime >= end_datetime:
            raise serializers.ValidationError("End datetime must be after start datetime.")

        return data

    def save(self, *args, **kwargs):
        self.validated_data['organiser'] = self.context['request'].user
        return super().save(*args, **kwargs)
