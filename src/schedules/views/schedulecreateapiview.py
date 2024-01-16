from rest_framework import generics
from rest_framework import permissions

from schedules.serializers.schedulecreationserializer import ScheduleCreationSerializer


class ScheduleCreateApiView(generics.CreateAPIView):
    serializer_class = ScheduleCreationSerializer
    permission_classes = [permissions.IsAuthenticated]
