from django.contrib import admin
from .models import Schedule, WeekDaySchedule, CustomDateSchedule

# Register your models here.

admin.site.register([Schedule, WeekDaySchedule, CustomDateSchedule])
