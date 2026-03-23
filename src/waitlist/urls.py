from django.urls import path, include

from .views import (
    waitlist_router,
    PromoteWaitlistEntryView,
    AcceptOfferView,
    DeclineOfferView,
    BulkWaitlistActionView,
    WaitlistStatsView,
)


app_name = "waitlist"
urlpatterns = [
    path("api/", include((waitlist_router.urls, "waitlist"))),
    path("api/waitlist/promote", PromoteWaitlistEntryView.as_view()),
    path("api/waitlist/<int:entry_id>/accept", AcceptOfferView.as_view()),
    path("api/waitlist/<int:entry_id>/decline", DeclineOfferView.as_view()),
    path("api/waitlist/bulk-action", BulkWaitlistActionView.as_view()),
    path("api/waitlist/stats", WaitlistStatsView.as_view()),
]
