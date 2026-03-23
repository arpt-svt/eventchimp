from django.urls import path, include

from .views import (
    notification_router,
    SendNotificationView,
    ProcessPendingNotificationsView,
    NotificationStatsView,
)


app_name = "notifications"
urlpatterns = [
    path("api/", include((notification_router.urls, "notifications"))),
    path("api/notifications/send", SendNotificationView.as_view()),
    path("api/notifications/process-pending", ProcessPendingNotificationsView.as_view()),
    path("api/notifications/stats", NotificationStatsView.as_view()),
]
