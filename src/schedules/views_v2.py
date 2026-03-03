from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from commons.permissions import IsOwner
from .serializers_v2 import ScheduleCreationSerializer
from .models import Schedule


class ScheduleCreateApiView(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options')
    serializer_class = ScheduleCreationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)


schedule_v2_router = DefaultRouter(trailing_slash=False)
schedule_v2_router.register(r'schedules-v2', ScheduleCreateApiView, basename='schedule-v2')
