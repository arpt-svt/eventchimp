import zoneinfo
from datetime import time

from django.utils import timezone


def convert_weekday_schedules_to_tz(weekday_schedules, src_timezone, target_timezone):
    if not weekday_schedules:
        return
    src_zone = zoneinfo.ZoneInfo(src_timezone)
    target_zone = zoneinfo.ZoneInfo(target_timezone)
    today = timezone.localtime(timezone.now(), src_zone)
    weekday_to_timing_map = {}
    # print(src_zone, target_zone, today)
    for schedule in weekday_schedules:
        if schedule["day_of_week"] not in weekday_to_timing_map:
            weekday_to_timing_map[schedule["day_of_week"]] = []
        weekday_to_timing_map[schedule["day_of_week"]].append((schedule["start_time"], schedule["end_time"]))

    intervals = []
    for i in range(7):
        curr_date = today + timezone.timedelta(days=i)
        weekday = curr_date.weekday()
        if weekday not in weekday_to_timing_map:
            continue

        for start_time, end_time in weekday_to_timing_map[weekday]:
            start_datetime_src = curr_date.replace(
                microsecond=0, second=0, minute=start_time.minute, hour=start_time.hour
            )
            end_datetime_src = curr_date.replace(microsecond=0, second=0, minute=end_time.minute, hour=end_time.hour)
            start_datetime_target = timezone.localtime(start_datetime_src, target_zone)
            end_datetime_target = timezone.localtime(end_datetime_src, target_zone)
            if end_datetime_target <= start_datetime_target:
                end_datetime_target = end_datetime_target + timezone.timedelta(days=1)
            # print("TZ", start_datetime, end_target_tz, start_datetime_target, end_datetime_target, weekday)
            intervals += get_time_intervals(start_datetime_target, end_datetime_target)
    # print(intervals)
    merged_intervals = merge_intervals_by_weekday(intervals)
    return merged_intervals


def get_time_intervals(start_datetime, end_datetime):
    curr_datetime = start_datetime.replace(microsecond=0, second=0, minute=0, hour=0) + timezone.timedelta(days=1)
    intervals = []
    while curr_datetime < end_datetime:
        intervals.append(
            {
                "day_of_week": start_datetime.weekday(),
                "start_time": start_datetime.time(),
                "end_time": time(0, 0)
            }
        )
        start_datetime = curr_datetime
        curr_datetime += timezone.timedelta(days=1)
    intervals.append(
        {
            "day_of_week": start_datetime.weekday(),
            "start_time": start_datetime.time(),
            "end_time": end_datetime.time()
        }
    )
    return intervals


def merge_intervals_by_weekday(intervals):
    intervals_by_weekday = {}
    for interval in intervals:
        day_of_week = interval["day_of_week"]
        if day_of_week not in intervals_by_weekday:
            intervals_by_weekday[day_of_week] = []
        intervals_by_weekday[day_of_week].append(interval)
    merged = []
    for intervals in intervals_by_weekday.values():
        merged += merge_intervals(intervals)

    return merged


def merge_intervals(intervals):
    if len(intervals) <= 1:
        return intervals
    merged = []
    intervals.sort(key=lambda x: x["start_time"])
    for interval in intervals:
        if not merged:
            merged.append(interval)

        if merged[-1]["end_time"] == time(0, 0):
            break

        if merged[-1]["end_time"] < interval["start_time"]:
            merged.append(interval)
        else:
            if interval["end_time"] == time(0, 0) or interval["end_time"] > merged[-1]["end_time"]:
                merged[-1]["end_time"] = interval["end_time"]
    return merged


def convert_custom_date_schedule_to_tz(custom_schedules, src_timezone, target_timezone):
    src_zone = zoneinfo.ZoneInfo(src_timezone)
    target_zone = zoneinfo.ZoneInfo(target_timezone)
    curr_datetime = timezone.localtime(timezone.now(), src_zone)
    updated_schedule = []
    for schedule in custom_schedules:
        start_datetime = timezone.localtime(schedule["start_datetime"], target_zone)
        end_datetime = timezone.localtime(schedule["end_datetime"], target_zone)
        start_time = timezone.localtime(
            value=curr_datetime.replace(
                microsecond=0, second=0, minute=schedule["start_time"].minute, hour=schedule["start_time"].hour
            ),
            timezone=target_zone
        ).time()
        end_time = timezone.localtime(
            value=curr_datetime.replace(
                microsecond=0, second=0, minute=schedule["end_time"].minute, hour=schedule["end_time"].hour
            ),
            timezone=target_zone
        ).time()
        updated_schedule.append({
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "start_time": start_time,
            "end_time": end_time,
        })
    return updated_schedule


def get_datetime_intervals(start_datetime, end_datetime):
    curr_datetime = start_datetime.replace(microsecond=0, second=0, minute=0, hour=0) + timezone.timedelta(days=1)
    intervals = []
    while curr_datetime < end_datetime:
        intervals.append(
            {
                "day_of_week": start_datetime.weekday(),
                "start_datetime": start_datetime,
                "end_datetime": curr_datetime
            }
        )
        start_datetime = curr_datetime
        curr_datetime += timezone.timedelta(days=1)
    intervals.append(
        {
            "day_of_week": start_datetime.weekday(),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime
        }
    )
    return intervals
