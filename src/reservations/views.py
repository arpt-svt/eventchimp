from django.utils import timezone
from rest_framework import (
    viewsets,
    response,
    status,
    routers,
    views,
    permissions
)

from commons.permissions import IsOwner
from .models import Reservation
from .availability_helper import get_available_slots
from .serializers import (
    ReservationSerializer,
    AvailabilityRequestSerializer,
)


class ReservationViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options', 'delete')
    serializer_class = ReservationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [IsOwner()]

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


class GetAvailabiltiyApiView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        serializer = AvailabilityRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_timezone = serializer.validated_data["timezone"]
        event_id = serializer.validated_data["event_id"]
        available_slots = get_available_slots(
            event_id=event_id,
            start_datetime=serializer.validated_data["start_datetime"],
            end_datetime=serializer.validated_data["end_datetime"],
        )
        for idx in range(len(available_slots)):
            available_slots[idx]["start_datetime"] = timezone.localtime(
                available_slots[idx]["start_datetime"],
                user_timezone
            )
            available_slots[idx]["end_datetime"] = timezone.localtime(
                available_slots[idx]["end_datetime"],
                user_timezone
            )

        available_slots_by_date = {}
        for slot in available_slots:
            slot_start = slot["start_datetime"]
            slot_start_date = slot_start.date()
            if slot_start.date() not in available_slots_by_date:
                available_slots_by_date[slot_start_date] = []
            available_slots_by_date[slot_start_date].append(slot)

        resp = []
        for slot_date, slots in available_slots_by_date.items():
            resp.append(
                {
                    "date": slot_date,
                    "available_slots": [{"start_datetime": slot["start_datetime"]} for slot in slots]
                }
            )
        return response.Response(resp, status=status.HTTP_200_OK)


reservation_router = routers.DefaultRouter(trailing_slash=False)
reservation_router.register(r'reservations', ReservationViewSet, basename='reservations')
