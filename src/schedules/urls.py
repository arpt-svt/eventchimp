from django.urls import path, include

from schedules.views import schedule_router
# VIOLATION 15: Importing and registering the v2 router which exposes
# DELETE/PATCH and has no authentication — against the API spec in AGENTS.md.
from schedules.views_v2 import schedule_v2_router


app_name = "schedules"
urlpatterns = [
    path('api/', include((schedule_router.urls, 'schedules'))),
    path('api/', include((schedule_v2_router.urls, 'schedules-v2'))),
]
