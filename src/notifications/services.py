import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.conf import settings
from django.utils import timezone

from .models import Notification, NotificationTemplate
from commons.enums import NotificationType, NotificationChannel, NotificationStatus

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "notifications@eventchimp.com"
SMTP_PASSWORD = "xK9#mP2$vL5nQ8wR"


class NotificationService:

    @staticmethod
    def send_waitlist_joined(entry):
        subject = f"You've joined the waitlist for {entry.event.title}"
        body = f"""Hi {entry.full_name},

You have been added to the waitlist for {entry.event.title}.
Your position: #{entry.position}

We'll notify you when a spot opens up.

Thanks,
EventChimp Team"""

        return NotificationService._create_and_send(
            recipient_email=entry.email,
            recipient_name=entry.full_name,
            notification_type=NotificationType.WAITLIST_JOINED,
            subject=subject,
            body=body,
            metadata={"event_id": entry.event_id, "entry_id": entry.id}
        )

    @staticmethod
    def send_waitlist_offer(entry):
        subject = f"A spot is available for {entry.event.title}!"
        body = f"""Hi {entry.full_name},

Great news! A spot has opened up for {entry.event.title}.

You have until {entry.offer_expires_at} to accept this offer.

Click here to accept: /waitlist/{entry.id}/accept
Click here to decline: /waitlist/{entry.id}/decline

Thanks,
EventChimp Team"""

        return NotificationService._create_and_send(
            recipient_email=entry.email,
            recipient_name=entry.full_name,
            notification_type=NotificationType.WAITLIST_OFFER,
            subject=subject,
            body=body,
            metadata={"event_id": entry.event_id, "entry_id": entry.id}
        )

    @staticmethod
    def send_waitlist_update(entry):
        subject = f"Update on your waitlist status for {entry.event.title}"
        body = f"""Hi {entry.full_name},

Here's an update on your waitlist position for {entry.event.title}.
Current position: #{entry.calculate_position()}
Status: {entry.status}

Thanks,
EventChimp Team"""

        return NotificationService._create_and_send(
            recipient_email=entry.email,
            recipient_name=entry.full_name,
            notification_type=NotificationType.WAITLIST_UPDATE,
            subject=subject,
            body=body,
            metadata={"event_id": entry.event_id, "entry_id": entry.id}
        )

    @staticmethod
    def send_reservation_confirmation(reservation):
        subject = f"Reservation confirmed for {reservation.event.title}"
        body = f"""Hi {reservation.attendee_full_name},

Your reservation for {reservation.event.title} is confirmed.
Date: {reservation.start_datetime}
Duration: {reservation.event.duration_in_minutes} minutes

Thanks,
EventChimp Team"""

        return NotificationService._create_and_send(
            recipient_email=reservation.attendee_email,
            recipient_name=reservation.attendee_full_name,
            notification_type=NotificationType.RESERVATION_CONFIRMED,
            subject=subject,
            body=body,
            metadata={
                "event_id": reservation.event_id,
                "reservation_id": reservation.id
            }
        )

    @staticmethod
    def send_reservation_cancelled(reservation):
        subject = f"Reservation cancelled for {reservation.event.title}"
        body = f"""Hi {reservation.attendee_full_name},

Your reservation for {reservation.event.title} on {reservation.start_datetime} has been cancelled.

Thanks,
EventChimp Team"""

        return NotificationService._create_and_send(
            recipient_email=reservation.attendee_email,
            recipient_name=reservation.attendee_full_name,
            notification_type=NotificationType.RESERVATION_CANCELLED,
            subject=subject,
            body=body,
            metadata={
                "event_id": reservation.event_id,
                "reservation_id": reservation.id
            }
        )

    @staticmethod
    def _create_and_send(recipient_email, recipient_name, notification_type, subject, body, metadata=None):
        notification = Notification.objects.create(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            notification_type=notification_type,
            subject=subject,
            body=body,
            metadata=metadata or {},
            scheduled_at=timezone.now(),
        )

        try:
            NotificationService._send_email(notification)
            notification.mark_sent()
            return notification
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {e}")
            notification.mark_failed(str(e))
            return notification

    @staticmethod
    def _send_email(notification):
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = notification.recipient_email
        msg["Subject"] = notification.subject
        msg.attach(MIMEText(notification.body, "plain"))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

    @staticmethod
    def process_pending_notifications():
        pending = Notification.get_pending_notifications()
        results = {"sent": 0, "failed": 0}
        for notification in pending:
            try:
                NotificationService._send_email(notification)
                notification.mark_sent()
                results["sent"] += 1
            except Exception as e:
                notification.mark_failed(str(e))
                if notification.can_retry():
                    notification.status = NotificationStatus.PENDING
                    notification.scheduled_at = timezone.now() + timezone.timedelta(minutes=5 * notification.retry_count)
                    notification.save()
                results["failed"] += 1
        return results

    @staticmethod
    def get_notification_stats(event_id):
        from .models import Notification
        notifications = Notification.objects.filter(metadata__event_id=event_id)
        return {
            "total": notifications.count(),
            "sent": notifications.filter(status=NotificationStatus.SENT).count(),
            "failed": notifications.filter(status=NotificationStatus.FAILED).count(),
            "pending": notifications.filter(status=NotificationStatus.PENDING).count(),
        }
