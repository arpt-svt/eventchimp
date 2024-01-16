from rest_framework import viewsets, response, status, routers

from .models import Reservation
from .serializers import ReservationSerializer
from commons.permissions import IsOwner


class ReservationViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options', 'delete')
    serializer_class = ReservationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        event_id = self.request.query_params.get('event_id', None)

        if event_id is not None:
            return Reservation.objects.filter(
                event_id=event_id,
                event__organiser_id=self.request.user
            )

        return Reservation.objects.none()

    def destroy(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation.soft_delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)


reservation_router = routers.DefaultRouter(trailing_slash=False)
reservation_router.register(r'events', ReservationViewSet, basename='reservations')
