from rest_framework import serializers
from django.utils import timezone

from commons.serializerfields import AutoTzDateTimeField
from commons.enums import WaitlistStatus, WaitlistPriority
from .models import WaitlistEntry, WaitlistConfig


class WaitlistEntrySerializer(serializers.ModelSerializer):
    preferred_start_datetime = AutoTzDateTimeField(required=False, allow_null=True)
    preferred_end_datetime = AutoTzDateTimeField(required=False, allow_null=True)
    created_at = AutoTzDateTimeField(read_only=True)
    updated_at = AutoTzDateTimeField(read_only=True)
    last_notified_at = AutoTzDateTimeField(read_only=True)
    offered_at = AutoTzDateTimeField(read_only=True)
    offer_expires_at = AutoTzDateTimeField(read_only=True)
    position_in_queue = serializers.SerializerMethodField()

    class Meta:
        model = WaitlistEntry
        fields = (
            "id",
            "event",
            "email",
            "full_name",
            "phone",
            "status",
            "priority",
            "position",
            "preferred_start_datetime",
            "preferred_end_datetime",
            "notes",
            "max_wait_days",
            "notification_count",
            "last_notified_at",
            "offered_at",
            "offer_expires_at",
            "position_in_queue",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "position",
            "notification_count",
            "last_notified_at",
            "offered_at",
            "offer_expires_at",
            "is_active",
            "created_at",
            "updated_at",
        )

    def get_position_in_queue(self, obj):
        return obj.calculate_position()

    def validate_email(self, value):
        return value.lower()

    def validate(self, data):
        event = data.get("event")
        email = data.get("email")

        if WaitlistEntry.objects.filter(event=event, email=email, is_active=True).exists():
            raise serializers.ValidationError("This email is already on the waitlist for this event.")

        config = getattr(event, "waitlist_config", None)
        if config and not config.is_enabled:
            raise serializers.ValidationError("Waitlist is not enabled for this event.")

        if config and config.max_size > 0:
            current_count = WaitlistEntry.get_waitlist_count(event.id)
            if current_count >= config.max_size:
                raise serializers.ValidationError("Waitlist is full.")

        preferred_start = data.get("preferred_start_datetime")
        preferred_end = data.get("preferred_end_datetime")
        if preferred_start and preferred_end:
            if preferred_start >= preferred_end:
                raise serializers.ValidationError(
                    "Preferred end datetime must be after preferred start datetime."
                )

        return data

    def save(self, **kwargs):
        event = self.validated_data["event"]
        self.validated_data["position"] = WaitlistEntry.get_waitlist_count(event.id) + 1
        return super().save(**kwargs)


class WaitlistConfigSerializer(serializers.ModelSerializer):
    created_at = AutoTzDateTimeField(read_only=True)
    updated_at = AutoTzDateTimeField(read_only=True)

    class Meta:
        model = WaitlistConfig
        fields = (
            "id",
            "event",
            "is_enabled",
            "max_size",
            "auto_promote",
            "offer_expiry_hours",
            "allow_priority_upgrade",
            "notify_on_join",
            "notify_on_promotion",
            "notify_position_change",
            "admin_email",
            "webhook_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class WaitlistPromoteSerializer(serializers.Serializer):
    entry_id = serializers.IntegerField()
    offer_expiry_hours = serializers.IntegerField(min_value=1, max_value=168, default=24)


class WaitlistBulkActionSerializer(serializers.Serializer):
    entry_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    action = serializers.ChoiceField(choices=["promote", "remove", "notify"])


class WaitlistStatsSerializer(serializers.Serializer):
    total_entries = serializers.IntegerField()
    waiting_count = serializers.IntegerField()
    offered_count = serializers.IntegerField()
    accepted_count = serializers.IntegerField()
    declined_count = serializers.IntegerField()
    expired_count = serializers.IntegerField()
    average_wait_time_hours = serializers.FloatField()
    conversion_rate = serializers.FloatField()
