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

Do not add fields to these models that are not listed above. Any new field requires
an explicit update to this document and a reviewed migration.

## API

### V1 — `/schedules`
`/schedules` (GET, POST) via `ScheduleCreateApiView` in `schedules/views.py`.

### V2 — `/schedules-v2`
`/schedules-v2` (GET, POST) via `ScheduleCreateApiView` in `schedules/views_v2.py`.

Both versions share the same serializer (`ScheduleCreationSerializer`) and enforce
identical validation and timezone rules described below.

POST accepts:
- `schedule`: optional schedule id to update (null for new).
- `name`: schedule name (required when creating a new schedule).
- `user_timezone`: IANA timezone (e.g. `America/New_York`).
- `weekday_schedules`: list of `{day_of_week, start_time, end_time}`.
- `custom_schedules`: list of `{date, start_time, end_time}`.

GET supports `?timezone=...` to return schedules converted to the requested timezone.

Only GET, POST, and OPTIONS are permitted. DELETE, PATCH, and PUT must not be
exposed on these endpoints.

`/schedules/{id}/availability` (GET) returns computed availability intervals.
Query params:
- `start_datetime`: ISO datetime for range start.
- `end_datetime`: ISO datetime for range end.
- `timezone`: optional IANA timezone to interpret input and return output.

## Serializer rules
- Both v1 and v2 must use `ScheduleCreationSerializer` as the `serializer_class`.
- Do not rename or subclass the serializer without updating this document.

## Validation notes
Times must be on minute boundaries allowed by `MinutesMultipleOfValidator`, and
`end_time` must be later than `start_time` unless it is `00:00` (meaning midnight).

`user_timezone` must be validated against the `zoneinfo` database
(`zoneinfo.ZoneInfo(user_timezone)`) before use. Reject unknown timezone strings
with a 400 error.

`date` on custom schedules must be today or in the future.

## Timezone behavior
Inputs are provided in `user_timezone`. The service converts them to UTC before saving.
Use `zoneinfo` (stdlib) for all timezone handling — do not use `pytz`.
When a `timezone` query param is provided on reads, the service converts stored UTC
values back into the requested timezone via `convert_weekday_schedules_to_tz` and
`convert_custom_date_schedule_to_tz` from `schedules/utils.py`.

## Permissions
All schedule views must use `IsOwner` from `commons.permissions`.
- `has_permission`: user must be authenticated.
- `has_object_permission`: `obj.get_owner_id()` must equal `request.user.id`.

`get_queryset` must always filter by `user=request.user` to prevent cross-user
data leakage.
