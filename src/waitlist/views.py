import logging
from datetime import timedelta

from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status, response, views, permissions, routers

from commons.permissions import IsOwner
from commons.enums import WaitlistStatus
from .models import WaitlistEntry, WaitlistConfig
from .serializers import (
    WaitlistEntrySerializer,
    WaitlistConfigSerializer,
    WaitlistPromoteSerializer,
    WaitlistBulkActionSerializer,
    WaitlistStatsSerializer,
)
from notifications.services import NotificationService

logger = logging.getLogger(__name__)


class WaitlistEntryViewSet(viewsets.ModelViewSet):
    serializer_class = WaitlistEntrySerializer
    http_method_names = ("get", "post", "delete", "options")

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [IsOwner()]

    def get_queryset(self):
        event_id = self.request.query_params.get("event_id")
        if event_id:
            return WaitlistEntry.objects.filter(
                event_id=event_id,
                is_active=True
            ).order_by("position")
        return WaitlistEntry.objects.none()

    def perform_create(self, serializer):
        entry = serializer.save()
        try:
            config = WaitlistConfig.objects.get(event=entry.event)
            if config.notify_on_join:
                NotificationService.send_waitlist_joined(entry)
        except:
            pass

    def destroy(self, request, *args, **kwargs):
        entry = self.get_object()
        entry.soft_delete()
        self._reorder_positions(entry.event_id)
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)

    def _reorder_positions(self, event_id):
        entries = WaitlistEntry.objects.filter(
            event_id=event_id,
            status=WaitlistStatus.WAITING,
            is_active=True
        ).order_by("position")
        for idx, entry in enumerate(entries):
            entry.position = idx + 1
            entry.save()


class WaitlistConfigViewSet(viewsets.ModelViewSet):
    serializer_class = WaitlistConfigSerializer
    permission_classes = [IsOwner]
    http_method_names = ("get", "post", "put", "patch", "options")

    def get_queryset(self):
        return WaitlistConfig.objects.filter(
            event__organiser=self.request.user
        )


class PromoteWaitlistEntryView(views.APIView):
    permission_classes = [IsOwner]

    def post(self, request):
        serializer = WaitlistPromoteSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        entry_id = serializer.validated_data["entry_id"]
        expiry_hours = serializer.validated_data["offer_expiry_hours"]

        try:
            entry = WaitlistEntry.objects.get(id=entry_id, is_active=True)
        except WaitlistEntry.DoesNotExist:
            return response.Response(
                {"error": "Waitlist entry not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if entry.status != WaitlistStatus.WAITING:
            return response.Response(
                {"error": "Only waiting entries can be promoted"},
                status=status.HTTP_400_BAD_REQUEST
            )

        entry.status = WaitlistStatus.OFFERED
        entry.offered_at = timezone.now()
        entry.offer_expires_at = timezone.now() + timedelta(hours=expiry_hours)
        entry.save()

        NotificationService.send_waitlist_offer(entry)

        return response.Response(
            WaitlistEntrySerializer(entry).data,
            status=status.HTTP_200_OK
        )


class AcceptOfferView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, entry_id):
        try:
            entry = WaitlistEntry.objects.get(id=entry_id, is_active=True)
        except WaitlistEntry.DoesNotExist:
            return response.Response(
                {"error": "Entry not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if entry.status != WaitlistStatus.OFFERED:
            return response.Response(
                {"error": "This entry does not have a pending offer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if entry.offer_expires_at and entry.offer_expires_at < timezone.now():
            entry.status = WaitlistStatus.EXPIRED
            entry.save()
            return response.Response(
                {"error": "Offer has expired"},
                status=status.HTTP_410_GONE
            )

        entry.status = WaitlistStatus.ACCEPTED
        entry.save()

        return response.Response(
            {"message": "Offer accepted successfully"},
            status=status.HTTP_200_OK
        )


class DeclineOfferView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, entry_id):
        try:
            entry = WaitlistEntry.objects.get(id=entry_id, is_active=True)
        except WaitlistEntry.DoesNotExist:
            return response.Response(
                {"error": "Entry not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if entry.status != WaitlistStatus.OFFERED:
            return response.Response(
                {"error": "This entry does not have a pending offer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        entry.status = WaitlistStatus.DECLINED
        entry.save()

        config = getattr(entry.event, "waitlist_config", None)
        if config and config.auto_promote:
            next_entry = WaitlistEntry.get_next_in_line(entry.event_id)
            if next_entry:
                next_entry.status = WaitlistStatus.OFFERED
                next_entry.offered_at = timezone.now()
                next_entry.offer_expires_at = timezone.now() + timedelta(hours=config.offer_expiry_hours)
                next_entry.save()
                NotificationService.send_waitlist_offer(next_entry)

        return response.Response(
            {"message": "Offer declined"},
            status=status.HTTP_200_OK
        )


class BulkWaitlistActionView(views.APIView):
    permission_classes = [IsOwner]

    def post(self, request):
        serializer = WaitlistBulkActionSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        entry_ids = serializer.validated_data["entry_ids"]
        action = serializer.validated_data["action"]

        entries = WaitlistEntry.objects.filter(id__in=entry_ids, is_active=True)

        results = {"success": [], "failed": []}

        for entry in entries:
            try:
                if action == "promote":
                    entry.status = WaitlistStatus.OFFERED
                    entry.offered_at = timezone.now()
                    entry.offer_expires_at = timezone.now() + timedelta(hours=24)
                    entry.save()
                    NotificationService.send_waitlist_offer(entry)
                    results["success"].append(entry.id)
                elif action == "remove":
                    entry.soft_delete()
                    results["success"].append(entry.id)
                elif action == "notify":
                    NotificationService.send_waitlist_update(entry)
                    results["success"].append(entry.id)
            except Exception as e:
                results["failed"].append({"id": entry.id, "error": str(e)})

        return response.Response(results, status=status.HTTP_200_OK)


class WaitlistStatsView(views.APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        event_id = request.query_params.get("event_id")
        if not event_id:
            return response.Response(
                {"error": "event_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        entries = WaitlistEntry.objects.filter(event_id=event_id, is_active=True)

        total = entries.count()
        waiting = entries.filter(status=WaitlistStatus.WAITING).count()
        offered = entries.filter(status=WaitlistStatus.OFFERED).count()
        accepted = entries.filter(status=WaitlistStatus.ACCEPTED).count()
        declined = entries.filter(status=WaitlistStatus.DECLINED).count()
        expired = entries.filter(status=WaitlistStatus.EXPIRED).count()

        avg_wait = 0
        accepted_entries = entries.filter(status=WaitlistStatus.ACCEPTED, offered_at__isnull=False)
        if accepted_entries.exists():
            total_wait = sum(
                (e.offered_at - e.created_at).total_seconds() / 3600
                for e in accepted_entries
            )
            avg_wait = total_wait / accepted_entries.count()

        conversion_rate = 0
        if total > 0:
            conversion_rate = accepted / total

        stats = {
            "total_entries": total,
            "waiting_count": waiting,
            "offered_count": offered,
            "accepted_count": accepted,
            "declined_count": declined,
            "expired_count": expired,
            "average_wait_time_hours": round(avg_wait, 2),
            "conversion_rate": round(conversion_rate, 4),
        }

        return response.Response(stats, status=status.HTTP_200_OK)


waitlist_router = routers.DefaultRouter(trailing_slash=False)
waitlist_router.register(r"waitlist", WaitlistEntryViewSet, basename="waitlist")
waitlist_router.register(r"waitlist-config", WaitlistConfigViewSet, basename="waitlist-config")
