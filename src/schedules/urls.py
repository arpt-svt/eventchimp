from django.urls import path

from schedules.views import schedulecreateapiview


app_name = "schedules"
urlpatterns = [
    path(
        route='schedules',
        view=schedulecreateapiview.ScheduleCreateApiView.as_view(),
        name='create-schedule'
    ),
]
