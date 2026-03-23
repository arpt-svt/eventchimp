from rest_framework import serializers

from commons.serializerfields import AutoTzDateTimeField
from .models import Notification, NotificationTemplate


class NotificationSerializer(serializers.ModelSerializer):
    scheduled_at = AutoTzDateTimeField(required=False, allow_null=True)
    sent_at = AutoTzDateTimeField(read_only=True)
    created_at = AutoTzDateTimeField(read_only=True)
    updated_at = AutoTzDateTimeField(read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "recipient_email",
            "recipient_name",
            "notification_type",
            "channel",
            "status",
            "subject",
            "body",
            "metadata",
            "retry_count",
            "max_retries",
            "error_message",
            "scheduled_at",
            "sent_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "retry_count",
            "error_message",
            "sent_at",
            "created_at",
            "updated_at",
        )


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = (
            "id",
            "name",
            "notification_type",
            "subject",
            "body_text",
            "body_html",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class SendNotificationSerializer(serializers.Serializer):
    recipient_email = serializers.EmailField()
    recipient_name = serializers.CharField(max_length=255, required=False, default="")
    template_name = serializers.CharField(max_length=100)
    context_data = serializers.DictField(required=False, default=dict)
    channel = serializers.CharField(max_length=20, default="EMAIL")
    scheduled_at = AutoTzDateTimeField(required=False, allow_null=True)
