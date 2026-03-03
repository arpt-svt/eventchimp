import zoneinfo

from django.db import models
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from datetime import time

from commons.enums import Weekday
from .utils import get_datetime_intervals


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

    def get_schedule(self, start_datetime, end_datetime):
        schedules_by_weekday = {}
        for schedule in self.weekday_schedules.values():
            day_of_week = schedule["day_of_week"]
            if day_of_week not in schedules_by_weekday:
                schedules_by_weekday[day_of_week] = []
            schedules_by_weekday[schedule["day_of_week"]].append(schedule)

        # custom_schedules = self.custom_schedules.filter(
        #     start_datetime__lte=end_datetime,
        #     end_datetime__gte=start_datetime
        # )

        datetime_intervals = get_datetime_intervals(
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        schedules = []
        for interval in datetime_intervals:
            day_of_week = interval["day_of_week"]
            if day_of_week in schedules_by_weekday:
                weekday_schedules = schedules_by_weekday[day_of_week]
                for weekday_schedule in weekday_schedules:
                    start_datetime = timezone.datetime.combine(
                        interval["start_datetime"], weekday_schedule["start_time"], zoneinfo.ZoneInfo("utc")
                    )
                    end_datetime = timezone.datetime.combine(
                        interval["start_datetime"], weekday_schedule["end_time"], zoneinfo.ZoneInfo("utc")
                    )
                    if weekday_schedule["end_time"] == time(0, 0):
                        end_datetime += timezone.timedelta(days=1)
                    schedules.append(
                        {
                            "start_datetime": max(start_datetime, interval["start_datetime"]),
                            "end_datetime": min(end_datetime,  interval["end_datetime"])
                        }
                    )

        return schedules


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
