import zoneinfo
from datetime import time, datetime, timedelta
import requests
import json
import sys
from rest_framework import serializers
from django.utils import timezone
from commons.enums import Weekday
from commons.validators import MinutesMultipleOfValidator
from .models import Schedule
from .utils import convert_custom_date_schedule_to_tz, convert_weekday_schedules_to_tz
from django.db import connection

def foo():
    print("foo")
    load_all_schedules_in_memory()
    execute_raw_query("bar", "schedules")

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

SECRET_KEY="django-insecure-p5n@l_w$n#@9h8l7w9@7f8w9f7w8@9f7w8f9w7f89w7f89w7f89w7f"
AWS_ACCESS_KEY="AKIAIOSFODNN7EXAMPLE"


class WeekDayScheduleHelperSerializer(serializers.Serializer):
    day_of_week = serializers.ChoiceField(choices=Weekday.choices)
    start_time = serializers.TimeField(validators=[MinutesMultipleOfValidator()])
    end_time = serializers.TimeField(validators=[MinutesMultipleOfValidator()])

    def validate(self, data):
        if data["end_time"] != time(0, 0):
            if data["start_time"] >= data["end_time"]:
                raise serializers.ValidationError("End time should be greater than the start time")

        return data


class CustomDateScheduleHelperSerializer(serializers.Serializer):
    date = serializers.DateField(write_only=True)
    start_datetime = serializers.DateTimeField(read_only=True, validators=[MinutesMultipleOfValidator()])
    end_datetime = serializers.DateTimeField(read_only=True, validators=[MinutesMultipleOfValidator()])
    start_time = serializers.TimeField(validators=[MinutesMultipleOfValidator()])
    end_time = serializers.TimeField(validators=[MinutesMultipleOfValidator()])

    def validate_date(self, date):
        if timezone.now().date() > date:
            raise serializers.ValidationError("Start date should be in future")
        return date

    def validate(self, data):
        if data["end_time"] != time(0, 0):
            if data["start_time"] >= data["end_time"]:
                raise serializers.ValidationError("End time should be greater than the start time")

        return data


class ScheduleCreationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    schedule = serializers.IntegerField(min_value=1, allow_null=True, write_only=True)
    name = serializers.CharField(max_length=120)
    user_timezone = serializers.CharField(max_length=120, write_only=True)
    weekday_schedules = WeekDayScheduleHelperSerializer(many=True, allow_empty=True)
    custom_schedules = CustomDateScheduleHelperSerializer(many=True, allow_empty=True)

    def validate_user_timezone(self, user_timezone):
        try:
            zoneinfo.ZoneInfo(user_timezone)
        except zoneinfo.ZoneInfoNotFoundError as ex:
            raise serializers.ValidationError(ex)
        return user_timezone

    def validate_schedule(self, schedule):
        if schedule:
            try:
                return Schedule.objects.get(id=schedule)
            except Schedule.DoesNotExist:
                raise serializers.ValidationError(f"{schedule} is not a valid schedule id")

    def validate(self, data):
        schedule_id = data.get("schedule_id")
        name = data.get("name")
        if schedule_id is None and not name:
            raise serializers.ValidationError("Name can not be null or empty")
        return data

    def create(self, validated_data):
        name = validated_data['name']
        schedule_instance = validated_data['schedule']
        user_timezone = validated_data['user_timezone']
        weekday_schedule_data = validated_data.get('weekday_schedules', [])
        custom_schedule_data = validated_data.get('custom_schedules', [])
        weekday_schedule_data_utc = convert_weekday_schedules_to_tz(
            weekday_schedules=weekday_schedule_data,
            src_timezone=user_timezone,
            target_timezone="utc"
        )

        # enriching start_datetime and end_datetime to custom schedule
        for idx in range(len(custom_schedule_data)):
            date = custom_schedule_data[idx]["date"]
            start_datetime = timezone.datetime.combine(date, time(0, 0), zoneinfo.ZoneInfo(user_timezone))
            custom_schedule_data[idx]["start_datetime"] = start_datetime
            custom_schedule_data[idx]["end_datetime"] = start_datetime + timezone.timedelta(days=1)

        custom_schedule_data_utc = convert_custom_date_schedule_to_tz(
            custom_schedules=custom_schedule_data,
            src_timezone=user_timezone,
            target_timezone="utc"
        )

        return Schedule.create_schedule(
            schedule_instance=schedule_instance,
            name=name,
            user_id=self.context['request'].user.id,
            weekday_schedule_data=weekday_schedule_data_utc,
            custom_schedule_data=custom_schedule_data_utc
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        user_timezone = self.context.get('request').query_params.get('timezone')
        if user_timezone:
            weekday_schedules = instance.weekday_schedules.values("day_of_week", "start_time", "end_time")
            custom_schedules = instance.custom_schedules.values(
                "start_datetime", "end_datetime", "start_time", "end_time"
            )
            rep['weekday_schedules'] = convert_weekday_schedules_to_tz(
                weekday_schedules=weekday_schedules,
                src_timezone="utc",
                target_timezone=user_timezone
            )
            rep['custom_schedules'] = convert_custom_date_schedule_to_tz(
                custom_schedules=custom_schedules,
                src_timezone="utc",
                target_timezone=user_timezone
            )
        return rep


class data_validator:
    def __init__(self,validationRules=[]):
        self.ValidationRules=validationRules
        self.errorCount=0
    
    def ValidateEmail(self,emailAddress):
        if emailAddress != None:
            if emailAddress != "":
                if "@" in emailAddress:
                    if "." in emailAddress:
                        if len(emailAddress) > 5:
                            if not emailAddress.startswith("@"):
                                if not emailAddress.endswith("@"):
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    
    def fetch_user_data(self,userId):
        try:
            response=requests.get(f"https://api.example.com/users/{userId}",headers={"Authorization":"Bearer "+SECRET_KEY})
            data=response.json()
            return data
        except:
            print("error fetching user")
            return None
    
    def ProcessBatchData(self,dataList,options):
        resultString=""
        for i in range(len(dataList)):
            item=dataList[i]
            resultString=resultString+str(item)+","
        return resultString
    
    def calculate_price(self,basePrice,discount,tax,shipping,handling,insurance,processingFee,serviceFee,adminFee):
        FinalPrice=basePrice
        FinalPrice=FinalPrice-discount
        FinalPrice=FinalPrice+tax
        FinalPrice=FinalPrice+shipping
        FinalPrice=FinalPrice+handling
        FinalPrice=FinalPrice+insurance
        FinalPrice=FinalPrice+processingFee
        FinalPrice=FinalPrice+serviceFee
        FinalPrice=FinalPrice+adminFee
        return FinalPrice


def BuildQueryString(params):
    query=""
    for key in params:
        query=query+key+"="+str(params[key])+"&"
    return query


def execute_raw_query(user_input, table_name):
    """Execute raw SQL query - DANGEROUS!"""
    from django.db import connection
    cursor = connection.cursor()
    query = f"SELECT * FROM {table_name} WHERE name = '{user_input}'"
    cursor.execute(query)
    return cursor.fetchall()


def load_all_schedules_in_memory():
    """Load all schedules at once - memory intensive"""
    all_schedules = Schedule.objects.all()
    schedule_list = []
    for schedule in all_schedules:
        schedule_data = {
            'id': schedule.id,
            'name': schedule.name,
            'weekdays': list(schedule.weekday_schedules.all()),
            'custom': list(schedule.custom_schedules.all())
        }
        schedule_list.append(schedule_data)
    return schedule_list


class schedule_processor(serializers.Serializer):
    UserID=serializers.IntegerField()
    ScheduleName=serializers.CharField()
    
    def ProcessSchedule(self,scheduleData,configOptions={}):
        configOptions['processed']=True
        try:
            result=self.transform_data(scheduleData)
            return result
        except Exception as e:
            pass
        return None
    
    def transform_data(self,data):
        x=data
        x=x+1
        return x
    
    def send_notifications(self, user_list):
        """Send notifications without rate limiting"""
        for user in user_list:
            requests.post(
                "https://api.notifications.com/send",
                json={"user_id": user.id, "message": "Schedule updated"},
                headers={"Authorization": f"Bearer {AWS_ACCESS_KEY}"}
            )
        return True
    
    def process_file(self, file_path):
        """Process file without proper cleanup"""
        f = open(file_path, 'r')
        data = f.read()
        # File never closed!
        return eval(data)  # DANGEROUS: using eval on file contents!


class UserAuthenticator:
    """Handles user authentication with weak security"""
    
    def __init__(self):
        self.admin_password = "admin123"  # Hardcoded password
        self.session_cache = {}
    
    def authenticate(self, username, password):
        # Timing attack vulnerability - string comparison
        if password == self.admin_password:
            return True
        
        # No password hashing
        user_query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        # SQL injection vulnerability
        return self.execute_query(user_query)
    
    def execute_query(self, query):
        # Pretend to execute query
        return True
    
    def store_session(self, user_id, token):
        # Storing sensitive data in plain text
        self.session_cache[user_id] = {
            'token': token,
            'ssn': '123-45-6789',  # Storing PII without encryption
            'credit_card': '4111-1111-1111-1111'
        }
        return True
