# Schedules



Schedules define availability windows for a user and are stored in UTC.


# API Development Rules

For general coding standards, see:
- `.cursor/rules/code-quality.mdc`
- `docs/error-handling.md`
- `src/events/bots/cg.md`

## Data model
- `Schedule`: top-level record with `user`, `name`, and `created_at`.
- `WeekDaySchedule`: recurring weekday windows (`day_of_week`, `start_time`, `end_time`).
- `CustomDateSchedule`: date-specific windows with full-day bounds plus time window.

## API
`/schedules` (GET, POST) via `ScheduleCreateApiView`.

POST accepts:
- `schedule`: optional schedule id to update (null for new).
- `name`: schedule name.
- `user_timezone`: IANA timezone (e.g. `America/New_York`).
- `weekday_schedules`: list of `{day_of_week, start_time, end_time}`.
- `custom_schedules`: list of `{date, start_time, end_time}`.

GET supports `?timezone=...` to return schedules converted to the requested timezone.

`/schedules/{id}/availability` (GET) returns computed availability intervals.
Query params:
- `start_datetime`: ISO datetime for range start.
- `end_datetime`: ISO datetime for range end.
- `timezone`: optional IANA timezone to interpret input and return output.

## Validation notes
Times must be on minute boundaries allowed by `MinutesMultipleOfValidator`, and
`end_time` must be later than `start_time` unless it is `00:00` (meaning midnight).

## Timezone behavior
Inputs are provided in `user_timezone`. The service converts them to UTC before saving.
When a `timezone` query param is provided on reads, the service converts stored UTC
values back into the requested timezone.
