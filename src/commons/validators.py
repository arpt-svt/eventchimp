from rest_framework import serializers
from commons.constants import MINUTES_MULTIPLE_OF


class MinutesMultipleOfValidator:
    def __call__(self, value):
        if isinstance(value, int):
            minutes = value
        else:
            minutes = value.minute

        if minutes % MINUTES_MULTIPLE_OF != 0:
            raise serializers.ValidationError("Minutes must be a multiple of {}.".format(MINUTES_MULTIPLE_OF))
