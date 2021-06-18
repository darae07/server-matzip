from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.renderers import JSONRenderer
import json
from django.core.serializers import serialize


