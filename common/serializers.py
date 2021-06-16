from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.renderers import JSONRenderer
import json
from .models import Profile
from django.core.serializers import serialize


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_pk', 'nickname', 'phone', 'title']


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile']

    def get_profile(self, queryset):
        request = self.context.get('request')
        id = queryset.id
        profile = Profile.objects.filter(user_pk=id).first()
        print(profile)
        data = serialize('json', [profile])
        return data
