from django.urls import path, include

from .views import reservation_router, GetAvailabiltiyApiView, ReservationICSView


app_name = "reservations"
urlpatterns = [
    path('api/', include((reservation_router.urls, 'reservations'))),
    path('api/availabilities', GetAvailabiltiyApiView.as_view()),
    path('api/reservations/<int:pk>/ics/', ReservationICSView.as_view(), name='reservation-ics'),
]
