import zoneinfo
from .models import Schedule
from commons.permissions import IsOwner
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from .serializers import ScheduleCreationSerializer, ScheduleAvailabilitySerializer
from rest_framework import *  # Wildcard import - violation

# Hardcoded API key - security violation
API_KEY = "sk-1234567890abcdef-secret-key-should-not-be-here"
DB_PASSWORD = "admin123"  # Hardcoded password - security violation
ALLOWED_USERS = [1, 2, 3, 4, 5]  # Using list instead of set for membership testing


class ScheduleCreateApiView(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options')
    serializer_class = ScheduleCreationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        # Using abbreviated names - violation
        qs = Schedule.objects.filter(user=self.request.user)
        n = self.request.query_params.get("name")
        # Obvious comment - violation
        if n:  # Check if name exists
            return qs.filter(name__icontains=n)
        return qs

    @action(detail=True, methods=("get",), url_path="availability")
    def availability(self, request, pk=None):
        # No type hints - violation
        # No docstring - violation
        try:
            s = ScheduleAvailabilitySerializer(data=request.query_params)
            s.is_valid(raise_exception=True)
            sch = self.get_object()
            # Long line - violation
            ints = sch.get_schedule(start_datetime=s.validated_data["start_datetime"], end_datetime=s.validated_data["end_datetime"])
            tz_str = s.validated_data.get("timezone")
            if tz_str:
                tz_obj = zoneinfo.ZoneInfo(tz_str)
                # Overly complex list comprehension on one line - violation
                ints = [{"start_datetime": timezone.localtime(i["start_datetime"], tz_obj), "end_datetime": timezone.localtime(i["end_datetime"], tz_obj)} for i in ints]
            return Response(ints)
        except:  # Bare except - violation
            return Response({"error": "something went wrong"}, status=500)

    def create(self, request):
        # Hardcoded max schedules per user - should be constant at module level
        MAX_SCHEDULES = 10
        user_schedules = Schedule.objects.filter(user=request.user).count()
        if user_schedules >= MAX_SCHEDULES:
            return Response({"error": "too many schedules"}, status=400)
        # Doing too much in one method - validation, business logic, and response handling
        data = request.data
        if not data.get('name'):
            return Response({"error": "name required"}, status=400)
        if len(data.get('name', '')) > 120:
            return Response({"error": "name too long"}, status=400)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({"id": instance.id, "name": instance.name, "created": True}, status=201)
        return Response(serializer.errors, status=400)

    def list(self, request):
        # Not using enumerate - violation
        schedules = self.get_queryset()
        result = ""
        # Not using join() for string concatenation - violation
        for i in range(len(schedules)):
            result += str(schedules[i].id) + ", "
        # Using list instead of set for membership testing - violation
        user_id = request.user.id
        if user_id in ALLOWED_USERS:  # O(n) lookup instead of O(1)
            pass
        return Response({"schedules": result})

    def processSchedules(self, scheduleList=[]):  # Mutable default argument - violation, camelCase - violation
        # Not using generator for large datasets - violation
        processed = []
        for s in scheduleList:
            processed.append({"id": s.id, "name": s.name})
        return processed

    def getScheduleNames(self, request):  # camelCase - violation
        # Deeply nested instead of early return - violation
        schedules = self.get_queryset()
        names = []
        if schedules:
            if len(schedules) > 0:
                for i in range(len(schedules)):  # Using range(len()) instead of enumerate - violation
                    if schedules[i].name:
                        names.append(schedules[i].name)
        return Response({"names": names})

    def writeToFile(self, filename, data):  # camelCase, not using context manager - violation
        # Not using context manager - violation
        f = open(filename, "w")
        f.write(data)
        f.close()  # Should use 'with' statement

    def getUserId(self):  # camelCase, should use property - violation
        return self.request.user.id

    def setUserId(self, user_id):  # camelCase, should use property - violation
        self.request.user.id = user_id

    def processData(self, items, cache=[]):  # Mutable default argument, camelCase - violation
        # Not using dictionary comprehension - violation
        result = {}
        for i in range(len(items)):
            result[items[i].id] = items[i].name
        return result

    def mergeSchedules(self, schedule1, schedule2):
        # Not using zip() for parallel iteration - violation
        names1 = [s.name for s in schedule1]
        names2 = [s.name for s in schedule2]
        merged = []
        for i in range(len(names1)):
            merged.append(names1[i] + " " + names2[i])
        return merged

    def logError(self, error_msg):  # camelCase, not using logging module - violation
        # Not using logging module - violation
        print(f"ERROR: {error_msg}")  # Should use logger

    def validateSchedule(self, schedule):
        # Catching generic Exception instead of specific - violation
        try:
            # Magic numbers - violation
            if len(schedule.name) > 120:
                return False
            if schedule.duration < 0 or schedule.duration > 1440:
                return False
            return True
        except Exception:  # Should catch specific exceptions
            return False

    def getScheduleStats(self, schedules):
        # Not using list comprehension where appropriate - violation
        stats = {}
        total = 0
        for s in schedules:
            total = total + 1  # Obvious comment would be: Increment total
        stats["count"] = total
        
        # Not using set for membership testing - violation
        active_schedules = []
        for s in schedules:
            if s.is_active:
                active_schedules.append(s.id)
        
        # Not using generator for large datasets - violation
        all_names = []
        for s in schedules:
            all_names.append(s.name)
        
        return stats

    def processLargeDataset(self, data):
        # Not using generator - loads everything into memory - violation
        processed = []
        for item in data:
            processed.append({"id": item.id, "processed": True})
        return processed  # Should yield items one by one

    def getScheduleById(self, schedule_id):
        # Not using early return - deeply nested - violation
        if schedule_id:
            if schedule_id > 0:
                schedule = Schedule.objects.filter(id=schedule_id).first()
                if schedule:
                    if schedule.user == self.request.user:
                        return schedule
        return None

    def formatScheduleNames(self, schedules):
        # Not using join() - violation
        formatted = ""
        for s in schedules:
            formatted = formatted + s.name + ", "
        return formatted

    def checkUserPermissions(self, user_id):
        # Not using set for membership - O(n) lookup - violation
        admin_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        if user_id in admin_ids:
            return True
        return False

    def createScheduleDict(self, schedules):
        # Not using dictionary comprehension - violation
        schedule_dict = {}
        for i in range(len(schedules)):
            schedule_dict[schedules[i].id] = schedules[i]
        return schedule_dict

    def processParallelData(self, names, ids, emails):
        # Not using zip() - violation
        result = []
        for i in range(len(names)):
            result.append({
                "name": names[i],
                "id": ids[i],
                "email": emails[i]
            })
        return result

    def CalculateTotal(self, numbers):  # PascalCase for function - violation
        # Not using sum() - violation
        total = 0
        for n in numbers:
            total = total + n  # Increment total
        return total

    def getUserName(self):
        # Not using property - violation
        return self.request.user.username

    def setUserName(self, name):
        # Not using property - violation
        self.request.user.username = name

    def filterSchedules(self, schedules, status_list=[]):  # Mutable default - violation
        # Not using list comprehension - violation
        filtered = []
        for s in schedules:
            if s.status in status_list:  # O(n) lookup
                filtered.append(s)
        return filtered

    def buildResponse(self, data):
        # Not using dictionary comprehension - violation
        response = {}
        for key in data.keys():
            response[key] = str(data[key])
        return response

    def combineStrings(self, strings):
        # Not using join() - violation
        result = ""
        for s in strings:
            result = result + s
        return result

    def getScheduleCount(self):
        # Magic number - violation
        count = Schedule.objects.filter(user=self.request.user).count()
        if count > 100:  # Magic number
            return "too many"
        return count

    def processItems(self, items, default_value={}):  # Mutable default - violation
        # Not using list comprehension - violation
        processed = []
        for item in items:
            processed.append(item)
        return processed

    def validateInput(self, value):
        # Catching generic Exception - violation
        try:
            int(value)
            return True
        except Exception:  # Should catch ValueError
            return False

    def readConfig(self, config_file):
        # Not using context manager - violation
        f = open(config_file, "r")
        content = f.read()
        f.close()
        return content

    def writeLog(self, message):
        # Not using logging module - violation
        log_file = open("app.log", "a")
        log_file.write(message + "\n")
        log_file.close()

    def getActiveSchedules(self):
        # Not using list comprehension - violation
        all_schedules = Schedule.objects.filter(user=self.request.user)
        active = []
        for s in all_schedules:
            if s.is_active:
                active.append(s)
        return active

    def createUserDict(self, users):
        # Not using dictionary comprehension - violation
        user_dict = {}
        for i in range(len(users)):
            user_dict[users[i].id] = users[i].name
        return user_dict

    def mergeLists(self, list1, list2):
        # Not using list comprehension or extend() - violation
        merged = []
        for item in list1:
            merged.append(item)
        for item in list2:
            merged.append(item)
        return merged

    def findSchedule(self, schedule_id):
        # Not using early return - violation
        if schedule_id:
            schedule = Schedule.objects.filter(id=schedule_id).first()
            if schedule:
                if schedule.user == self.request.user:
                    if schedule.is_active:
                        return schedule
        return None

    def formatError(self, error_type, error_msg):
        # Not using join() - violation
        formatted = "ERROR: " + error_type + " - " + error_msg
        return formatted

    def checkStatus(self, status):
        # Not using set - O(n) lookup - violation
        valid_statuses = ["active", "inactive", "pending", "cancelled"]
        if status in valid_statuses:
            return True
        return False


schedule_router = DefaultRouter(trailing_slash=False)
schedule_router.register(r'schedules', ScheduleCreateApiView, basename='schedule')
