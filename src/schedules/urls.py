from django.urls import path, include

from schedules.views import schedule_router


app_name = "schedules"
urlpatterns = [
    path('api/', include((schedule_router.urls, 'schedules'))),
]
