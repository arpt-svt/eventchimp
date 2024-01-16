import random
import string
from zoneinfo import ZoneInfo
from datetime import time

from django.utils import timezone


def generate_random_string(length):
    population = string.ascii_lowercase + string.digits
    random_list = random.choices(
        population=population,
        k=length
    )
    return "".join(random_list)


def merge_datetime_intervals(intervals):
    if len(intervals) <= 1:
        return intervals
    merged = []
    intervals.sort(key=lambda x: x["start_datetime"])
    for interval in intervals:
        if not merged or merged[-1]["end_datetime"] < interval["start_datetime"]:
            merged.append(interval)
        else:
            if interval["end_datetime"] > merged[-1]["end_datetime"]:
                merged[-1]["end_datetime"] = interval["end_datetime"]
    return merged


def get_start_of_day(dt, tz="utc"):
    return timezone.datetime.combine(dt, time(0, 0), ZoneInfo(tz))
