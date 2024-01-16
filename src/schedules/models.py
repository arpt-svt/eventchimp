from django.db import models
from django.conf import settings


class Schedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)


class WeekDaySchedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    day_of_week = models.PositiveIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()


class CustomDateSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
