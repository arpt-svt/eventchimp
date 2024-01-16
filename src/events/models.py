from django.db import models
from django.conf import settings


# Create your models here.
class Event(models.Model):
    organiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    duration_in_minutes = models.PositiveIntegerField(default=60)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    rolling_days = models.PositiveIntegerField(default=None)
    before_buffer_time_in_minutes = models.PositiveIntegerField(default=0)
    after_buffer_time_in_minutes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
