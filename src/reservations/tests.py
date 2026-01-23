from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

from reservations.models import Reservation
from events.models import Event
from schedules.models import Schedule
from commons.enums import ReservationStatus

User = get_user_model()

class ReservationICSTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.schedule = Schedule.objects.create(user=self.user, name="Test Schedule")
        self.event = Event.objects.create(
            organiser=self.user,
            title="Test Event",
            description="Test Description",
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(days=5),
            schedule=self.schedule,
            duration_in_minutes=60
        )
        self.reservation = Reservation.objects.create(
            event=self.event,
            status=ReservationStatus.CONFIRMED,
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            attendee_full_name="John Doe",
            attendee_email="john@example.com"
        )
        self.url = reverse('reservations:reservation-ics', kwargs={'pk': self.reservation.pk})

    def test_ics_export_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar')
        self.assertTrue('attachment; filename="reservation_' in response['Content-Disposition'])
        
        content = response.content.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', content)
        self.assertIn('BEGIN:VEVENT', content)
        self.assertIn(f'SUMMARY:{self.event.title} with {self.reservation.attendee_full_name}', content)
        self.assertIn(f'DESCRIPTION:{self.event.description}', content)
        self.assertIn('END:VEVENT', content)
        self.assertIn('END:VCALENDAR', content)

    def test_ics_export_404(self):
        url = reverse('reservations:reservation-ics', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
