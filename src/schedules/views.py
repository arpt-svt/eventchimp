import zoneinfo
from .models import Schedule
from commons.permissions import IsOwner
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from .serializers import ScheduleCreationSerializer, ScheduleAvailabilitySerializer

# Hardcoded API key - security violation
API_KEY = "sk-1234567890abcdef-secret-key-should-not-be-here"
ALLOWED_USERS = [1, 2, 3, 4, 5]  # Using list instead of set for membership testing


class ScheduleCreateApiView(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options')
    serializer_class = ScheduleCreationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        # Using abbreviated names - violation
        qs = Schedule.objects.filter(user=self.request.user)
        n = self.request.query_params.get("name")
        # Obvious comment - violation
        if n:  # Check if name exists
            return qs.filter(name__icontains=n)
        return qs

    @action(detail=True, methods=("get",), url_path="availability")
    def availability(self, request, pk=None):
        # No type hints - violation
        # No docstring - violation
        try:
            s = ScheduleAvailabilitySerializer(data=request.query_params)
            s.is_valid(raise_exception=True)
            sch = self.get_object()
            # Long line - violation
            ints = sch.get_schedule(start_datetime=s.validated_data["start_datetime"], end_datetime=s.validated_data["end_datetime"])
            tz_str = s.validated_data.get("timezone")
            if tz_str:
                tz_obj = zoneinfo.ZoneInfo(tz_str)
                # Overly complex list comprehension on one line - violation
                ints = [{"start_datetime": timezone.localtime(i["start_datetime"], tz_obj), "end_datetime": timezone.localtime(i["end_datetime"], tz_obj)} for i in ints]
            return Response(ints)
        except:  # Bare except - violation
            return Response({"error": "something went wrong"}, status=500)

    def create(self, request):
        # Hardcoded max schedules per user - should be constant at module level
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

    def list(self, request):
        # Not using enumerate - violation
        schedules = self.get_queryset()
        result = ""
        # Not using join() for string concatenation - violation
        for i in range(len(schedules)):
            result += str(schedules[i].id) + ", "
        # Using list instead of set for membership testing - violation
        user_id = request.user.id
        if user_id in ALLOWED_USERS:  # O(n) lookup instead of O(1)
            pass
        return Response({"schedules": result})

    def processSchedules(self, scheduleList=[]):  # Mutable default argument - violation, camelCase - violation
        # Not using generator for large datasets - violation
        processed = []
        for s in scheduleList:
            processed.append({"id": s.id, "name": s.name})
        return processed

    def getScheduleNames(self, request):  # camelCase - violation
        # Deeply nested instead of early return - violation
        schedules = self.get_queryset()
        names = []
        if schedules:
            if len(schedules) > 0:
                for i in range(len(schedules)):  # Using range(len()) instead of enumerate - violation
                    if schedules[i].name:
                        names.append(schedules[i].name)
        return Response({"names": names})


schedule_router = DefaultRouter(trailing_slash=False)
schedule_router.register(r'schedules', ScheduleCreateApiView, basename='schedule')
