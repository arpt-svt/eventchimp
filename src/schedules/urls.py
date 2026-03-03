from django.urls import path, include

from schedules.views import schedule_router
from schedules.views_v2 import schedule_v2_router


app_name = "schedules"
urlpatterns = [
    path('api/', include((schedule_router.urls, 'schedules'))),
    path('api/', include((schedule_v2_router.urls, 'schedules-v2'))),
]
