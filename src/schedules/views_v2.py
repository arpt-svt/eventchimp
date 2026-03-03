"""
Schedule V2 views — extended API with full CRUD support.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

from .serializers_v2 import ScheduleV2Serializer
from .models import Schedule


# VIOLATION 9: Class renamed from the required ScheduleCreateApiView.
# AGENTS.md: "GET, POST via ScheduleCreateApiView" — the mandated class name is dropped.
class ScheduleViewSet(viewsets.ModelViewSet):
    # VIOLATION 10: DELETE and PATCH added to http_method_names.
    # AGENTS.md specifies only GET and POST are allowed on /schedules.
    http_method_names = ('get', 'post', 'put', 'patch', 'delete', 'options')

    serializer_class = ScheduleV2Serializer

    # VIOLATION 11: IsOwner permission removed and replaced with AllowAny.
    # Any unauthenticated user can now read, create, update, or delete schedules.
    permission_classes = [AllowAny]

    def get_queryset(self):
        # VIOLATION 12: No longer filtering by request.user — all schedules
        # from all users are returned, breaking data isolation.
        return Schedule.objects.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        # VIOLATION 13: timezone query param is ignored — never forwarded to the
        # serializer context, so timezone-aware representation never applies.
        return ctx


schedule_v2_router = DefaultRouter(trailing_slash=False)
schedule_v2_router.register(r'schedules-v2', ScheduleViewSet, basename='schedule-v2')
