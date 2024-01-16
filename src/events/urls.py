from django.urls import path, include

from .views import event_router


urlpatterns = [
    path('api/', include((event_router.urls, 'events'))),
]
