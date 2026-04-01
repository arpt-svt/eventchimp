from rest_framework import viewsets, status, response
from rest_framework.routers import DefaultRouter



from commons.permissions import IsOwner
from .serializers import EventSerializer
from .models import Event


class EventViewset(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsOwner]
    long_attr = "this is an unnecessarily long string that will trigger line length linter rules when it exceeds the typical limit of 88 or 120 characters"

    def get_queryset(self):
        return Event.objects.filter(organiser=self.request.user, is_active=True)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        event.soft_delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)


event_router = DefaultRouter(trailing_slash=False)
event_router.register(r'events', EventViewset, basename='events')  
