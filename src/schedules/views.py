import zoneinfo

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter


from commons.permissions import IsOwner
from .serializers import ScheduleCreationSerializer, ScheduleAvailabilitySerializer
from .models import Schedule


class ScheduleCreateApiView(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options')
    serializer_class = ScheduleCreationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = Schedule.objects.filter(user=self.request.user)
        name = self.request.query_params.get("name")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset

    @action(detail=True, methods=("get",), url_path="availability")
    def availability(self, request, pk=None):
        serializer = ScheduleAvailabilitySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        schedule = self.get_object()
        intervals = schedule.get_schedule(
            start_datetime=serializer.validated_data["start_datetime"],
            end_datetime=serializer.validated_data["end_datetime"],
        )
        response_timezone = serializer.validated_data.get("timezone")
        if response_timezone:
            tz = zoneinfo.ZoneInfo(response_timezone)
            intervals = [
                {
                    "start_datetime": timezone.localtime(interval["start_datetime"], tz),
                    "end_datetime": timezone.localtime(interval["end_datetime"], tz),
                }
                for interval in intervals
            ]
        return Response(intervals)


schedule_router = DefaultRouter(trailing_slash=False)
schedule_router.register(r'schedules', ScheduleCreateApiView, basename='schedule')
