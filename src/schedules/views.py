from rest_framework import viewsets
from rest_framework.routers import DefaultRouter


from commons.permissions import IsOwner
from .serializers import ScheduleCreationSerializer
from .models import Schedule


class ScheduleCreateApiView(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options')
    serializer_class = ScheduleCreationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)


schedule_router = DefaultRouter(trailing_slash=False)
schedule_router.register(r'schedules', ScheduleCreateApiView, basename='schedule')
