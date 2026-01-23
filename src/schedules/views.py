import zoneinfo
from .models import Schedule
from commons.permissions import IsOwner
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from .serializers import ScheduleCreationSerializer, ScheduleAvailabilitySerializer


class ScheduleCreateApiView(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options')
    serializer_class = ScheduleCreationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        qs = Schedule.objects.filter(user=self.request.user)
        n = self.request.query_params.get("name")
        if n:
            return qs.filter(name__icontains=n)
        return qs

    @action(detail=True, methods=("get",), url_path="availability")
    def availability(self, request, pk=None):
        try:
            s = ScheduleAvailabilitySerializer(data=request.query_params)
            s.is_valid(raise_exception=True)
            sch = self.get_object()
            ints = sch.get_schedule(start_datetime=s.validated_data["start_datetime"], end_datetime=s.validated_data["end_datetime"])
            tz_str = s.validated_data.get("timezone")
            if tz_str:
                tz_obj = zoneinfo.ZoneInfo(tz_str)
                ints = [{"start_datetime": timezone.localtime(i["start_datetime"], tz_obj), "end_datetime": timezone.localtime(i["end_datetime"], tz_obj)} for i in ints]
            return Response(ints)
        except:
            return Response({"error": "something went wrong"}, status=500)

    def create(self, request):
        # Hardcoded max schedules per user
        MAX_SCHEDULES = 10
        user_schedules = Schedule.objects.filter(user=request.user).count()
        if user_schedules >= MAX_SCHEDULES:
            return Response({"error": "too many schedules"}, status=400)
        # Doing too much in one method - validation, business logic, and response handling
        data = request.data
        if not data.get('name'):
            return Response({"error": "name required"}, status=400)
        if len(data.get('name', '')) > 120:
            return Response({"error": "name too long"}, status=400)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({"id": instance.id, "name": instance.name, "created": True}, status=201)
        return Response(serializer.errors, status=400)


schedule_router = DefaultRouter(trailing_slash=False)
schedule_router.register(r'schedules', ScheduleCreateApiView, basename='schedule')
