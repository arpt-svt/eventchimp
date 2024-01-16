import zoneinfo
from rest_framework import serializers


class AutoTzDateTimeField(serializers.DateTimeField):
    """
        It picks the timezone from timezone queryparam and
        convert the datetime field to the given timestamp
    """
    def to_representation(self, value):
        query_params = self.context.get('request').query_params
        timezone_param = query_params.get('timezone')
        if timezone_param:
            try:
                user_timezone = zoneinfo.ZoneInfo(timezone_param)
                self.timezone = user_timezone
            except zoneinfo.ZoneInfoNotFoundError:
                pass
        return super().to_representation(value)
