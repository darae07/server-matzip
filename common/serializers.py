from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.renderers import JSONRenderer
import json
from django.core.serializers import serialize
from .models import CommonUser


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonUser
        fields = ['id', 'username', 'email', 'last_login', 'is_superuser', 'is_staff',
                  'date_joined', 'greetings', 'nickname']

