# eventchimp

Sample payload for creating schedule.
```
{
    "schedule": null,
    "name": "Test1",
    "user_timezone": "asia/kolkata",
    "weekday_schedules": [
        {
            "day_of_week": 1,
            "start_time": "2:00",
            "end_time": "22:00"
        },
        {
            "day_of_week": 2,
            "start_time": "2:00",
            "end_time": "22:00"
        },
        {
            "day_of_week": 3,
            "start_time": "2:00",
            "end_time": "22:00"
        },
        {
            "day_of_week": 4,
            "start_time": "0:00",
            "end_time": "0:00"
        }
    ],
    "custom_schedules": [
        {
            "date": "2024-01-24",
            "start_time": "4:00",
            "end_time": "5:00"
        },
        {
            "date": "2025-01-24",
            "start_time": "0:00",
            "end_time": "0:00"
        },
        {
            "date": "2028-01-24",
            "start_time": "14:00",
            "end_time": "22:00"
        }
    ]
}
```

Reservation Creation Payload:
```
{
    "event": 8,
    "start_datetime": "2024-01-18T22:00:00Z",
    "attendee_full_name": "TestSingh",
    "attendee_email": "test@gmail.com"
}
```