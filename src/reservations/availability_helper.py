import json

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings

from reservations.models import Reservation
from events.models import Event
from commons.utils import merge_datetime_intervals, get_start_of_day


def datetime_serializer(obj):
    if isinstance(obj, timezone.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def get_available_slots(event_id, start_datetime, end_datetime):
    if end_datetime <= start_datetime:
        return []
    q_s, q_e = start_datetime, end_datetime
    event = get_object_or_404(Event, pk=event_id)
    slots_start_datetime = timezone.now() + timezone.timedelta(minutes=event.notice_in_minutes)
    start_datetime = max(
        start_datetime,
        event.start_datetime,
    )
    end_datetime = min(end_datetime, event.end_datetime)
    if event.rolling_days:
        tom = get_start_of_day(timezone.now() + timezone.timedelta(days=1))
        end_datetime = min(end_datetime, tom + timezone.timedelta(days=event.rolling_days))

    before_buffer = event.before_buffer_time_in_minutes
    after_buffer = event.after_buffer_time_in_minutes
    reservations = Reservation.get_active_reservations(
        event_id=event_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    ).values("start_datetime", "end_datetime")
    if before_buffer > 0 or after_buffer > 0:
        reservations = add_buffer_to_reservations(
            reservations=reservations,
            before_buffer_time_in_minutes=before_buffer,
            after_buffer_time_in_minutes=after_buffer
        )

    reservation_neg = get_negation_interval(
        reservations,
        start_datetime,
        end_datetime
    )
    schedules = event.schedule.get_schedule(
        start_datetime,
        end_datetime
    )

    availabilities = find_common_interval(schedules, reservation_neg)
    available_slots = []
    for availability in availabilities:
        available_slots += split_into_slots(
            start_datetime=availability["start_datetime"],
            end_datetime=availability["end_datetime"],
            step_in_minutes=event.step_in_minutes
        )
    if settings.DEBUG:
        debug_data = {
            "q_start": q_s,
            "q_end": q_e,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "event.notice_in_minutes": event.notice_in_minutes,
            "event.rolling_days": event.rolling_days,
            "event.before_buffer_time_in_minutes": event.before_buffer_time_in_minutes,
            "event.after_buffer_time_in_minutes": event.after_buffer_time_in_minutes,
            "reservations": reservations,
            "reservation_neg": reservation_neg,
            "schedules": schedules,
            "availability": availabilities,
            "available_slots": available_slots,
        }
        print(json.dumps(debug_data, default=datetime_serializer, indent=2))
    return list(filter(lambda x: x["start_datetime"] > slots_start_datetime, available_slots))


def get_negation_interval(intervals, min_datetime, max_datetime):
    intervals.sort(key=lambda x: x["start_datetime"])
    negation = []
    curr_start = min_datetime
    for interval in intervals:
        interval_start = interval["start_datetime"]
        if curr_start < interval_start:
            negation.append({
                "start_datetime": curr_start,
                "end_datetime": interval_start
            })
        curr_start = max(curr_start, interval["end_datetime"])
    if curr_start < max_datetime:
        negation.append({
                "start_datetime": curr_start,
                "end_datetime": max_datetime
            })
    return negation


def add_buffer_to_reservations(reservations, before_buffer_time_in_minutes, after_buffer_time_in_minutes):
    reservations_with_buffer = []
    for reservation in reservations:
        reservation["start_datetime"] += timezone.timedelta(minutes=-1*before_buffer_time_in_minutes)
        reservation["end_datetime"] += timezone.timedelta(minutes=1*after_buffer_time_in_minutes)
        reservations_with_buffer.append(
            reservation
        )
    return reservations_with_buffer


def find_common_interval(interval_a, interval_b):
    a_n = len(interval_a)
    b_n = len(interval_b)

    if not a_n or not b_n:
        return []

    i, j = 0, 0
    common_intervals = []
    while i < a_n and j < b_n:
        start = max(interval_a[i]["start_datetime"], interval_b[j]["start_datetime"])
        end = min(interval_a[i]["end_datetime"], interval_b[j]["end_datetime"])
        if start < end:
            common_intervals.append(
                {
                    "start_datetime": start,
                    "end_datetime": end
                }
            )
        if interval_a[i]["end_datetime"] < interval_b[j]["end_datetime"]:
            i += 1
        else:
            j += 1
    return merge_datetime_intervals(common_intervals)


def split_into_slots(start_datetime, end_datetime, step_in_minutes):
    slots = []
    curr_start = start_datetime
    curr_end = curr_start + timezone.timedelta(minutes=step_in_minutes)
    while curr_end <= end_datetime:
        slots.append(
            {
                "start_datetime": curr_start,
                "end_datetime": curr_end,
            }
        )
        curr_start = curr_end
        curr_end = curr_start + timezone.timedelta(minutes=step_in_minutes)
    return slots
