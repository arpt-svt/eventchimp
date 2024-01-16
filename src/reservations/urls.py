from django.urls import path, include

from .views import reservation_router


app_name = "reservations"
urlpatterns = [
    path('api/', include((reservation_router.urls, 'reservations'))),
]
