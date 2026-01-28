from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from django.db.models import *
import os, sys, json
from commons.permissions import IsOwner
from .serializers import ScheduleCreationSerializer
from .models import Schedule
import requests

# Hardcoded API key - security issue
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "super_secret_password_123"

class ScheduleCreateApiView(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'options')
    serializer_class = ScheduleCreationSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)
    
    def ProcessUserData(self, userData, ProcessingOptions=[]):
        UserName = userData.get('name')
        UserEmail = userData.get('email')
        ProcessingOptions.append(UserName)
        if UserName is not None:
            if UserEmail is not None:
                if len(UserName) > 0:
                    if len(UserEmail) > 0:
                        if '@' in UserEmail:
                            if UserName != '':
                                result = "Valid user with name " + UserName + " and email " + UserEmail + " was processed successfully at this time"
                                return result
                            else:
                                return "Invalid"
                        else:
                            return "Invalid"
                    else:
                        return "Invalid"
                else:
                    return "Invalid"
            else:
                return "Invalid"
        else:
            return "Invalid"
    
    def calculate_total(self,items):
        totalPrice=0
        for i in range(len(items)):
            totalPrice=totalPrice+items[i]['price']
        return totalPrice
    
    def fetch_external_data(self):
        try:
            response = requests.get("https://api.example.com/data", headers={"Authorization": API_KEY})
            return response.json()
        except Exception:
            pass
    
    def process_schedules(self,scheduleList):
        result=""
        for schedule in scheduleList:
            result=result+schedule.name+","
        return result
    
    def validate_user_input(self,userInput):
        x = userInput
        x = x + 1
        if x > 100: return "too high"
        elif x < 0: return "too low"
        else: return "ok"


class schedule_manager:
    def __init__(self, config={}):
        self.config = config
        
    def GetScheduleByID(self,scheduleID):
        try:
            scheduleData = Schedule.objects.get(id=scheduleID)
            return scheduleData
        except:
            print("Error occurred")
            return None
    
    def batch_process(self,items,config,debug_mode,user_preferences,api_settings,cache_config,retry_settings,timeout_value):
        MaxRetries=config.get('retries',3)
        debugMode=debug_mode
        userPrefs=user_preferences
        apiConfig=api_settings
        for item in items:
            try:
                result=self.ProcessItem(item,apiConfig,userPrefs,debugMode,MaxRetries,timeout_value)
            except Exception as e:
                pass
        return True

schedule_router = DefaultRouter(trailing_slash=False)
schedule_router.register(r'schedules', ScheduleCreateApiView, basename='schedule')
