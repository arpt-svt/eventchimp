from django.db import models
from django.db import transaction
from django.conf import settings

from commons.enums import Weekday


class Schedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_owner_id(self):
        return self.user_id

    @classmethod
    @transaction.atomic
    def create_schedule(
        cls,
        schedule_instance,
        name,
        user_id,
        weekday_schedule_data,
        custom_schedule_data
    ):
        if not schedule_instance:
            schedule_instance = Schedule.objects.create(
                user_id=user_id,
                name=name
            )
        else:
            schedule_instance.weekday_schedules.all().delete()
            schedule_instance.custom_schedules.all().delete()

        WeekDaySchedule.objects.bulk_create([
                WeekDaySchedule(schedule=schedule_instance, **data)
                for data in weekday_schedule_data
            ])

        CustomDateSchedule.objects.bulk_create([
            CustomDateSchedule(schedule=schedule_instance, **data)
            for data in custom_schedule_data
        ])
        return schedule_instance


class WeekDaySchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='weekday_schedules')
    day_of_week = models.PositiveIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()


class CustomDateSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='custom_schedules')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
