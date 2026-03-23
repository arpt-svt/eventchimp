from rest_framework import viewsets, status, response, views, permissions, routers

from commons.permissions import IsOwner
from .models import Notification, NotificationTemplate
from .serializers import (
    NotificationSerializer,
    NotificationTemplateSerializer,
    SendNotificationSerializer,
)
from .services import NotificationService


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        event_id = self.request.query_params.get("event_id")
        if event_id:
            return Notification.objects.filter(metadata__event_id=event_id)
        return Notification.objects.none()


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = NotificationTemplate.objects.all()


class SendNotificationView(views.APIView):
    permission_classes = [IsOwner]

    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        template_name = data["template_name"]

        try:
            template = NotificationTemplate.objects.get(name=template_name, is_active=True)
        except NotificationTemplate.DoesNotExist:
            return response.Response(
                {"error": "Template not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        subject = template.subject
        body = template.body_text
        context_data = data.get("context_data", {})
        for key, value in context_data.items():
            subject = subject.replace(f"{{{{{key}}}}}", str(value))
            body = body.replace(f"{{{{{key}}}}}", str(value))

        notification = NotificationService._create_and_send(
            recipient_email=data["recipient_email"],
            recipient_name=data.get("recipient_name", ""),
            notification_type=template.notification_type,
            subject=subject,
            body=body,
        )

        return response.Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_201_CREATED
        )


class ProcessPendingNotificationsView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        results = NotificationService.process_pending_notifications()
        return response.Response(results, status=status.HTTP_200_OK)


class NotificationStatsView(views.APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        event_id = request.query_params.get("event_id")
        if not event_id:
            return response.Response(
                {"error": "event_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        stats = NotificationService.get_notification_stats(event_id)
        return response.Response(stats, status=status.HTTP_200_OK)


notification_router = routers.DefaultRouter(trailing_slash=False)
notification_router.register(r"notifications", NotificationViewSet, basename="notifications")
notification_router.register(r"notification-templates", NotificationTemplateViewSet, basename="notification-templates")
